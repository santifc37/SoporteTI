import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Asignacion(Base):
    """Tabla `asignaciones` (docs/MER.md).

    La asignación activa de una solicitud es la que tiene
    `fecha_finalizacion IS NULL` (a lo sumo una por solicitud, índice
    `uq_asignacion_activa`). El técnico responsable se obtiene de ahí.
    """

    __tablename__ = "asignaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    solicitud_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("solicitudes.id"))
    tecnico_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"))
    asignado_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"))
    observacion: Mapped[str | None] = mapped_column(Text)
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_finalizacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
