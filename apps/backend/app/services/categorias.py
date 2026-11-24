"""Gestión de categorías (docs/contrato-api.md §6).

Reglas:
- Solo el coordinador crea y modifica categorías.
- El nombre es único sin distinguir mayúsculas (índice uq_categorias_nombre).
- Las categorías no se eliminan: se desactivan para retirarlas del uso, y
  las solicitudes que ya la usan la conservan.
- Solicitantes y técnicos solo ven las categorías activas, que son las que
  se pueden elegir al registrar una solicitud.
"""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models import Categoria
from app.schemas.categorias import CategoriaActualizar, CategoriaCrear


def _categoria_duplicada() -> ApiError:
    return ApiError(409, "CATEGORIA_DUPLICADA", "Ya existe una categoría con ese nombre.")


def _nombre_en_uso(db: Session, nombre: str, excluir_id: uuid.UUID | None = None) -> bool:
    consulta = select(Categoria.id).where(func.lower(Categoria.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Categoria.id != excluir_id)
    return db.scalar(consulta) is not None


def _escapar_like(texto: str) -> str:
    """Evita que % y _ escritos por el usuario actúen como comodines."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def listar_categorias(
    db: Session,
    *,
    activa: bool | None,
    busqueda: str | None,
    page: int,
    limit: int,
) -> tuple[list[Categoria], int]:
    """Devuelve una página de categorías y el total de resultados del filtro."""
    consulta = select(Categoria)
    if activa is not None:
        consulta = consulta.where(Categoria.activa == activa)
    if busqueda and busqueda.strip():
        patron = f"%{_escapar_like(busqueda.strip())}%"
        consulta = consulta.where(
            or_(
                Categoria.nombre.ilike(patron, escape="\\"),
                Categoria.descripcion.ilike(patron, escape="\\"),
            )
        )

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    categorias = db.scalars(
        consulta.order_by(Categoria.nombre, Categoria.id)
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()
    return list(categorias), total


def obtener_categoria(db: Session, categoria_id: uuid.UUID) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró la categoría.")
    return categoria


def _guardar(db: Session, categoria: Categoria) -> Categoria:
    try:
        db.commit()
    except IntegrityError:
        # Dos peticiones simultáneas con el mismo nombre: gana la primera.
        db.rollback()
        raise _categoria_duplicada()
    db.refresh(categoria)
    return categoria


def crear_categoria(db: Session, datos: CategoriaCrear) -> Categoria:
    if _nombre_en_uso(db, datos.nombre):
        raise _categoria_duplicada()

    categoria = Categoria(
        nombre=datos.nombre,
        descripcion=datos.descripcion or None,
        activa=True,
    )
    db.add(categoria)
    return _guardar(db, categoria)


def actualizar_categoria(
    db: Session, categoria_id: uuid.UUID, datos: CategoriaActualizar
) -> Categoria:
    categoria = obtener_categoria(db, categoria_id)
    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios and _nombre_en_uso(db, cambios["nombre"], excluir_id=categoria.id):
        raise _categoria_duplicada()
    if "descripcion" in cambios:
        # Una descripción vacía se guarda como NULL.
        cambios["descripcion"] = cambios["descripcion"] or None

    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)
    return _guardar(db, categoria)
