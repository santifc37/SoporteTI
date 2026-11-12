
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import (
    Asignacion,
    Base,
    Solicitud,
    SolicitudInformacion,
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
    app.dependency_overrides.pop(get_current_user, None)


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


def test_tecnico_asignado_puede_solicitar_informacion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "Por favor, indique cuándo comenzó la falla."},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()

    assert cuerpo["mensaje"] == (
        "Solicitud de información registrada correctamente"
    )

    peticion = cuerpo["solicitud_informacion"]
    assert peticion["solicitud_id"] == str(solicitud.id)
    assert peticion["solicitado_por"] == str(escenario["tecnico"].id)
    assert peticion["contenido"] == (
        "Por favor, indique cuándo comenzó la falla."
    )
    assert peticion["estado"] == "pendiente"
    assert peticion["fecha_solicitud"] is not None

    registrada = db.scalar(select(SolicitudInformacion))
    assert registrada is not None
    assert registrada.solicitud_id == solicitud.id


def test_solicitar_informacion_no_cambia_estado_de_solicitud(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="en_atencion",
    )
    estado_anterior = solicitud.estado
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "Necesitamos información adicional."},
    )

    assert respuesta.status_code == 201
    db.refresh(solicitud)
    assert solicitud.estado == estado_anterior


def test_tecnico_no_asignado_no_puede_solicitar_informacion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["otro_tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "Solicito información adicional."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


@pytest.mark.parametrize("rol", ["solicitante", "coordinador"])
def test_otros_roles_no_pueden_usar_endpoint_de_tecnico(
    client, db, escenario, rol
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario[rol])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "Solicito información adicional."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_solicitud_inexistente_devuelve_404(client, escenario):
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{uuid.uuid4()}/information-requests",
        json={"contenido": "Solicito información adicional."},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == (
        "SOLICITUD_NO_ENCONTRADA"
    )


def test_solicitud_cerrada_no_admite_peticiones_de_informacion(
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
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "Solicito información adicional."},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


def test_contenido_vacio_es_rechazado(client, db, escenario):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": ""},
    )

    assert respuesta.status_code == 422


def test_contenido_con_solo_espacios_es_rechazado(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "   "},
    )

    assert respuesta.status_code == 422
