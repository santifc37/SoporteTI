"""Pruebas de RF-06: registro de solicitudes por el solicitante.

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
"""

import itertools
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Base, Categoria, Solicitud, Usuario
from app.models.historial_cambio import HistorialCambio

URL = "/api/v1/requests"


# En PostgreSQL el número ST-000001 lo genera una secuencia (migración 0001).
# SQLite no la tiene, así que en las pruebas se simula con este contador.
_consecutivo = itertools.count(1)


def _numerar(_mapper, _conexion, solicitud):
    if solicitud.numero is None:
        solicitud.numero = f"ST-{next(_consecutivo):06d}"


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    event.listen(Solicitud, "before_insert", _numerar)
    with Session(engine) as session:
        yield session
    event.remove(Solicitud, "before_insert", _numerar)
    engine.dispose()


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


def nuevo_usuario(db, rol="solicitante") -> Usuario:
    usuario = Usuario(
        nombre="Laura",
        apellido="Docente",
        correo=f"{uuid.uuid4().hex[:8]}@organizacion.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


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


@pytest.fixture()
def solicitante(db):
    usuario = nuevo_usuario(db, "solicitante")
    como(usuario)
    return usuario


def datos(**cambios):
    base = {
        "titulo": "Equipo no enciende",
        "descripcion": "El computador no enciende al presionar el botón.",
        "tipo": "incidente",
        "ubicacion": "Oficina administrativa",
        "placa_equipo": "EQ-001",
        "medio_contacto": "correo",
        "dato_contacto": "laura@organizacion.com",
    }
    base.update(cambios)
    return base


def total_solicitudes(db) -> int:
    return db.scalar(select(func.count()).select_from(Solicitud))


# ------------------------------- registro válido ------------------------------


def test_solicitante_registra_solicitud(client, db, solicitante):
    respuesta = client.post(URL, json=datos())

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Solicitud creada correctamente"
    s = cuerpo["solicitud"]
    assert s["estado"] == "registrado"
    assert s["prioridad"] is None
    assert s["solicitante_id"] == str(solicitante.id)
    assert s["numero"].startswith("ST-")
    assert s["titulo"] == "Equipo no enciende"


def test_la_solicitud_queda_guardada_y_recuperable(client, db, solicitante):
    id_creada = client.post(URL, json=datos()).json()["solicitud"]["id"]

    guardada = db.get(Solicitud, uuid.UUID(id_creada))

    assert guardada is not None
    assert guardada.ubicacion == "Oficina administrativa"
    assert guardada.placa_equipo == "EQ-001"
    assert guardada.dato_contacto == "laura@organizacion.com"


def test_la_creacion_queda_en_el_historial(client, db, solicitante):
    id_creada = uuid.UUID(client.post(URL, json=datos()).json()["solicitud"]["id"])

    registro = db.scalar(
        select(HistorialCambio).where(HistorialCambio.solicitud_id == id_creada)
    )

    assert registro is not None
    assert registro.tipo_cambio == "creacion"
    assert registro.valor_nuevo == "registrado"
    assert registro.usuario_id == solicitante.id


def test_cada_solicitud_recibe_un_numero_distinto(client, solicitante):
    primero = client.post(URL, json=datos()).json()["solicitud"]["numero"]
    segundo = client.post(URL, json=datos()).json()["solicitud"]["numero"]

    assert primero != segundo


def test_con_categoria_activa(client, db, solicitante):
    categoria = Categoria(nombre="Hardware", activa=True)
    db.add(categoria)
    db.commit()

    respuesta = client.post(URL, json=datos(categoria_id=str(categoria.id)))

    assert respuesta.status_code == 201
    assert respuesta.json()["solicitud"]["categoria_id"] == str(categoria.id)


def test_sin_categoria_ni_placa(client, solicitante):
    respuesta = client.post(
        URL, json=datos(tipo="requerimiento", categoria_id=None, placa_equipo=None)
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["solicitud"]["categoria_id"] is None


def test_contacto_por_telefono(client, solicitante):
    respuesta = client.post(
        URL, json=datos(medio_contacto="telefono", dato_contacto="+57 300 123 4567")
    )

    assert respuesta.status_code == 201


def test_el_solicitante_sale_de_la_sesion_no_del_cuerpo(client, db, solicitante):
    otro = nuevo_usuario(db, "solicitante")
    como(solicitante)

    respuesta = client.post(URL, json=datos(solicitante_id=str(otro.id)))

    # El campo no está permitido: no se puede crear a nombre de otro usuario.
    assert respuesta.status_code == 422
    assert total_solicitudes(db) == 0


# ------------------------------ datos no válidos ------------------------------


@pytest.mark.parametrize(
    "cambio",
    [
        {"titulo": ""},
        {"titulo": "x" * 201},
        {"descripcion": "   "},
        {"tipo": "queja"},
        {"ubicacion": ""},
        {"medio_contacto": "whatsapp"},
        {"dato_contacto": "no-es-correo"},
        {"medio_contacto": "telefono", "dato_contacto": "llamar a Laura"},
        {"categoria_id": "no-es-un-uuid"},
        {"estado": "cerrado"},
        {"prioridad": "alta"},
    ],
)
def test_datos_invalidos_devuelven_422_y_no_guardan(client, db, solicitante, cambio):
    respuesta = client.post(URL, json=datos(**cambio))

    assert respuesta.status_code == 422
    assert total_solicitudes(db) == 0


@pytest.mark.parametrize(
    "campo",
    ["titulo", "descripcion", "tipo", "ubicacion", "medio_contacto", "dato_contacto"],
)
def test_campos_obligatorios(client, db, solicitante, campo):
    cuerpo = datos()
    cuerpo.pop(campo)

    assert client.post(URL, json=cuerpo).status_code == 422
    assert total_solicitudes(db) == 0


def test_categoria_inexistente(client, db, solicitante):
    respuesta = client.post(URL, json=datos(categoria_id=str(uuid.uuid4())))

    assert respuesta.status_code == 422
    error = respuesta.json()["error"]
    assert error["codigo"] == "ERROR_VALIDACION"
    assert error["detalles"][0]["campo"] == "categoria_id"
    assert total_solicitudes(db) == 0


def test_categoria_inactiva(client, db, solicitante):
    categoria = Categoria(nombre="Impresoras", activa=False)
    db.add(categoria)
    db.commit()

    respuesta = client.post(URL, json=datos(categoria_id=str(categoria.id)))

    assert respuesta.status_code == 422
    assert total_solicitudes(db) == 0


# ---------------------------------- permisos ----------------------------------


def test_sin_sesion_devuelve_401(client, db):
    assert client.post(URL, json=datos()).status_code == 401
    assert total_solicitudes(db) == 0


@pytest.mark.parametrize("rol", ["tecnico", "coordinador"])
def test_solo_el_solicitante_registra_solicitudes(client, db, rol):
    como(nuevo_usuario(db, rol))

    respuesta = client.post(URL, json=datos())

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    assert total_solicitudes(db) == 0
