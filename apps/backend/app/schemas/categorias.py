"""Esquemas de la gestión de categorías (docs/contrato-api.md §6)."""

import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from app.schemas.pagination import Pagination

NombreCategoria = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
Descripcion = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]


# --------------------------------- peticiones --------------------------------


class CategoriaCrear(BaseModel):
    """POST /categories (solo coordinador). Se crea activa."""

    model_config = ConfigDict(extra="forbid")

    nombre: NombreCategoria
    descripcion: Descripcion | None = None


class CategoriaActualizar(BaseModel):
    """PATCH /categories/{id} (solo coordinador). Todos los campos son opcionales."""

    model_config = ConfigDict(extra="forbid")

    nombre: NombreCategoria | None = None
    descripcion: Descripcion | None = None
    activa: bool | None = None

    @model_validator(mode="after")
    def _sin_nulos_salvo_descripcion(self):
        # Solo la descripción puede borrarse enviando null.
        for campo in self.model_fields_set - {"descripcion"}:
            if getattr(self, campo) is None:
                raise ValueError(f"El campo {campo} no puede ser nulo.")
        return self


# --------------------------------- respuestas --------------------------------


class CategoriaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    descripcion: str | None
    activa: bool


class CategoriasPagina(BaseModel):
    data: list[CategoriaRespuesta]
    pagination: Pagination


class CategoriaMensaje(BaseModel):
    mensaje: str
    categoria: CategoriaRespuesta
