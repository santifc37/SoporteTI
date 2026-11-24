
import io
import uuid
import warnings
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Adjunto, Asignacion, Intervencion, Solicitud


register_heif_opener()

TAMANO_MAXIMO_ENTRADA = 10 * 1024 * 1024
DIMENSION_MAXIMA = (1920, 1920)
CALIDAD_WEBP = 80
TIPO_WEBP = "image/webp"


class ErrorImagen(Exception):
    """Error al validar o convertir una imagen."""


class ErrorStorage(Exception):
    """Error al guardar, leer o eliminar archivos locales."""


def _storage_root() -> Path:
    return (Path(__file__).resolve().parents[2] / "storage").resolve()


def _resolver_ruta_storage(ruta: str) -> Path:
    if not ruta or "\x00" in ruta:
        raise ErrorStorage("La ruta del archivo no es vÃ¡lida.")
    relativa = Path(ruta)
    if relativa.is_absolute():
        raise ErrorStorage("La ruta del archivo no es vÃ¡lida.")
    raiz = _storage_root()
    destino = (raiz / relativa).resolve()
    try:
        destino.relative_to(raiz)
    except ValueError as error:
        raise ErrorStorage("La ruta del archivo no es vÃ¡lida.") from error
    return destino


def subir_a_storage(ruta: str, contenido: bytes) -> None:
    destino = _resolver_ruta_storage(ruta)
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("xb") as archivo:
            archivo.write(contenido)
    except FileExistsError as error:
        raise ErrorStorage("Ya existe un archivo con esa ruta.") from error
    except OSError as error:
        try:
            destino.unlink(missing_ok=True)
        except OSError:
            pass
        raise ErrorStorage("No fue posible guardar el archivo localmente.") from error


def leer_de_storage(ruta: str) -> bytes:
    destino = _resolver_ruta_storage(ruta)
    try:
        return destino.read_bytes()
    except OSError as error:
        raise ErrorStorage("No fue posible recuperar el archivo local.") from error


def eliminar_de_storage(ruta: str) -> None:
    destino = _resolver_ruta_storage(ruta)
    try:
        destino.unlink(missing_ok=True)
    except OSError as error:
        raise ErrorStorage("No fue posible eliminar el archivo local.") from error


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
