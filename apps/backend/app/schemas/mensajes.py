"""Esquemas de la conversación: RF-22, RF-23 y RF-26 (docs/contrato-api.md §12)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pagination import Pagination


class EnviarMensaje(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contenido: str = Field(min_length=1)

    @field_validator("contenido")
    @classmethod
    def validar_contenido(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El contenido del mensaje no puede estar vacío.")
        return valor


class Remitente(BaseModel):
    id: uuid.UUID
    nombre: str
    rol: str


class MensajeConversacion(BaseModel):
    """Mensaje en la consulta de la conversación (§12.1)."""

    id: uuid.UUID
    solicitud_id: uuid.UUID
    remitente: Remitente
    contenido: str
    fecha_envio: datetime


class MensajesLista(BaseModel):
    data: list[MensajeConversacion]
    pagination: Pagination


class MensajeCreado(BaseModel):
    """Mensaje recién enviado (§12.2)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitud_id: uuid.UUID
    remitente_id: uuid.UUID
    contenido: str
    fecha_envio: datetime


class MensajeEnviadoRespuesta(BaseModel):
    mensaje: str
    data: MensajeCreado
