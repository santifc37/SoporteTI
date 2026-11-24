
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Adjunto
from app.services.intervenciones import consultar_intervenciones


def consultar_adjuntos_intervencion(
    db: Session,
    solicitud_id: uuid.UUID,
    intervencion_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> list[dict]:
    """Consulta las imágenes de una intervención y genera sus URL firmadas."""

    # Valida que el usuario pueda consultar las intervenciones de la solicitud.
    intervenciones = consultar_intervenciones(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario_id,
        rol=rol,
    )

    # También comprueba que la intervención pertenezca a la solicitud
    # y que sea visible para el usuario según sus permisos.
    intervencion_valida = any(
        intervencion["id"] == intervencion_id
        for intervencion in intervenciones
    )

    if not intervencion_valida:
        raise ApiError(
            404,
            "INTERVENCION_NO_ENCONTRADA",
            "La intervención no existe o no tienes permiso para consultarla.",
        )

    adjuntos = db.scalars(
        select(Adjunto)
        .where(
            Adjunto.solicitud_id == solicitud_id,
            Adjunto.intervencion_id == intervencion_id,
            Adjunto.mensaje_id.is_(None),
        )
        .order_by(Adjunto.fecha_subida.asc())
    ).all()

    return [
        {
            "id": adjunto.id,
            "intervencion_id": adjunto.intervencion_id,
            "nombre_archivo": adjunto.nombre_archivo,
            "tipo_archivo": adjunto.tipo_archivo,
            "tamano": adjunto.tamano,
            "fecha_subida": adjunto.fecha_subida,
            "url": f"/api/v1/attachments/{adjunto.id}/download",
        }
        for adjunto in adjuntos
    ]
