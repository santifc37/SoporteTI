
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.core.errors import ApiError
from app.models import Asignacion, Categoria, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio
from app.schemas.pagination import Pagination, calcular_total_paginas
from app.schemas.solicitud import (
    CategoriaResumen,
    SolicitudesPagina,
    SolicitudResumen,
    UsuarioResumen,
)


@dataclass(frozen=True)
class FiltrosSolicitudes:
    """Filtros opcionales de las solicitudes asignadas al técnico."""

    estado: str | None = None
    prioridad: str | None = None
    categoria_id: uuid.UUID | None = None
    tipo: str | None = None
    busqueda: str | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None


def _condiciones(tecnico_id: uuid.UUID, filtros: FiltrosSolicitudes) -> list:
    """Condiciones de consulta: asignación activa del técnico y filtros."""
    condiciones = [
        Asignacion.tecnico_id == tecnico_id,
        Asignacion.fecha_finalizacion.is_(None),
    ]

    if filtros.estado:
        condiciones.append(Solicitud.estado == filtros.estado)
    if filtros.prioridad:
        condiciones.append(Solicitud.prioridad == filtros.prioridad)
    if filtros.categoria_id:
        condiciones.append(Solicitud.categoria_id == filtros.categoria_id)
    if filtros.tipo:
        condiciones.append(Solicitud.tipo == filtros.tipo)
    if filtros.busqueda:
        patron = f"%{filtros.busqueda.strip()}%"
        condiciones.append(
            or_(Solicitud.numero.ilike(patron), Solicitud.titulo.ilike(patron))
        )
    if filtros.fecha_desde:
        condiciones.append(Solicitud.fecha_creacion >= filtros.fecha_desde)
    if filtros.fecha_hasta:
        condiciones.append(Solicitud.fecha_creacion <= filtros.fecha_hasta)

    return condiciones


def _nombre_completo(usuario: Usuario) -> str:
    return f"{usuario.nombre} {usuario.apellido}".strip()


def listar_solicitudes_asignadas(
    db: Session,
    tecnico_id: uuid.UUID,
    filtros: FiltrosSolicitudes,
    page: int,
    limit: int,
) -> SolicitudesPagina:
    """RF-13: consulta las solicitudes asignadas actualmente al técnico."""

    condiciones = _condiciones(tecnico_id, filtros)

    total = db.scalar(
        select(func.count(Solicitud.id))
        .join(Asignacion, Asignacion.solicitud_id == Solicitud.id)
        .where(*condiciones)
    )

    solicitante = aliased(Usuario)
    tecnico = aliased(Usuario)

    filas = db.execute(
        select(Solicitud, solicitante, Categoria, tecnico)
        .join(Asignacion, Asignacion.solicitud_id == Solicitud.id)
        .join(tecnico, tecnico.id == Asignacion.tecnico_id)
        .join(solicitante, solicitante.id == Solicitud.solicitante_id)
        .outerjoin(Categoria, Categoria.id == Solicitud.categoria_id)
        .where(*condiciones)
        .order_by(Solicitud.fecha_creacion.desc(), Solicitud.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    data = [
        SolicitudResumen(
            id=sol.id,
            numero=sol.numero,
            titulo=sol.titulo,
            tipo=sol.tipo,
            prioridad=sol.prioridad,
            estado=sol.estado,
            categoria=(
                CategoriaResumen(id=cat.id, nombre=cat.nombre) if cat else None
            ),
            solicitante=UsuarioResumen(
                id=sol_user.id,
                nombre=_nombre_completo(sol_user),
            ),
            tecnico_asignado=UsuarioResumen(
                id=tec.id,
                nombre=_nombre_completo(tec),
            ),
            fecha_creacion=sol.fecha_creacion,
        )
        for sol, sol_user, cat, tec in filas
    ]

    return SolicitudesPagina(
        data=data,
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=calcular_total_paginas(total, limit),
        ),
    )


def actualizar_estado_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
    tecnico_id: uuid.UUID,
    nuevo_estado: str,
) -> tuple[Solicitud, str]:
    """RF-14: actualiza el estado de una solicitud asignada al técnico."""

    solicitud = db.scalar(
        select(Solicitud)
        .where(Solicitud.id == solicitud_id)
        .with_for_update()
    )

    if solicitud is None:
        raise ApiError(
            404,
            "SOLICITUD_NO_ENCONTRADA",
            "La solicitud indicada no existe.",
        )

    asignacion = db.scalar(
        select(Asignacion)
        .where(
            Asignacion.solicitud_id == solicitud_id,
            Asignacion.tecnico_id == tecnico_id,
            Asignacion.fecha_finalizacion.is_(None),
        )
        .with_for_update()
    )

    if asignacion is None:
        raise ApiError(
            403,
            "SIN_PERMISO",
            "No tienes una asignación activa para esta solicitud.",
        )

    transiciones = {
        "asignado": {"en_atencion"},
        "en_atencion": {"en_espera"},
        "en_espera": {"en_atencion"},
    }

    if nuevo_estado not in transiciones.get(solicitud.estado, set()):
        raise ApiError(
            409,
            "TRANSICION_NO_PERMITIDA",
            "No se permite realizar ese cambio de estado.",
        )

    estado_anterior = solicitud.estado

    try:
        solicitud.estado = nuevo_estado
        solicitud.fecha_actualizacion = datetime.now(timezone.utc)
        solicitud.version += 1

        historial = HistorialCambio(
            solicitud_id=solicitud.id,
            usuario_id=tecnico_id,
            tipo_cambio="cambio_estado",
            valor_anterior=estado_anterior,
            valor_nuevo=nuevo_estado,
        )

        db.add(historial)
        db.commit()
        db.refresh(solicitud)

        return solicitud, estado_anterior

    except Exception:
        db.rollback()
        raise
