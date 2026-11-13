
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.config import (
    SESSION_COOKIE_NAME,
    get_session_cookie_samesite,
    get_session_cookie_secure,
    get_session_duration_hours,
)
from app.database.session import get_db
from app.schemas.auth import (
    CambiarContrasenaPeticion,
    LoginPeticion,
    LoginRespuesta,
    MensajeRespuesta,
    MeRespuesta,
    UsuarioActualDetalle,
    UsuarioSesion,
)
from app.services.autenticacion import (
    cambiar_contrasena,
    cerrar_sesion,
    iniciar_sesion,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginRespuesta)
def login(datos: LoginPeticion, response: Response, db: Session = Depends(get_db)):
    """Inicia sesión con correo y contraseña (RF-01) y establece la cookie."""
    usuario, token = iniciar_sesion(db, datos.correo, datos.contrasena)

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=get_session_duration_hours() * 3600,
        httponly=True,
        secure=get_session_cookie_secure(),
        samesite=get_session_cookie_samesite(),
        path="/",
    )
    return LoginRespuesta(
        mensaje="Inicio de sesión exitoso",
        usuario=UsuarioSesion(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            correo=usuario.correo,
            rol=usuario.rol,
        ),
    )


@router.post("/logout", response_model=MensajeRespuesta)
def logout(
    response: Response,
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoca la sesión actual y elimina la cookie."""
    cerrar_sesion(db, usuario.sesion_id)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=get_session_cookie_secure(),
        samesite=get_session_cookie_samesite(),
    )
    return MensajeRespuesta(mensaje="Sesión cerrada correctamente")


@router.post("/change-password", response_model=MensajeRespuesta)
def cambiar_clave(
    datos: CambiarContrasenaPeticion,
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permite al usuario autenticado cambiar su contraseña (RF-04)."""
    cambiar_contrasena(
        db,
        usuario.id,
        usuario.sesion_id,
        datos.contrasena_actual,
        datos.contrasena_nueva,
    )
    return MensajeRespuesta(mensaje="Contraseña actualizada correctamente")


@router.get("/me", response_model=MeRespuesta)
def me(usuario: UsuarioActual = Depends(get_current_user)):
    """Devuelve el usuario autenticado. Responde 401 si no hay sesión válida."""
    return MeRespuesta(
        usuario=UsuarioActualDetalle(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            correo=usuario.correo,
            rol=usuario.rol,
            activo=usuario.activo,
        )
    )
