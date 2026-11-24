"""Endpoints de asignación de técnicos: RF-11 y RF-12 (docs/contrato-api.md §9)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.api.permisos import requiere_rol
from app.database.session import get_db
from app.schemas.asignacion import (
    AsignacionCreadaMensaje,
    AsignacionesLista,
    AsignacionRespuesta,
    AsignarTecnico,
)
from app.services.asignaciones import asignar_tecnico, consultar_asignaciones

router = APIRouter(tags=["Asignaciones"])


@router.post(
    "/requests/{solicitud_id}/assignments",
    response_model=AsignacionCreadaMensaje,
    status_code=201,
)
def asignar(
    solicitud_id: uuid.UUID,
    datos: AsignarTecnico,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(requiere_rol("coordinador")),
):
    """Asigna (RF-11) o reasigna (RF-12) el técnico responsable de una solicitud."""

    asignacion, solicitud = asignar_tecnico(
        db=db, solicitud_id=solicitud_id, coordinador_id=usuario.id, datos=datos
    )
    return AsignacionCreadaMensaje(
        mensaje="Técnico asignado correctamente",
        asignacion=AsignacionRespuesta.model_validate(asignacion),
        estado_solicitud=solicitud.estado,
    )


@router.get("/requests/{solicitud_id}/assignments", response_model=AsignacionesLista)
def listar(
    solicitud_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Historial de asignaciones; el solicitante solo ve al responsable actual."""

    return AsignacionesLista(
        data=consultar_asignaciones(
            db=db, solicitud_id=solicitud_id, usuario_id=usuario.id, rol=usuario.rol
        )
    )
