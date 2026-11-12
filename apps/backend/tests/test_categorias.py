"""Pruebas de la gestión de categorías (docs/contrato-api.md §6).

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Table, Uuid, create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.database.session import get_db
from app.main import app
from app.models import Base, Categoria

URL = "/api/v1/categories"

# `asignaciones` tiene una clave foránea a `solicitudes`. Si el modelo Solicitud
# todavía no existe en esta rama, se registra una tabla mínima solo para que
# SQLite pueda crear el esquema de prueba.
if "solicitudes" not in Base.metadata.tables:
    Table("solicitudes", Base.metadata, Column("id", Uuid, primary_key=True))


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


def como(rol: str):
    """Simula la sesión de un usuario con el rol indicado."""
    app.dependency_overrides[get_current_user] = lambda: UsuarioActual(
        id=uuid.uuid4(),
        rol=rol,
        nombre="Prueba",
        apellido="Usuario",
        correo=f"{rol}@organizacion.com",
        activo=True,
        sesion_id=uuid.uuid4(),
    )


def nueva_categoria(db, nombre="Hardware", activa=True, descripcion=None) -> Categoria:
    c = Categoria(nombre=nombre, activa=activa, descripcion=descripcion)
    db.add(c)
    db.commit()
    return c


# --------------------------------- permisos ----------------------------------


def test_sin_sesion_devuelve_401(client):
    assert client.get(URL).status_code == 401
    assert client.post(URL, json={"nombre": "Redes"}).status_code == 401


@pytest.mark.parametrize("rol", ["solicitante", "tecnico"])
def test_solo_el_coordinador_crea_y_modifica(client, db, rol):
    categoria = nueva_categoria(db)
    como(rol)

    crear = client.post(URL, json={"nombre": "Redes"})
    modificar = client.patch(f"{URL}/{categoria.id}", json={"activa": False})

    for respuesta in (crear, modificar):
        assert respuesta.status_code == 403
        assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    db.refresh(categoria)
    assert categoria.activa is True
    assert db.scalar(select(func.count()).select_from(Categoria)) == 1


# ----------------------------------- crear -----------------------------------


def test_coordinador_crea_categoria_activa(client, db):
    como("coordinador")

    respuesta = client.post(
        URL, json={"nombre": " Hardware ", "descripcion": "Componentes físicos"}
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Categoría creada correctamente"
    assert cuerpo["categoria"]["nombre"] == "Hardware"
    assert cuerpo["categoria"]["activa"] is True
    assert db.get(Categoria, uuid.UUID(cuerpo["categoria"]["id"])) is not None


def test_nombre_duplicado_sin_importar_mayusculas(client, db):
    nueva_categoria(db, "Hardware")
    como("coordinador")

    respuesta = client.post(URL, json={"nombre": "HARDWARE"})

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CATEGORIA_DUPLICADA"


@pytest.mark.parametrize(
    "cuerpo",
    [{}, {"nombre": "   "}, {"nombre": "x" * 101}, {"nombre": "Redes", "activa": False}],
)
def test_crear_con_datos_invalidos_devuelve_422_y_no_guarda(client, db, cuerpo):
    como("coordinador")

    assert client.post(URL, json=cuerpo).status_code == 422
    assert db.scalar(select(Categoria)) is None


# ---------------------------------- listar -----------------------------------


def test_coordinador_ve_todas_y_puede_filtrar(client, db):
    nueva_categoria(db, "Hardware")
    nueva_categoria(db, "Software")
    nueva_categoria(db, "Impresoras", activa=False)
    como("coordinador")

    todas = client.get(URL).json()
    inactivas = client.get(URL, params={"activa": False}).json()

    assert [c["nombre"] for c in todas["data"]] == ["Hardware", "Impresoras", "Software"]
    assert todas["pagination"] == {"page": 1, "limit": 20, "total": 3, "total_pages": 1}
    assert [c["nombre"] for c in inactivas["data"]] == ["Impresoras"]
    assert set(todas["data"][0]) == {"id", "nombre", "descripcion", "activa"}


@pytest.mark.parametrize("rol", ["solicitante", "tecnico"])
def test_otros_roles_solo_ven_las_activas(client, db, rol):
    nueva_categoria(db, "Hardware")
    nueva_categoria(db, "Impresoras", activa=False)
    como(rol)

    # Aunque pidan las inactivas, solo reciben las activas.
    for params in ({}, {"activa": False}):
        cuerpo = client.get(URL, params=params).json()
        assert [c["nombre"] for c in cuerpo["data"]] == ["Hardware"]


def test_busqueda_por_nombre_o_descripcion(client, db):
    nueva_categoria(db, "Hardware", descripcion="Equipos y periféricos")
    nueva_categoria(db, "Redes", descripcion="Internet y wifi")
    como("coordinador")

    assert [c["nombre"] for c in client.get(URL, params={"busqueda": "red"}).json()["data"]] == ["Redes"]
    assert [c["nombre"] for c in client.get(URL, params={"busqueda": "WIFI"}).json()["data"]] == ["Redes"]
    assert client.get(URL, params={"busqueda": "%"}).json()["pagination"]["total"] == 0


def test_paginacion(client, db):
    for nombre in ("A", "B", "C"):
        nueva_categoria(db, nombre)
    como("coordinador")

    cuerpo = client.get(URL, params={"page": 2, "limit": 2}).json()

    assert [c["nombre"] for c in cuerpo["data"]] == ["C"]
    assert cuerpo["pagination"]["total_pages"] == 2


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"limit": 101}])
def test_parametros_invalidos_devuelven_422(client, params):
    como("coordinador")

    assert client.get(URL, params=params).status_code == 422


# --------------------------------- modificar ---------------------------------


def test_coordinador_modifica_categoria(client, db):
    categoria = nueva_categoria(db, "Hardware")
    como("coordinador")

    respuesta = client.patch(
        f"{URL}/{categoria.id}",
        json={"nombre": "Hardware y periféricos", "descripcion": "Equipos y dispositivos"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "Categoría actualizada correctamente"
    db.refresh(categoria)
    assert categoria.nombre == "Hardware y periféricos"


def test_desactivar_y_reactivar(client, db):
    categoria = nueva_categoria(db)
    como("coordinador")

    assert client.patch(f"{URL}/{categoria.id}", json={"activa": False}).json()["categoria"]["activa"] is False
    assert client.patch(f"{URL}/{categoria.id}", json={"activa": True}).json()["categoria"]["activa"] is True


def test_renombrar_a_un_nombre_existente_devuelve_409(client, db):
    nueva_categoria(db, "Hardware")
    software = nueva_categoria(db, "Software")
    como("coordinador")

    respuesta = client.patch(f"{URL}/{software.id}", json={"nombre": "hardware"})

    assert respuesta.status_code == 409
    db.refresh(software)
    assert software.nombre == "Software"


def test_cambiar_mayusculas_del_mismo_nombre_si_se_permite(client, db):
    categoria = nueva_categoria(db, "hardware")
    como("coordinador")

    assert client.patch(f"{URL}/{categoria.id}", json={"nombre": "Hardware"}).status_code == 200


def test_borrar_la_descripcion(client, db):
    categoria = nueva_categoria(db, descripcion="Algo")
    como("coordinador")

    respuesta = client.patch(f"{URL}/{categoria.id}", json={"descripcion": None})

    assert respuesta.status_code == 200
    assert respuesta.json()["categoria"]["descripcion"] is None


@pytest.mark.parametrize("cuerpo", [{"nombre": None}, {"activa": None}, {"id": str(uuid.uuid4())}])
def test_patch_rechaza_nulos_y_campos_no_permitidos(client, db, cuerpo):
    categoria = nueva_categoria(db)
    como("coordinador")

    assert client.patch(f"{URL}/{categoria.id}", json=cuerpo).status_code == 422


def test_patch_categoria_inexistente_devuelve_404(client):
    como("coordinador")

    respuesta = client.patch(f"{URL}/{uuid.uuid4()}", json={"nombre": "X"})

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"
