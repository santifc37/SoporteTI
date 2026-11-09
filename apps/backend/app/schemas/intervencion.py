
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


VisibilidadIntervencion = Literal["interna", "solicitante"]


class CrearIntervencion(BaseModel):
    descripcion: str = Field(min_length=1)
    diagnostico: str | None = None
    visibilidad: VisibilidadIntervencion = "interna"

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("La descripción no puede estar vacía.")

        return valor


class IntervencionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitud_id: uuid.UUID
    tecnico_id: uuid.UUID
    descripcion: str
    diagnostico: str | None
    visibilidad: VisibilidadIntervencion
    fecha_registro: datetime
