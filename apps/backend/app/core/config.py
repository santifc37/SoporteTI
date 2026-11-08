
import os
from pathlib import Path

from dotenv import load_dotenv


# Ruta de la carpeta apps/backend
BACKEND_DIR = Path(__file__).resolve().parents[2]

# Cargar las variables del archivo .env
load_dotenv(BACKEND_DIR / ".env")


def get_database_url() -> str:
    """Obtiene y adapta la URL de conexión a PostgreSQL."""
    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise RuntimeError(
            "No se encontró DATABASE_URL. Configura la conexión en apps/backend/.env"
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    return database_url


def get_cors_origins() -> list[str]:
    """Obtiene los orígenes permitidos para el frontend."""
    origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    return [
        origin.strip()
        for origin in origins.split(",")
        if origin.strip()
    ]
