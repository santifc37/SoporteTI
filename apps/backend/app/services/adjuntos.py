
import io
import logging
import os
import uuid
import warnings
from pathlib import Path
from urllib.parse import quote

import httpx
from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import config
from app.core.errors import ApiError
from app.models import Adjunto, Asignacion, Intervencion, Solicitud


logger = logging.getLogger(__name__)

register_heif_opener()

TAMANO_MAXIMO_ENTRADA = 10 * 1024 * 1024
DIMENSION_MAXIMA = (1920, 1920)
CALIDAD_WEBP = 80
TIPO_WEBP = "image/webp"


class ErrorImagen(Exception):
    """Error al validar o convertir una imagen."""


class ErrorStorage(Exception):
    """Error al comunicarse con Supabase Storage."""


def convertir_a_webp(contenido: bytes) -> bytes:
    """Valida una imagen y la convierte a WebP."""

    if not contenido:
        raise ErrorImagen("El archivo está vacío.")

    if len(contenido) > TAMANO_MAXIMO_ENTRADA:
        raise ErrorImagen("La imagen supera el límite de 10 MB.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            imagen = Image.open(io.BytesIO(contenido))
            imagen.seek(0)
            imagen.load()

            imagen = ImageOps.exif_transpose(imagen)
            imagen.thumbnail(DIMENSION_MAXIMA, Image.Resampling.LANCZOS)

            if "A" in imagen.getbands():
                imagen = imagen.convert("RGBA")
            else:
                imagen = imagen.convert("RGB")

            salida = io.BytesIO()
            imagen.save(
                salida,
                format="WEBP",
                quality=CALIDAD_WEBP,
                method=6,
            )

            return salida.getvalue()

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as error:
        raise ErrorImagen(
            "El archivo no es una imagen válida o no se puede procesar."
        ) from error


def crear_ruta_storage(
    solicitud_id: uuid.UUID,
    intervencion_id: uuid.UUID,
) -> str:
    """Genera una ruta única para almacenar la imagen."""

    return (
        f"solicitudes/{solicitud_id}/"
        f"intervenciones/{intervencion_id}/{uuid.uuid4()}.webp"
    )


def _obtener_configuracion_storage() -> tuple[str, str, str]:
    """Obtiene las credenciales de Supabase Storage."""

    supabase_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "").strip()

    if not supabase_url or not service_role_key or not bucket:
        raise ErrorStorage(
            "Falta configurar SUPABASE_URL, "
            "SUPABASE_SERVICE_ROLE_KEY o SUPABASE_STORAGE_BUCKET."
        )

    return supabase_url, service_role_key, bucket


def _registrar_error_supabase(
    operacion: str,
    error: httpx.HTTPStatusError,
) -> None:
    """Registra errores HTTP sin exponer credenciales."""

    respuesta = error.response
    detalle = (respuesta.text or "").strip()

    if len(detalle) > 1500:
        detalle = detalle[:1500] + "... (respuesta truncada)"

    logger.error(
        "Supabase Storage rechazó la operación '%s'. "
        "Código HTTP: %s. Respuesta: %s",
        operacion,
        respuesta.status_code,
        detalle or "(sin detalle)",
    )


def subir_a_storage(ruta: str, contenido: bytes) -> None:
    """Sube una imagen WebP al bucket privado."""

    supabase_url, service_role_key, bucket = (
        _obtener_configuracion_storage()
    )

    ruta_codificada = quote(ruta, safe="/")
    bucket_codificado = quote(bucket, safe="")

    url = (
        f"{supabase_url}/storage/v1/object/"
        f"{bucket_codificado}/{ruta_codificada}"
    )

    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "Content-Type": TIPO_WEBP,
        "x-upsert": "false",
    }

    try:
        respuesta = httpx.post(
            url,
            headers=headers,
            content=contenido,
            timeout=30.0,
        )
        respuesta.raise_for_status()

    except httpx.HTTPStatusError as error:
        _registrar_error_supabase("subida de imagen", error)
        raise ErrorStorage(
            f"Supabase Storage respondió HTTP {error.response.status_code}."
        ) from error

    except httpx.RequestError as error:
        logger.error(
            "Error de conexión con Supabase Storage al subir: %s",
            type(error).__name__,
        )
        raise ErrorStorage(
            "No fue posible conectar con Supabase Storage."
        ) from error


def crear_url_firmada(
    ruta: str,
    expiracion_segundos: int = 3600,
) -> str:
    """
    Genera una URL temporal para consultar una imagen privada.
    La URL tendrá una validez predeterminada de una hora.
    """

    supabase_url, service_role_key, bucket = (
        _obtener_configuracion_storage()
    )

    ruta_codificada = quote(ruta, safe="/")
    bucket_codificado = quote(bucket, safe="")

    url = (
        f"{supabase_url}/storage/v1/object/sign/"
        f"{bucket_codificado}/{ruta_codificada}"
    )

    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "Content-Type": "application/json",
    }

    try:
        respuesta = httpx.post(
            url,
            headers=headers,
            json={"expiresIn": expiracion_segundos},
            timeout=30.0,
        )
        respuesta.raise_for_status()

        datos = respuesta.json()
        url_firmada = datos.get("signedURL")

        if not url_firmada:
            raise ErrorStorage(
                "Supabase no devolvió una URL firmada."
            )

        if url_firmada.startswith("http://") or url_firmada.startswith(
            "https://"
        ):
            return url_firmada

        if url_firmada.startswith("/storage/v1/"):
            return f"{supabase_url}{url_firmada}"

        if url_firmada.startswith("/"):
            return f"{supabase_url}/storage/v1{url_firmada}"

        return f"{supabase_url}/storage/v1/{url_firmada}"

    except httpx.HTTPStatusError as error:
        _registrar_error_supabase("generación de URL firmada", error)
        raise ErrorStorage(
            "No fue posible generar el enlace de la imagen."
        ) from error

    except httpx.RequestError as error:
        logger.error(
            "Error de conexión con Supabase Storage al generar URL: %s",
            type(error).__name__,
        )
        raise ErrorStorage(
            "No fue posible conectar con Supabase Storage."
        ) from error


def eliminar_de_storage(ruta: str) -> None:
    """Elimina una imagen de Storage."""

    supabase_url, service_role_key, bucket = (
        _obtener_configuracion_storage()
    )

    ruta_codificada = quote(ruta, safe="/")
    bucket_codificado = quote(bucket, safe="")

    url = (
        f"{supabase_url}/storage/v1/object/"
        f"{bucket_codificado}/{ruta_codificada}"
    )

    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
    }

    try:
        respuesta = httpx.delete(
            url,
            headers=headers,
            timeout=30.0,
        )
        respuesta.raise_for_status()

    except httpx.HTTPStatusError as error:
        _registrar_error_supabase("eliminación de imagen", error)
        raise ErrorStorage(
            "No fue posible eliminar la imagen de Supabase Storage."
        ) from error

    except httpx.RequestError as error:
        logger.error(
            "Error de conexión con Supabase Storage al eliminar: %s",
            type(error).__name__,
        )
        raise ErrorStorage(
            "No fue posible conectar con Supabase Storage."
        ) from error


def registrar_adjunto(
    db: Session,
    solicitud_id: uuid.UUID,
    intervencion_id: uuid.UUID,
    tecnico_id: uuid.UUID,
    archivo: UploadFile,
) -> Adjunto:
    """RF-25: registra una imagen asociada a una intervención técnica."""

    solicitud = db.scalar(
        select(Solicitud).where(Solicitud.id == solicitud_id)
    )

    if solicitud is None:
        raise ApiError(
            404,
            "SOLICITUD_NO_ENCONTRADA",
            "La solicitud indicada no existe.",
        )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se pueden adjuntar imágenes a una solicitud cerrada.",
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

    intervencion = db.scalar(
        select(Intervencion).where(
            Intervencion.id == intervencion_id,
            Intervencion.solicitud_id == solicitud_id,
            Intervencion.tecnico_id == tecnico_id,
        )
    )

    if intervencion is None:
        raise ApiError(
            404,
            "INTERVENCION_NO_ENCONTRADA",
            "La intervención indicada no existe o no te pertenece.",
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

    ruta_storage = crear_ruta_storage(
        solicitud_id,
        intervencion_id,
    )

    nombre_original = Path(
        archivo.filename or "imagen"
    ).name[:255]

    subir_a_storage(ruta_storage, contenido_webp)

    adjunto = Adjunto(
        solicitud_id=solicitud_id,
        intervencion_id=intervencion_id,
        subido_por=tecnico_id,
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
