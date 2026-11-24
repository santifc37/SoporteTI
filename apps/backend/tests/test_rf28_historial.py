"""Pruebas de RF-28: consulta del historial de cambios (docs/contrato-api.md §14).

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
"""

import itertools
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio

URL = "/api/v1/requests"
_contador = itertools.count(1)
INICIO = datetime(2026, 11, 6, 10, 0, tzinfo=timezone.utc)


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


def crear_solicitud(db, solicitante, estado="registrado"):
    n = next(_contador)
    solicitud = Solicitud(
        numero=f"ST-{n:06d}",
        titulo=f"Solicitud {n}",
        descripcion="Descripción",
        tipo="incidente",
        solicitante_id=solicitante.id,
        ubicacion="Oficina",
        medio_contacto="correo",
        dato_contacto="a@test.com",
        estado=estado,
        version=1,
    )
    db.add(solicitud)
    db.commit()
    return solicitud


def registrar(db, solicitud, usuario, tipo, anterior=None, nuevo=None, minutos=0, observacion=None):
    cambio = HistorialCambio(
        solicitud_id=solicitud.id,
        usuario_id=usuario.id,
        tipo_cambio=tipo,
        valor_anterior=anterior,
        valor_nuevo=nuevo,
        observacion=observacion,
        fecha_cambio=INICIO + timedelta(minutes=minutos),
    )
    db.add(cambio)
    db.commit()
    return cambio


def asignar(db, solicitud, tecnico, coordinador, finalizada=False):
    asignacion = Asignacion(
        solicitud_id=solicitud.id,
        tecnico_id=tecnico.id,
        asignado_por=coordinador.id,
        fecha_finalizacion=INICIO if finalizada else None,
    )
    db.add(asignacion)
    db.commit()
    return asignacion


@pytest.fixture()
def e(db):
    return {
        "laura": crear_usuario(db, "solicitante", "Laura"),
        "pedro": crear_usuario(db, "solicitante", "Pedro"),
        "carlos": crear_usuario(db, "tecnico", "Carlos"),
        "ana": crear_usuario(db, "tecnico", "Ana"),
        "coordinador": crear_usuario(db, "coordinador", "Marta"),
    }


@pytest.fixture()
def con_historial(db, e):
    """Solicitud de Laura con tres cambios, asignada actualmente a Carlos."""
    solicitud = crear_solicitud(db, e["laura"], "asignado")
    registrar(db, solicitud, e["laura"], "creacion", nuevo="registrado", minutos=0)
    registrar(
        db, solicitud, e["coordinador"], "cambio_estado", "registrado", "en_evaluacion",
        minutos=10, observacion="Inicio de evaluación",
    )
    registrar(db, solicitud, e["coordinador"], "asignacion", None, "Carlos Prueba", minutos=20)
    asignar(db, solicitud, e["carlos"], e["coordinador"])
    return solicitud


def historial(client, solicitud, **params):
    return client.get(f"{URL}/{solicitud.id}/history", params=params)


# ============================ Permisos ============================


def test_coordinador_consulta_cualquier_historial(client, e, con_historial):
    como(e["coordinador"])
    respuesta = historial(client, con_historial)
    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 3


def test_solicitante_propietario_consulta_su_historial(client, e, con_historial):
    como(e["laura"])
    assert historial(client, con_historial).status_code == 200


def test_solicitante_ajeno_recibe_403(client, e, con_historial):
    como(e["pedro"])
    respuesta = historial(client, con_historial)
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_tecnico_asignado_actualmente_consulta(client, e, con_historial):
    como(e["carlos"])
    assert historial(client, con_historial).status_code == 200


def test_tecnico_no_asignado_recibe_403(client, e, con_historial):
    como(e["ana"])
    assert historial(client, con_historial).status_code == 403


def test_tecnico_reasignado_pierde_acceso(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "asignado")
    asignar(db, solicitud, e["carlos"], e["coordinador"], finalizada=True)
    asignar(db, solicitud, e["ana"], e["coordinador"])

    como(e["carlos"])
    assert historial(client, solicitud).status_code == 403
    como(e["ana"])
    assert historial(client, solicitud).status_code == 200


def test_tecnico_sin_asignacion_recibe_403(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["carlos"])
    assert historial(client, solicitud).status_code == 403


def test_solicitud_inexistente_responde_404(client, e):
    como(e["coordinador"])
    respuesta = client.get(f"{URL}/{uuid.uuid4()}/history")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_sin_sesion_responde_401(client, con_historial):
    app.dependency_overrides.pop(get_current_user, None)
    assert historial(client, con_historial).status_code == 401


def test_id_invalido_responde_422(client, e):
    como(e["coordinador"])
    assert client.get(f"{URL}/no-es-uuid/history").status_code == 422


# ============================ Contenido ============================


def test_formato_de_cada_registro(client, e, con_historial):
    como(e["coordinador"])
    cambio = historial(client, con_historial).json()["data"][1]

    assert cambio["solicitud_id"] == str(con_historial.id)
    assert cambio["tipo_cambio"] == "cambio_estado"
    assert cambio["valor_anterior"] == "registrado"
    assert cambio["valor_nuevo"] == "en_evaluacion"
    assert cambio["observacion"] == "Inicio de evaluación"
    assert cambio["usuario"] == {
        "id": str(e["coordinador"].id),
        "nombre": "Marta Prueba",
        "rol": "coordinador",
    }
    assert cambio["fecha_cambio"].startswith("2026-11-06T10:10")


def test_orden_cronologico(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    # Se insertan desordenados a propósito.
    registrar(db, solicitud, e["coordinador"], "cambio_prioridad", None, "alta", minutos=30)
    registrar(db, solicitud, e["laura"], "creacion", None, "registrado", minutos=0)
    registrar(db, solicitud, e["coordinador"], "cambio_estado", "registrado", "en_evaluacion", minutos=15)

    como(e["coordinador"])
    tipos = [c["tipo_cambio"] for c in historial(client, solicitud).json()["data"]]
    assert tipos == ["creacion", "cambio_estado", "cambio_prioridad"]


def test_solo_incluye_cambios_de_esa_solicitud(client, db, e, con_historial):
    otra = crear_solicitud(db, e["laura"])
    registrar(db, otra, e["laura"], "creacion", None, "registrado")

    como(e["coordinador"])
    datos = historial(client, con_historial).json()["data"]
    assert len(datos) == 3
    assert all(c["solicitud_id"] == str(con_historial.id) for c in datos)


def test_solicitud_sin_cambios_devuelve_lista_vacia(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["laura"])
    cuerpo = historial(client, solicitud).json()
    assert cuerpo["data"] == []
    assert cuerpo["pagination"] == {"page": 1, "limit": 20, "total": 0, "total_pages": 0}


def test_solicitud_cerrada_conserva_historial(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "cerrado")
    registrar(db, solicitud, e["laura"], "creacion", None, "registrado", minutos=0)
    registrar(db, solicitud, e["laura"], "cancelacion", "registrado", "cerrado", minutos=5)

    como(e["laura"])
    respuesta = historial(client, solicitud)
    assert respuesta.status_code == 200
    assert respuesta.json()["data"][-1]["tipo_cambio"] == "cancelacion"


# ============================ Paginación ============================


def test_paginacion(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    for i in range(5):
        registrar(db, solicitud, e["coordinador"], "cambio_prioridad", None, f"p{i}", minutos=i)

    como(e["coordinador"])
    cuerpo = historial(client, solicitud, page=2, limit=2).json()
    assert [c["valor_nuevo"] for c in cuerpo["data"]] == ["p2", "p3"]
    assert cuerpo["pagination"] == {"page": 2, "limit": 2, "total": 5, "total_pages": 3}


def test_pagina_fuera_de_rango_devuelve_vacio(client, e, con_historial):
    como(e["coordinador"])
    cuerpo = historial(client, con_historial, page=5).json()
    assert cuerpo["data"] == []
    assert cuerpo["pagination"]["total"] == 3


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"limit": 101}])
def test_parametros_de_paginacion_invalidos(client, e, con_historial, params):
    como(e["coordinador"])
    assert historial(client, con_historial, **params).status_code == 422


# ============================ Solo lectura ============================


@pytest.mark.parametrize("metodo", ["post", "put", "patch", "delete"])
def test_no_se_puede_modificar_el_historial(client, db, e, con_historial, metodo):
    como(e["coordinador"])
    respuesta = getattr(client, metodo)(f"{URL}/{con_historial.id}/history")
    assert respuesta.status_code == 405
    assert db.scalar(select(func.count()).select_from(HistorialCambio)) == 3
