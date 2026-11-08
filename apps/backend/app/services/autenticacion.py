import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
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
    """RF-01: valida las credenciales y crea una sesión.

    Devuelve el usuario y el token en claro, que solo se entrega una vez (en
    la cookie). Por seguridad, un correo inexistente y una contraseña
    incorrecta producen exactamente el mismo error.
    """
    usuario = db.scalar(
        select(Usuario).where(func.lower(Usuario.correo) == correo.strip().lower())
    )

    # Se verifica siempre una contraseña, exista o no el usuario.
    contrasena_valida = verify_password(
        contrasena, usuario.password_hash if usuario else HASH_FICTICIO
    )
    if usuario is None or not contrasena_valida:
        raise ApiError(401, "CREDENCIALES_INVALIDAS", "Correo o contraseña incorrectos.")

    # Solo se informa de la cuenta desactivada a quien conoce la contraseña.
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
    """Devuelve (sesión, usuario) si el token corresponde a una sesión vigente.

    Una sesión es vigente si no está revocada ni vencida. Si la cuenta está
    desactivada se lanza USUARIO_INACTIVO.
    """
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
    """Revoca la sesión indicada (no se borra: queda como histórico)."""
    sesion = db.get(Sesion, sesion_id)
    if sesion is not None and not sesion.revocada:
        sesion.revocada = True
        db.commit()
