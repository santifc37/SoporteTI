"""RF-20 (cierre por solución o administrativo) y RF-15 (cancelación).

Transiciones permitidas (requisitos.md §8.1):

    resuelto       → cerrado   coordinador   tipo "solucion"
    en_evaluacion  → cerrado   coordinador   tipo "administrativo", motivo obligatorio
    registrado     → cerrado   solicitante   tipo "cancelacion", motivo obligatorio
    en_evaluacion  → cerrado   solicitante   tipo "cancelacion", motivo obligatorio

Una solicitud cerrada no se reabre (RN-21) y conserva toda su información.
El tipo, el responsable, la fecha y el motivo quedan en la solicitud y en
su historial (requisitos.md §8.2).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Asignacion, Solicitud
from app.models.historial_cambio import HistorialCambio
from app.schemas.cierre import CancelarSolicitud, CerrarSolicitud
from app.services.notificaciones import notificar, referencia
from app.services.solicitudes import _solicitud_para_modificar

# Estado desde el que se permite cada tipo de cierre del coordinador.
ESTADO_REQUERIDO = {
    "solucion": "resuelto",
    "administrativo": "en_evaluacion",
}
ESTADOS_CANCELABLES = {"registrado", "en_evaluacion"}

# Valores de historial_cambios.tipo_cambio (docs/MER.md).
TIPO_CAMBIO = {
    "solucion": "cierre_solucion",
    "administrativo": "cierre_administrativo",
    "cancelacion": "cancelacion",
}


def _rechazar_si_cerrada(solicitud: Solicitud) -> None:
    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "La solicitud ya está cerrada y no puede reabrirse ni modificarse.",
        )


def _cerrar(
    db: Session,
    solicitud: Solicitud,
    usuario_id: uuid.UUID,
    tipo_cierre: str,
    motivo: str | None,
) -> str:
    """Cierra la solicitud y registra el historial en una misma transacción."""
    estado_anterior = solicitud.estado
    ahora = datetime.now(timezone.utc)

    try:
        solicitud.estado = "cerrado"
        solicitud.tipo_cierre = tipo_cierre
        solicitud.motivo_cierre = motivo
        solicitud.cerrado_por = usuario_id
        solicitud.fecha_cierre = ahora
        solicitud.fecha_actualizacion = ahora
        solicitud.version += 1

        db.add(
            HistorialCambio(
                solicitud_id=solicitud.id,
                usuario_id=usuario_id,
                tipo_cambio=TIPO_CAMBIO[tipo_cierre],
                valor_anterior=estado_anterior,
                valor_nuevo="cerrado",
                observacion=motivo,
            )
        )
        db.commit()
        db.refresh(solicitud)
        return estado_anterior

    except Exception:
        db.rollback()
        raise


def _notificar_cierre(db: Session, solicitud: Solicitud, tipo_cierre: str) -> None:
    """Avisa del cierre al solicitante y al técnico asignado, si lo hay."""
    detalle = {
        "solucion": "fue cerrada como solucionada",
        "administrativo": "fue cerrada administrativamente",
    }[tipo_cierre]
    ref = referencia(solicitud)

    notificar(
        db, solicitud.solicitante_id, solicitud, "solicitud_cerrada", f"Tu solicitud {ref} {detalle}."
    )

    tecnico_id = db.scalar(
        select(Asignacion.tecnico_id).where(
            Asignacion.solicitud_id == solicitud.id,
            Asignacion.fecha_finalizacion.is_(None),
        )
    )
    if tecnico_id is not None:
        notificar(db, tecnico_id, solicitud, "solicitud_cerrada", f"La solicitud {ref} {detalle}.")


def cerrar_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
    coordinador_id: uuid.UUID,
    datos: CerrarSolicitud,
) -> tuple[Solicitud, str]:
    """RF-20: el coordinador cierra por solución o por causa administrativa."""

    solicitud = _solicitud_para_modificar(db, solicitud_id)
    _rechazar_si_cerrada(solicitud)

    requerido = ESTADO_REQUERIDO[datos.tipo_cierre]
    if solicitud.estado != requerido:
        mensajes = {
            "solucion": "Solo se puede cerrar por solución una solicitud resuelta.",
            "administrativo": "El cierre administrativo solo se permite durante la evaluación.",
        }
        raise ApiError(409, "ESTADO_NO_PERMITIDO", mensajes[datos.tipo_cierre])

    # RF-27: se confirman junto con el cierre (el commit lo hace _cerrar).
    _notificar_cierre(db, solicitud, datos.tipo_cierre)

    estado_anterior = _cerrar(
        db, solicitud, coordinador_id, datos.tipo_cierre, datos.motivo_cierre
    )
    return solicitud, estado_anterior


def cancelar_solicitud(
    db: Session,
    solicitud_id: uuid.UUID,
    solicitante_id: uuid.UUID,
    datos: CancelarSolicitud,
) -> tuple[Solicitud, str]:
    """RF-15: el solicitante cancela su solicitud antes de que sea asignada."""

    solicitud = _solicitud_para_modificar(db, solicitud_id)

    if solicitud.solicitante_id != solicitante_id:
        raise ApiError(
            403, "PERMISO_DENEGADO", "Solo puedes cancelar tus propias solicitudes."
        )

    _rechazar_si_cerrada(solicitud)

    if solicitud.estado not in ESTADOS_CANCELABLES:
        raise ApiError(
            409,
            "ESTADO_NO_PERMITIDO",
            "Solo se puede cancelar una solicitud registrada o en evaluación.",
        )

    estado_anterior = _cerrar(db, solicitud, solicitante_id, "cancelacion", datos.motivo)
    return solicitud, estado_anterior
