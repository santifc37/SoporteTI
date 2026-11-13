
import uuid

from pydantic import BaseModel, ConfigDict, Field


class LoginPeticion(BaseModel):
    correo: str = Field(min_length=1, max_length=255)
    contrasena: str = Field(min_length=1, max_length=128)


class CambioContrasenaPeticion(BaseModel):
    """Petición para cambiar la contraseña del usuario autenticado (RF-04)."""

    model_config = ConfigDict(extra="forbid")

    contrasena_actual: str = Field(min_length=1, max_length=128)
    contrasena_nueva: str = Field(min_length=8, max_length=128)


class RestablecerContrasenaPeticion(BaseModel):
    """Petición para que un coordinador restablezca la contraseña (RF-04)."""

    model_config = ConfigDict(extra="forbid")

    contrasena_temporal: str = Field(min_length=8, max_length=128)


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
