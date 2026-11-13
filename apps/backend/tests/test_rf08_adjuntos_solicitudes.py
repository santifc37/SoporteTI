
import uuid
from io import BytesIO

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Adjunto, Asignacion, Base, Solicitud, Usuario


URL = "/api/v1"


def crear_imagen():
    imagen = Image.new("RGB", (800, 600), "red")
    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


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


@pytest.fixture()
def escenario(db):
    solicitante = crear_usuario(db, "solicitante", "Juan")
    tecnico = crear_usuario(db, "tecnico", "Carlos")
    otro_tecnico = crear_usuario(db, "tecnico", "Luis")
    coordinador = crear_usuario(db, "coordinador", "Ana")

    solicitud = Solicitud(
        numero=f"ST-{uuid.uuid4().hex[:6]}",
        titulo="Solicitud de prueba",
        descripcion="Descripción de prueba",
        tipo="incidente",
        solicitante_id=solicitante.id,
        ubicacion="Oficina",
        medio_contacto="correo",
        dato_contacto="prueba@test.com",
        estado="asignado",
    )
    db.add(solicitud)
    db.commit()

    asignacion = Asignacion(
        solicitud_id=solicitud.id,
        tecnico_id=tecnico.id,
        asignado_por=coordinador.id,
    )
    db.add(asignacion)
    db.commit()

    return {
        "solicitante": solicitante,
        "tecnico": tecnico,
        "otro_tecnico": otro_tecnico,
        "coordinador": coordinador,
        "solicitud": solicitud,
    }


def simular_subida(monkeypatch):
    from app.services import adjuntos_solicitudes

    contenido = {}

    def subir(ruta, archivo):
        contenido["ruta"] = ruta
        contenido["archivo"] = archivo

    monkeypatch.setattr(
        adjuntos_solicitudes,
        "subir_a_storage",
        subir,
    )

    return contenido


def test_solicitante_propietario_puede_adjuntar_imagen(
    client, db, escenario, monkeypatch
):
    contenido_subido = simular_subida(monkeypatch)
    como(escenario["solicitante"])

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["mensaje"] == "Archivo adjuntado correctamente"
    assert respuesta.json()["adjunto"]["tipo_archivo"] == "image/webp"

    imagen = Image.open(BytesIO(contenido_subido["archivo"]))
    assert imagen.format == "WEBP"

    adjunto = db.scalar(select(Adjunto))
    assert adjunto is not None
    assert adjunto.solicitud_id == escenario["solicitud"].id
    assert adjunto.intervencion_id is None
    assert adjunto.mensaje_id is None
    assert adjunto.subido_por == escenario["solicitante"].id


def test_tecnico_asignado_puede_adjuntar_imagen(
    client, escenario, monkeypatch
):
    simular_subida(monkeypatch)
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 201


def test_coordinador_puede_adjuntar_imagen(
    client, escenario, monkeypatch
):
    simular_subida(monkeypatch)
    como(escenario["coordinador"])

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 201


def test_tecnico_no_asignado_no_puede_adjuntar(
    client, escenario
):
    como(escenario["otro_tecnico"])

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 403


def test_solicitante_no_propietario_no_puede_adjuntar(
    client, db, escenario
):
    otro_solicitante = crear_usuario(
        db,
        "solicitante",
        "Pedro",
    )
    como(otro_solicitante)

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 403


def test_solicitud_cerrada_no_admite_adjuntos(
    client, db, escenario
):
    escenario["solicitud"].estado = "cerrado"
    db.commit()

    como(escenario["solicitante"])

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


def test_archivo_que_no_es_imagen_es_rechazado(
    client, escenario
):
    como(escenario["solicitante"])

    respuesta = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "documento.txt",
                BytesIO(b"esto no es una imagen"),
                "text/plain",
            )
        },
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "IMAGEN_NO_VALIDA"


def test_consultar_adjuntos_de_solicitud(
    client, db, escenario, monkeypatch
):
    simular_subida(monkeypatch)
    como(escenario["solicitante"])

    subida = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    assert subida.status_code == 201

    consulta = client.get(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments"
    )

    assert consulta.status_code == 200
    assert len(consulta.json()["data"]) == 1
    assert consulta.json()["data"][0]["nombre_archivo"] == "evidencia.png"


def test_consultar_adjuntos_sin_permiso_es_rechazado(
    client, escenario
):
    como(escenario["otro_tecnico"])

    respuesta = client.get(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments"
    )

    assert respuesta.status_code == 403


def test_descargar_adjunto(
    client, db, escenario, monkeypatch
):
    simular_subida(monkeypatch)
    como(escenario["solicitante"])

    subida = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    adjunto_id = subida.json()["adjunto"]["id"]

    class RespuestaStorage:
        content = b"contenido-webp"

        @staticmethod
        def raise_for_status():
            return None

    from app.services import adjuntos_solicitudes

    monkeypatch.setattr(
        adjuntos_solicitudes,
        "_obtener_configuracion_storage",
        lambda: ("https://ejemplo.supabase.co", "clave-prueba", "adjuntos"),
    )
    monkeypatch.setattr(
        adjuntos_solicitudes.httpx,
        "get",
        lambda *args, **kwargs: RespuestaStorage(),
    )

    respuesta = client.get(
        f"{URL}/attachments/{adjunto_id}/download"
    )

    assert respuesta.status_code == 200
    assert respuesta.content == b"contenido-webp"
    assert respuesta.headers["content-type"] == "image/webp"


def test_descargar_adjunto_sin_permiso_es_rechazado(
    client, db, escenario, monkeypatch
):
    simular_subida(monkeypatch)
    como(escenario["solicitante"])

    subida = client.post(
        f"{URL}/requests/{escenario['solicitud'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_imagen(),
                "image/png",
            )
        },
    )

    adjunto_id = subida.json()["adjunto"]["id"]

    como(escenario["otro_tecnico"])

    respuesta = client.get(
        f"{URL}/attachments/{adjunto_id}/download"
    )

    assert respuesta.status_code == 403
