
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.errors import ApiError
from app.database.session import get_db
from app.schemas.solicitud import (
    ActualizarEstadoSolicitud,
    EstadoSolicitud,
    PrioridadSolicitud,
    SolicitudesPagina,
    TipoSolicitud,
)
from app.services.solicitudes import (
    FiltrosSolicitudes,
    actualizar_estado_solicitud,
    listar_solicitudes_asignadas,
)

router = APIRouter(tags=["Solicitudes"])


@router.get("/requests", response_model=SolicitudesPagina)
def consultar_solicitudes(
    estado: EstadoSolicitud | None = None,
    prioridad: PrioridadSolicitud | None = None,
    categoria_id: uuid.UUID | None = None,
    tipo: TipoSolicitud | None = None,
    busqueda: str | None = Query(default=None, max_length=100),
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Consulta las solicitudes a las que tiene acceso el usuario (RF-07, RF-13)."""

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise ApiError(
            422,
            "ERROR_VALIDACION",
            "Los datos enviados no son válidos.",
            [
                {
                    "campo": "fecha_desde",
                    "mensaje": "No puede ser posterior a fecha_hasta.",
                }
            ],
        )

    if usuario.rol == "tecnico":
        filtros = FiltrosSolicitudes(
            estado=estado,
            prioridad=prioridad,
            categoria_id=categoria_id,
            tipo=tipo,
            busqueda=busqueda,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
        return listar_solicitudes_asignadas(
            db, usuario.id, filtros, page, limit
        )

    raise ApiError(
        501,
        "NO_IMPLEMENTADO",
        "La consulta de solicitudes para este rol aún no está disponible.",
    )


@router.patch("/requests/{solicitud_id}/status")
def cambiar_estado_solicitud(
    solicitud_id: uuid.UUID,
    datos: ActualizarEstadoSolicitud,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-14: permite al técnico asignado actualizar el estado."""

    if usuario.rol != "tecnico":
        raise ApiError(
            403,
            "SIN_PERMISO",
            "No tienes permiso para realizar esta operación.",
        )

    solicitud, estado_anterior = actualizar_estado_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        tecnico_id=usuario.id,
        nuevo_estado=datos.estado,
    )

    return {
        "mensaje": "Estado actualizado correctamente",
        "solicitud": {
            "id": str(solicitud.id),
            "estado_anterior": estado_anterior,
            "estado_actual": solicitud.estado,
            "fecha_actualizacion": solicitud.fecha_actualizacion,
        },
    }
