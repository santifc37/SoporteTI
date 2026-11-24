
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Mensaje(Base):
    """Tabla mensajes (migración 0001)."""

    __tablename__ = "mensajes"

    __table_args__ = (
        UniqueConstraint(
            "solicitud_id",
            "id",
            name="uq_mensajes_solicitud",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    solicitud_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("solicitudes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    remitente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    fecha_envio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
