"""Endpoint de estadísticas: RF-29 (docs/contrato-api.md §16)."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.permisos import requiere_rol
from app.core.errors import ApiError
from app.database.session import get_db
from app.schemas.estadisticas import Estadisticas
from app.services.estadisticas import calcular_estadisticas

router = APIRouter(tags=["Estadísticas"])


@router.get(
    "/statistics",
    response_model=Estadisticas,
    dependencies=[Depends(requiere_rol("coordinador"))],
)
def consultar_estadisticas(
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    db: Session = Depends(get_db),
):
    """Consolidado de solicitudes para el coordinador (RF-29, CA-06).

    El rango de fechas se aplica sobre la fecha de creación y afecta a todos
    los indicadores por igual. `tiempo_promedio_atencion` está en horas.
    """

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise ApiError(
            422,
            "ERROR_VALIDACION",
            "Los datos enviados no son válidos.",
            [{"campo": "fecha_desde", "mensaje": "No puede ser posterior a fecha_hasta."}],
        )

    return calcular_estadisticas(db, fecha_desde, fecha_hasta)
