"""Hash de contraseñas y tokens de sesión (RNF-04, docs/diseno.md §9).

- Contraseñas: Argon2id (algoritmo de hash pensado para contraseñas). Nunca se
  guardan en texto plano.
- Sesiones: el navegador recibe un token aleatorio; en la base de datos solo se
  guarda su hash SHA-256 (`sesiones.token_hash`), así que una filtración de la
  tabla no permite usar las sesiones.
"""

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()


def hash_password(contrasena: str) -> str:
    return _hasher.hash(contrasena)


def verify_password(contrasena: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, contrasena)
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """True si el hash usa parámetros antiguos y conviene regenerarlo."""
    return _hasher.check_needs_rehash(password_hash)


def generate_session_token() -> str:
    """Token aleatorio de 256 bits que viaja en la cookie."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Hash de una contraseña inexistente: permite hacer el mismo trabajo de
# verificación cuando el correo no existe y no revelar así qué cuentas existen.
HASH_FICTICIO = hash_password("contrasena-ficticia-no-usar")
