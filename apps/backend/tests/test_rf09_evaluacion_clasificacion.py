"""Pruebas de RF-09 (inicio de la evaluación) y RF-10 (clasificación y prioridad).

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
"""

import itertools
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
from app.models import Asignacion, Base, Categoria, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio

URL = "/api/v1/requests"
_contador = itertools.count(1)


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


def crear_usuario(db, rol):
    usuario = Usuario(
        nombre=rol.capitalize(),
        apellido="Prueba",
        correo=f"{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, **campos):
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
        "version": 1,
    }
    datos.update(campos)
    solicitud = Solicitud(**datos)
    db.add(solicitud)
    db.commit()
    return solicitud


def crear_categoria(db, nombre, activa=True):
    categoria = Categoria(nombre=nombre, activa=activa)
    db.add(categoria)
    db.commit()
    return categoria


def historial(db, solicitud, tipo):
    return db.scalars(
        select(HistorialCambio).where(
            HistorialCambio.solicitud_id == solicitud.id,
            HistorialCambio.tipo_cambio == tipo,
        )
    ).all()


@pytest.fixture()
def e(db):
    return {
        "solicitante": crear_usuario(db, "solicitante"),
        "tecnico": crear_usuario(db, "tecnico"),
        "coordinador": crear_usuario(db, "coordinador"),
    }


# ======================= RF-09: inicio de la evaluación =======================


def evaluar(client, solicitud, estado="en_evaluacion"):
    return client.patch(f"{URL}/{solicitud.id}/status", json={"estado": estado})


def test_coordinador_inicia_la_evaluacion(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    respuesta = evaluar(client, solicitud)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()["solicitud"]
    assert cuerpo["estado_anterior"] == "registrado"
    assert cuerpo["estado_actual"] == "en_evaluacion"
    db.refresh(solicitud)
    assert solicitud.estado == "en_evaluacion"
    assert solicitud.version == 2


def test_inicio_de_evaluacion_queda_en_el_historial(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    evaluar(client, solicitud)

    [registro] = historial(db, solicitud, "cambio_estado")
    assert (registro.valor_anterior, registro.valor_nuevo) == ("registrado", "en_evaluacion")
    assert registro.usuario_id == e["coordinador"].id


@pytest.mark.parametrize("estado", ["en_evaluacion", "asignado", "en_atencion", "cerrado"])
def test_solo_se_evalua_una_solicitud_registrada(client, db, e, estado):
    solicitud = crear_solicitud(db, e["solicitante"], estado=estado)
    como(e["coordinador"])

    respuesta = evaluar(client, solicitud)

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "ESTADO_NO_PERMITIDO"
    db.refresh(solicitud)
    assert solicitud.estado == estado
    assert historial(db, solicitud, "cambio_estado") == []


@pytest.mark.parametrize("destino", ["en_atencion", "en_espera"])
def test_coordinador_no_hace_las_transiciones_del_tecnico(client, db, e, destino):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    assert evaluar(client, solicitud, destino).status_code == 403
    db.refresh(solicitud)
    assert solicitud.estado == "registrado"


def test_tecnico_no_puede_iniciar_la_evaluacion(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"], estado="asignado")
    db.add(Asignacion(solicitud_id=solicitud.id, tecnico_id=e["tecnico"].id, asignado_por=e["coordinador"].id))
    db.commit()
    como(e["tecnico"])

    assert evaluar(client, solicitud).status_code == 409
    db.refresh(solicitud)
    assert solicitud.estado == "asignado"


def test_solicitante_no_puede_iniciar_la_evaluacion(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["solicitante"])

    assert evaluar(client, solicitud).status_code == 403


def test_evaluar_solicitud_inexistente_devuelve_404(client, e):
    como(e["coordinador"])

    respuesta = client.patch(f"{URL}/{uuid.uuid4()}/status", json={"estado": "en_evaluacion"})

    assert respuesta.status_code == 404


# ===================== RF-10: clasificación y prioridad ======================


def clasificar(client, solicitud, cuerpo):
    return client.patch(f"{URL}/{solicitud.id}", json=cuerpo)


def test_coordinador_establece_categoria_y_prioridad(client, db, e):
    hardware = crear_categoria(db, "Hardware")
    solicitud = crear_solicitud(db, e["solicitante"], estado="en_evaluacion")
    como(e["coordinador"])

    respuesta = clasificar(
        client, solicitud, {"categoria_id": str(hardware.id), "prioridad": "alta"}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Solicitud actualizada correctamente"
    assert cuerpo["solicitud"] == {
        "id": str(solicitud.id),
        "numero": solicitud.numero,
        "categoria_id": str(hardware.id),
        "prioridad": "alta",
        "estado": "en_evaluacion",
    }
    db.refresh(solicitud)
    assert (solicitud.categoria_id, solicitud.prioridad) == (hardware.id, "alta")
    assert solicitud.version == 2


def test_la_clasificacion_queda_en_el_historial(client, db, e):
    hardware = crear_categoria(db, "Hardware")
    redes = crear_categoria(db, "Redes")
    solicitud = crear_solicitud(
        db, e["solicitante"], categoria_id=hardware.id, prioridad="baja"
    )
    como(e["coordinador"])

    clasificar(client, solicitud, {"categoria_id": str(redes.id), "prioridad": "alta"})

    [categoria] = historial(db, solicitud, "cambio_categoria")
    [prioridad] = historial(db, solicitud, "cambio_prioridad")
    assert (categoria.valor_anterior, categoria.valor_nuevo) == ("Hardware", "Redes")
    assert (prioridad.valor_anterior, prioridad.valor_nuevo) == ("baja", "alta")
    assert prioridad.usuario_id == e["coordinador"].id


def test_se_puede_enviar_solo_la_prioridad(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    respuesta = clasificar(client, solicitud, {"prioridad": "media"})

    assert respuesta.status_code == 200
    assert respuesta.json()["solicitud"]["prioridad"] == "media"
    assert historial(db, solicitud, "cambio_categoria") == []


def test_enviar_el_mismo_valor_no_genera_historial(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"], prioridad="alta")
    como(e["coordinador"])

    respuesta = clasificar(client, solicitud, {"prioridad": "alta"})

    assert respuesta.status_code == 200
    assert historial(db, solicitud, "cambio_prioridad") == []
    db.refresh(solicitud)
    assert solicitud.version == 1


def test_quitar_la_categoria(client, db, e):
    hardware = crear_categoria(db, "Hardware")
    solicitud = crear_solicitud(db, e["solicitante"], categoria_id=hardware.id)
    como(e["coordinador"])

    respuesta = clasificar(client, solicitud, {"categoria_id": None})

    assert respuesta.status_code == 200
    assert respuesta.json()["solicitud"]["categoria_id"] is None
    [registro] = historial(db, solicitud, "cambio_categoria")
    assert (registro.valor_anterior, registro.valor_nuevo) == ("Hardware", None)


def test_categoria_inexistente_devuelve_422(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    respuesta = clasificar(client, solicitud, {"categoria_id": str(uuid.uuid4())})

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["detalles"][0]["campo"] == "categoria_id"
    db.refresh(solicitud)
    assert solicitud.categoria_id is None


def test_categoria_inactiva_devuelve_422_y_no_cambia_nada(client, db, e):
    inactiva = crear_categoria(db, "Impresoras", activa=False)
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    respuesta = clasificar(
        client, solicitud, {"categoria_id": str(inactiva.id), "prioridad": "alta"}
    )

    assert respuesta.status_code == 422
    db.refresh(solicitud)
    assert (solicitud.categoria_id, solicitud.prioridad) == (None, None)


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"prioridad": "urgente"},
        {"prioridad": None},
        {"categoria_id": "no-es-uuid"},
        {"prioridad": "alta", "estado": "cerrado"},
        {"prioridad": "alta", "solicitante_id": str(uuid.uuid4())},
    ],
)
def test_datos_invalidos_devuelven_422(client, db, e, cuerpo):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    assert clasificar(client, solicitud, cuerpo).status_code == 422
    db.refresh(solicitud)
    assert (solicitud.prioridad, solicitud.estado) == (None, "registrado")


def test_no_se_clasifica_una_solicitud_cerrada(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"], estado="cerrado")
    como(e["coordinador"])

    respuesta = clasificar(client, solicitud, {"prioridad": "alta"})

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


@pytest.mark.parametrize("rol", ["solicitante", "tecnico"])
def test_solo_el_coordinador_clasifica(client, db, e, rol):
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e[rol])

    respuesta = clasificar(client, solicitud, {"prioridad": "alta"})

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    db.refresh(solicitud)
    assert solicitud.prioridad is None


def test_clasificar_solicitud_inexistente_devuelve_404(client, e):
    como(e["coordinador"])

    assert client.patch(f"{URL}/{uuid.uuid4()}", json={"prioridad": "alta"}).status_code == 404


def test_clasificar_sin_sesion_devuelve_401(client, db, e):
    solicitud = crear_solicitud(db, e["solicitante"])

    assert clasificar(client, solicitud, {"prioridad": "alta"}).status_code == 401


# ============================ flujo de punta a punta ============================


def test_flujo_evaluar_y_clasificar(client, db, e):
    """Registro → evaluación → clasificación, con su historial en orden."""
    redes = crear_categoria(db, "Redes")
    solicitud = crear_solicitud(db, e["solicitante"])
    como(e["coordinador"])

    assert evaluar(client, solicitud).status_code == 200
    assert clasificar(
        client, solicitud, {"categoria_id": str(redes.id), "prioridad": "media"}
    ).status_code == 200

    detalle = client.get(f"{URL}/{solicitud.id}").json()
    assert detalle["estado"] == "en_evaluacion"
    assert detalle["prioridad"] == "media"
    assert detalle["categoria"]["nombre"] == "Redes"
