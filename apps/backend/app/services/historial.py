"""RF-28: consulta del historial de cambios de una solicitud (docs/contrato-api.md §14).

Reglas:
- Solicitante: solo el historial de sus propias solicitudes.
- Técnico: solo si tiene la solicitud asignada actualmente (RN-05).
- Coordinador: cualquier solicitud.
- Es de solo lectura: la API no permite modificar ni eliminar registros.
- Se ordena cronológicamente (del más antiguo al más reciente).
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Asignacion, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio
from app.schemas.historial import CambioHistorial, HistorialLista, UsuarioHistorial
from app.schemas.pagination import Pagination, calcular_total_paginas


def _puede_consultar(
    db: Session, solicitud: Solicitud, usuario_id: uuid.UUID, rol: str
) -> bool:
    if rol == "coordinador":
        return True
    if rol == "solicitante":
        return solicitud.solicitante_id == usuario_id
    if rol == "tecnico":
        tecnico_actual = db.scalar(
            select(Asignacion.tecnico_id).where(
                Asignacion.solicitud_id == solicitud.id,
                Asignacion.fecha_finalizacion.is_(None),
            )
        )
        return tecnico_actual == usuario_id
    return False


def consultar_historial(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    page: int,
    limit: int,
) -> HistorialLista:
    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la solicitud.")

    if not _puede_consultar(db, solicitud, usuario_id, rol):
        raise ApiError(
            403,
            "PERMISO_DENEGADO",
            "No tienes permisos para consultar el historial de esta solicitud.",
        )

    total = db.scalar(
        select(func.count())
        .select_from(HistorialCambio)
        .where(HistorialCambio.solicitud_id == solicitud_id)
    )

    filas = db.execute(
        select(HistorialCambio, Usuario)
        .join(Usuario, Usuario.id == HistorialCambio.usuario_id)
        .where(HistorialCambio.solicitud_id == solicitud_id)
        .order_by(HistorialCambio.fecha_cambio.asc(), HistorialCambio.id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    data = [
        CambioHistorial(
            id=cambio.id,
            solicitud_id=cambio.solicitud_id,
            usuario=UsuarioHistorial(
                id=autor.id,
                nombre=f"{autor.nombre} {autor.apellido}".strip(),
                rol=autor.rol,
            ),
            tipo_cambio=cambio.tipo_cambio,
            valor_anterior=cambio.valor_anterior,
            valor_nuevo=cambio.valor_nuevo,
            observacion=cambio.observacion,
            fecha_cambio=cambio.fecha_cambio,
        )
        for cambio, autor in filas
    ]

    return HistorialLista(
        data=data,
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=calcular_total_paginas(total, limit),
        ),
    )
