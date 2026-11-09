import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SolicitudInformacion(Base):
    """Tabla solicitudes_informacion (docs/MER.md)."""

    __tablename__ = "solicitudes_informacion"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    solicitud_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("solicitudes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    solicitado_por: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pendiente",
        server_default="pendiente",
    )

    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )