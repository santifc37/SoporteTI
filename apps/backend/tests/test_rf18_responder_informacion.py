"""Pruebas de RF-18, parte del solicitante (docs/contrato-api.md §11.2 y §11.3).

- GET  /requests/{id}/information-requests: consultar peticiones.
- POST /information-requests/{id}/responses: responder una petición.

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
from app.models import (
    Asignacion,
    Base,
    RespuestaInformacion,
    Solicitud,
    SolicitudInformacion,
    Usuario,
)

URL_SOLICITUDES = "/api/v1/requests"
URL_PETICIONES = "/api/v1/information-requests"
_contador = itertools.count(1)
INICIO = datetime(2026, 11, 6, 13, 30, tzinfo=timezone.utc)


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


def crear_solicitud(db, solicitante, estado="en_atencion"):
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


def asignar(db, solicitud, tecnico, coordinador, finalizada=False):
    db.add(
        Asignacion(
            solicitud_id=solicitud.id,
            tecnico_id=tecnico.id,
            asignado_por=coordinador.id,
            fecha_finalizacion=INICIO if finalizada else None,
        )
    )
    db.commit()


def crear_peticion(db, solicitud, autor, contenido="¿El equipo enciende alguna luz?", minutos=0):
    peticion = SolicitudInformacion(
        solicitud_id=solicitud.id,
        solicitado_por=autor.id,
        contenido=contenido,
        estado="pendiente",
        fecha_solicitud=INICIO + timedelta(minutes=minutos),
    )
    db.add(peticion)
    db.commit()
    return peticion


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
def caso(db, e):
    """Solicitud de Laura en atención, asignada a Carlos, con una petición pendiente."""
    solicitud = crear_solicitud(db, e["laura"])
    asignar(db, solicitud, e["carlos"], e["coordinador"])
    peticion = crear_peticion(db, solicitud, e["carlos"])
    return solicitud, peticion


def listar(client, solicitud):
    return client.get(f"{URL_SOLICITUDES}/{solicitud.id}/information-requests")


def responder(client, peticion, contenido="Sí, enciende una luz roja."):
    return client.post(f"{URL_PETICIONES}/{peticion.id}/responses", json={"contenido": contenido})


# ===================== §11.2 Consultar peticiones: permisos =====================


def test_solicitante_propietario_consulta_peticiones(client, e, caso):
    solicitud, peticion = caso
    como(e["laura"])
    respuesta = listar(client, solicitud)
    assert respuesta.status_code == 200
    assert [p["id"] for p in respuesta.json()["data"]] == [str(peticion.id)]


def test_tecnico_asignado_consulta_peticiones(client, e, caso):
    como(e["carlos"])
    assert listar(client, caso[0]).status_code == 200


def test_coordinador_consulta_peticiones(client, e, caso):
    como(e["coordinador"])
    assert listar(client, caso[0]).status_code == 200


def test_solicitante_ajeno_no_consulta(client, e, caso):
    como(e["pedro"])
    respuesta = listar(client, caso[0])
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_tecnico_no_asignado_no_consulta(client, e, caso):
    como(e["ana"])
    assert listar(client, caso[0]).status_code == 403


def test_tecnico_reasignado_pierde_acceso(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    asignar(db, solicitud, e["carlos"], e["coordinador"], finalizada=True)
    asignar(db, solicitud, e["ana"], e["coordinador"])
    como(e["carlos"])
    assert listar(client, solicitud).status_code == 403


def test_consultar_solicitud_inexistente_404(client, e):
    como(e["coordinador"])
    respuesta = client.get(f"{URL_SOLICITUDES}/{uuid.uuid4()}/information-requests")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_consultar_sin_sesion_401(client, caso):
    app.dependency_overrides.pop(get_current_user, None)
    assert listar(client, caso[0]).status_code == 401


# ===================== §11.2 Consultar peticiones: contenido =====================


def test_formato_de_peticion_pendiente(client, e, caso):
    solicitud, peticion = caso
    como(e["laura"])
    dato = listar(client, solicitud).json()["data"][0]

    assert dato["id"] == str(peticion.id)
    assert dato["contenido"] == "¿El equipo enciende alguna luz?"
    assert dato["estado"] == "pendiente"
    assert dato["solicitado_por"] == {
        "id": str(e["carlos"].id),
        "nombre": "Carlos Prueba",
        "rol": "tecnico",
    }
    assert dato["fecha_solicitud"].startswith("2026-11-06T13:30")
    assert dato["respuesta"] is None


def test_peticion_respondida_incluye_respuesta(client, e, caso):
    solicitud, peticion = caso
    como(e["laura"])
    responder(client, peticion)

    dato = listar(client, solicitud).json()["data"][0]
    assert dato["estado"] == "respondida"
    assert dato["respuesta"]["contenido"] == "Sí, enciende una luz roja."
    assert dato["respuesta"]["respondido_por"] == str(e["laura"].id)
    assert dato["respuesta"]["solicitud_informacion_id"] == str(peticion.id)


def test_orden_cronologico(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    asignar(db, solicitud, e["carlos"], e["coordinador"])
    crear_peticion(db, solicitud, e["carlos"], "Segunda", minutos=30)
    crear_peticion(db, solicitud, e["carlos"], "Primera", minutos=0)

    como(e["laura"])
    contenidos = [p["contenido"] for p in listar(client, solicitud).json()["data"]]
    assert contenidos == ["Primera", "Segunda"]


def test_solo_peticiones_de_esa_solicitud(client, db, e, caso):
    otra = crear_solicitud(db, e["laura"])
    crear_peticion(db, otra, e["carlos"], "De otra solicitud")

    como(e["laura"])
    assert len(listar(client, caso[0]).json()["data"]) == 1


def test_solicitud_sin_peticiones_lista_vacia(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e["laura"])
    assert listar(client, solicitud).json() == {"data": []}


def test_solicitud_cerrada_sigue_consultable(client, db, e, caso):
    solicitud, _ = caso
    solicitud.estado = "cerrado"
    db.commit()
    como(e["laura"])
    assert listar(client, solicitud).status_code == 200


# ===================== §11.3 Responder petición =====================


def test_solicitante_responde_peticion(client, db, e, caso):
    _, peticion = caso
    como(e["laura"])
    respuesta = responder(client, peticion)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Respuesta registrada correctamente"
    assert cuerpo["respuesta"]["solicitud_informacion_id"] == str(peticion.id)
    assert cuerpo["respuesta"]["respondido_por"] == str(e["laura"].id)
    assert cuerpo["respuesta"]["contenido"] == "Sí, enciende una luz roja."
    assert "fecha_respuesta" in cuerpo["respuesta"]

    db.refresh(peticion)
    assert peticion.estado == "respondida"


def test_responder_no_cambia_estado_de_la_solicitud(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_espera")
    asignar(db, solicitud, e["carlos"], e["coordinador"])
    peticion = crear_peticion(db, solicitud, e["carlos"])

    como(e["laura"])
    assert responder(client, peticion).status_code == 201
    db.refresh(solicitud)
    assert solicitud.estado == "en_espera"


def test_contenido_se_guarda_sin_espacios_extremos(client, e, caso):
    como(e["laura"])
    respuesta = responder(client, caso[1], "   Luz roja   ")
    assert respuesta.json()["respuesta"]["contenido"] == "Luz roja"


def test_no_se_responde_dos_veces(client, db, e, caso):
    _, peticion = caso
    como(e["laura"])
    assert responder(client, peticion).status_code == 201

    segunda = responder(client, peticion, "Otra respuesta")
    assert segunda.status_code == 409
    assert segunda.json()["error"]["codigo"] == "PETICION_YA_RESPONDIDA"
    assert db.scalar(select(func.count()).select_from(RespuestaInformacion)) == 1


def test_no_se_responde_en_solicitud_cerrada(client, db, e, caso):
    solicitud, peticion = caso
    solicitud.estado = "cerrado"
    db.commit()

    como(e["laura"])
    respuesta = responder(client, peticion)
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"
    db.refresh(peticion)
    assert peticion.estado == "pendiente"


def test_solicitante_ajeno_no_responde(client, db, e, caso):
    _, peticion = caso
    como(e["pedro"])
    respuesta = responder(client, peticion)
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    assert db.scalar(select(func.count()).select_from(RespuestaInformacion)) == 0


@pytest.mark.parametrize("rol", ["carlos", "coordinador"])
def test_otros_roles_no_responden(client, e, caso, rol):
    como(e[rol])
    respuesta = responder(client, caso[1])
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_peticion_inexistente_404(client, e):
    como(e["laura"])
    respuesta = client.post(
        f"{URL_PETICIONES}/{uuid.uuid4()}/responses", json={"contenido": "Hola"}
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


@pytest.mark.parametrize("cuerpo", [{}, {"contenido": ""}, {"contenido": "    "}])
def test_contenido_invalido_422(client, e, caso, cuerpo):
    como(e["laura"])
    respuesta = client.post(f"{URL_PETICIONES}/{caso[1].id}/responses", json=cuerpo)
    assert respuesta.status_code == 422


def test_responder_sin_sesion_401(client, caso):
    app.dependency_overrides.pop(get_current_user, None)
    assert responder(client, caso[1]).status_code == 401
