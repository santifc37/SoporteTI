
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import (
    Asignacion,
    Base,
    Intervencion,
    Solicitud,
    Usuario,
)


URL = "/api/v1/requests"


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


def como(usuario):
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
        correo=f"{uuid.uuid4()}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, tecnico, estado="asignado"):
    solicitud = Solicitud(
        numero=f"ST-{uuid.uuid4().hex[:6]}",
        titulo="Solicitud de prueba",
        descripcion="Descripción de prueba",
        tipo="incidente",
        solicitante_id=solicitante.id,
        ubicacion="Oficina",
        medio_contacto="correo",
        dato_contacto="prueba@test.com",
        estado=estado,
    )
    db.add(solicitud)
    db.commit()

    asignacion = Asignacion(
        solicitud_id=solicitud.id,
        tecnico_id=tecnico.id,
        asignado_por=tecnico.id,
    )
    db.add(asignacion)
    db.commit()

    return solicitud


def crear_intervencion(
    db,
    solicitud,
    tecnico,
    descripcion,
    visibilidad,
    fecha,
):
    intervencion = Intervencion(
        solicitud_id=solicitud.id,
        tecnico_id=tecnico.id,
        descripcion=descripcion,
        diagnostico="Diagnóstico de prueba",
        visibilidad=visibilidad,
        fecha_registro=fecha,
    )
    db.add(intervencion)
    db.commit()
    return intervencion


@pytest.fixture()
def escenario(db):
    return {
        "solicitante": crear_usuario(db, "solicitante", "Juan"),
        "otro_solicitante": crear_usuario(db, "solicitante", "Pedro"),
        "tecnico": crear_usuario(db, "tecnico", "Carlos"),
        "otro_tecnico": crear_usuario(db, "tecnico", "Luis"),
        "coordinador": crear_usuario(db, "coordinador", "Ana"),
    }


def test_solicitante_solo_consulta_intervenciones_visibles(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    crear_intervencion(
        db,
        solicitud,
        escenario["tecnico"],
        "Revisión interna del equipo.",
        "interna",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    crear_intervencion(
        db,
        solicitud,
        escenario["tecnico"],
        "Se realizó mantenimiento al equipo.",
        "solicitante",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    como(escenario["solicitante"])

    respuesta = client.get(f"{URL}/{solicitud.id}/interventions")

    assert respuesta.status_code == 200
    datos = respuesta.json()["data"]

    assert len(datos) == 1
    assert datos[0]["descripcion"] == "Se realizó mantenimiento al equipo."
    assert datos[0]["visibilidad"] == "solicitante"


def test_solicitante_no_puede_consultar_solicitud_de_otro_usuario(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["otro_solicitante"])

    respuesta = client.get(f"{URL}/{solicitud.id}/interventions")

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_tecnico_asignado_consulta_intervenciones_internas_y_visibles(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    crear_intervencion(
        db,
        solicitud,
        escenario["tecnico"],
        "Primera intervención interna.",
        "interna",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    crear_intervencion(
        db,
        solicitud,
        escenario["tecnico"],
        "Segunda intervención visible.",
        "solicitante",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    como(escenario["tecnico"])

    respuesta = client.get(f"{URL}/{solicitud.id}/interventions")

    assert respuesta.status_code == 200
    datos = respuesta.json()["data"]

    assert len(datos) == 2
    assert datos[0]["descripcion"] == "Primera intervención interna."
    assert datos[1]["descripcion"] == "Segunda intervención visible."
    assert datos[0]["tecnico_nombre"] == "Carlos Prueba"


def test_tecnico_no_asignado_no_puede_consultar_intervenciones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["otro_tecnico"])

    respuesta = client.get(f"{URL}/{solicitud.id}/interventions")

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_coordinador_puede_consultar_todas_las_intervenciones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    crear_intervencion(
        db,
        solicitud,
        escenario["tecnico"],
        "Intervención interna.",
        "interna",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    crear_intervencion(
        db,
        solicitud,
        escenario["tecnico"],
        "Intervención visible.",
        "solicitante",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    como(escenario["coordinador"])

    respuesta = client.get(f"{URL}/{solicitud.id}/interventions")

    assert respuesta.status_code == 200
    datos = respuesta.json()["data"]

    assert len(datos) == 2
    assert {dato["visibilidad"] for dato in datos} == {
        "interna",
        "solicitante",
    }


def test_solicitud_inexistente_devuelve_404(client, escenario):
    como(escenario["coordinador"])

    respuesta = client.get(
        f"{URL}/{uuid.uuid4()}/interventions"
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == (
        "SOLICITUD_NO_ENCONTRADA"
    )


def test_solicitud_sin_intervenciones_devuelve_lista_vacia(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["tecnico"])

    respuesta = client.get(f"{URL}/{solicitud.id}/interventions")

    assert respuesta.status_code == 200
    assert respuesta.json()["data"] == []
