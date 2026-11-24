"""Endpoints de cierre (RF-20) y cancelación (RF-15) (docs/contrato-api.md §13)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual
from app.api.permisos import requiere_rol
from app.database.session import get_db
from app.models import Solicitud
from app.schemas.cierre import (
    CancelarSolicitud,
    CerrarSolicitud,
    SolicitudCerrada,
    SolicitudCerradaMensaje,
)
from app.services.cierres import cancelar_solicitud, cerrar_solicitud

router = APIRouter(tags=["Cierre y cancelación"])


def _respuesta(mensaje: str, solicitud: Solicitud, estado_anterior: str) -> SolicitudCerradaMensaje:
    return SolicitudCerradaMensaje(
        mensaje=mensaje,
        solicitud=SolicitudCerrada(
            id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_actual=solicitud.estado,
            tipo_cierre=solicitud.tipo_cierre,
            motivo_cierre=solicitud.motivo_cierre,
            cerrado_por=solicitud.cerrado_por,
            fecha_cierre=solicitud.fecha_cierre,
        ),
    )


@router.post("/requests/{solicitud_id}/close", response_model=SolicitudCerradaMensaje)
def cerrar(
    solicitud_id: uuid.UUID,
    datos: CerrarSolicitud,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(requiere_rol("coordinador")),
):
    """RF-20: cierre por solución (desde resuelto) o administrativo (desde en evaluación)."""

    solicitud, estado_anterior = cerrar_solicitud(
        db=db, solicitud_id=solicitud_id, coordinador_id=usuario.id, datos=datos
    )
    return _respuesta("Solicitud cerrada correctamente", solicitud, estado_anterior)


@router.post("/requests/{solicitud_id}/cancel", response_model=SolicitudCerradaMensaje)
def cancelar(
    solicitud_id: uuid.UUID,
    datos: CancelarSolicitud,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(requiere_rol("solicitante")),
):
    """RF-15: el solicitante cancela su solicitud (registrada o en evaluación)."""

    solicitud, estado_anterior = cancelar_solicitud(
        db=db, solicitud_id=solicitud_id, solicitante_id=usuario.id, datos=datos
    )
    return _respuesta("Solicitud cancelada correctamente", solicitud, estado_anterior)
