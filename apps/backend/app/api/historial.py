"""Endpoint del historial de cambios: RF-28 (docs/contrato-api.md §14.1)."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.database.session import get_db
from app.schemas.historial import HistorialLista
from app.services.historial import consultar_historial

router = APIRouter(tags=["Historial"])


@router.get("/requests/{solicitud_id}/history", response_model=HistorialLista)
def historial(
    solicitud_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Historial de una solicitud: solicitante dueño, técnico asignado o coordinador."""

    return consultar_historial(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
        page=page,
        limit=limit,
    )
