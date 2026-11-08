
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_database_url


@lru_cache
def get_engine():
    """Crea el motor de conexión a la base de datos."""
    return create_engine(
        get_database_url(),
        pool_pre_ping=True
    )


def get_db():
    """Proporciona una sesión de base de datos a los endpoints."""
    db = Session(get_engine())

    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> None:
    """Comprueba la conexión ejecutando una consulta de lectura."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
