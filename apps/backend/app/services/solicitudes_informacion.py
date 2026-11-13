
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import (
    Asignacion,
    RespuestaInformacion,
    Solicitud,
    SolicitudInformacion,
    Usuario,
)
from app.schemas.respuesta_informacion import CrearRespuestaInformacion
from app.schemas.solicitud_informacion import CrearSolicitudInformacion


def _obtener_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
) -> Solicitud:
    solicitud = db.scalar(
        select(Solicitud).where(Solicitud.id == solicitud_id)
    )

    if solicitud is None:
        raise ApiError(
            404,
            "SOLICITUD_NO_ENCONTRADA",
            "La solicitud indicada no existe.",
        )

    return solicitud


def _verificar_acceso(
    db: Session,
    solicitud: Solicitud,
    usuario_id: uuid.UUID,
    rol: str,
) -> None:
    """Comprueba el acceso del usuario a las peticiones de información."""

    if rol == "coordinador":
        return

    if rol == "solicitante":
        if solicitud.solicitante_id == usuario_id:
            return

    elif rol == "tecnico":
        asignacion = db.scalar(
            select(Asignacion).where(
                Asignacion.solicitud_id == solicitud.id,
                Asignacion.tecnico_id == usuario_id,
                Asignacion.fecha_finalizacion.is_(None),
            )
        )

        if asignacion is not None:
            return

    raise ApiError(
        403,
        "SIN_PERMISO",
        "No tienes permiso para consultar esta información.",
    )


def crear_solicitud_informacion(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    datos: CrearSolicitudInformacion,
) -> SolicitudInformacion:
    """RF-18: permite al técnico asignado o al coordinador crear peticiones."""

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

    if rol == "tecnico":
        asignacion = db.scalar(
            select(Asignacion).where(
                Asignacion.solicitud_id == solicitud_id,
                Asignacion.tecnico_id == usuario_id,
                Asignacion.fecha_finalizacion.is_(None),
            )
        )

        if asignacion is None:
            raise ApiError(
                403,
                "SIN_PERMISO",
                "No tienes una asignación activa para esta solicitud.",
            )

    elif rol != "coordinador":
        raise ApiError(
            403,
            "SIN_PERMISO",
            "No tienes permiso para solicitar información adicional.",
        )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se puede solicitar información en una solicitud cerrada.",
        )

    peticion = SolicitudInformacion(
        solicitud_id=solicitud_id,
        solicitado_por=usuario_id,
        contenido=datos.contenido,
        estado="pendiente",
    )

    try:
        db.add(peticion)
        db.commit()
        db.refresh(peticion)
        return peticion

    except Exception:
        db.rollback()
        raise


def consultar_solicitudes_informacion(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> list[dict]:
    """RF-18: consulta las peticiones y sus respuestas según los permisos."""

    solicitud = _obtener_solicitud(db, solicitud_id)

    _verificar_acceso(
        db=db,
        solicitud=solicitud,
        usuario_id=usuario_id,
        rol=rol,
    )

    resultados = db.execute(
        select(SolicitudInformacion, Usuario)
        .join(
            Usuario,
            Usuario.id == SolicitudInformacion.solicitado_por,
        )
        .where(SolicitudInformacion.solicitud_id == solicitud_id)
        .order_by(SolicitudInformacion.fecha_solicitud.asc())
    ).all()

    peticiones = []

    for peticion, autor in resultados:
        respuesta = db.scalar(
            select(RespuestaInformacion).where(
                RespuestaInformacion.solicitud_informacion_id
                == peticion.id
            )
        )

        peticiones.append(
            {
                "id": peticion.id,
                "contenido": peticion.contenido,
                "estado": peticion.estado,
                "solicitado_por": {
                    "id": autor.id,
                    "nombre": f"{autor.nombre} {autor.apellido}",
                    "rol": autor.rol,
                },
                "fecha_solicitud": peticion.fecha_solicitud,
                "respuesta": (
                    {
                        "id": respuesta.id,
                        "respondido_por": respuesta.respondido_por,
                        "contenido": respuesta.contenido,
                        "fecha_respuesta": respuesta.fecha_respuesta,
                    }
                    if respuesta is not None
                    else None
                ),
            }
        )

    return peticiones


def responder_solicitud_informacion(
    db: Session,
    solicitud_informacion_id: uuid.UUID,
    solicitante_id: uuid.UUID,
    datos: CrearRespuestaInformacion,
) -> RespuestaInformacion:
    """RF-18: registra la respuesta del solicitante propietario."""

    peticion = db.scalar(
        select(SolicitudInformacion)
        .where(SolicitudInformacion.id == solicitud_informacion_id)
        .with_for_update()
    )

    if peticion is None:
        raise ApiError(
            404,
            "PETICION_NO_ENCONTRADA",
            "La petición de información indicada no existe.",
        )

    solicitud = _obtener_solicitud(db, peticion.solicitud_id)

    if solicitud.solicitante_id != solicitante_id:
        raise ApiError(
            403,
            "SIN_PERMISO",
            "No puedes responder peticiones de otra solicitud.",
        )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se puede responder una petición de una solicitud cerrada.",
        )

    if peticion.estado != "pendiente":
        raise ApiError(
            409,
            "PETICION_NO_PENDIENTE",
            "Esta petición ya fue respondida.",
        )

    respuesta_existente = db.scalar(
        select(RespuestaInformacion).where(
            RespuestaInformacion.solicitud_informacion_id == peticion.id
        )
    )

    if respuesta_existente is not None:
        raise ApiError(
            409,
            "PETICION_YA_RESPONDIDA",
            "Esta petición ya tiene una respuesta registrada.",
        )

    respuesta = RespuestaInformacion(
        solicitud_informacion_id=peticion.id,
        respondido_por=solicitante_id,
        contenido=datos.contenido,
    )

    try:
        db.add(respuesta)
        peticion.estado = "respondida"
        db.commit()
        db.refresh(respuesta)
        return respuesta

    except Exception:
        db.rollback()
        raise
