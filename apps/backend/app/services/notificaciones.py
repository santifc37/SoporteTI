"""RF-27: notificaciones internas de la plataforma.

- Solo existen dentro de la plataforma: no se envían por correo, SMS ni otros
  servicios externos (requisitos.md RF-27, diseno.md §12.4).
- Cada usuario consulta únicamente sus propias notificaciones y puede
  marcarlas como leídas.
- `notificar()` solo agrega la notificación a la sesión; la confirma el
  `commit` de la operación que la origina, para que el aviso y el evento se
  guarden juntos o no se guarde ninguno.

Eventos que generan notificación:

| Evento | Destinatario | tipo |
|---|---|---|
| Asignación o reasignación | Técnico nuevo | `asignacion` |
| Asignación o reasignación | Solicitante | `tecnico_asignado` |
| Reasignación | Técnico anterior | `reasignacion` |
| Cierre por el coordinador | Solicitante y técnico asignado | `solicitud_cerrada` |
| Mensaje nuevo | Solicitante y técnico asignado (menos el remitente) | `nuevo_mensaje` |
| Respuesta a una petición de información | Quien hizo la petición | `respuesta_informacion` |
"""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Notificacion, Solicitud
from app.schemas.notificaciones import NotificacionesLista, NotificacionRespuesta
from app.schemas.pagination import Pagination, calcular_total_paginas


def notificar(
    db: Session,
    usuario_id: uuid.UUID,
    solicitud: Solicitud | None,
    tipo: str,
    contenido: str,
) -> None:
    """Agrega una notificación a la transacción en curso (sin hacer commit)."""

    db.add(
        Notificacion(
            usuario_id=usuario_id,
            solicitud_id=solicitud.id if solicitud is not None else None,
            tipo=tipo,
            contenido=contenido,
        )
    )


def referencia(solicitud: Solicitud) -> str:
    """Texto corto para identificar la solicitud en el aviso."""
    return f"{solicitud.numero} «{solicitud.titulo}»"


def listar_notificaciones(
    db: Session,
    usuario_id: uuid.UUID,
    leida: bool | None,
    page: int,
    limit: int,
) -> NotificacionesLista:
    """Notificaciones del usuario, de la más reciente a la más antigua."""

    condiciones = [Notificacion.usuario_id == usuario_id]
    if leida is not None:
        condiciones.append(Notificacion.leida.is_(leida))

    total = db.scalar(select(func.count()).select_from(Notificacion).where(*condiciones))
    no_leidas = db.scalar(
        select(func.count())
        .select_from(Notificacion)
        .where(Notificacion.usuario_id == usuario_id, Notificacion.leida.is_(False))
    )

    notificaciones = db.scalars(
        select(Notificacion)
        .where(*condiciones)
        .order_by(Notificacion.fecha_creacion.desc(), Notificacion.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return NotificacionesLista(
        data=[NotificacionRespuesta.model_validate(n) for n in notificaciones],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=calcular_total_paginas(total, limit),
        ),
        no_leidas=no_leidas,
    )


def marcar_leida(
    db: Session, notificacion_id: uuid.UUID, usuario_id: uuid.UUID
) -> Notificacion:
    """Marca como leída una notificación propia.

    Una notificación de otro usuario responde 404 (y no 403) para no revelar
    que existe.
    """

    notificacion = db.get(Notificacion, notificacion_id)
    if notificacion is None or notificacion.usuario_id != usuario_id:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la notificación.")

    if not notificacion.leida:
        notificacion.leida = True
        db.commit()
        db.refresh(notificacion)
    return notificacion


def marcar_todas_leidas(db: Session, usuario_id: uuid.UUID) -> int:
    """Marca como leídas todas las notificaciones pendientes del usuario."""

    resultado = db.execute(
        update(Notificacion)
        .where(Notificacion.usuario_id == usuario_id, Notificacion.leida.is_(False))
        .values(leida=True)
    )
    db.commit()
    return resultado.rowcount
