"""Dependencias compartidas de la API."""

import uuid
from dataclasses import dataclass

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.config import SESSION_COOKIE_NAME
from app.core.errors import ApiError
from app.database.session import get_db
from app.services.autenticacion import obtener_sesion_valida


@dataclass(frozen=True)
class UsuarioActual:
    """Usuario autenticado de la petición en curso."""

    id: uuid.UUID
    rol: str
    nombre: str
    apellido: str
    correo: str
    activo: bool
    sesion_id: uuid.UUID


def get_current_user(
    token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> UsuarioActual:
    """Exige una sesión válida y devuelve el usuario autenticado (RNF-05).

    Responde 401 SESION_NO_VALIDA si no hay cookie o la sesión no existe,
    está revocada o venció.
    """
    resultado = obtener_sesion_valida(db, token) if token else None
    if resultado is None:
        raise ApiError(
            401, "SESION_NO_VALIDA", "Debes iniciar sesión para realizar esta operación."
        )

    sesion, usuario = resultado
    return UsuarioActual(
        id=usuario.id,
        rol=usuario.rol,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        activo=usuario.activo,
        sesion_id=sesion.id,
    )
