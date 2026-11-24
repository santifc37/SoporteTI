
"""Configuración de Alembic para SoporteTI.

Selecciona la conexión según APP_ENV:
- local: apps/backend/.env.local
- producción: apps/backend/.env
"""

import os
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool


# Ruta de la carpeta apps/backend
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Seleccionar el archivo de variables del entorno
APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
ENV_FILE = BACKEND_DIR / (".env.local" if APP_ENV == "local" else ".env")

load_dotenv(ENV_FILE)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Cuando existan los modelos de SQLAlchemy, cambiar por:
# from app.models import Base
# target_metadata = Base.metadata
target_metadata = None


def obtener_url() -> str:
    """Obtiene y adapta la URL de conexión a PostgreSQL."""
    url = os.getenv("DATABASE_URL", "").strip()

    if not url:
        raise RuntimeError(
            f"No se encontró DATABASE_URL. Revisa el archivo {ENV_FILE.name}"
        )

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse."""
    context.configure(
        url=obtener_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones directamente en la base de datos."""
    engine = create_engine(
        obtener_url(),
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
