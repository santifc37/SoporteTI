
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Intervencion, Solicitud, Usuario


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
    return {
        "solicitante": crear_usuario(db, "solicitante", "Juan"),
        "tecnico": crear_usuario(db, "tecnico", "Carlos"),
        "otro_tecnico": crear_usuario(db, "tecnico", "Luis"),
        "coordinador": crear_usuario(db, "coordinador", "Ana"),
    }


def test_tecnico_asignado_puede_registrar_intervencion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={"descripcion": "Se revisó el equipo."},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()

    assert cuerpo["solicitud_id"] == str(solicitud.id)
    assert cuerpo["tecnico_id"] == str(escenario["tecnico"].id)
    assert cuerpo["descripcion"] == "Se revisó el equipo."
    assert cuerpo["diagnostico"] is None
    assert cuerpo["visibilidad"] == "interna"
    assert cuerpo["fecha_registro"] is not None

    intervencion = db.scalar(select(Intervencion))
    assert intervencion is not None
    assert intervencion.solicitud_id == solicitud.id


def test_intervencion_puede_tener_diagnostico_y_ser_visible_al_solicitante(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={
            "descripcion": "Se realizó una revisión.",
            "diagnostico": "El disco presenta sectores dañados.",
            "visibilidad": "solicitante",
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()

    assert cuerpo["diagnostico"] == "El disco presenta sectores dañados."
    assert cuerpo["visibilidad"] == "solicitante"


def test_tecnico_no_asignado_no_puede_registrar_intervencion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["otro_tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={"descripcion": "Revisión del equipo."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


@pytest.mark.parametrize("rol", ["solicitante", "coordinador"])
def test_otros_roles_no_pueden_registrar_intervenciones(
    client, db, escenario, rol
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario[rol])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={"descripcion": "Revisión del equipo."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_solicitud_inexistente_devuelve_404(client, escenario):
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{uuid.uuid4()}/interventions",
        json={"descripcion": "Revisión del equipo."},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_NO_ENCONTRADA"


def test_solicitud_cerrada_no_admite_intervenciones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="cerrado",
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={"descripcion": "Revisión del equipo."},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


def test_descripcion_vacia_es_rechazada(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={"descripcion": ""},
    )

    assert respuesta.status_code == 422


def test_descripcion_con_solo_espacios_es_rechazada(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/interventions",
        json={"descripcion": "   "},
    )

    assert respuesta.status_code == 422
