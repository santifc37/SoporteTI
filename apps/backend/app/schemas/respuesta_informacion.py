import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrearRespuestaInformacion(BaseModel):
    contenido: str = Field(min_length=1)

    @field_validator("contenido")
    @classmethod
    def validar_contenido(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El contenido de la respuesta no puede estar vacío."
            )

        return valor


class RespuestaInformacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitud_informacion_id: uuid.UUID
    respondido_por: uuid.UUID
    contenido: str
    fecha_respuesta: datetime