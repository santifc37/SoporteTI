import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Asignacion, Solicitud, SolicitudInformacion
from app.schemas.solicitud_informacion import CrearSolicitudInformacion


def crear_solicitud_informacion(
    db: Session,
    solicitud_id: uuid.UUID,
    tecnico_id: uuid.UUID,
    datos: CrearSolicitudInformacion,
) -> SolicitudInformacion:
    """RF-18: permite al técnico asignado solicitar información adicional."""

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
        select(Asignacion).where(
            Asignacion.solicitud_id == solicitud_id,
            Asignacion.tecnico_id == tecnico_id,
            Asignacion.fecha_finalizacion.is_(None),
        )
    )

    if asignacion is None:
        raise ApiError(
            403,
            "SIN_PERMISO",
            "No tienes una asignación activa para esta solicitud.",
        )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se puede solicitar información en una solicitud cerrada.",
        )

    peticion = SolicitudInformacion(
        solicitud_id=solicitud_id,
        solicitado_por=tecnico_id,
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