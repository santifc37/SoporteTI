from pydantic import BaseModel


class Pagination(BaseModel):
    """Objeto `pagination` de docs/contrato-api.md §17."""

    page: int
    limit: int
    total: int
    total_pages: int


def calcular_total_paginas(total: int, limit: int) -> int:
    """Páginas necesarias para `total` registros (0 si no hay resultados)."""
    return (total + limit - 1) // limit
