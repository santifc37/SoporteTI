import uuid
from datetime import datetime

from sqlalchemy import DateTime, FetchedValue, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Solicitud(Base):
    """Tabla `solicitudes` (docs/MER.md)."""

    __tablename__ = "solicitudes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # ST-000001: lo genera PostgreSQL con una secuencia (migración 0001).
    numero: Mapped[str] = mapped_column(String(20), unique=True, server_default=FetchedValue())
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(20))
    solicitante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"))
    categoria_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categorias.id"))
    prioridad: Mapped[str | None] = mapped_column(String(10))
    estado: Mapped[str] = mapped_column(String(20), server_default="registrado")
    ubicacion: Mapped[str] = mapped_column(String(200))
    placa_equipo: Mapped[str | None] = mapped_column(String(50))
    medio_contacto: Mapped[str] = mapped_column(String(20))
    dato_contacto: Mapped[str] = mapped_column(String(255))
    solucion_final: Mapped[str | None] = mapped_column(Text)
    resuelto_por: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_resolucion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tipo_cierre: Mapped[str | None] = mapped_column(String(20))
    motivo_cierre: Mapped[str | None] = mapped_column(Text)
    cerrado_por: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, server_default="1")
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
