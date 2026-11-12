
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.schemas.solucion import RegistrarSolucion

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
    return [
        Asignacion.tecnico_id == tecnico_id,
        Asignacion.fecha_finalizacion.is_(None),
        *_condiciones_de_filtros(filtros),
    ]


def _condiciones_de_filtros(filtros: FiltrosSolicitudes) -> list:
    """Condiciones de los filtros comunes a todos los roles (RF-07, RF-13)."""
    condiciones = []

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


def registrar_solucion(
    db: Session,
    solicitud_id: uuid.UUID,
    tecnico_id: uuid.UUID,
    datos: RegistrarSolucion,
) -> tuple[Solicitud, str]:
    """RF-19: registra la solución y marca la solicitud como resuelta."""

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

    if solicitud.estado not in {"en_atencion", "en_espera"}:
        raise ApiError(
            409,
            "TRANSICION_NO_PERMITIDA",
            "Solo se puede registrar una solución cuando la solicitud está en atención o en espera.",
        )

    estado_anterior = solicitud.estado
    fecha_resolucion = datetime.now(timezone.utc)

    try:
        solicitud.estado = "resuelto"
        solicitud.solucion_final = datos.solucion
        solicitud.resuelto_por = tecnico_id
        solicitud.fecha_resolucion = fecha_resolucion
        solicitud.fecha_actualizacion = fecha_resolucion
        solicitud.version += 1

        historial = HistorialCambio(
            solicitud_id=solicitud.id,
            usuario_id=tecnico_id,
            tipo_cambio="solucion",
            valor_anterior=estado_anterior,
            valor_nuevo=datos.solucion,
        )

        db.add(historial)
        db.commit()
        db.refresh(solicitud)

        return solicitud, estado_anterior

    except Exception:
        db.rollback()
        raise


# ------------------------------ RF-06: crear solicitud ------------------------------

from app.schemas.solicitud import CrearSolicitud


def crear_solicitud(
    db: Session,
    solicitante_id: uuid.UUID,
    datos: CrearSolicitud,
) -> Solicitud:
    """RF-06: registra una solicitud en estado `registrado`.

    - El solicitante es el usuario de la sesión, nunca un dato del cliente.
    - La prioridad queda vacía: la asigna el coordinador al evaluarla (RN-10).
    - La categoría es opcional, pero si se envía debe existir y estar activa.
    - La solicitud y su registro de creación en el historial se guardan en la
      misma transacción (contrato-api.md §19, regla 1).
    - El número legible (ST-000001) lo genera PostgreSQL con una secuencia.
    """

    if datos.categoria_id is not None:
        categoria = db.get(Categoria, datos.categoria_id)
        if categoria is None or not categoria.activa:
            raise ApiError(
                422,
                "ERROR_VALIDACION",
                "Los datos enviados no son válidos.",
                [
                    {
                        "campo": "categoria_id",
                        "mensaje": "La categoría no existe o no está activa.",
                    }
                ],
            )

    solicitud = Solicitud(
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        tipo=datos.tipo,
        categoria_id=datos.categoria_id,
        ubicacion=datos.ubicacion,
        placa_equipo=datos.placa_equipo or None,
        medio_contacto=datos.medio_contacto,
        dato_contacto=datos.dato_contacto,
        solicitante_id=solicitante_id,
        estado="registrado",
    )

    try:
        db.add(solicitud)
        db.flush()  # inserta la solicitud antes que su registro de historial

        db.add(
            HistorialCambio(
                solicitud_id=solicitud.id,
                usuario_id=solicitante_id,
                tipo_cambio="creacion",
                valor_nuevo="registrado",
                observacion="Registro de la solicitud",
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(solicitud)
    return solicitud



# --------------------------- RF-07: consulta de solicitudes ---------------------------

from sqlalchemy import and_

from app.schemas.solicitud import SolicitudDetalle


def listar_solicitudes(
    db: Session,
    filtros: FiltrosSolicitudes,
    page: int,
    limit: int,
    *,
    solicitante_id: uuid.UUID | None = None,
    tecnico_id: uuid.UUID | None = None,
    tipo_cierre: str | None = None,
) -> SolicitudesPagina:
    """RF-07: lista solicitudes para el solicitante (propias) y el coordinador (todas).

    El técnico asignado se toma de la asignación activa; las solicitudes sin
    asignar aparecen con `tecnico_asignado = null`.
    """

    asignacion_activa = aliased(Asignacion)
    union_asignacion = and_(
        asignacion_activa.solicitud_id == Solicitud.id,
        asignacion_activa.fecha_finalizacion.is_(None),
    )

    condiciones = _condiciones_de_filtros(filtros)
    if solicitante_id:
        condiciones.append(Solicitud.solicitante_id == solicitante_id)
    if tecnico_id:
        condiciones.append(asignacion_activa.tecnico_id == tecnico_id)
    if tipo_cierre:
        condiciones.append(Solicitud.tipo_cierre == tipo_cierre)

    total = db.scalar(
        select(func.count(Solicitud.id))
        .select_from(Solicitud)
        .outerjoin(asignacion_activa, union_asignacion)
        .where(*condiciones)
    )

    solicitante = aliased(Usuario)
    tecnico = aliased(Usuario)

    filas = db.execute(
        select(Solicitud, solicitante, Categoria, tecnico)
        .join(solicitante, solicitante.id == Solicitud.solicitante_id)
        .outerjoin(Categoria, Categoria.id == Solicitud.categoria_id)
        .outerjoin(asignacion_activa, union_asignacion)
        .outerjoin(tecnico, tecnico.id == asignacion_activa.tecnico_id)
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
            tecnico_asignado=(
                UsuarioResumen(id=tec.id, nombre=_nombre_completo(tec)) if tec else None
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


def obtener_solicitud_detalle(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> SolicitudDetalle:
    """RF-07: detalle de una solicitud según los permisos del usuario.

    - Solicitante: solo las propias.
    - Técnico: solo si la tiene asignada actualmente (RN-05).
    - Coordinador: cualquiera.
    """

    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la solicitud.")

    asignacion = db.scalar(
        select(Asignacion).where(
            Asignacion.solicitud_id == solicitud.id,
            Asignacion.fecha_finalizacion.is_(None),
        )
    )

    if rol == "solicitante":
        autorizado = solicitud.solicitante_id == usuario_id
    elif rol == "tecnico":
        autorizado = asignacion is not None and asignacion.tecnico_id == usuario_id
    else:
        autorizado = rol == "coordinador"

    if not autorizado:
        raise ApiError(
            403, "PERMISO_DENEGADO", "No tienes permisos para consultar esta solicitud."
        )

    solicitante = db.get(Usuario, solicitud.solicitante_id)
    categoria = db.get(Categoria, solicitud.categoria_id) if solicitud.categoria_id else None
    tecnico = db.get(Usuario, asignacion.tecnico_id) if asignacion else None

    return SolicitudDetalle(
        id=solicitud.id,
        numero=solicitud.numero,
        titulo=solicitud.titulo,
        descripcion=solicitud.descripcion,
        tipo=solicitud.tipo,
        prioridad=solicitud.prioridad,
        estado=solicitud.estado,
        ubicacion=solicitud.ubicacion,
        placa_equipo=solicitud.placa_equipo,
        medio_contacto=solicitud.medio_contacto,
        dato_contacto=solicitud.dato_contacto,
        solicitante=UsuarioResumen(
            id=solicitante.id, nombre=_nombre_completo(solicitante)
        ),
        categoria=(
            CategoriaResumen(id=categoria.id, nombre=categoria.nombre)
            if categoria
            else None
        ),
        tecnico_asignado=(
            UsuarioResumen(id=tecnico.id, nombre=_nombre_completo(tecnico))
            if tecnico
            else None
        ),
        solucion_final=solicitud.solucion_final,
        resuelto_por=solicitud.resuelto_por,
        fecha_resolucion=solicitud.fecha_resolucion,
        tipo_cierre=solicitud.tipo_cierre,
        motivo_cierre=solicitud.motivo_cierre,
        fecha_creacion=solicitud.fecha_creacion,
        fecha_actualizacion=solicitud.fecha_actualizacion,
        fecha_cierre=solicitud.fecha_cierre,
    )



# ---------------------- RF-09: inicio de la evaluación (coordinador) ----------------------

from app.schemas.solicitud import ClasificarSolicitud


def _solicitud_para_modificar(db: Session, solicitud_id: uuid.UUID) -> Solicitud:
    """Obtiene la solicitud bloqueándola para evitar cambios simultáneos."""
    solicitud = db.scalar(
        select(Solicitud).where(Solicitud.id == solicitud_id).with_for_update()
    )
    if solicitud is None:
        raise ApiError(
            404,
            "SOLICITUD_NO_ENCONTRADA",
            "La solicitud indicada no existe.",
        )
    return solicitud


def iniciar_evaluacion(
    db: Session,
    solicitud_id: uuid.UUID,
    coordinador_id: uuid.UUID,
    nuevo_estado: str,
) -> tuple[Solicitud, str]:
    """RF-09 / RF-14: el coordinador pasa una solicitud de `registrado` a `en_evaluacion`.

    Es la única transición que el coordinador hace por esta ruta; las demás
    son del técnico asignado (en_atencion, en_espera) o tienen ruta propia
    (asignación, resolución, cierre y cancelación).
    """

    if nuevo_estado != "en_evaluacion":
        raise ApiError(
            403,
            "PERMISO_DENEGADO",
            "Ese cambio de estado le corresponde al técnico asignado.",
        )

    solicitud = _solicitud_para_modificar(db, solicitud_id)

    if solicitud.estado != "registrado":
        raise ApiError(
            409,
            "ESTADO_NO_PERMITIDO",
            "Solo se puede iniciar la evaluación de una solicitud registrada.",
        )

    estado_anterior = solicitud.estado

    try:
        solicitud.estado = "en_evaluacion"
        solicitud.fecha_actualizacion = datetime.now(timezone.utc)
        solicitud.version += 1

        db.add(
            HistorialCambio(
                solicitud_id=solicitud.id,
                usuario_id=coordinador_id,
                tipo_cambio="cambio_estado",
                valor_anterior=estado_anterior,
                valor_nuevo="en_evaluacion",
                observacion="Inicio de evaluación",
            )
        )
        db.commit()
        db.refresh(solicitud)
        return solicitud, estado_anterior

    except Exception:
        db.rollback()
        raise


# ------------------------- RF-10: clasificación y prioridad -------------------------


def clasificar_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
    coordinador_id: uuid.UUID,
    datos: ClasificarSolicitud,
) -> Solicitud:
    """RF-10: el coordinador establece la categoría y la prioridad.

    - No se modifican solicitudes cerradas (RN-22).
    - La categoría debe existir y estar activa.
    - Cada cambio real queda en el historial (RN-30); enviar el mismo valor
      no genera registros.
    """

    solicitud = _solicitud_para_modificar(db, solicitud_id)

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se puede modificar una solicitud cerrada.",
        )

    cambios = datos.model_dump(exclude_unset=True)
    registros: list[HistorialCambio] = []

    if "categoria_id" in cambios and cambios["categoria_id"] != solicitud.categoria_id:
        nueva = None
        if cambios["categoria_id"] is not None:
            nueva = db.get(Categoria, cambios["categoria_id"])
            if nueva is None or not nueva.activa:
                raise ApiError(
                    422,
                    "ERROR_VALIDACION",
                    "Los datos enviados no son válidos.",
                    [
                        {
                            "campo": "categoria_id",
                            "mensaje": "La categoría no existe o no está activa.",
                        }
                    ],
                )
        anterior = (
            db.get(Categoria, solicitud.categoria_id) if solicitud.categoria_id else None
        )
        registros.append(
            HistorialCambio(
                solicitud_id=solicitud.id,
                usuario_id=coordinador_id,
                tipo_cambio="cambio_categoria",
                valor_anterior=anterior.nombre if anterior else None,
                valor_nuevo=nueva.nombre if nueva else None,
            )
        )
        solicitud.categoria_id = cambios["categoria_id"]

    if "prioridad" in cambios and cambios["prioridad"] != solicitud.prioridad:
        registros.append(
            HistorialCambio(
                solicitud_id=solicitud.id,
                usuario_id=coordinador_id,
                tipo_cambio="cambio_prioridad",
                valor_anterior=solicitud.prioridad,
                valor_nuevo=cambios["prioridad"],
            )
        )
        solicitud.prioridad = cambios["prioridad"]

    if not registros:
        return solicitud  # nada cambió

    try:
        solicitud.fecha_actualizacion = datetime.now(timezone.utc)
        solicitud.version += 1
        db.add_all(registros)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    except Exception:
        db.rollback()
        raise
