
from fastapi import APIRouter

from app.api.asignaciones import router as asignaciones_router
from app.api.auth import router as auth_router
from app.api.categorias import router as categorias_router
from app.api.health import router as health_router
from app.api.solicitudes import router as solicitudes_router
from app.api.usuarios import router as usuarios_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(usuarios_router)
api_router.include_router(categorias_router)
api_router.include_router(solicitudes_router)
api_router.include_router(asignaciones_router)
