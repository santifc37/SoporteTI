
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Adjunto(Base):
    """Tabla adjuntos (docs/MER.md)."""

    __tablename__ = "adjuntos"

    __table_args__ = (
        ForeignKeyConstraint(
            ["solicitud_id", "mensaje_id"],
            ["mensajes.solicitud_id", "mensajes.id"],
            name="fk_adjuntos_mensaje",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["solicitud_id", "intervencion_id"],
            ["intervenciones.solicitud_id", "intervenciones.id"],
            name="fk_adjuntos_intervencion",
            ondelete="RESTRICT",
        ),
        Index("ix_adjuntos_solicitud", "solicitud_id"),
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

    mensaje_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        nullable=True,
    )

    intervencion_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        nullable=True,
    )

    subido_por: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )

    nombre_archivo: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    ruta_storage: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    tipo_archivo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    tamano: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    fecha_subida: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
