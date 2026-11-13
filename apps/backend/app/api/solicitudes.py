
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.services.adjuntos import registrar_adjunto, ErrorStorage

from app.schemas.solucion import RegistrarSolucion
from app.schemas.solicitud_informacion import (
    CrearSolicitudInformacion,
    SolicitudInformacionRespuesta,
)
from app.schemas.respuesta_informacion import (
    CrearRespuestaInformacion,
    RespuestaInformacionRespuesta,
)
from app.services.solicitudes_informacion import (
    crear_solicitud_informacion,
    consultar_solicitudes_informacion,
    responder_solicitud_informacion,
)

from app.schemas.intervencion import CrearIntervencion, IntervencionRespuesta,IntervencionesRespuesta
from app.services.intervenciones import registrar_intervencion,consultar_intervenciones

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.errors import ApiError
from app.database.session import get_db
from app.schemas.solicitud import (
    ActualizarEstadoSolicitud,
    EstadoSolicitud,
    PrioridadSolicitud,
    SolicitudesPagina,
    TipoCierre,
    TipoSolicitud,
)
from app.services.solicitudes import (
    FiltrosSolicitudes,
    actualizar_estado_solicitud,
    listar_solicitudes,
    listar_solicitudes_asignadas,
    registrar_solucion,
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
    solicitante_id: uuid.UUID | None = None,
    tecnico_id: uuid.UUID | None = None,
    tipo_cierre: TipoCierre | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """Consulta las solicitudes a las que tiene acceso el usuario (RF-07, RF-13).

    - Técnico: solo las que tiene asignadas actualmente.
    - Solicitante: solo las propias.
    - Coordinador: todas; además puede filtrar por solicitante, técnico y tipo de cierre.

    Los filtros nunca amplían los permisos (contrato-api.md §17).
    """

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

    filtros = FiltrosSolicitudes(
        estado=estado,
        prioridad=prioridad,
        categoria_id=categoria_id,
        tipo=tipo,
        busqueda=busqueda,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    if usuario.rol == "tecnico":
        return listar_solicitudes_asignadas(
            db, usuario.id, filtros, page, limit
        )

    if usuario.rol == "solicitante":
        # Aunque envíe solicitante_id, solo ve las suyas.
        return listar_solicitudes(
            db, filtros, page, limit, solicitante_id=usuario.id
        )

    if usuario.rol == "coordinador":
        return listar_solicitudes(
            db,
            filtros,
            page,
            limit,
            solicitante_id=solicitante_id,
            tecnico_id=tecnico_id,
            tipo_cierre=tipo_cierre,
        )

    raise ApiError(
        403, "PERMISO_DENEGADO", "No tienes permisos para realizar esta operación."
    )


@router.patch("/requests/{solicitud_id}/status")
def cambiar_estado_solicitud(
    solicitud_id: uuid.UUID,
    datos: ActualizarEstadoSolicitud,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-14: cambio de estado según el rol.

    - Técnico asignado: asignado → en_atencion, en_atencion ↔ en_espera.
    - Coordinador (RF-09): registrado → en_evaluacion.
    """

    if usuario.rol == "coordinador":
        solicitud, estado_anterior = iniciar_evaluacion(
            db=db,
            solicitud_id=solicitud_id,
            coordinador_id=usuario.id,
            nuevo_estado=datos.estado,
        )
    elif usuario.rol == "tecnico":
        solicitud, estado_anterior = actualizar_estado_solicitud(
            db=db,
            solicitud_id=solicitud_id,
            tecnico_id=usuario.id,
            nuevo_estado=datos.estado,
        )
    else:
        raise ApiError(
            403,
            "SIN_PERMISO",
            "No tienes permiso para realizar esta operación.",
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

@router.post(
    "/requests/{solicitud_id}/interventions",
    response_model=IntervencionRespuesta,
    status_code=201,
)
def crear_intervencion(
    solicitud_id: uuid.UUID,
    datos: CrearIntervencion,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    if usuario.rol != "tecnico":
        raise ApiError(
            403,
            "SIN_PERMISO",
            "Solo los técnicos pueden registrar intervenciones.",
        )

    return registrar_intervencion(
        db=db,
        solicitud_id=solicitud_id,
        tecnico_id=usuario.id,
        datos=datos,
    )


@router.get(
    "/requests/{solicitud_id}/interventions",
    response_model=IntervencionesRespuesta,
)
def obtener_intervenciones(
    solicitud_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    intervenciones = consultar_intervenciones(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
    )

    return {"data": intervenciones}



# ------------------------- RF-18: información adicional -------------------------

@router.post(
    "/requests/{solicitud_id}/information-requests",
    status_code=201,
)
def crear_peticion_informacion(
    solicitud_id: uuid.UUID,
    datos: CrearSolicitudInformacion,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-18: técnico asignado o coordinador solicitan información."""

    peticion = crear_solicitud_informacion(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
        datos=datos,
    )

    return {
        "mensaje": "Solicitud de información registrada correctamente",
        "solicitud_informacion": SolicitudInformacionRespuesta.model_validate(
            peticion
        ),
    }


@router.get(
    "/requests/{solicitud_id}/information-requests",
)
def obtener_peticiones_informacion(
    solicitud_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-18: consulta las peticiones y sus respuestas."""

    peticiones = consultar_solicitudes_informacion(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=usuario.id,
        rol=usuario.rol,
    )

    return {"data": peticiones}


@router.post(
    "/information-requests/{solicitud_informacion_id}/responses",
    status_code=201,
)
def responder_peticion_informacion(
    solicitud_informacion_id: uuid.UUID,
    datos: CrearRespuestaInformacion,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-18: el solicitante propietario responde una petición."""

    if usuario.rol != "solicitante":
        raise ApiError(
            403,
            "SIN_PERMISO",
            "Solo el solicitante puede responder esta petición.",
        )

    respuesta = responder_solicitud_informacion(
        db=db,
        solicitud_informacion_id=solicitud_informacion_id,
        solicitante_id=usuario.id,
        datos=datos,
    )

    return {
        "mensaje": "Respuesta registrada correctamente",
        "respuesta": RespuestaInformacionRespuesta.model_validate(respuesta),
    }



@router.post("/requests/{solicitud_id}/resolve")
def resolver_solicitud(
    solicitud_id: uuid.UUID,
    datos: RegistrarSolucion,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-19: permite al técnico asignado registrar la solución."""

    if usuario.rol != "tecnico":
        raise ApiError(
            403,
            "SIN_PERMISO",
            "Solo los técnicos pueden registrar la solución.",
        )

    solicitud, estado_anterior = registrar_solucion(
        db=db,
        solicitud_id=solicitud_id,
        tecnico_id=usuario.id,
        datos=datos,
    )

    return {
        "mensaje": "Solución registrada correctamente",
        "solicitud": {
            "id": solicitud.id,
            "estado_anterior": estado_anterior,
            "estado_actual": solicitud.estado,
            "solucion_final": solicitud.solucion_final,
            "resuelto_por": solicitud.resuelto_por,
            "fecha_resolucion": solicitud.fecha_resolucion,
            "fecha_actualizacion": solicitud.fecha_actualizacion,
        },
    }


@router.post(
    "/requests/{solicitud_id}/interventions/{intervencion_id}/attachments",
    status_code=201,
)
def adjuntar_imagen_intervencion(
    solicitud_id: uuid.UUID,
    intervencion_id: uuid.UUID,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-25: adjunta una imagen WebP a una intervención técnica."""

    if usuario.rol != "tecnico":
        raise ApiError(
            403,
            "SIN_PERMISO",
            "Solo los técnicos pueden adjuntar imágenes.",
        )

    try:
        adjunto = registrar_adjunto(
            db=db,
            solicitud_id=solicitud_id,
            intervencion_id=intervencion_id,
            tecnico_id=usuario.id,
            archivo=archivo,
        )
    except ErrorStorage as error:
        raise ApiError(
            502,
            "ERROR_ALMACENAMIENTO",
            "No fue posible almacenar la imagen.",
        ) from error

    return {
        "mensaje": "Imagen adjuntada correctamente.",
        "adjunto": {
            "id": adjunto.id,
            "solicitud_id": adjunto.solicitud_id,
            "nombre_archivo": adjunto.nombre_archivo,
            "tipo_archivo": adjunto.tipo_archivo,
            "tamano": adjunto.tamano,
            "fecha_subida": adjunto.fecha_subida,
        },
    }


# ------------------------------ RF-06: crear solicitud ------------------------------

from app.api.permisos import requiere_rol
from app.schemas.solicitud import (
    CrearSolicitud,
    SolicitudCreada,
    SolicitudCreadaMensaje,
)
from app.services.solicitudes import crear_solicitud


@router.post(
    "/requests",
    response_model=SolicitudCreadaMensaje,
    status_code=201,
)
def registrar_solicitud(
    datos: CrearSolicitud,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(requiere_rol("solicitante")),
):
    """RF-06: el solicitante registra una solicitud de soporte."""

    solicitud = crear_solicitud(db=db, solicitante_id=usuario.id, datos=datos)

    return SolicitudCreadaMensaje(
        mensaje="Solicitud creada correctamente",
        solicitud=SolicitudCreada.model_validate(solicitud),
    )


# --------------------------- RF-07: detalle de una solicitud ---------------------------

from app.schemas.solicitud import SolicitudDetalle
from app.services.solicitudes import obtener_solicitud_detalle


@router.get("/requests/{solicitud_id}", response_model=SolicitudDetalle)
def detalle_solicitud(
    solicitud_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """RF-07: detalle de una solicitud (contrato-api.md §7.3).

    Pueden consultarla el solicitante propietario, el técnico asignado
    actualmente y el coordinador.
    """

    return obtener_solicitud_detalle(
        db=db, solicitud_id=solicitud_id, usuario_id=usuario.id, rol=usuario.rol
    )



# ------------------- RF-09 / RF-10: evaluación y clasificación -------------------

from app.schemas.solicitud import (
    ClasificarSolicitud,
    SolicitudClasificada,
    SolicitudClasificadaMensaje,
)
from app.services.solicitudes import clasificar_solicitud, iniciar_evaluacion


@router.patch("/requests/{solicitud_id}", response_model=SolicitudClasificadaMensaje)
def clasificar(
    solicitud_id: uuid.UUID,
    datos: ClasificarSolicitud,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(requiere_rol("coordinador")),
):
    """RF-10: el coordinador establece la categoría y la prioridad (contrato §7.4)."""

    solicitud = clasificar_solicitud(
        db=db, solicitud_id=solicitud_id, coordinador_id=usuario.id, datos=datos
    )

    return SolicitudClasificadaMensaje(
        mensaje="Solicitud actualizada correctamente",
        solicitud=SolicitudClasificada(
            id=solicitud.id,
            numero=solicitud.numero,
            categoria_id=solicitud.categoria_id,
            prioridad=solicitud.prioridad,
            estado=solicitud.estado,
        ),
    )
