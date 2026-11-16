
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Adjunto, Mensaje, Solicitud
from app.services.adjuntos import (
    TAMANO_MAXIMO_ENTRADA,
    TIPO_WEBP,
    ErrorImagen,
    ErrorStorage,
    convertir_a_webp,
    eliminar_de_storage,
    subir_a_storage,
)
from app.services.mensajes import _solicitud_accesible


def registrar_adjunto_mensaje(
    db: Session,
    solicitud_id: uuid.UUID,
    mensaje_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    archivo,
) -> Adjunto:
    """RF-24: convierte y asocia una imagen WebP a un mensaje."""

    solicitud = _solicitud_accesible(
        db, solicitud_id, usuario_id, rol
    )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se pueden adjuntar imágenes a una solicitud cerrada.",
        )

    mensaje = db.scalar(
        select(Mensaje).where(
            Mensaje.id == mensaje_id,
            Mensaje.solicitud_id == solicitud_id,
        )
    )

    if mensaje is None:
        raise ApiError(
            404,
            "MENSAJE_NO_ENCONTRADO",
            "El mensaje no existe en esta solicitud.",
        )

    contenido_original = archivo.file.read(
        TAMANO_MAXIMO_ENTRADA + 1
    )

    try:
        contenido_webp = convertir_a_webp(contenido_original)
    except ErrorImagen as error:
        raise ApiError(
            422,
            "IMAGEN_NO_VALIDA",
            str(error),
        ) from error

    ruta_storage = (
        f"solicitudes/{solicitud_id}/"
        f"mensajes/{mensaje_id}/{uuid.uuid4()}.webp"
    )

    nombre_original = Path(
        archivo.filename or "imagen"
    ).name[:255]

    subir_a_storage(ruta_storage, contenido_webp)

    adjunto = Adjunto(
        solicitud_id=solicitud_id,
        mensaje_id=mensaje_id,
        intervencion_id=None,
        subido_por=usuario_id,
        nombre_archivo=nombre_original,
        ruta_storage=ruta_storage,
        tipo_archivo=TIPO_WEBP,
        tamano=len(contenido_webp),
    )

    try:
        db.add(adjunto)
        db.commit()
        db.refresh(adjunto)
        return adjunto

    except Exception:
        db.rollback()

        try:
            eliminar_de_storage(ruta_storage)
        except ErrorStorage:
            pass

        raise


def consultar_adjuntos_mensaje(
    db: Session,
    solicitud_id: uuid.UUID,
    mensaje_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> list[Adjunto]:
    """RF-24: lista los adjuntos de un mensaje autorizado."""

    _solicitud_accesible(
        db, solicitud_id, usuario_id, rol
    )

    mensaje = db.scalar(
        select(Mensaje).where(
            Mensaje.id == mensaje_id,
            Mensaje.solicitud_id == solicitud_id,
        )
    )

    if mensaje is None:
        raise ApiError(
            404,
            "MENSAJE_NO_ENCONTRADO",
            "El mensaje no existe en esta solicitud.",
        )

    return list(
        db.scalars(
            select(Adjunto)
            .where(
                Adjunto.solicitud_id == solicitud_id,
                Adjunto.mensaje_id == mensaje_id,
            )
            .order_by(
                Adjunto.fecha_subida.asc(),
                Adjunto.id.asc(),
            )
        ).all()
    )
