
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio


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


@pytest.fixture()
def escenario(db):
    solicitante = crear_usuario(db, "solicitante", "Juan")
    tecnico = crear_usuario(db, "tecnico", "Carlos")
    otro_tecnico = crear_usuario(db, "tecnico", "Luis")
    coordinador = crear_usuario(db, "coordinador", "Ana")

    return {
        "solicitante": solicitante,
        "tecnico": tecnico,
        "otro_tecnico": otro_tecnico,
        "coordinador": coordinador,
    }


def test_tecnico_asignado_puede_iniciar_atencion(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_atencion"},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()

    assert cuerpo["mensaje"] == "Estado actualizado correctamente"
    assert cuerpo["solicitud"]["estado_anterior"] == "asignado"
    assert cuerpo["solicitud"]["estado_actual"] == "en_atencion"

    db.refresh(solicitud)
    assert solicitud.estado == "en_atencion"


def test_cambio_de_estado_registra_historial(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_atencion"},
    )

    assert respuesta.status_code == 200

    historial = db.scalar(
        select(HistorialCambio).where(
            HistorialCambio.solicitud_id == solicitud.id
        )
    )

    assert historial is not None
    assert historial.usuario_id == escenario["tecnico"].id
    assert historial.tipo_cambio == "cambio_estado"
    assert historial.valor_anterior == "asignado"
    assert historial.valor_nuevo == "en_atencion"


def test_tecnico_no_asignado_no_puede_cambiar_estado(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["otro_tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_atencion"},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_transicion_no_permitida_es_rechazada(client, db, escenario):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="asignado",
    )
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_espera"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "TRANSICION_NO_PERMITIDA"

    db.refresh(solicitud)
    assert solicitud.estado == "asignado"


def test_tecnico_puede_pasar_de_atencion_a_espera(client, db, escenario):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="en_atencion",
    )
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_espera"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["solicitud"]["estado_actual"] == "en_espera"


def test_tecnico_puede_reanudar_una_solicitud_en_espera(client, db, escenario):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="en_espera",
    )
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_atencion"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["solicitud"]["estado_actual"] == "en_atencion"


def test_coordinador_no_usa_la_ruta_del_tecnico(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["coordinador"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "en_atencion"},
    )

    assert respuesta.status_code == 403


def test_solicitud_inexistente_devuelve_404(client, escenario):
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{uuid.uuid4()}/status",
        json={"estado": "en_atencion"},
    )

    assert respuesta.status_code == 404


def test_estado_no_admitido_devuelve_422(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.patch(
        f"{URL}/{solicitud.id}/status",
        json={"estado": "cerrado"},
    )

    assert respuesta.status_code == 422
