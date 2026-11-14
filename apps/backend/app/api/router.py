
from fastapi import APIRouter

from app.api.asignaciones import router as asignaciones_router
from app.api.auth import router as auth_router
from app.api.categorias import router as categorias_router
from app.api.cierres import router as cierres_router
from app.api.estadisticas import router as estadisticas_router
from app.api.health import router as health_router
from app.api.historial import router as historial_router
from app.api.mensajes import router as mensajes_router
from app.api.notificaciones import router as notificaciones_router
from app.api.peticiones_informacion import router as peticiones_informacion_router
from app.api.solicitudes import router as solicitudes_router
from app.api.usuarios import router as usuarios_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(usuarios_router)
api_router.include_router(categorias_router)
api_router.include_router(solicitudes_router)
api_router.include_router(asignaciones_router)
api_router.include_router(cierres_router)
api_router.include_router(estadisticas_router)
api_router.include_router(historial_router)
api_router.include_router(peticiones_informacion_router)
api_router.include_router(mensajes_router)
api_router.include_router(notificaciones_router)
