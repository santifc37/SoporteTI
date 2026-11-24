"""RF-03 (gestión de usuarios) y RF-05 (datos de contacto).

Reglas (docs/contrato-api.md §5, docs/MER.md §3.2):
- Solo el coordinador consulta, crea y administra cuentas. No hay registro público.
- El correo es único sin distinguir mayúsculas.
- Cada usuario puede modificar sus propios datos de contacto, pero nadie
  puede cambiar su propio rol ni el estado de su propia cuenta.
- Si el medio de contacto preferido es teléfono, el teléfono es obligatorio.
- Al desactivar una cuenta se revocan sus sesiones abiertas.
- Un técnico con solicitudes asignadas no puede desactivarse ni cambiar de
  rol: primero hay que reasignarlas (RN-12).
- Las cuentas no se eliminan: se desactivan.
"""

import uuid

from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual
from app.core.errors import ApiError
from app.core.security import hash_password
from app.models import Asignacion, Sesion, Usuario
from app.schemas.usuarios import MENSAJE_TELEFONO, UsuarioActualizar, UsuarioCrear

ROL_COORDINADOR = "coordinador"
ROL_TECNICO = "tecnico"

# Campos que un usuario puede cambiar en su propia cuenta.
CAMPOS_PROPIOS = {"nombre", "apellido", "telefono", "medio_contacto_preferido"}


def _correo_duplicado() -> ApiError:
    return ApiError(409, "CORREO_DUPLICADO", "Ya existe una cuenta con ese correo.")


def _correo_en_uso(db: Session, correo: str, excluir_id: uuid.UUID | None = None) -> bool:
    consulta = select(Usuario.id).where(func.lower(Usuario.correo) == correo.lower())
    if excluir_id is not None:
        consulta = consulta.where(Usuario.id != excluir_id)
    return db.scalar(consulta) is not None


def _escapar_like(texto: str) -> str:
    """Evita que % y _ escritos por el usuario actúen como comodines."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# --------------------------------- consultas ---------------------------------


def listar_usuarios(
    db: Session,
    *,
    rol: str | None,
    activo: bool | None,
    busqueda: str | None,
    page: int,
    limit: int,
) -> tuple[list[Usuario], int]:
    """Devuelve una página de usuarios y el total de resultados del filtro."""
    consulta = select(Usuario)
    if rol is not None:
        consulta = consulta.where(Usuario.rol == rol)
    if activo is not None:
        consulta = consulta.where(Usuario.activo == activo)
    if busqueda and busqueda.strip():
        patron = f"%{_escapar_like(busqueda.strip())}%"
        consulta = consulta.where(
            or_(
                Usuario.nombre.ilike(patron, escape="\\"),
                Usuario.apellido.ilike(patron, escape="\\"),
                Usuario.correo.ilike(patron, escape="\\"),
            )
        )

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    usuarios = db.scalars(
        consulta.order_by(Usuario.apellido, Usuario.nombre, Usuario.id)
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()
    return list(usuarios), total


def obtener_usuario(db: Session, usuario_id: uuid.UUID) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise ApiError(404, "RECURSO_NO_ENCONTRADO", "No se encontró el usuario.")
    return usuario


# ---------------------------------- creación ---------------------------------


def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    """RF-03: el coordinador crea una cuenta, activa por defecto."""
    if _correo_en_uso(db, datos.correo):
        raise _correo_duplicado()

    usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        correo=datos.correo,
        password_hash=hash_password(datos.contrasena),
        rol=datos.rol,
        activo=True,
        medio_contacto_preferido=datos.medio_contacto_preferido,
        telefono=datos.telefono,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        # Dos peticiones simultáneas con el mismo correo: gana la primera.
        db.rollback()
        raise _correo_duplicado()
    db.refresh(usuario)
    return usuario


# -------------------------------- modificación -------------------------------


def actualizar_usuario(
    db: Session, actor: UsuarioActual, usuario_id: uuid.UUID, datos: UsuarioActualizar
) -> Usuario:
    """RF-03 / RF-05: modifica una cuenta según quién hace la petición."""
    es_coordinador = actor.rol == ROL_COORDINADOR
    es_propia = actor.id == usuario_id

    if not es_coordinador and not es_propia:
        raise ApiError(403, "PERMISO_DENEGADO", "No puedes modificar otras cuentas.")

    usuario = obtener_usuario(db, usuario_id)
    cambios = datos.model_dump(exclude_unset=True)

    if not es_coordinador and set(cambios) - CAMPOS_PROPIOS:
        raise ApiError(
            403, "PERMISO_DENEGADO", "Solo puedes modificar tu nombre y tus datos de contacto."
        )

    if es_propia and (
        cambios.get("rol", usuario.rol) != usuario.rol
        or cambios.get("activo", usuario.activo) != usuario.activo
    ):
        raise ApiError(
            403, "PERMISO_DENEGADO", "No puedes cambiar tu propio rol ni el estado de tu cuenta."
        )

    if "correo" in cambios and _correo_en_uso(db, cambios["correo"], excluir_id=usuario.id):
        raise _correo_duplicado()

    # Regla del teléfono sobre el resultado final, no solo sobre lo enviado.
    medio = cambios.get("medio_contacto_preferido", usuario.medio_contacto_preferido)
    telefono = cambios["telefono"] if "telefono" in cambios else usuario.telefono
    if medio == "telefono" and not telefono:
        raise ApiError(
            422,
            "ERROR_VALIDACION",
            "Los datos enviados no son válidos.",
            [{"campo": "telefono", "mensaje": MENSAJE_TELEFONO}],
        )

    se_desactiva = usuario.activo and cambios.get("activo") is False
    deja_de_ser_tecnico = usuario.rol == ROL_TECNICO and cambios.get("rol", ROL_TECNICO) != ROL_TECNICO
    if (se_desactiva or deja_de_ser_tecnico) and usuario.rol == ROL_TECNICO:
        tiene_asignaciones = db.scalar(
            select(Asignacion.id).where(
                Asignacion.tecnico_id == usuario.id,
                Asignacion.fecha_finalizacion.is_(None),
            )
        )
        if tiene_asignaciones is not None:
            raise ApiError(
                409,
                "TECNICO_CON_ASIGNACIONES",
                "El técnico tiene solicitudes asignadas. Reasígnalas antes de "
                "desactivarlo o cambiar su rol.",
            )

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    if se_desactiva:
        db.execute(
            update(Sesion)
            .where(Sesion.usuario_id == usuario.id, Sesion.revocada.is_(False))
            .values(revocada=True)
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _correo_duplicado()
    db.refresh(usuario)
    return usuario
