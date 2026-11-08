from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base de los modelos SQLAlchemy.

    El esquema real lo gestiona Alembic (alembic/versions/); los modelos solo
    describen las tablas existentes para poder consultarlas desde los servicios.
    """
