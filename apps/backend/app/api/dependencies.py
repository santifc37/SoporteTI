"""Dependencias compartidas de la API.

IMPORTANTE: `get_current_user` es un PUNTO DE ENLACE TEMPORAL.

La autenticación real (login, cookie de sesión, tabla `sesiones`; RF-01 y
RF-02, docs/diseno.md §9) todavía no está implementada. Cuando exista, solo
debe reemplazarse el cuerpo de `get_current_user`: los endpoints ya dependen
de `UsuarioActual` y no cambian.

Mientras tanto, por defecto TODAS las rutas protegidas responden 401. Para
probar a mano en local se puede activar `DEV_AUTH_ENABLED=true` en `.env` y
enviar el encabezado `X-Dev-User-Id: <uuid>`. El rol sale de la base de datos,
nunca del encabezado. No activar nunca fuera del entorno local.
"""

import os
import uuid
from dataclasses import dataclass

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.database.session import get_db
from app.models import Usuario


@dataclass(frozen=True)
class UsuarioActual:
    id: uuid.UUID
    rol: str


def _dev_auth_activa() -> bool:
    return os.getenv("DEV_AUTH_ENABLED", "false").strip().lower() == "true"


def get_current_user(
    x_dev_user_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> UsuarioActual:
    sesion_invalida = ApiError(
        401, "SESION_NO_VALIDA", "Debes iniciar sesión para realizar esta operación."
    )

    if not _dev_auth_activa() or not x_dev_user_id:
        raise sesion_invalida

    try:
        usuario_id = uuid.UUID(x_dev_user_id)
    except ValueError:
        raise sesion_invalida

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise sesion_invalida
    if not usuario.activo:
        raise ApiError(401, "USUARIO_INACTIVO", "La cuenta está desactivada.")

    return UsuarioActual(id=usuario.id, rol=usuario.rol)
