
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Adjunto, Asignacion, Solicitud
from app.services.adjuntos import (
    TAMANO_MAXIMO_ENTRADA,
    TIPO_WEBP,
    ErrorImagen,
    ErrorStorage,
    convertir_a_webp,
    eliminar_de_storage,
    subir_a_storage,
    leer_de_storage,
)


def _obtener_solicitud_autorizada(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> Solicitud:
    """Valida que el usuario pueda consultar la solicitud."""

    solicitud = db.get(Solicitud, solicitud_id)

    if solicitud is None:
        raise ApiError(
            404,
            "SOLICITUD_NO_ENCONTRADA",
            "La solicitud indicada no existe.",
        )

    if rol == "solicitante":
        autorizado = solicitud.solicitante_id == usuario_id

    elif rol == "tecnico":
        asignacion = db.scalar(
            select(Asignacion).where(
                Asignacion.solicitud_id == solicitud_id,
                Asignacion.tecnico_id == usuario_id,
                Asignacion.fecha_finalizacion.is_(None),
            )
        )
        autorizado = asignacion is not None

    elif rol == "coordinador":
        autorizado = True

    else:
        autorizado = False

    if not autorizado:
        raise ApiError(
            403,
            "PERMISO_DENEGADO",
            "No tienes permisos para consultar los adjuntos de esta solicitud.",
        )

    return solicitud


def registrar_adjunto_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    archivo,
) -> Adjunto:
    """RF-08: registra una imagen directamente en una solicitud."""

    solicitud = _obtener_solicitud_autorizada(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario_id,
        rol=rol,
    )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se pueden adjuntar imágenes a una solicitud cerrada.",
        )

    contenido_original = archivo.file.read(TAMANO_MAXIMO_ENTRADA + 1)

    try:
        contenido_webp = convertir_a_webp(contenido_original)
    except ErrorImagen as error:
        raise ApiError(
            422,
            "IMAGEN_NO_VALIDA",
            str(error),
        ) from error

    ruta_storage = (
        f"solicitudes/{solicitud_id}/attachments/{uuid.uuid4()}.webp"
    )

    nombre_original = Path(archivo.filename or "imagen").name[:255]

    subir_a_storage(ruta_storage, contenido_webp)

    adjunto = Adjunto(
        solicitud_id=solicitud_id,
        mensaje_id=None,
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


def consultar_adjuntos_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> list[Adjunto]:
    """RF-08: consulta los adjuntos asociados directamente a una solicitud."""

    _obtener_solicitud_autorizada(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario_id,
        rol=rol,
    )

    return list(
        db.scalars(
            select(Adjunto)
            .where(
                Adjunto.solicitud_id == solicitud_id,
                Adjunto.mensaje_id.is_(None),
                Adjunto.intervencion_id.is_(None),
            )
            .order_by(Adjunto.fecha_subida.desc(), Adjunto.id.desc())
        ).all()
    )


def descargar_adjunto(
    db: Session,
    adjunto_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> tuple[Adjunto, bytes]:
    """Valida permisos y obtiene el archivo privado desde disco local."""
    adjunto = db.get(Adjunto, adjunto_id)
    if adjunto is None:
        raise ApiError(404, "ADJUNTO_NO_ENCONTRADO", "El archivo indicado no existe.")

    if adjunto.intervencion_id is not None:
        from app.services.intervenciones import consultar_intervenciones
        visibles = consultar_intervenciones(
            db=db,
            solicitud_id=adjunto.solicitud_id,
            usuario_id=usuario_id,
            rol=rol,
        )
        if not any(item["id"] == adjunto.intervencion_id for item in visibles):
            raise ApiError(404, "ADJUNTO_NO_ENCONTRADO", "El archivo no existe o no tienes permiso para consultarlo.")
    elif adjunto.mensaje_id is not None:
        from app.services.mensajes import _solicitud_accesible
        _solicitud_accesible(db, adjunto.solicitud_id, usuario_id, rol)
    else:
        _obtener_solicitud_autorizada(
            db=db,
            solicitud_id=adjunto.solicitud_id,
            usuario_id=usuario_id,
            rol=rol,
        )

    return adjunto, leer_de_storage(adjunto.ruta_storage)
