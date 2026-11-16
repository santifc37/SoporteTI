"""Pruebas de RF-22, RF-23 y RF-26: conversación de las solicitudes (docs/contrato-api.md §12).

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
from app.models import Asignacion, Base, Mensaje, Solicitud, Usuario

URL = "/api/v1/requests"
_contador = itertools.count(1)
INICIO = datetime(2026, 11, 6, 14, 0, tzinfo=timezone.utc)


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


def crear_mensaje(db, solicitud, remitente, contenido, minutos=0):
    mensaje = Mensaje(
        solicitud_id=solicitud.id,
        remitente_id=remitente.id,
        contenido=contenido,
        fecha_envio=INICIO + timedelta(minutes=minutos),
    )
    db.add(mensaje)
    db.commit()
    return mensaje


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
def solicitud(db, e):
    """Solicitud de Laura en atención, asignada a Carlos."""
    s = crear_solicitud(db, e["laura"])
    asignar(db, s, e["carlos"], e["coordinador"])
    return s


def consultar(client, solicitud, **params):
    return client.get(f"{URL}/{solicitud.id}/messages", params=params)


def enviar(client, solicitud, contenido="El equipo sigue sin encender."):
    return client.post(f"{URL}/{solicitud.id}/messages", json={"contenido": contenido})


def total_mensajes(db):
    return db.scalar(select(func.count()).select_from(Mensaje))


# ======================== RF-23: enviar mensajes ========================


@pytest.mark.parametrize("quien", ["laura", "carlos", "coordinador"])
def test_participantes_autorizados_envian(client, db, e, solicitud, quien):
    como(e[quien])
    respuesta = enviar(client, solicitud)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Mensaje enviado correctamente"
    assert cuerpo["data"]["solicitud_id"] == str(solicitud.id)
    assert cuerpo["data"]["remitente_id"] == str(e[quien].id)
    assert cuerpo["data"]["contenido"] == "El equipo sigue sin encender."
    assert "fecha_envio" in cuerpo["data"]
    assert total_mensajes(db) == 1


def test_enviar_no_cambia_estado(client, db, e, solicitud):
    como(e["laura"])
    enviar(client, solicitud)
    db.refresh(solicitud)
    assert solicitud.estado == "en_atencion"


@pytest.mark.parametrize("estado", ["registrado", "en_evaluacion", "en_espera", "resuelto"])
def test_solicitante_escribe_en_cualquier_estado_abierto(client, db, e, estado):
    s = crear_solicitud(db, e["laura"], estado)
    como(e["laura"])
    assert enviar(client, s).status_code == 201
    db.refresh(s)
    assert s.estado == estado


def test_no_se_envia_en_solicitud_cerrada(client, db, e, solicitud):
    solicitud.estado = "cerrado"
    db.commit()
    como(e["laura"])
    respuesta = enviar(client, solicitud)
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"
    assert total_mensajes(db) == 0


def test_solicitante_ajeno_no_envia(client, db, e, solicitud):
    como(e["pedro"])
    respuesta = enviar(client, solicitud)
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    assert total_mensajes(db) == 0


def test_tecnico_no_asignado_no_envia(client, e, solicitud):
    como(e["ana"])
    assert enviar(client, solicitud).status_code == 403


def test_tecnico_reasignado_no_envia(client, db, e):
    s = crear_solicitud(db, e["laura"])
    asignar(db, s, e["carlos"], e["coordinador"], finalizada=True)
    asignar(db, s, e["ana"], e["coordinador"])
    como(e["carlos"])
    assert enviar(client, s).status_code == 403
    como(e["ana"])
    assert enviar(client, s).status_code == 201


def test_enviar_a_solicitud_inexistente_404(client, e):
    como(e["coordinador"])
    respuesta = client.post(f"{URL}/{uuid.uuid4()}/messages", json={"contenido": "Hola"})
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


@pytest.mark.parametrize(
    "cuerpo",
    [{}, {"contenido": ""}, {"contenido": "    "}, {"contenido": "Hola", "remitente_id": "x"}],
)
def test_contenido_invalido_422(client, db, e, solicitud, cuerpo):
    como(e["laura"])
    respuesta = client.post(f"{URL}/{solicitud.id}/messages", json=cuerpo)
    assert respuesta.status_code == 422
    assert total_mensajes(db) == 0


def test_contenido_se_guarda_sin_espacios_extremos(client, e, solicitud):
    como(e["laura"])
    assert enviar(client, solicitud, "   Hola   ").json()["data"]["contenido"] == "Hola"


def test_enviar_sin_sesion_401(client, solicitud):
    app.dependency_overrides.pop(get_current_user, None)
    assert enviar(client, solicitud).status_code == 401


# ======================== RF-22 / RF-26: consultar la conversación ========================


@pytest.mark.parametrize("quien", ["laura", "carlos", "coordinador"])
def test_participantes_consultan(client, db, e, solicitud, quien):
    crear_mensaje(db, solicitud, e["laura"], "Hola")
    como(e[quien])
    respuesta = consultar(client, solicitud)
    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 1


@pytest.mark.parametrize("quien", ["pedro", "ana"])
def test_no_participantes_no_consultan(client, e, solicitud, quien):
    como(e[quien])
    respuesta = consultar(client, solicitud)
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_consultar_solicitud_inexistente_404(client, e):
    como(e["coordinador"])
    assert client.get(f"{URL}/{uuid.uuid4()}/messages").status_code == 404


def test_formato_del_mensaje(client, db, e, solicitud):
    mensaje = crear_mensaje(db, solicitud, e["carlos"], "¿Puede reiniciar el equipo?")
    como(e["laura"])
    dato = consultar(client, solicitud).json()["data"][0]

    assert dato["id"] == str(mensaje.id)
    assert dato["solicitud_id"] == str(solicitud.id)
    assert dato["remitente"] == {
        "id": str(e["carlos"].id),
        "nombre": "Carlos Prueba",
        "rol": "tecnico",
    }
    assert dato["contenido"] == "¿Puede reiniciar el equipo?"
    assert dato["fecha_envio"].startswith("2026-11-06T14:00")


def test_orden_cronologico_conserva_autor(client, db, e, solicitud):
    # Se insertan desordenados a propósito.
    crear_mensaje(db, solicitud, e["laura"], "Tercero", minutos=20)
    crear_mensaje(db, solicitud, e["laura"], "Primero", minutos=0)
    crear_mensaje(db, solicitud, e["carlos"], "Segundo", minutos=10)

    como(e["coordinador"])
    datos = consultar(client, solicitud).json()["data"]
    assert [m["contenido"] for m in datos] == ["Primero", "Segundo", "Tercero"]
    assert [m["remitente"]["rol"] for m in datos] == ["solicitante", "tecnico", "solicitante"]


def test_solo_mensajes_de_esa_solicitud(client, db, e, solicitud):
    otra = crear_solicitud(db, e["laura"])
    crear_mensaje(db, solicitud, e["laura"], "De esta")
    crear_mensaje(db, otra, e["laura"], "De otra")

    como(e["laura"])
    assert [m["contenido"] for m in consultar(client, solicitud).json()["data"]] == ["De esta"]


def test_conversacion_vacia(client, e, solicitud):
    como(e["laura"])
    assert consultar(client, solicitud).json() == {
        "data": [],
        "pagination": {"page": 1, "limit": 20, "total": 0, "total_pages": 0},
    }


def test_solicitud_cerrada_conserva_conversacion(client, db, e, solicitud):
    crear_mensaje(db, solicitud, e["laura"], "Gracias")
    solicitud.estado = "cerrado"
    db.commit()
    como(e["laura"])
    respuesta = consultar(client, solicitud)
    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 1


def test_mensaje_enviado_aparece_en_la_conversacion(client, e, solicitud):
    como(e["laura"])
    enviar(client, solicitud, "Primer mensaje")
    como(e["carlos"])
    datos = consultar(client, solicitud).json()["data"]
    assert [m["contenido"] for m in datos] == ["Primer mensaje"]


def test_paginacion(client, db, e, solicitud):
    for i in range(5):
        crear_mensaje(db, solicitud, e["laura"], f"m{i}", minutos=i)

    como(e["laura"])
    cuerpo = consultar(client, solicitud, page=2, limit=2).json()
    assert [m["contenido"] for m in cuerpo["data"]] == ["m2", "m3"]
    assert cuerpo["pagination"] == {"page": 2, "limit": 2, "total": 5, "total_pages": 3}


def test_filtro_desde_trae_solo_mensajes_nuevos(client, db, e, solicitud):
    crear_mensaje(db, solicitud, e["laura"], "Viejo", minutos=0)
    crear_mensaje(db, solicitud, e["carlos"], "Nuevo 1", minutos=10)
    crear_mensaje(db, solicitud, e["laura"], "Nuevo 2", minutos=20)

    como(e["laura"])
    cuerpo = consultar(client, solicitud, desde="2026-11-06T14:05:00Z").json()
    assert [m["contenido"] for m in cuerpo["data"]] == ["Nuevo 1", "Nuevo 2"]
    assert cuerpo["pagination"]["total"] == 2


@pytest.mark.parametrize(
    "params", [{"page": 0}, {"limit": 0}, {"limit": 101}, {"desde": "no-es-fecha"}]
)
def test_parametros_invalidos_422(client, e, solicitud, params):
    como(e["laura"])
    assert consultar(client, solicitud, **params).status_code == 422


def test_consultar_sin_sesion_401(client, solicitud):
    app.dependency_overrides.pop(get_current_user, None)
    assert consultar(client, solicitud).status_code == 401
