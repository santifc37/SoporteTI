"""Endpoints de RF-18, parte del solicitante (docs/contrato-api.md §11.2 y §11.3).

El `POST /requests/{id}/information-requests` del técnico (§11.1) está en
`app/api/solicitudes.py`.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.api.permisos import requiere_rol
from app.database.session import get_db
from app.schemas.peticiones_informacion import (
    PeticionesInformacionLista,
    RespuestaRegistradaMensaje,
)
from app.schemas.respuesta_informacion import (
    CrearRespuestaInformacion,
    RespuestaInformacionRespuesta,
)
from app.services.peticiones_informacion import (
    listar_peticiones_informacion,
    responder_peticion_informacion,
)

router = APIRouter(tags=["Peticiones de información"])


@router.get(
    "/requests/{solicitud_id}/information-requests",
    response_model=PeticionesInformacionLista,
)
def listar(
    solicitud_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Peticiones de información de una solicitud, con su respuesta si la tiene."""

    return PeticionesInformacionLista(
        data=listar_peticiones_informacion(
            db=db, solicitud_id=solicitud_id, usuario_id=usuario.id, rol=usuario.rol
        )
    )


@router.post(
    "/information-requests/{peticion_id}/responses",
    response_model=RespuestaRegistradaMensaje,
    status_code=201,
)
def responder(
    peticion_id: uuid.UUID,
    datos: CrearRespuestaInformacion,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(requiere_rol("solicitante")),
):
    """El solicitante propietario responde una petición de información pendiente."""

    respuesta = responder_peticion_informacion(
        db=db, peticion_id=peticion_id, solicitante_id=usuario.id, datos=datos
    )
    return RespuestaRegistradaMensaje(
        mensaje="Respuesta registrada correctamente",
        respuesta=RespuestaInformacionRespuesta.model_validate(respuesta),
    )
