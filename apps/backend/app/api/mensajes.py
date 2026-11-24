
"""Endpoints de la conversación: RF-22, RF-23 y RF-24."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.services.adjuntos import ErrorStorage
from app.api.dependencies import UsuarioActual, get_current_user
from app.core.errors import ApiError
from app.database.session import get_db
from app.schemas.mensajes import (
    EnviarMensaje,
    MensajeCreado,
    MensajeEnviadoRespuesta,
    MensajesLista,
)
from app.services.adjuntos_mensajes import (
    consultar_adjuntos_mensaje,
    registrar_adjunto_mensaje,
)
from app.services.mensajes import enviar_mensaje, listar_mensajes


router = APIRouter(tags=["Mensajes"])


@router.get(
    "/requests/{solicitud_id}/messages",
    response_model=MensajesLista,
)
def consultar(
    solicitud_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    desde: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Consulta la conversación de una solicitud."""

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
    """Envía un mensaje a la conversación."""

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


@router.post(
    "/requests/{solicitud_id}/messages/{mensaje_id}/attachments",
    status_code=201,
)
def adjuntar_imagen_mensaje(
    solicitud_id: uuid.UUID,
    mensaje_id: uuid.UUID,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Adjunta una imagen WebP a un mensaje."""

    try:
        adjunto = registrar_adjunto_mensaje(
            db=db,
            solicitud_id=solicitud_id,
            mensaje_id=mensaje_id,
            usuario_id=usuario.id,
            rol=usuario.rol,
            archivo=archivo,
        )
    except ErrorStorage as error:
        raise ApiError(
            502,
            "ERROR_ALMACENAMIENTO",
            "No fue posible almacenar la imagen.",
        ) from error

    return {
        "mensaje": "Imagen adjuntada correctamente",
        "adjunto": {
            "id": adjunto.id,
            "solicitud_id": adjunto.solicitud_id,
            "mensaje_id": adjunto.mensaje_id,
            "nombre_archivo": adjunto.nombre_archivo,
            "tipo_archivo": adjunto.tipo_archivo,
            "tamano": adjunto.tamano,
            "fecha_subida": adjunto.fecha_subida,
        },
    }


@router.get(
    "/requests/{solicitud_id}/messages/{mensaje_id}/attachments"
)
def obtener_adjuntos_mensaje(
    solicitud_id: uuid.UUID,
    mensaje_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Consulta los adjuntos y genera URL temporales para sus imágenes."""

    adjuntos = consultar_adjuntos_mensaje(
        db=db,
        solicitud_id=solicitud_id,
        mensaje_id=mensaje_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
    )

    data = [
        {
            "id": adjunto.id,
            "mensaje_id": adjunto.mensaje_id,
            "nombre_archivo": adjunto.nombre_archivo,
            "tipo_archivo": adjunto.tipo_archivo,
            "tamano": adjunto.tamano,
            "subido_por": adjunto.subido_por,
            "fecha_subida": adjunto.fecha_subida,
            "url": f"/api/v1/attachments/{adjunto.id}/download",
        }
        for adjunto in adjuntos
    ]

    return {"data": data}
