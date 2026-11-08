
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


SESSION_COOKIE_NAME = "soporteti_session"


def get_session_duration_hours() -> int:
    """Duración de una sesión en horas (SESSION_DURATION_HOURS, 8 por defecto)."""
    try:
        horas = int(os.getenv("SESSION_DURATION_HOURS", "8"))
    except ValueError:
        return 8
    return horas if horas > 0 else 8


def get_session_cookie_secure() -> bool:
    """La cookie solo viaja por HTTPS cuando es true. Activar en producción."""
    return os.getenv("SESSION_COOKIE_SECURE", "false").strip().lower() == "true"


def get_session_cookie_samesite() -> str:
    """Atributo SameSite de la cookie: lax (por defecto), strict o none.

    `none` exige SESSION_COOKIE_SECURE=true y solo se necesita si frontend y
    backend están en sitios distintos.
    """
    valor = os.getenv("SESSION_COOKIE_SAMESITE", "lax").strip().lower()
    return valor if valor in {"lax", "strict", "none"} else "lax"


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
