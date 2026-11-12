"""Esquemas de RF-03 (gestión de usuarios) y RF-05 (datos de contacto).

Siguen docs/contrato-api.md §5. Los campos que no aparecen aquí (id,
password_hash, fechas) no se aceptan en las peticiones: `extra="forbid"`
responde 422 si alguien intenta enviarlos.
"""

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.schemas.pagination import Pagination

Rol = Literal["solicitante", "tecnico", "coordinador"]
MedioContacto = Literal["correo", "telefono"]

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Correo = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]
Telefono = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=7, max_length=20, pattern=r"^\+?[0-9 ()-]+$"
    ),
]
# Misma longitud mínima que scripts/crear_usuario.py.
Contrasena = Annotated[str, Field(min_length=8, max_length=128)]

MENSAJE_TELEFONO = "El teléfono es obligatorio cuando el medio de contacto preferido es teléfono."


# --------------------------------- peticiones --------------------------------


class UsuarioCrear(BaseModel):
    """POST /users (solo coordinador)."""

    model_config = ConfigDict(extra="forbid")

    nombre: Nombre
    apellido: Nombre
    correo: Correo
    contrasena: Contrasena
    rol: Rol
    medio_contacto_preferido: MedioContacto = "correo"
    telefono: Telefono | None = None

    @model_validator(mode="after")
    def _telefono_si_es_el_medio(self):
        if self.medio_contacto_preferido == "telefono" and not self.telefono:
            raise ValueError(MENSAJE_TELEFONO)
        return self


class UsuarioActualizar(BaseModel):
    """PATCH /users/{id}. Todos los campos son opcionales.

    Qué campos puede enviar cada actor lo decide el servicio, porque depende
    de quién hace la petición (contrato-api.md §5.4).
    """

    model_config = ConfigDict(extra="forbid")

    nombre: Nombre | None = None
    apellido: Nombre | None = None
    correo: Correo | None = None
    telefono: Telefono | None = None
    medio_contacto_preferido: MedioContacto | None = None
    rol: Rol | None = None
    activo: bool | None = None

    @model_validator(mode="after")
    def _sin_nulos_salvo_telefono(self):
        # Solo el teléfono puede borrarse enviando null.
        for campo in self.model_fields_set - {"telefono"}:
            if getattr(self, campo) is None:
                raise ValueError(f"El campo {campo} no puede ser nulo.")
        return self


# --------------------------------- respuestas --------------------------------


class UsuarioResumen(BaseModel):
    """Usuario devuelto al crear o modificar (contrato-api.md §5.3 y §5.4)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    apellido: str
    correo: str
    rol: str
    activo: bool


class UsuarioListado(UsuarioResumen):
    """Elemento de GET /users (contrato-api.md §5.1)."""

    medio_contacto_preferido: str
    telefono: str | None
    fecha_creacion: datetime


class UsuarioDetalle(UsuarioListado):
    """Respuesta de GET /users/{id} (contrato-api.md §5.2)."""

    fecha_actualizacion: datetime


class UsuariosPagina(BaseModel):
    data: list[UsuarioListado]
    pagination: Pagination


class UsuarioMensaje(BaseModel):
    mensaje: str
    usuario: UsuarioResumen
