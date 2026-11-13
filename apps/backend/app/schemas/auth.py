
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LoginPeticion(BaseModel):
    correo: str = Field(min_length=1, max_length=255)
    contrasena: str = Field(min_length=1, max_length=128)


class CambiarContrasenaPeticion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contrasena_actual: str = Field(min_length=1, max_length=128)
    contrasena_nueva: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validar_contrasena_nueva(self):
        if self.contrasena_actual == self.contrasena_nueva:
            raise ValueError(
                "La nueva contraseña debe ser diferente a la actual."
            )
        return self


class RestablecerContrasenaPeticion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contrasena_temporal: str = Field(min_length=8, max_length=128)


class UsuarioSesion(BaseModel):
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
