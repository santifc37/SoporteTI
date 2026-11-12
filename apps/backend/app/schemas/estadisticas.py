"""Esquemas de estadísticas del coordinador: RF-29 y CA-06 (docs/contrato-api.md §16)."""

import uuid

from pydantic import BaseModel


class CantidadPorCategoria(BaseModel):
    categoria_id: uuid.UUID
    nombre: str
    cantidad: int


class CantidadPorTecnico(BaseModel):
    tecnico_id: uuid.UUID
    nombre: str
    cantidad: int


class Estadisticas(BaseModel):
    total_solicitudes: int
    # Siempre trae los siete estados y las tres prioridades, aunque valgan 0.
    por_estado: dict[str, int]
    por_prioridad: dict[str, int]
    sin_prioridad: int
    por_categoria: list[CantidadPorCategoria]
    sin_categoria: int
    # CA-06 pide la situación de los casos "y sus responsables": solicitudes
    # por técnico según la asignación activa.
    por_tecnico: list[CantidadPorTecnico]
    sin_asignar: int
    # Horas promedio entre el registro y la resolución de las solicitudes
    # resueltas del periodo; null si todavía no hay ninguna (contrato §16).
    tiempo_promedio_atencion: float | None
    solicitudes_con_tiempo: int
