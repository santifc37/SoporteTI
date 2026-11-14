import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Notificacion(Base):
    """Tabla notificaciones (migración 0001, docs/MER.md). Solo avisos internos."""

    __tablename__ = "notificaciones"

    __table_args__ = (Index("ix_notificaciones_usuario", "usuario_id", "leida"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    solicitud_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("solicitudes.id", ondelete="RESTRICT"), nullable=True
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
