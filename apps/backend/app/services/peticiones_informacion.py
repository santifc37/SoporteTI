"""RF-18, parte del solicitante: consultar y responder peticiones de información.

Reglas (docs/contrato-api.md §11.2 y §11.3):
- Consultar: solicitante propietario, técnico asignado actualmente o coordinador.
- Responder: solo el solicitante propietario de la solicitud relacionada.
- La petición debe estar `pendiente`; se admite una sola respuesta.
- Al responder, la petición pasa a `respondida`.
- La respuesta no cambia el estado de la solicitud.
- No se responde en solicitudes cerradas.

La creación de peticiones por el técnico (§11.1) está en
`app/services/solicitudes_informacion.py` y no se modifica aquí.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import RespuestaInformacion, Solicitud, SolicitudInformacion, Usuario
from app.schemas.peticiones_informacion import AutorPeticion, PeticionInformacionDetalle
from app.schemas.respuesta_informacion import (
    CrearRespuestaInformacion,
    RespuestaInformacionRespuesta,
)
from app.services.historial import _puede_consultar
from app.services.notificaciones import notificar, referencia


def listar_peticiones_informacion(
    db: Session,
    solicitud_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
) -> list[PeticionInformacionDetalle]:
    """§11.2: peticiones de una solicitud con su respuesta, en orden cronológico."""

    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la solicitud.")

    if not _puede_consultar(db, solicitud, usuario_id, rol):
        raise ApiError(
            403,
            "PERMISO_DENEGADO",
            "No tienes permisos para consultar las peticiones de esta solicitud.",
        )

    filas = db.execute(
        select(SolicitudInformacion, Usuario, RespuestaInformacion)
        .join(Usuario, Usuario.id == SolicitudInformacion.solicitado_por)
        .outerjoin(
            RespuestaInformacion,
            RespuestaInformacion.solicitud_informacion_id == SolicitudInformacion.id,
        )
        .where(SolicitudInformacion.solicitud_id == solicitud_id)
        .order_by(SolicitudInformacion.fecha_solicitud.asc(), SolicitudInformacion.id.asc())
    ).all()

    return [
        PeticionInformacionDetalle(
            id=peticion.id,
            contenido=peticion.contenido,
            estado=peticion.estado,
            solicitado_por=AutorPeticion(
                id=autor.id,
                nombre=f"{autor.nombre} {autor.apellido}".strip(),
                rol=autor.rol,
            ),
            fecha_solicitud=peticion.fecha_solicitud,
            respuesta=(
                RespuestaInformacionRespuesta.model_validate(respuesta)
                if respuesta is not None
                else None
            ),
        )
        for peticion, autor, respuesta in filas
    ]


def responder_peticion_informacion(
    db: Session,
    peticion_id: uuid.UUID,
    solicitante_id: uuid.UUID,
    datos: CrearRespuestaInformacion,
) -> RespuestaInformacion:
    """§11.3: el solicitante propietario responde una petición pendiente."""

    peticion = db.scalar(
        select(SolicitudInformacion)
        .where(SolicitudInformacion.id == peticion_id)
        .with_for_update()
    )
    if peticion is None:
        raise ApiError(
            404, "RECURSO_NO_ENCONTRADO", "No se encontró la petición de información."
        )

    solicitud = db.get(Solicitud, peticion.solicitud_id)
    if solicitud.solicitante_id != solicitante_id:
        raise ApiError(
            403,
            "PERMISO_DENEGADO",
            "Solo el solicitante de la solicitud puede responder esta petición.",
        )

    if solicitud.estado == "cerrado":
        raise ApiError(
            409,
            "SOLICITUD_CERRADA",
            "No se pueden responder peticiones de una solicitud cerrada.",
        )

    if peticion.estado != "pendiente":
        raise ApiError(
            409, "PETICION_YA_RESPONDIDA", "Esta petición de información ya fue respondida."
        )

    respuesta = RespuestaInformacion(
        solicitud_informacion_id=peticion.id,
        respondido_por=solicitante_id,
        contenido=datos.contenido,
    )
    peticion.estado = "respondida"

    # RF-27: avisa a quien hizo la petición; se guarda junto con la respuesta.
    notificar(
        db,
        peticion.solicitado_por,
        solicitud,
        "respuesta_informacion",
        f"El solicitante respondió tu petición de información en {referencia(solicitud)}.",
    )

    try:
        db.add(respuesta)
        db.commit()
    except IntegrityError:
        # Otra respuesta se registró al mismo tiempo (uq_respuestas_solicitud_informacion).
        db.rollback()
        raise ApiError(
            409, "PETICION_YA_RESPONDIDA", "Esta petición de información ya fue respondida."
        )

    db.refresh(respuesta)
    return respuesta
