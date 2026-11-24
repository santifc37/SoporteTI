"""Endpoints de categorías (docs/contrato-api.md §6)."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.api.permisos import requiere_rol
from app.database.session import get_db
from app.schemas.categorias import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaMensaje,
    CategoriaRespuesta,
    CategoriasPagina,
)
from app.schemas.pagination import Pagination, calcular_total_paginas
from app.services.categorias import actualizar_categoria, crear_categoria, listar_categorias

router = APIRouter(prefix="/categories", tags=["Categorías"])

solo_coordinador = requiere_rol("coordinador")


@router.get("", response_model=CategoriasPagina)
def listar(
    activa: bool | None = None,
    busqueda: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista categorías. Solicitantes y técnicos solo reciben las activas."""
    if usuario.rol != "coordinador":
        activa = True

    categorias, total = listar_categorias(
        db, activa=activa, busqueda=busqueda, page=page, limit=limit
    )
    return CategoriasPagina(
        data=[CategoriaRespuesta.model_validate(c) for c in categorias],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=calcular_total_paginas(total, limit),
        ),
    )


@router.post(
    "",
    response_model=CategoriaMensaje,
    status_code=201,
    dependencies=[Depends(solo_coordinador)],
)
def crear(datos: CategoriaCrear, db: Session = Depends(get_db)):
    """Crea una categoría activa."""
    return CategoriaMensaje(
        mensaje="Categoría creada correctamente",
        categoria=CategoriaRespuesta.model_validate(crear_categoria(db, datos)),
    )


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaMensaje,
    dependencies=[Depends(solo_coordinador)],
)
def actualizar(
    categoria_id: uuid.UUID, datos: CategoriaActualizar, db: Session = Depends(get_db)
):
    """Modifica una categoría. Para retirarla del uso se envía {"activa": false}."""
    return CategoriaMensaje(
        mensaje="Categoría actualizada correctamente",
        categoria=CategoriaRespuesta.model_validate(
            actualizar_categoria(db, categoria_id, datos)
        ),
    )
