
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Intervencion(Base):
    """Tabla intervenciones (docs/MER.md)."""

    __tablename__ = "intervenciones"

    __table_args__ = (
        UniqueConstraint(
            "solicitud_id",
            "id",
            name="uq_intervenciones_solicitud",
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

    tecnico_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    diagnostico: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visibilidad: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="interna",
        server_default="interna",
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
