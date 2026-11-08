
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_cors_origins
from app.core.errors import register_error_handlers


app = FastAPI(
    title="SoporteTI API",
    description="API del sistema de gestión de solicitudes de soporte TI.",
    version="1.0.0"
)


register_error_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API de SoporteTI funcionando correctamente"
    }


app.include_router(api_router, prefix="/api/v1")
