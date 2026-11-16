"""Endpoints de las notificaciones internas: RF-27."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.database.session import get_db
from app.schemas.notificaciones import (
    NotificacionesLeidasMensaje,
    NotificacionesLista,
    NotificacionLeidaMensaje,
    NotificacionRespuesta,
)
from app.services.notificaciones import (
    listar_notificaciones,
    marcar_leida,
    marcar_todas_leidas,
)

router = APIRouter(tags=["Notificaciones"])


@router.get("/notifications", response_model=NotificacionesLista)
def consultar(
    leida: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Notificaciones del usuario autenticado; `leida` filtra por leídas o no leídas."""

    return listar_notificaciones(
        db=db, usuario_id=usuario.id, leida=leida, page=page, limit=limit
    )


@router.patch("/notifications/read-all", response_model=NotificacionesLeidasMensaje)
def leer_todas(
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Marca como leídas todas las notificaciones del usuario."""

    actualizadas = marcar_todas_leidas(db=db, usuario_id=usuario.id)
    return NotificacionesLeidasMensaje(
        mensaje="Notificaciones marcadas como leídas", actualizadas=actualizadas
    )


@router.patch("/notifications/{notificacion_id}/read", response_model=NotificacionLeidaMensaje)
def leer(
    notificacion_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Marca como leída una notificación propia."""

    notificacion = marcar_leida(db=db, notificacion_id=notificacion_id, usuario_id=usuario.id)
    return NotificacionLeidaMensaje(
        mensaje="Notificación marcada como leída",
        notificacion=NotificacionRespuesta.model_validate(notificacion),
    )
