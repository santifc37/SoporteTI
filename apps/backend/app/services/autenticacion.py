
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import get_session_duration_hours
from app.core.errors import ApiError
from app.core.security import (
    HASH_FICTICIO,
    generate_session_token,
    hash_password,
    hash_session_token,
    password_needs_rehash,
    verify_password,
)
from app.models import Sesion, Usuario


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def iniciar_sesion(db: Session, correo: str, contrasena: str) -> tuple[Usuario, str]:
    """RF-01: valida las credenciales y crea una sesión."""
    usuario = db.scalar(
        select(Usuario).where(func.lower(Usuario.correo) == correo.strip().lower())
    )

    contrasena_valida = verify_password(
        contrasena, usuario.password_hash if usuario else HASH_FICTICIO
    )
    if usuario is None or not contrasena_valida:
        raise ApiError(401, "CREDENCIALES_INVALIDAS", "Correo o contraseña incorrectos.")

    if not usuario.activo:
        raise ApiError(401, "USUARIO_INACTIVO", "La cuenta está desactivada.")

    if password_needs_rehash(usuario.password_hash):
        usuario.password_hash = hash_password(contrasena)

    token = generate_session_token()
    db.add(
        Sesion(
            usuario_id=usuario.id,
            token_hash=hash_session_token(token),
            fecha_expiracion=_ahora() + timedelta(hours=get_session_duration_hours()),
        )
    )
    db.commit()
    return usuario, token


def obtener_sesion_valida(db: Session, token: str) -> tuple[Sesion, Usuario] | None:
    """Devuelve la sesión y el usuario si el token corresponde a una sesión vigente."""
    fila = db.execute(
        select(Sesion, Usuario)
        .join(Usuario, Usuario.id == Sesion.usuario_id)
        .where(
            Sesion.token_hash == hash_session_token(token),
            Sesion.revocada.is_(False),
            Sesion.fecha_expiracion > _ahora(),
        )
    ).first()

    if fila is None:
        return None

    sesion, usuario = fila
    if not usuario.activo:
        raise ApiError(401, "USUARIO_INACTIVO", "La cuenta está desactivada.")

    return sesion, usuario


def cerrar_sesion(db: Session, sesion_id: uuid.UUID) -> None:
    """Revoca la sesión indicada."""
    sesion = db.get(Sesion, sesion_id)
    if sesion is not None and not sesion.revocada:
        sesion.revocada = True
        db.commit()


def cambiar_contrasena(
    db: Session,
    usuario_id: uuid.UUID,
    sesion_id: uuid.UUID,
    contrasena_actual: str,
    contrasena_nueva: str,
) -> None:
    """RF-04: permite al usuario autenticado cambiar su contraseña."""
    usuario = db.get(Usuario, usuario_id)

    if usuario is None or not usuario.activo:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró el usuario.")

    if not verify_password(contrasena_actual, usuario.password_hash):
        raise ApiError(
            401,
            "CONTRASENA_ACTUAL_INCORRECTA",
            "La contraseña actual no es correcta.",
        )

    usuario.password_hash = hash_password(contrasena_nueva)

    # Se conserva la sesión actual y se revocan las demás.
    db.execute(
        update(Sesion)
        .where(
            Sesion.usuario_id == usuario_id,
            Sesion.id != sesion_id,
            Sesion.revocada.is_(False),
        )
        .values(revocada=True)
    )

    db.commit()


def restablecer_contrasena(
    db: Session,
    usuario_id: uuid.UUID,
    contrasena_temporal: str,
) -> None:
    """RF-04: el coordinador asigna una contraseña temporal a una cuenta."""
    usuario = db.get(Usuario, usuario_id)

    if usuario is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró el usuario.")

    usuario.password_hash = hash_password(contrasena_temporal)

    # El restablecimiento invalida todas las sesiones de la cuenta.
    db.execute(
        update(Sesion)
        .where(
            Sesion.usuario_id == usuario_id,
            Sesion.revocada.is_(False),
        )
        .values(revocada=True)
    )

    db.commit()
