
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
    RespuestaInformacion,
    Solicitud,
    SolicitudInformacion,
    Usuario,
)


URL = "/api/v1/requests"
URL_RESPUESTAS = "/api/v1/information-requests"


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
    db.refresh(usuario)
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
    db.refresh(solicitud)

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


def crear_peticion(client, solicitud):
    return client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": "Por favor, indique cuándo comenzó la falla."},
    )


def test_tecnico_asignado_puede_solicitar_informacion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = crear_peticion(client, solicitud)

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


def test_coordinador_puede_solicitar_informacion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["coordinador"])

    respuesta = crear_peticion(client, solicitud)

    assert respuesta.status_code == 201
    assert respuesta.json()["solicitud_informacion"]["solicitado_por"] == (
        str(escenario["coordinador"].id)
    )


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

    respuesta = crear_peticion(client, solicitud)

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

    respuesta = crear_peticion(client, solicitud)

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_solicitante_no_puede_crear_peticion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["solicitante"])

    respuesta = crear_peticion(client, solicitud)

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

    respuesta = crear_peticion(client, solicitud)

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


@pytest.mark.parametrize("contenido", ["", "   "])
def test_contenido_vacio_es_rechazado(
    client, db, escenario, contenido
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/information-requests",
        json={"contenido": contenido},
    )

    assert respuesta.status_code == 422


def test_solicitante_propietario_puede_consultar_peticiones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    assert creada.status_code == 201

    como(escenario["solicitante"])
    respuesta = client.get(
        f"{URL}/{solicitud.id}/information-requests"
    )

    assert respuesta.status_code == 200
    peticiones = respuesta.json()["data"]
    assert len(peticiones) == 1
    assert peticiones[0]["contenido"] == (
        "Por favor, indique cuándo comenzó la falla."
    )
    assert peticiones[0]["estado"] == "pendiente"
    assert peticiones[0]["respuesta"] is None


def test_tecnico_asignado_puede_consultar_peticiones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])
    assert crear_peticion(client, solicitud).status_code == 201

    respuesta = client.get(
        f"{URL}/{solicitud.id}/information-requests"
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 1


def test_coordinador_puede_consultar_peticiones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])
    assert crear_peticion(client, solicitud).status_code == 201

    como(escenario["coordinador"])
    respuesta = client.get(
        f"{URL}/{solicitud.id}/information-requests"
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 1


def test_otro_solicitante_no_puede_consultar_peticiones(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    otro_solicitante = crear_usuario(
        db, "solicitante", "Pedro"
    )
    como(otro_solicitante)

    respuesta = client.get(
        f"{URL}/{solicitud.id}/information-requests"
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_solicitante_propietario_puede_responder_peticion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    como(escenario["solicitante"])
    respuesta = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "La falla comenzó esta mañana."},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Respuesta registrada correctamente"
    assert cuerpo["respuesta"]["contenido"] == (
        "La falla comenzó esta mañana."
    )
    assert cuerpo["respuesta"]["respondido_por"] == str(
        escenario["solicitante"].id
    )

    peticion = db.scalar(
        select(SolicitudInformacion).where(
            SolicitudInformacion.id == uuid.UUID(peticion_id)
        )
    )
    assert peticion.estado == "respondida"

    respuesta_db = db.scalar(select(RespuestaInformacion))
    assert respuesta_db is not None
    assert respuesta_db.solicitud_informacion_id == peticion.id


def test_responder_no_cambia_estado_de_solicitud(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="en_espera",
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    como(escenario["solicitante"])
    respuesta = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "Ya proporcioné la información."},
    )

    assert respuesta.status_code == 201
    db.refresh(solicitud)
    assert solicitud.estado == "en_espera"


def test_otro_solicitante_no_puede_responder_peticion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    otro_solicitante = crear_usuario(
        db, "solicitante", "Pedro"
    )
    como(otro_solicitante)

    respuesta = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "Respuesta no autorizada."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_tecnico_no_puede_responder_peticion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    respuesta = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "Respuesta desde técnico."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_peticion_inexistente_devuelve_404(
    client, escenario
):
    como(escenario["solicitante"])

    respuesta = client.post(
        f"{URL_RESPUESTAS}/{uuid.uuid4()}/responses",
        json={"contenido": "Respuesta de prueba."},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == (
        "PETICION_NO_ENCONTRADA"
    )


def test_no_se_puede_responder_dos_veces(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    como(escenario["solicitante"])
    primera = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "Primera respuesta."},
    )
    segunda = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "Segunda respuesta."},
    )

    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert segunda.json()["error"]["codigo"] in {
        "PETICION_NO_PENDIENTE",
        "PETICION_YA_RESPONDIDA",
    }


def test_no_se_puede_responder_peticion_de_solicitud_cerrada(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    solicitud.estado = "cerrado"
    db.commit()

    como(escenario["solicitante"])
    respuesta = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": "Respuesta tardía."},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


@pytest.mark.parametrize("contenido", ["", "   "])
def test_respuesta_vacia_es_rechazada(
    client, db, escenario, contenido
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    como(escenario["tecnico"])
    creada = crear_peticion(client, solicitud)
    peticion_id = creada.json()["solicitud_informacion"]["id"]

    como(escenario["solicitante"])
    respuesta = client.post(
        f"{URL_RESPUESTAS}/{peticion_id}/responses",
        json={"contenido": contenido},
    )

    assert respuesta.status_code == 422
