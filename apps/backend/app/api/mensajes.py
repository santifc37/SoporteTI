"""Endpoints de la conversación: RF-22, RF-23 y RF-26 (docs/contrato-api.md §12)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.database.session import get_db
from app.schemas.mensajes import (
    EnviarMensaje,
    MensajeCreado,
    MensajeEnviadoRespuesta,
    MensajesLista,
)
from app.services.mensajes import enviar_mensaje, listar_mensajes

router = APIRouter(tags=["Mensajes"])


@router.get("/requests/{solicitud_id}/messages", response_model=MensajesLista)
def consultar(
    solicitud_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    desde: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Conversación de la solicitud en orden cronológico (RF-22, RF-26)."""

    return listar_mensajes(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
        page=page,
        limit=limit,
        desde=desde,
    )


@router.post(
    "/requests/{solicitud_id}/messages",
    response_model=MensajeEnviadoRespuesta,
    status_code=201,
)
def enviar(
    solicitud_id: uuid.UUID,
    datos: EnviarMensaje,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Envía un mensaje a la conversación de la solicitud (RF-23)."""

    mensaje = enviar_mensaje(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
        datos=datos,
    )
    return MensajeEnviadoRespuesta(
        mensaje="Mensaje enviado correctamente",
        data=MensajeCreado.model_validate(mensaje),
    )
