
from pydantic import BaseModel, Field, field_validator


class RegistrarSolucion(BaseModel):
    solucion: str = Field(min_length=1)

    @field_validator("solucion")
    @classmethod
    def validar_solucion(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "La descripción de la solución no puede estar vacía."
            )

        return valor
