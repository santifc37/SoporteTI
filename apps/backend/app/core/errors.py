from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Error de negocio con el formato de docs/contrato-api.md §18.

    Ejemplo de respuesta:
        {"error": {"codigo": "...", "mensaje": "...", "detalles": null}}
    """

    def __init__(
        self,
        status_code: int,
        codigo: str,
        mensaje: str,
        detalles: Any = None,
    ) -> None:
        super().__init__(mensaje)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "codigo": exc.codigo,
                    "mensaje": exc.mensaje,
                    "detalles": exc.detalles,
                }
            },
        )
