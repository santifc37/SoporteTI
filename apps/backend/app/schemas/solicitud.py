import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel

from app.schemas.pagination import Pagination

# Valores controlados (docs/contrato-api.md §8 y MER.md).
EstadoSolicitud = Literal[
    "registrado",
    "en_evaluacion",
    "asignado",
    "en_atencion",
    "en_espera",
    "resuelto",
    "cerrado",
]
PrioridadSolicitud = Literal["baja", "media", "alta"]
TipoSolicitud = Literal["incidente", "requerimiento"]


class CategoriaResumen(BaseModel):
    id: uuid.UUID
    nombre: str


class UsuarioResumen(BaseModel):
    id: uuid.UUID
    nombre: str


class SolicitudResumen(BaseModel):
    """Elemento de `GET /api/v1/requests` (docs/contrato-api.md §7.1)."""

    id: uuid.UUID
    numero: str
    titulo: str
    tipo: TipoSolicitud
    prioridad: PrioridadSolicitud | None
    estado: EstadoSolicitud
    categoria: CategoriaResumen | None
    solicitante: UsuarioResumen
    tecnico_asignado: UsuarioResumen | None
    fecha_creacion: datetime


class SolicitudesPagina(BaseModel):
    data: list[SolicitudResumen]
    pagination: Pagination

class ActualizarEstadoSolicitud(BaseModel):
    estado: Literal["en_atencion", "en_espera"]