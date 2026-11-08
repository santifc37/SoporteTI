import uuid

from pydantic import BaseModel, Field


class LoginPeticion(BaseModel):
    correo: str = Field(min_length=1, max_length=255)
    contrasena: str = Field(min_length=1, max_length=128)


class UsuarioSesion(BaseModel):
    """Datos del usuario que se devuelven al iniciar sesión."""

    id: uuid.UUID
    nombre: str
    apellido: str
    correo: str
    rol: str


class LoginRespuesta(BaseModel):
    mensaje: str
    usuario: UsuarioSesion


class UsuarioActualDetalle(UsuarioSesion):
    activo: bool


class MeRespuesta(BaseModel):
    usuario: UsuarioActualDetalle


class MensajeRespuesta(BaseModel):
    mensaje: str
