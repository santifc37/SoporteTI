"""RF-11 (asignación) y RF-12 (reasignación) de técnicos.

Reglas (docs/contrato-api.md §9, requisitos.md RN-11 a RN-14):
- Solo el coordinador asigna y reasigna.
- El técnico debe existir, tener rol técnico y estar activo.
- La primera asignación se hace sobre una solicitud `en_evaluacion` y la
  pasa a `asignado`.
- Reasignar finaliza la asignación activa y crea una nueva; las anteriores se
  conservan como historial. No cambia el estado de la solicitud.
- Solo hay una asignación activa por solicitud (índice uq_asignacion_activa).
- El técnico anterior pierde el acceso, porque todo el acceso del técnico se
  calcula a partir de la asignación activa.
- Cada operación queda en historial_cambios.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Asignacion, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio
from app.schemas.asignacion import AsignacionHistorial, AsignarTecnico
from app.services.solicitudes import _solicitud_para_modificar

# Estados en los que la solicitud ya tiene técnico y se puede reasignar.
ESTADOS_REASIGNABLES = {"asignado", "en_atencion", "en_espera"}


def _nombre(usuario: Usuario) -> str:
    return f"{usuario.nombre} {usuario.apellido}".strip()


def _asignacion_activa(db: Session, solicitud_id: uuid.UUID) -> Asignacion | None:
    return db.scalar(
        select(Asignacion).where(
            Asignacion.solicitud_id == solicitud_id,
            Asignacion.fecha_finalizacion.is_(None),
        )
    )


def asignar_tecnico(
    db: Session,
    solicitud_id: uuid.UUID,
    coordinador_id: uuid.UUID,
    datos: AsignarTecnico,
) -> tuple[Asignacion, Solicitud]:
    """Asigna (RF-11) o reasigna (RF-12) el técnico responsable."""

    solicitud = _solicitud_para_modificar(db, solicitud_id)

    if solicitud.estado == "cerrado":
        raise ApiError(
            409, "SOLICITUD_CERRADA", "No se puede asignar una solicitud cerrada."
        )

    tecnico = db.get(Usuario, datos.tecnico_id)
    if tecnico is None or tecnico.rol != "tecnico" or not tecnico.activo:
        raise ApiError(
            422,
            "TECNICO_NO_VALIDO",
            "El técnico no existe, no tiene el rol de técnico o está inactivo.",
            [{"campo": "tecnico_id", "mensaje": "Debe ser un técnico activo."}],
        )

    anterior = _asignacion_activa(db, solicitud.id)

    if anterior is None and solicitud.estado != "en_evaluacion":
        raise ApiError(
            409,
            "ESTADO_NO_PERMITIDO",
            "La primera asignación solo se puede hacer con la solicitud en evaluación.",
        )
    if anterior is not None and solicitud.estado not in ESTADOS_REASIGNABLES:
        raise ApiError(
            409,
            "ESTADO_NO_PERMITIDO",
            "Solo se puede reasignar una solicitud asignada, en atención o en espera.",
        )
    if anterior is not None and anterior.tecnico_id == tecnico.id:
        raise ApiError(
            409,
            "TECNICO_YA_ASIGNADO",
            "La solicitud ya está asignada a ese técnico.",
        )

    ahora = datetime.now(timezone.utc)
    registros: list[HistorialCambio] = []

    try:
        if anterior is not None:
            # RF-12: se finaliza la asignación anterior antes de crear la nueva,
            # para no violar la regla de una sola asignación activa.
            anterior.fecha_finalizacion = ahora
            db.flush()
            tecnico_anterior = db.get(Usuario, anterior.tecnico_id)
            registros.append(
                HistorialCambio(
                    solicitud_id=solicitud.id,
                    usuario_id=coordinador_id,
                    tipo_cambio="reasignacion",
                    valor_anterior=_nombre(tecnico_anterior),
                    valor_nuevo=_nombre(tecnico),
                    observacion=datos.observacion or None,
                )
            )
        else:
            # RF-11: primera asignación; la solicitud pasa a "asignado".
            registros.append(
                HistorialCambio(
                    solicitud_id=solicitud.id,
                    usuario_id=coordinador_id,
                    tipo_cambio="asignacion",
                    valor_nuevo=_nombre(tecnico),
                    observacion=datos.observacion or None,
                )
            )
            registros.append(
                HistorialCambio(
                    solicitud_id=solicitud.id,
                    usuario_id=coordinador_id,
                    tipo_cambio="cambio_estado",
                    valor_anterior=solicitud.estado,
                    valor_nuevo="asignado",
                )
            )
            solicitud.estado = "asignado"

        nueva = Asignacion(
            solicitud_id=solicitud.id,
            tecnico_id=tecnico.id,
            asignado_por=coordinador_id,
            observacion=datos.observacion or None,
            fecha_asignacion=ahora,
        )
        db.add(nueva)

        solicitud.fecha_actualizacion = ahora
        solicitud.version += 1
        db.add_all(registros)
        db.commit()
        db.refresh(nueva)
        db.refresh(solicitud)
        return nueva, solicitud

    except Exception:
        db.rollback()
        raise


def consultar_asignaciones(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> list[AsignacionHistorial]:
    """Historial de asignaciones de una solicitud, en orden cronológico.

    - Coordinador y técnico asignado actualmente: todas las asignaciones.
    - Solicitante propietario: solo el responsable actual, sin datos internos.
    """

    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la solicitud.")

    activa = _asignacion_activa(db, solicitud.id)

    if rol == "solicitante":
        autorizado = solicitud.solicitante_id == usuario_id
    elif rol == "tecnico":
        autorizado = activa is not None and activa.tecnico_id == usuario_id
    else:
        autorizado = rol == "coordinador"

    if not autorizado:
        raise ApiError(
            403, "PERMISO_DENEGADO", "No tienes permisos para consultar esta solicitud."
        )

    if rol == "solicitante":
        if activa is None:
            return []
        tecnico = db.get(Usuario, activa.tecnico_id)
        return [
            AsignacionHistorial(
                id=activa.id,
                tecnico_id=activa.tecnico_id,
                tecnico_nombre=_nombre(tecnico),
                asignado_por=None,
                fecha_asignacion=activa.fecha_asignacion,
                fecha_finalizacion=None,
                observacion=None,
            )
        ]

    filas = db.execute(
        select(Asignacion, Usuario)
        .join(Usuario, Usuario.id == Asignacion.tecnico_id)
        .where(Asignacion.solicitud_id == solicitud.id)
        .order_by(Asignacion.fecha_asignacion, Asignacion.id)
    ).all()

    return [
        AsignacionHistorial(
            id=asignacion.id,
            tecnico_id=asignacion.tecnico_id,
            tecnico_nombre=_nombre(tecnico),
            asignado_por=asignacion.asignado_por,
            fecha_asignacion=asignacion.fecha_asignacion,
            fecha_finalizacion=asignacion.fecha_finalizacion,
            observacion=asignacion.observacion,
        )
        for asignacion, tecnico in filas
    ]
