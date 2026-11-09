import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrearSolicitudInformacion(BaseModel):
    contenido: str = Field(min_length=1)

    @field_validator("contenido")
    @classmethod
    def validar_contenido(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El contenido de la solicitud de información no puede estar vacío."
            )

        return valor


class SolicitudInformacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitud_id: uuid.UUID
    solicitado_por: uuid.UUID
    contenido: str
    estado: str
    fecha_solicitud: datetime