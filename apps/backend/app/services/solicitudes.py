import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import Asignacion, Categoria, Solicitud, Usuario
from app.schemas.pagination import Pagination, calcular_total_paginas
from app.schemas.solicitud import (
    CategoriaResumen,
    SolicitudesPagina,
    SolicitudResumen,
    UsuarioResumen,
)


@dataclass(frozen=True)
class FiltrosSolicitudes:
    """Filtros opcionales de docs/contrato-api.md §7.1 que aplican al técnico.

    `tecnico_id` y `solicitante_id` no existen a propósito: los filtros no
    pueden ampliar los permisos del usuario (contrato §17).
    """

    estado: str | None = None
    prioridad: str | None = None
    categoria_id: uuid.UUID | None = None
    tipo: str | None = None
    busqueda: str | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None


def _condiciones(tecnico_id: uuid.UUID, filtros: FiltrosSolicitudes) -> list:
    """Condiciones WHERE: asignación activa del técnico + filtros opcionales."""
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
    """RF-13: solicitudes asignadas actualmente al técnico (RN-05).

    Una solicitud pertenece al técnico mientras su asignación esté activa
    (`fecha_finalizacion IS NULL`). Tras una reasignación el técnico anterior
    deja de verla (RN-14). Las solicitudes cerradas siguen visibles porque
    son de solo consulta (RN-23); se pueden excluir con el filtro `estado`.
    """
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
        # Orden estable: el desempate por id evita repetidos entre páginas.
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
            solicitante=UsuarioResumen(id=sol_user.id, nombre=_nombre_completo(sol_user)),
            tecnico_asignado=UsuarioResumen(id=tec.id, nombre=_nombre_completo(tec)),
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
