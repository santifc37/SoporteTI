
from fastapi import APIRouter, HTTPException

from app.database.session import check_database_connection


router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Comprueba que la API está funcionando."""
    return {
        "status": "ok",
        "service": "soporteti-api"
    }


@router.get("/health/db")
def database_health_check():
    """Comprueba la conexión con la base de datos."""
    try:
        check_database_connection()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No fue posible conectar con la base de datos."
        )

    return {
        "status": "ok",
        "database": "connected"
    }
