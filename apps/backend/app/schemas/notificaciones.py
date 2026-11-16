"""Esquemas de las notificaciones internas: RF-27."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.pagination import Pagination


class NotificacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitud_id: uuid.UUID | None
    tipo: str
    contenido: str
    leida: bool
    fecha_creacion: datetime


class NotificacionesLista(BaseModel):
    data: list[NotificacionRespuesta]
    pagination: Pagination
    no_leidas: int


class NotificacionLeidaMensaje(BaseModel):
    mensaje: str
    notificacion: NotificacionRespuesta


class NotificacionesLeidasMensaje(BaseModel):
    mensaje: str
    actualizadas: int
