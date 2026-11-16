"""Esquemas de RF-18, parte del solicitante (docs/contrato-api.md §11.2 y §11.3).

La creación de peticiones por el técnico (§11.1) está en
`app/schemas/solicitud_informacion.py`; aquí solo se agrega la consulta y la
respuesta.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.respuesta_informacion import RespuestaInformacionRespuesta


class AutorPeticion(BaseModel):
    id: uuid.UUID
    nombre: str
    rol: str


class PeticionInformacionDetalle(BaseModel):
    id: uuid.UUID
    contenido: str
    estado: str
    solicitado_por: AutorPeticion
    fecha_solicitud: datetime
    respuesta: RespuestaInformacionRespuesta | None


class PeticionesInformacionLista(BaseModel):
    data: list[PeticionInformacionDetalle]


class RespuestaRegistradaMensaje(BaseModel):
    mensaje: str
    respuesta: RespuestaInformacionRespuesta
