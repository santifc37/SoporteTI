
"""Endpoints de usuarios: RF-03, RF-04 y RF-05."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.api.permisos import requiere_rol
from app.database.session import get_db
from app.schemas.auth import RestablecerContrasenaPeticion, MensajeRespuesta
from app.schemas.pagination import Pagination, calcular_total_paginas
from app.schemas.usuarios import (
    Rol,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioDetalle,
    UsuarioListado,
    UsuarioMensaje,
    UsuarioResumen,
    UsuariosPagina,
)
from app.services.autenticacion import restablecer_contrasena
from app.services.usuarios import (
    actualizar_usuario,
    crear_usuario,
    listar_usuarios,
    obtener_usuario,
)

router = APIRouter(prefix="/users", tags=["Usuarios"])

solo_coordinador = requiere_rol("coordinador")


@router.get("", response_model=UsuariosPagina, dependencies=[Depends(solo_coordinador)])
def listar(
    rol: Rol | None = None,
    activo: bool | None = None,
    busqueda: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista los usuarios con filtros y paginación (RF-03)."""
    usuarios, total = listar_usuarios(
        db, rol=rol, activo=activo, busqueda=busqueda, page=page, limit=limit
    )
    return UsuariosPagina(
        data=[UsuarioListado.model_validate(u) for u in usuarios],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=calcular_total_paginas(total, limit),
        ),
    )


@router.get(
    "/{usuario_id}", response_model=UsuarioDetalle, dependencies=[Depends(solo_coordinador)]
)
def detalle(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    """Consulta un usuario (RF-03)."""
    return UsuarioDetalle.model_validate(obtener_usuario(db, usuario_id))


@router.post(
    "",
    response_model=UsuarioMensaje,
    status_code=201,
    dependencies=[Depends(solo_coordinador)],
)
def crear(datos: UsuarioCrear, db: Session = Depends(get_db)):
    """Crea una cuenta (RF-03). No existe registro público (RN-02)."""
    usuario = crear_usuario(db, datos)
    return UsuarioMensaje(
        mensaje="Usuario creado correctamente",
        usuario=UsuarioResumen.model_validate(usuario),
    )


@router.post(
    "/{usuario_id}/reset-password",
    response_model=MensajeRespuesta,
    dependencies=[Depends(solo_coordinador)],
)
def restablecer_clave(
    usuario_id: uuid.UUID,
    datos: RestablecerContrasenaPeticion,
    db: Session = Depends(get_db),
):
    """Permite al coordinador asignar una contraseña temporal (RF-04)."""
    restablecer_contrasena(db, usuario_id, datos.contrasena_temporal)
    return MensajeRespuesta(mensaje="Contraseña restablecida correctamente")


@router.patch("/{usuario_id}", response_model=UsuarioMensaje)
def actualizar(
    usuario_id: uuid.UUID,
    datos: UsuarioActualizar,
    actor: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Modifica una cuenta (RF-05)."""
    usuario = actualizar_usuario(db, actor, usuario_id, datos)
    return UsuarioMensaje(
        mensaje="Usuario actualizado correctamente",
        usuario=UsuarioResumen.model_validate(usuario),
    )
