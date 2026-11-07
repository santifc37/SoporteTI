"""Configuracion de Alembic para SoporteTI.

Lee la cadena de conexion de la variable DATABASE_URL del archivo .env,
para no guardar credenciales de Supabase en el repositorio.
"""

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

# Carga apps/backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Cuando existan los modelos de SQLAlchemy, cambiar por:
#   from app.models import Base
#   target_metadata = Base.metadata
target_metadata = None


def obtener_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta la variable DATABASE_URL en apps/backend/.env")
    # Supabase entrega la URL como postgresql://; se indica el driver psycopg 3.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse (alembic upgrade head --sql)."""
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
    engine = create_engine(obtener_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
