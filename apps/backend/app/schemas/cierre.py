"""Esquemas de cierre (RF-20) y cancelación (RF-15) (docs/contrato-api.md §13.2 y §13.3)."""

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from app.schemas.solicitud import EstadoSolicitud, TipoCierre

Motivo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class CerrarSolicitud(BaseModel):
    """POST /api/v1/requests/{id}/close (solo coordinador).

    La cancelación no va por aquí: la hace el solicitante en /cancel.
    """

    model_config = ConfigDict(extra="forbid")

    tipo_cierre: Literal["solucion", "administrativo"]
    motivo_cierre: Motivo | None = None

    @model_validator(mode="after")
    def _motivo_obligatorio_si_es_administrativo(self):
        # RN-35: todo cierre administrativo debe justificarse.
        if self.tipo_cierre == "administrativo" and not self.motivo_cierre:
            raise ValueError("El cierre administrativo exige un motivo.")
        return self


class CancelarSolicitud(BaseModel):
    """POST /api/v1/requests/{id}/cancel (solo el solicitante propietario)."""

    model_config = ConfigDict(extra="forbid")

    motivo: Motivo


class SolicitudCerrada(BaseModel):
    id: uuid.UUID
    estado_anterior: EstadoSolicitud
    estado_actual: EstadoSolicitud
    tipo_cierre: TipoCierre
    motivo_cierre: str | None
    cerrado_por: uuid.UUID
    fecha_cierre: datetime


class SolicitudCerradaMensaje(BaseModel):
    mensaje: str
    solicitud: SolicitudCerrada
