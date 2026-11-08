"""Pruebas de RF-13: consulta de solicitudes asignadas al técnico.

Usan SQLite en memoria (no tocan Supabase). El filtrado por asignación activa
<<<<<<< HEAD
se prueba con datos reales; la autenticación se sustituye mientras no exista
el login (RF-01).
=======
se prueba con datos reales. En la mayoría de pruebas la sesión se simula con
`como()`; una prueba usa el login real (RF-01) de punta a punta.
>>>>>>> d99aab98665419ab1253fcc9c486aab8b9f06f35
"""

import itertools
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
<<<<<<< HEAD
=======
from app.core.security import hash_password
>>>>>>> d99aab98665419ab1253fcc9c486aab8b9f06f35
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Categoria, Solicitud, Usuario

URL = "/api/v1/requests"
_contador = itertools.count(1)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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


def como(usuario: Usuario):
    """Simula la sesión del usuario indicado."""
    app.dependency_overrides[get_current_user] = lambda: UsuarioActual(
<<<<<<< HEAD
        id=usuario.id, rol=usuario.rol
    )


def crear_usuario(db, rol, nombre="Ana", apellido="Pérez"):
=======
        id=usuario.id,
        rol=usuario.rol,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        activo=True,
        sesion_id=uuid.uuid4(),
    )


def crear_usuario(db, rol, nombre="Ana", apellido="Pérez", contrasena="x"):
>>>>>>> d99aab98665419ab1253fcc9c486aab8b9f06f35
    usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        correo=f"{uuid.uuid4()}@test.com",
<<<<<<< HEAD
        password_hash="x",
=======
        password_hash=hash_password(contrasena),
>>>>>>> d99aab98665419ab1253fcc9c486aab8b9f06f35
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, tecnico=None, *, activa=True, **campos):
    """Crea una solicitud y, si se indica técnico, su asignación."""
    n = next(_contador)
    datos = {
        "numero": f"ST-{n:06d}",
        "titulo": f"Solicitud {n}",
        "descripcion": "Descripción",
        "tipo": "incidente",
        "solicitante_id": solicitante.id,
        "ubicacion": "Oficina",
        "medio_contacto": "correo",
        "dato_contacto": "a@test.com",
        "estado": "asignado",
        "fecha_creacion": datetime(2026, 11, 1) + timedelta(minutes=n),
    }
    datos.update(campos)
    solicitud = Solicitud(**datos)
    db.add(solicitud)
    db.commit()

    if tecnico is not None:
        db.add(
            Asignacion(
                solicitud_id=solicitud.id,
                tecnico_id=tecnico.id,
                asignado_por=tecnico.id,
                fecha_finalizacion=None if activa else datetime(2026, 11, 2),
            )
        )
        db.commit()
    return solicitud


@pytest.fixture()
def escenario(db):
    return {
        "solicitante": crear_usuario(db, "solicitante", "Juan", "Pérez"),
        "tecnico": crear_usuario(db, "tecnico", "Carlos", "Gómez"),
        "otro_tecnico": crear_usuario(db, "tecnico", "Luis", "Díaz"),
        "coordinador": crear_usuario(db, "coordinador"),
    }


def test_tecnico_ve_solo_sus_solicitudes_asignadas(client, db, escenario):
    solicitante, tecnico, otro = (
        escenario["solicitante"],
        escenario["tecnico"],
        escenario["otro_tecnico"],
    )
    propia = crear_solicitud(db, solicitante, tecnico)
    crear_solicitud(db, solicitante, otro)  # de otro técnico
    crear_solicitud(db, solicitante)  # sin asignar
    como(tecnico)

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert [s["id"] for s in cuerpo["data"]] == [str(propia.id)]
    assert cuerpo["pagination"]["total"] == 1


def test_reasignacion_quita_el_acceso_al_tecnico_anterior(client, db, escenario):
    """RN-14: tras reasignar, la asignación anterior queda finalizada."""
    solicitante, anterior, nuevo = (
        escenario["solicitante"],
        escenario["tecnico"],
        escenario["otro_tecnico"],
    )
    solicitud = crear_solicitud(db, solicitante, anterior, activa=False)
    db.add(
        Asignacion(
            solicitud_id=solicitud.id, tecnico_id=nuevo.id, asignado_por=nuevo.id
        )
    )
    db.commit()

    como(anterior)
    assert client.get(URL).json()["data"] == []

    como(nuevo)
    assert [s["id"] for s in client.get(URL).json()["data"]] == [str(solicitud.id)]


def test_respuesta_sigue_el_contrato(client, db, escenario):
    categoria = Categoria(nombre="Hardware")
    db.add(categoria)
    db.commit()
    crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        categoria_id=categoria.id,
        prioridad="alta",
        estado="en_atencion",
    )
    como(escenario["tecnico"])

    item = client.get(URL).json()["data"][0]

    assert set(item) == {
        "id", "numero", "titulo", "tipo", "prioridad", "estado",
        "categoria", "solicitante", "tecnico_asignado", "fecha_creacion",
    }
    assert item["numero"].startswith("ST-")
    assert item["prioridad"] == "alta"
    assert item["estado"] == "en_atencion"
    assert item["categoria"] == {"id": str(categoria.id), "nombre": "Hardware"}
    assert item["solicitante"]["nombre"] == "Juan Pérez"
    assert item["tecnico_asignado"]["nombre"] == "Carlos Gómez"


def test_solicitud_sin_categoria_ni_prioridad(client, db, escenario):
    crear_solicitud(db, escenario["solicitante"], escenario["tecnico"])
    como(escenario["tecnico"])

    item = client.get(URL).json()["data"][0]

    assert item["categoria"] is None
    assert item["prioridad"] is None


def test_filtros_por_estado_prioridad_y_busqueda(client, db, escenario):
    s, t = escenario["solicitante"], escenario["tecnico"]
    crear_solicitud(db, s, t, estado="asignado", prioridad="baja", titulo="Impresora")
    objetivo = crear_solicitud(
        db, s, t, estado="en_atencion", prioridad="alta", titulo="Monitor roto"
    )
    como(t)

    por_estado = client.get(URL, params={"estado": "en_atencion"}).json()["data"]
    assert [x["id"] for x in por_estado] == [str(objetivo.id)]

    por_prioridad = client.get(URL, params={"prioridad": "alta"}).json()["data"]
    assert [x["id"] for x in por_prioridad] == [str(objetivo.id)]

    por_titulo = client.get(URL, params={"busqueda": "monitor"}).json()["data"]
    assert [x["id"] for x in por_titulo] == [str(objetivo.id)]

    por_numero = client.get(URL, params={"busqueda": objetivo.numero}).json()["data"]
    assert [x["id"] for x in por_numero] == [str(objetivo.id)]


def test_filtro_por_rango_de_fechas(client, db, escenario):
    s, t = escenario["solicitante"], escenario["tecnico"]
    crear_solicitud(db, s, t, fecha_creacion=datetime(2026, 10, 1))
    reciente = crear_solicitud(db, s, t, fecha_creacion=datetime(2026, 11, 5))
    como(t)

    datos = client.get(URL, params={"fecha_desde": "2026-11-01T00:00:00"}).json()["data"]

    assert [x["id"] for x in datos] == [str(reciente.id)]


def test_fecha_desde_posterior_a_fecha_hasta_es_invalido(client, escenario):
    como(escenario["tecnico"])

    respuesta = client.get(
        URL,
        params={"fecha_desde": "2026-11-10T00:00:00", "fecha_hasta": "2026-11-01T00:00:00"},
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "ERROR_VALIDACION"


def test_valores_de_filtro_invalidos_son_rechazados(client, escenario):
    como(escenario["tecnico"])

    assert client.get(URL, params={"estado": "inventado"}).status_code == 422
    assert client.get(URL, params={"prioridad": "urgente"}).status_code == 422


def test_paginacion(client, db, escenario):
    s, t = escenario["solicitante"], escenario["tecnico"]
    for _ in range(25):
        crear_solicitud(db, s, t)
    como(t)

    pagina_3 = client.get(URL, params={"page": 3, "limit": 10}).json()

    assert len(pagina_3["data"]) == 5
    assert pagina_3["pagination"] == {"page": 3, "limit": 10, "total": 25, "total_pages": 3}


def test_paginacion_sin_repetidos_entre_paginas(client, db, escenario):
    s, t = escenario["solicitante"], escenario["tecnico"]
    # Misma fecha de creación: el orden debe seguir siendo estable.
    for _ in range(6):
        crear_solicitud(db, s, t, fecha_creacion=datetime(2026, 11, 1))
    como(t)

    p1 = client.get(URL, params={"page": 1, "limit": 3}).json()["data"]
    p2 = client.get(URL, params={"page": 2, "limit": 3}).json()["data"]

    ids = [x["id"] for x in p1 + p2]
    assert len(set(ids)) == 6


def test_sin_resultados(client, escenario):
    como(escenario["tecnico"])

    cuerpo = client.get(URL).json()

    assert cuerpo["data"] == []
    assert cuerpo["pagination"] == {"page": 1, "limit": 20, "total": 0, "total_pages": 0}


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"limit": 101}])
def test_parametros_de_paginacion_invalidos(client, escenario, params):
    como(escenario["tecnico"])

    assert client.get(URL, params=params).status_code == 422


def test_tecnico_no_puede_ver_solicitudes_de_otro_enviando_su_id(client, db, escenario):
    """Los filtros no amplían permisos (contrato §17)."""
    s, t, otro = escenario["solicitante"], escenario["tecnico"], escenario["otro_tecnico"]
    crear_solicitud(db, s, otro)
    como(t)

    respuesta = client.get(URL, params={"tecnico_id": str(otro.id)})

    assert respuesta.status_code == 200
    assert respuesta.json()["data"] == []


def test_sin_sesion_responde_401_con_formato_de_error(client):
    respuesta = client.get(URL)

    assert respuesta.status_code == 401
    assert respuesta.json() == {
        "error": {
            "codigo": "SESION_NO_VALIDA",
            "mensaje": "Debes iniciar sesión para realizar esta operación.",
            "detalles": None,
        }
    }


<<<<<<< HEAD
def test_encabezado_de_desarrollo_es_ignorado_si_no_esta_activado(client, escenario):
    """Sin DEV_AUTH_ENABLED el encabezado X-Dev-User-Id no autentica a nadie."""
    respuesta = client.get(URL, headers={"X-Dev-User-Id": str(escenario["tecnico"].id)})

    assert respuesta.status_code == 401
=======
def test_con_login_real_de_punta_a_punta(client, db, escenario):
    """Sin simular la sesión: login con cookie y consulta del técnico."""
    tecnico = crear_usuario(db, "tecnico", "Rosa", "Mejía", contrasena="Contrasena123")
    propia = crear_solicitud(db, escenario["solicitante"], tecnico)
    crear_solicitud(db, escenario["solicitante"], escenario["otro_tecnico"])

    login = client.post(
        "/api/v1/auth/login",
        json={"correo": tecnico.correo, "contrasena": "Contrasena123"},
    )
    assert login.status_code == 200

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert [s["id"] for s in respuesta.json()["data"]] == [str(propia.id)]
>>>>>>> d99aab98665419ab1253fcc9c486aab8b9f06f35


def test_roles_sin_implementar_responden_501(client, escenario):
    """Solicitante (RF-07) y coordinador son del integrante 1: ajustar al integrarlos."""
    for rol in ("solicitante", "coordinador"):
        como(escenario[rol])
        respuesta = client.get(URL)
        assert respuesta.status_code == 501
        assert respuesta.json()["error"]["codigo"] == "NO_IMPLEMENTADO"
