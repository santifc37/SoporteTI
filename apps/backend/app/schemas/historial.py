"""Esquemas de la consulta del historial de cambios: RF-28 (docs/contrato-api.md §14)."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.pagination import Pagination


class UsuarioHistorial(BaseModel):
    """Usuario responsable del cambio."""

    id: uuid.UUID
    nombre: str
    rol: str


class CambioHistorial(BaseModel):
    id: uuid.UUID
    solicitud_id: uuid.UUID
    usuario: UsuarioHistorial
    tipo_cambio: str
    valor_anterior: str | None
    valor_nuevo: str | None
    observacion: str | None
    fecha_cambio: datetime


class HistorialLista(BaseModel):
    data: list[CambioHistorial]
    pagination: Pagination
