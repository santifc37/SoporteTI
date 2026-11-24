"""Esquemas de asignación y reasignación de técnicos (docs/contrato-api.md §9)."""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.schemas.solicitud import EstadoSolicitud

Observacion = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]


class AsignarTecnico(BaseModel):
    """POST /api/v1/requests/{id}/assignments (solo coordinador)."""

    model_config = ConfigDict(extra="forbid")

    tecnico_id: uuid.UUID
    observacion: Observacion | None = None


class AsignacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitud_id: uuid.UUID
    tecnico_id: uuid.UUID
    asignado_por: uuid.UUID
    fecha_asignacion: datetime
    fecha_finalizacion: datetime | None
    observacion: str | None


class AsignacionCreadaMensaje(BaseModel):
    mensaje: str
    asignacion: AsignacionRespuesta
    estado_solicitud: EstadoSolicitud


class AsignacionHistorial(BaseModel):
    """Elemento de GET /api/v1/requests/{id}/assignments.

    Para el solicitante, `asignado_por` y `observacion` van vacíos: solo
    necesita saber quién lo atiende, no los datos internos de la asignación.
    """

    id: uuid.UUID
    tecnico_id: uuid.UUID
    tecnico_nombre: str
    asignado_por: uuid.UUID | None
    fecha_asignacion: datetime
    fecha_finalizacion: datetime | None
    observacion: str | None


class AsignacionesLista(BaseModel):
    data: list[AsignacionHistorial]
