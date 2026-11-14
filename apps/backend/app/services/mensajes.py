"""Conversación de las solicitudes: RF-22, RF-23 y RF-26 (docs/contrato-api.md §12).

Reglas:
- Participan el solicitante propietario, el técnico asignado actualmente y el
  coordinador. Un técnico no asignado (o reasignado) no accede a la conversación.
- El remitente se obtiene de la sesión.
- No se envían mensajes en solicitudes cerradas, pero su conversación se puede
  seguir consultando.
- El solicitante puede escribir en cualquier estado abierto, incluido `en_espera`.
- Enviar un mensaje no cambia el estado de la solicitud.
- La conversación se devuelve en orden cronológico (RF-26), paginada y con un
  filtro opcional `desde` para traer solo los mensajes nuevos (sin WebSockets).
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Mensaje, Solicitud, Usuario
from app.schemas.mensajes import EnviarMensaje, MensajeConversacion, MensajesLista, Remitente
from app.schemas.pagination import Pagination, calcular_total_paginas
from app.services.historial import _puede_consultar


def _solicitud_accesible(
    db: Session, solicitud_id: uuid.UUID, usuario_id: uuid.UUID, rol: str
) -> Solicitud:
    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la solicitud.")

    if not _puede_consultar(db, solicitud, usuario_id, rol):
        raise ApiError(
            403,
            "PERMISO_DENEGADO",
            "No tienes permisos para acceder a la conversación de esta solicitud.",
        )
    return solicitud


def listar_mensajes(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    page: int,
    limit: int,
    desde: datetime | None = None,
) -> MensajesLista:
    """§12.1: conversación de la solicitud en orden cronológico."""

    _solicitud_accesible(db, solicitud_id, usuario_id, rol)

    condiciones = [Mensaje.solicitud_id == solicitud_id]
    if desde is not None:
        condiciones.append(Mensaje.fecha_envio > desde)

    total = db.scalar(select(func.count()).select_from(Mensaje).where(*condiciones))

    filas = db.execute(
        select(Mensaje, Usuario)
        .join(Usuario, Usuario.id == Mensaje.remitente_id)
        .where(*condiciones)
        .order_by(Mensaje.fecha_envio.asc(), Mensaje.id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return MensajesLista(
        data=[
            MensajeConversacion(
                id=mensaje.id,
                solicitud_id=mensaje.solicitud_id,
                remitente=Remitente(
                    id=autor.id,
                    nombre=f"{autor.nombre} {autor.apellido}".strip(),
                    rol=autor.rol,
                ),
                contenido=mensaje.contenido,
                fecha_envio=mensaje.fecha_envio,
            )
            for mensaje, autor in filas
        ],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=calcular_total_paginas(total, limit),
        ),
    )


def enviar_mensaje(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    datos: EnviarMensaje,
) -> Mensaje:
    """§12.2: registra un mensaje sin cambiar el estado de la solicitud."""

    solicitud = _solicitud_accesible(db, solicitud_id, usuario_id, rol)

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se pueden enviar mensajes en una solicitud cerrada.",
        )

    mensaje = Mensaje(
        solicitud_id=solicitud.id,
        remitente_id=usuario_id,
        contenido=datos.contenido,
    )
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    return mensaje
