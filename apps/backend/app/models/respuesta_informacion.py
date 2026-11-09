import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RespuestaInformacion(Base):
    """Tabla respuestas_informacion (docs/MER.md)."""

    __tablename__ = "respuestas_informacion"

    __table_args__ = (
        UniqueConstraint(
            "solicitud_informacion_id",
            name="uq_respuestas_solicitud_informacion",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    solicitud_informacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("solicitudes_informacion.id", ondelete="RESTRICT"),
        nullable=False,
    )

    respondido_por: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    fecha_respuesta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )