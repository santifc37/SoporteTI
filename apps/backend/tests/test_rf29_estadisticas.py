"""Pruebas de RF-29: estadísticas del coordinador (CA-06).

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
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
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Categoria, Solicitud, Usuario

URL = "/api/v1/statistics"
_contador = itertools.count(1)
INICIO = datetime(2026, 11, 1, 8, 0)


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


def como(usuario: Usuario):
    """Simula la sesión del usuario indicado."""
    app.dependency_overrides[get_current_user] = lambda: UsuarioActual(
        id=usuario.id,
        rol=usuario.rol,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        activo=True,
        sesion_id=uuid.uuid4(),
    )


def crear_usuario(db, rol, nombre):
    usuario = Usuario(
        nombre=nombre,
        apellido="Prueba",
        correo=f"{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, tecnico=None, *, activa=True, **campos):
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
        "estado": "registrado",
        "fecha_creacion": INICIO,
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
                fecha_finalizacion=None if activa else INICIO + timedelta(hours=1),
            )
        )
        db.commit()
    return solicitud


@pytest.fixture()
def e(db):
    return {
        "laura": crear_usuario(db, "solicitante", "Laura"),
        "carlos": crear_usuario(db, "tecnico", "Carlos"),
        "luis": crear_usuario(db, "tecnico", "Luis"),
        "coordinador": crear_usuario(db, "coordinador", "Marta"),
    }


def consultar(client, **params):
    respuesta = client.get(URL, params=params)
    assert respuesta.status_code == 200
    return respuesta.json()


# ------------------------------- sin datos -------------------------------


def test_sin_solicitudes_todo_en_cero(client, e):
    como(e["coordinador"])

    datos = consultar(client)

    assert datos["total_solicitudes"] == 0
    assert set(datos["por_estado"]) == {
        "registrado", "en_evaluacion", "asignado", "en_atencion",
        "en_espera", "resuelto", "cerrado",
    }
    assert all(v == 0 for v in datos["por_estado"].values())
    assert datos["por_prioridad"] == {"baja": 0, "media": 0, "alta": 0}
    assert datos["por_categoria"] == []
    assert datos["por_tecnico"] == []
    assert datos["tiempo_promedio_atencion"] is None


# ------------------------------- conteos -------------------------------


def test_cantidades_por_estado_y_prioridad(client, db, e):
    crear_solicitud(db, e["laura"], estado="registrado")
    crear_solicitud(db, e["laura"], estado="en_evaluacion", prioridad="alta")
    crear_solicitud(db, e["laura"], estado="en_atencion", prioridad="alta")
    crear_solicitud(db, e["laura"], estado="cerrado", prioridad="baja")
    como(e["coordinador"])

    datos = consultar(client)

    assert datos["total_solicitudes"] == 4
    assert datos["por_estado"]["registrado"] == 1
    assert datos["por_estado"]["en_evaluacion"] == 1
    assert datos["por_estado"]["en_atencion"] == 1
    assert datos["por_estado"]["cerrado"] == 1
    assert datos["por_estado"]["asignado"] == 0
    assert datos["por_prioridad"] == {"baja": 1, "media": 0, "alta": 2}
    assert datos["sin_prioridad"] == 1


def test_cantidades_por_categoria(client, db, e):
    hardware = Categoria(nombre="Hardware")
    redes = Categoria(nombre="Redes")
    db.add_all([hardware, redes])
    db.commit()
    crear_solicitud(db, e["laura"], categoria_id=redes.id)
    crear_solicitud(db, e["laura"], categoria_id=redes.id)
    crear_solicitud(db, e["laura"], categoria_id=hardware.id)
    crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    datos = consultar(client)

    assert datos["por_categoria"] == [
        {"categoria_id": str(redes.id), "nombre": "Redes", "cantidad": 2},
        {"categoria_id": str(hardware.id), "nombre": "Hardware", "cantidad": 1},
    ]
    assert datos["sin_categoria"] == 1


def test_cantidades_por_tecnico_responsable(client, db, e):
    """CA-06: varios casos con sus responsables (según la asignación activa)."""
    crear_solicitud(db, e["laura"], e["carlos"])
    crear_solicitud(db, e["laura"], e["carlos"])
    crear_solicitud(db, e["laura"], e["luis"])
    crear_solicitud(db, e["laura"], e["luis"], activa=False)  # ya no es responsable
    crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    datos = consultar(client)

    assert datos["por_tecnico"] == [
        {"tecnico_id": str(e["carlos"].id), "nombre": "Carlos Prueba", "cantidad": 2},
        {"tecnico_id": str(e["luis"].id), "nombre": "Luis Prueba", "cantidad": 1},
    ]
    assert datos["sin_asignar"] == 2


# --------------------------- tiempo de atención ---------------------------


def test_tiempo_promedio_de_atencion_en_horas(client, db, e):
    crear_solicitud(db, e["laura"], estado="resuelto", fecha_resolucion=INICIO + timedelta(hours=2))
    crear_solicitud(db, e["laura"], estado="cerrado", fecha_resolucion=INICIO + timedelta(hours=4))
    crear_solicitud(db, e["laura"], estado="en_atencion")  # sin resolver: no cuenta
    como(e["coordinador"])

    datos = consultar(client)

    assert datos["tiempo_promedio_atencion"] == 3.0
    assert datos["solicitudes_con_tiempo"] == 2


def test_sin_solicitudes_resueltas_el_tiempo_es_nulo(client, db, e):
    crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    datos = consultar(client)

    assert datos["tiempo_promedio_atencion"] is None
    assert datos["solicitudes_con_tiempo"] == 0


# ------------------------------- fechas -------------------------------


def test_el_rango_de_fechas_aplica_a_todos_los_indicadores(client, db, e):
    crear_solicitud(db, e["laura"], e["carlos"], estado="en_atencion",
                    fecha_creacion=datetime(2026, 10, 1))
    crear_solicitud(db, e["laura"], estado="resuelto", prioridad="alta",
                    fecha_creacion=datetime(2026, 11, 5, 8), fecha_resolucion=datetime(2026, 11, 5, 10))
    como(e["coordinador"])

    datos = consultar(client, fecha_desde="2026-11-01T00:00:00", fecha_hasta="2026-11-30T23:59:59")

    assert datos["total_solicitudes"] == 1
    assert datos["por_estado"]["resuelto"] == 1
    assert datos["por_estado"]["en_atencion"] == 0
    assert datos["por_prioridad"]["alta"] == 1
    assert datos["por_tecnico"] == []
    assert datos["tiempo_promedio_atencion"] == 2.0


def test_fecha_desde_posterior_a_fecha_hasta_es_invalido(client, e):
    como(e["coordinador"])

    respuesta = client.get(
        URL, params={"fecha_desde": "2026-12-01T00:00:00", "fecha_hasta": "2026-11-01T00:00:00"}
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "ERROR_VALIDACION"


def test_fecha_con_formato_invalido_devuelve_422(client, e):
    como(e["coordinador"])

    assert client.get(URL, params={"fecha_desde": "ayer"}).status_code == 422


# ------------------------------- permisos -------------------------------


@pytest.mark.parametrize("rol", ["laura", "carlos"])
def test_solo_el_coordinador_consulta_estadisticas(client, e, rol):
    como(e[rol])

    respuesta = client.get(URL)

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_sin_sesion_devuelve_401(client):
    assert client.get(URL).status_code == 401
