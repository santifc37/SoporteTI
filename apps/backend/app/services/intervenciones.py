
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Asignacion, Intervencion, Solicitud
from app.schemas.intervencion import CrearIntervencion


def registrar_intervencion(
    db: Session,
    solicitud_id: uuid.UUID,
    tecnico_id: uuid.UUID,
    datos: CrearIntervencion,
) -> Intervencion:
    """RF-16: registra una intervención del técnico asignado."""

    solicitud = db.scalar(
        select(Solicitud).where(Solicitud.id == solicitud_id)
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
            "No se pueden registrar intervenciones en una solicitud cerrada.",
        )

    intervencion = Intervencion(
        solicitud_id=solicitud_id,
        tecnico_id=tecnico_id,
        descripcion=datos.descripcion.strip(),
        diagnostico=(
            datos.diagnostico.strip()
            if datos.diagnostico and datos.diagnostico.strip()
            else None
        ),
        visibilidad=datos.visibilidad,
    )

    try:
        db.add(intervencion)
        db.commit()
        db.refresh(intervencion)
        return intervencion

    except Exception:
        db.rollback()
        raise
