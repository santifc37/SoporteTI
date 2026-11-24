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
TipoCierre = Literal["solucion", "cancelacion", "administrativo"]


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
    # en_evaluacion: coordinador (RF-09). en_atencion / en_espera: técnico asignado (RF-14).
    estado: Literal["en_evaluacion", "en_atencion", "en_espera"]

# ------------------------------ RF-06: crear solicitud ------------------------------
# Esquemas de POST /api/v1/requests (docs/contrato-api.md §7.2).

import re
from typing import Annotated

from pydantic import ConfigDict, StringConstraints, model_validator

PATRON_CORREO = r"[^@\s]+@[^@\s]+\.[^@\s]+"
PATRON_TELEFONO = r"\+?[0-9 ()-]{7,20}"

Titulo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Descripcion = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
Ubicacion = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
PlacaEquipo = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
DatoContacto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class CrearSolicitud(BaseModel):
    """Datos que envía el solicitante.

    El solicitante, el estado, la prioridad y las fechas los asigna el backend;
    si se envían (por ejemplo `solicitante_id`), la petición se rechaza con 422.
    """

    model_config = ConfigDict(extra="forbid")

    titulo: Titulo
    descripcion: Descripcion
    tipo: TipoSolicitud
    categoria_id: uuid.UUID | None = None
    ubicacion: Ubicacion
    # Solo cuando la solicitud se refiere a un equipo identificable (RN-36).
    placa_equipo: PlacaEquipo | None = None
    medio_contacto: Literal["correo", "telefono"]
    dato_contacto: DatoContacto

    @model_validator(mode="after")
    def _dato_de_contacto_coherente(self):
        if self.medio_contacto == "correo" and not re.fullmatch(PATRON_CORREO, self.dato_contacto):
            raise ValueError("El dato de contacto debe ser un correo electrónico válido.")
        if self.medio_contacto == "telefono" and not re.fullmatch(PATRON_TELEFONO, self.dato_contacto):
            raise ValueError("El dato de contacto debe ser un número de teléfono válido.")
        return self


class SolicitudCreada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero: str
    titulo: str
    descripcion: str
    tipo: TipoSolicitud
    prioridad: PrioridadSolicitud | None
    estado: EstadoSolicitud
    solicitante_id: uuid.UUID
    categoria_id: uuid.UUID | None
    fecha_creacion: datetime


class SolicitudCreadaMensaje(BaseModel):
    mensaje: str
    solicitud: SolicitudCreada



# --------------------------- RF-07: detalle de una solicitud ---------------------------


class SolicitudDetalle(BaseModel):
    """Respuesta de GET /api/v1/requests/{id} (docs/contrato-api.md §7.3)."""

    id: uuid.UUID
    numero: str
    titulo: str
    descripcion: str
    tipo: TipoSolicitud
    prioridad: PrioridadSolicitud | None
    estado: EstadoSolicitud
    ubicacion: str
    placa_equipo: str | None
    medio_contacto: str
    dato_contacto: str
    solicitante: UsuarioResumen
    categoria: CategoriaResumen | None
    tecnico_asignado: UsuarioResumen | None
    solucion_final: str | None
    resuelto_por: uuid.UUID | None
    fecha_resolucion: datetime | None
    tipo_cierre: TipoCierre | None
    motivo_cierre: str | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_cierre: datetime | None



# ------------------------- RF-10: clasificación y prioridad -------------------------


class ClasificarSolicitud(BaseModel):
    """PATCH /api/v1/requests/{id} (docs/contrato-api.md §7.4).

    Solo se pueden enviar la categoría y la prioridad; cualquier otro campo
    (estado, solicitante, datos de cierre...) se rechaza con 422.
    """

    model_config = ConfigDict(extra="forbid")

    # null quita la categoría.
    categoria_id: uuid.UUID | None = None
    prioridad: PrioridadSolicitud | None = None

    @model_validator(mode="after")
    def _validar(self):
        if not self.model_fields_set:
            raise ValueError("Debes enviar categoria_id, prioridad o ambos.")
        if "prioridad" in self.model_fields_set and self.prioridad is None:
            raise ValueError("La prioridad no puede quitarse, solo cambiarse.")
        return self


class SolicitudClasificada(BaseModel):
    id: uuid.UUID
    numero: str
    categoria_id: uuid.UUID | None
    prioridad: PrioridadSolicitud | None
    estado: EstadoSolicitud


class SolicitudClasificadaMensaje(BaseModel):
    mensaje: str
    solicitud: SolicitudClasificada
