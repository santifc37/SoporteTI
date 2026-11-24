"""RF-29: estadísticas básicas para el coordinador (CA-06).

Todos los indicadores se calculan sobre las mismas solicitudes: las creadas
dentro del rango de fechas indicado (o todas, si no se indica).
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asignacion, Categoria, Solicitud, Usuario
from app.schemas.estadisticas import (
    CantidadPorCategoria,
    CantidadPorTecnico,
    Estadisticas,
)

ESTADOS = (
    "registrado",
    "en_evaluacion",
    "asignado",
    "en_atencion",
    "en_espera",
    "resuelto",
    "cerrado",
)
PRIORIDADES = ("baja", "media", "alta")


def _condiciones(fecha_desde: datetime | None, fecha_hasta: datetime | None) -> list:
    condiciones = []
    if fecha_desde:
        condiciones.append(Solicitud.fecha_creacion >= fecha_desde)
    if fecha_hasta:
        condiciones.append(Solicitud.fecha_creacion <= fecha_hasta)
    return condiciones


def calcular_estadisticas(
    db: Session,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> Estadisticas:
    condiciones = _condiciones(fecha_desde, fecha_hasta)

    total = db.scalar(select(func.count(Solicitud.id)).where(*condiciones)) or 0

    # --------------------------------- por estado ---------------------------------
    por_estado = dict.fromkeys(ESTADOS, 0)
    for estado, cantidad in db.execute(
        select(Solicitud.estado, func.count(Solicitud.id))
        .where(*condiciones)
        .group_by(Solicitud.estado)
    ):
        por_estado[estado] = cantidad

    # -------------------------------- por prioridad -------------------------------
    por_prioridad = dict.fromkeys(PRIORIDADES, 0)
    sin_prioridad = 0
    for prioridad, cantidad in db.execute(
        select(Solicitud.prioridad, func.count(Solicitud.id))
        .where(*condiciones)
        .group_by(Solicitud.prioridad)
    ):
        if prioridad is None:
            sin_prioridad = cantidad
        else:
            por_prioridad[prioridad] = cantidad

    # -------------------------------- por categoría -------------------------------
    cantidad_categoria = func.count(Solicitud.id).label("cantidad")
    por_categoria = [
        CantidadPorCategoria(categoria_id=cid, nombre=nombre, cantidad=cantidad)
        for cid, nombre, cantidad in db.execute(
            select(Categoria.id, Categoria.nombre, cantidad_categoria)
            .join(Solicitud, Solicitud.categoria_id == Categoria.id)
            .where(*condiciones)
            .group_by(Categoria.id, Categoria.nombre)
            .order_by(cantidad_categoria.desc(), Categoria.nombre)
        )
    ]
    sin_categoria = total - sum(c.cantidad for c in por_categoria)

    # ------------------------- por técnico (asignación activa) -------------------------
    cantidad_tecnico = func.count(Solicitud.id).label("cantidad")
    por_tecnico = [
        CantidadPorTecnico(
            tecnico_id=tid, nombre=f"{nombre} {apellido}".strip(), cantidad=cantidad
        )
        for tid, nombre, apellido, cantidad in db.execute(
            select(Usuario.id, Usuario.nombre, Usuario.apellido, cantidad_tecnico)
            .join(Asignacion, Asignacion.tecnico_id == Usuario.id)
            .join(Solicitud, Solicitud.id == Asignacion.solicitud_id)
            .where(Asignacion.fecha_finalizacion.is_(None), *condiciones)
            .group_by(Usuario.id, Usuario.nombre, Usuario.apellido)
            .order_by(cantidad_tecnico.desc(), Usuario.nombre)
        )
    ]
    sin_asignar = total - sum(t.cantidad for t in por_tecnico)

    # ------------------------- tiempo promedio de atención -------------------------
    # Se calcula en Python para que funcione igual en PostgreSQL y en SQLite.
    duraciones = [
        (resuelta - creada).total_seconds()
        for creada, resuelta in db.execute(
            select(Solicitud.fecha_creacion, Solicitud.fecha_resolucion).where(
                Solicitud.fecha_resolucion.is_not(None), *condiciones
            )
        )
    ]
    promedio_horas = (
        round(sum(duraciones) / len(duraciones) / 3600, 2) if duraciones else None
    )

    return Estadisticas(
        total_solicitudes=total,
        por_estado=por_estado,
        por_prioridad=por_prioridad,
        sin_prioridad=sin_prioridad,
        por_categoria=por_categoria,
        sin_categoria=sin_categoria,
        por_tecnico=por_tecnico,
        sin_asignar=sin_asignar,
        tiempo_promedio_atencion=promedio_horas,
        solicitudes_con_tiempo=len(duraciones),
    )
