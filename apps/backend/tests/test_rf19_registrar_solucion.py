
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, create_engine
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


def crear_solicitud(db, solicitante, tecnico, estado="en_atencion"):
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


def test_tecnico_asignado_puede_registrar_solucion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    solucion = "Se reemplazó el cable y se comprobó el funcionamiento."

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": solucion},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()

    assert cuerpo["mensaje"] == "Solución registrada correctamente"
    assert cuerpo["solicitud"]["estado_anterior"] == "en_atencion"
    assert cuerpo["solicitud"]["estado_actual"] == "resuelto"
    assert cuerpo["solicitud"]["solucion_final"] == solucion
    assert cuerpo["solicitud"]["resuelto_por"] == str(
        escenario["tecnico"].id
    )
    assert cuerpo["solicitud"]["fecha_resolucion"] is not None
    assert cuerpo["solicitud"]["fecha_actualizacion"] is not None

    db.refresh(solicitud)
    assert solicitud.estado == "resuelto"
    assert solicitud.solucion_final == solucion
    assert solicitud.resuelto_por == escenario["tecnico"].id
    assert solicitud.fecha_resolucion is not None


def test_tecnico_puede_resolver_solicitud_en_espera(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado="en_espera",
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": "Se completó la revisión técnica."},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["solicitud"]["estado_anterior"] == "en_espera"
    assert respuesta.json()["solicitud"]["estado_actual"] == "resuelto"


def test_registrar_solucion_crea_historial(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    solucion = "Se instaló el controlador correspondiente."

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": solucion},
    )

    assert respuesta.status_code == 200

    historial = db.scalar(
        select(HistorialCambio).where(
            HistorialCambio.solicitud_id == solicitud.id
        )
    )

    assert historial is not None
    assert historial.usuario_id == escenario["tecnico"].id
    assert historial.tipo_cambio == "solucion"
    assert historial.valor_anterior == "en_atencion"
    assert historial.valor_nuevo == solucion


def test_tecnico_no_asignado_no_puede_resolver(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["otro_tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": "Solución de prueba."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_coordinador_no_puede_usar_endpoint_de_solucion(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["coordinador"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": "Solución de prueba."},
    )

    assert respuesta.status_code == 403


def test_solicitud_inexistente_devuelve_404(client, escenario):
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{uuid.uuid4()}/resolve",
        json={"solucion": "Solución de prueba."},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_NO_ENCONTRADA"


@pytest.mark.parametrize(
    "estado",
    ["registrado", "en_evaluacion", "asignado", "resuelto", "cerrado"],
)
def test_no_permite_resolver_desde_estados_no_validos(
    client, db, escenario, estado
):
    solicitud = crear_solicitud(
        db,
        escenario["solicitante"],
        escenario["tecnico"],
        estado=estado,
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": "Solución de prueba."},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "TRANSICION_NO_PERMITIDA"

    db.refresh(solicitud)
    assert solicitud.estado == estado
    assert solicitud.solucion_final is None


@pytest.mark.parametrize("solucion", ["", "   ", "\n\t"])
def test_no_permite_solucion_vacia(client, db, escenario, solucion):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": solucion},
    )

    assert respuesta.status_code == 422

    db.refresh(solicitud)
    assert solicitud.estado == "en_atencion"
    assert solicitud.solucion_final is None


def test_no_permite_resolver_sin_asignacion_activa(
    client, db, escenario
):
    solicitud = crear_solicitud(
        db, escenario["solicitante"], escenario["tecnico"]
    )

    asignacion = db.scalar(
        select(Asignacion).where(
            Asignacion.solicitud_id == solicitud.id
        )
    )
    asignacion.fecha_finalizacion = solicitud.fecha_creacion
    db.commit()

    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/resolve",
        json={"solucion": "Solución de prueba."},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"
