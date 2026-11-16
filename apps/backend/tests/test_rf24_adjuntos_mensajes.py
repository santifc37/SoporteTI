
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
from app.models import (
    Adjunto,
    Asignacion,
    Base,
    Mensaje,
    Solicitud,
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
        correo=f"{uuid.uuid4().hex}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


@pytest.fixture()
def escenario(db):
    solicitante = crear_usuario(db, "solicitante", "Laura")
    tecnico = crear_usuario(db, "tecnico", "Carlos")
    otro = crear_usuario(db, "solicitante", "Pedro")
    coordinador = crear_usuario(db, "coordinador", "Marta")

    solicitud = Solicitud(
        numero=f"ST-{uuid.uuid4().hex[:6]}",
        titulo="Solicitud de prueba",
        descripcion="Descripción",
        tipo="incidente",
        solicitante_id=solicitante.id,
        ubicacion="Oficina",
        medio_contacto="correo",
        dato_contacto="laura@test.com",
        estado="en_atencion",
        version=1,
    )
    db.add(solicitud)
    db.commit()

    db.add(
        Asignacion(
            solicitud_id=solicitud.id,
            tecnico_id=tecnico.id,
            asignado_por=coordinador.id,
        )
    )

    mensaje = Mensaje(
        solicitud_id=solicitud.id,
        remitente_id=solicitante.id,
        contenido="El equipo no enciende.",
    )
    db.add(mensaje)
    db.commit()

    otro_mensaje = Mensaje(
        solicitud_id=solicitud.id,
        remitente_id=tecnico.id,
        contenido="Voy a revisar el equipo.",
    )
    db.add(otro_mensaje)
    db.commit()

    otra_solicitud = Solicitud(
        numero=f"ST-{uuid.uuid4().hex[:6]}",
        titulo="Otra solicitud",
        descripcion="Otra descripción",
        tipo="incidente",
        solicitante_id=solicitante.id,
        ubicacion="Oficina",
        medio_contacto="correo",
        dato_contacto="laura@test.com",
        estado="en_atencion",
        version=1,
    )
    db.add(otra_solicitud)
    db.commit()

    mensaje_otra_solicitud = Mensaje(
        solicitud_id=otra_solicitud.id,
        remitente_id=solicitante.id,
        contenido="Mensaje de otra solicitud.",
    )
    db.add(mensaje_otra_solicitud)
    db.commit()

    return {
        "solicitante": solicitante,
        "tecnico": tecnico,
        "otro": otro,
        "coordinador": coordinador,
        "solicitud": solicitud,
        "mensaje": mensaje,
        "otro_mensaje": otro_mensaje,
        "otra_solicitud": otra_solicitud,
        "mensaje_otra_solicitud": mensaje_otra_solicitud,
    }


def imagen_png():
    imagen = Image.new("RGB", (800, 600), "red")
    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def subir(client, escenario, mensaje=None):
    mensaje = mensaje or escenario["mensaje"]
    return client.post(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{mensaje.id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                imagen_png(),
                "image/png",
            )
        },
    )


def test_participante_puede_adjuntar_imagen_webp(
    client, db, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    subidas = {}

    def simular_subida(ruta, contenido):
        subidas["ruta"] = ruta
        subidas["contenido"] = contenido

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        simular_subida,
    )

    como(escenario["solicitante"])
    respuesta = subir(client, escenario)

    assert respuesta.status_code == 201
    dato = respuesta.json()["adjunto"]

    assert dato["mensaje_id"] == str(escenario["mensaje"].id)
    assert dato["solicitud_id"] == str(escenario["solicitud"].id)
    assert dato["tipo_archivo"] == "image/webp"

    imagen = Image.open(BytesIO(subidas["contenido"]))
    assert imagen.format == "WEBP"

    adjunto = db.scalar(select(Adjunto))
    assert adjunto is not None
    assert adjunto.mensaje_id == escenario["mensaje"].id
    assert adjunto.solicitud_id == escenario["solicitud"].id
    assert adjunto.intervencion_id is None
    assert adjunto.subido_por == escenario["solicitante"].id


def test_tecnico_asignado_puede_adjuntar(
    client, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["tecnico"])
    respuesta = subir(client, escenario)

    assert respuesta.status_code == 201


def test_coordinador_puede_adjuntar(
    client, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["coordinador"])
    assert subir(client, escenario).status_code == 201


def test_usuario_ajeno_no_puede_adjuntar(
    client, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["otro"])
    respuesta = subir(client, escenario)

    assert respuesta.status_code == 403


def test_tecnico_no_asignado_no_puede_adjuntar(
    client, db, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    otro_tecnico = crear_usuario(db, "tecnico", "Andres")

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(otro_tecnico)
    assert subir(client, escenario).status_code == 403


def test_no_se_puede_adjuntar_a_solicitud_cerrada(
    client, db, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    escenario["solicitud"].estado = "cerrado"
    db.commit()

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["solicitante"])
    respuesta = subir(client, escenario)

    assert respuesta.status_code == 409


def test_no_acepta_archivo_que_no_es_imagen(
    client, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["solicitante"])

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{escenario['mensaje'].id}/attachments",
        files={
            "archivo": (
                "archivo.txt",
                b"Esto no es una imagen",
                "text/plain",
            )
        },
    )

    assert respuesta.status_code == 422


def test_no_acepta_archivo_superior_a_10_mb(
    client, escenario
):
    como(escenario["solicitante"])

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{escenario['mensaje'].id}/attachments",
        files={
            "archivo": (
                "grande.png",
                b"x" * (10 * 1024 * 1024 + 1),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 422


def test_mensaje_de_otra_solicitud_no_se_puede_usar(
    client, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["solicitante"])

    respuesta = subir(
        client,
        escenario,
        escenario["mensaje_otra_solicitud"],
    )

    assert respuesta.status_code == 404



def test_consultar_adjuntos_del_mensaje(
    client, escenario, monkeypatch
):
    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    # Simula la URL firmada porque la subida también está simulada.
    from app.services import adjuntos

    monkeypatch.setattr(
        adjuntos,
        "crear_url_firmada",
        lambda ruta: f"https://storage.test/{ruta}",
    )

    como(escenario["solicitante"])
    assert subir(client, escenario).status_code == 201

    respuesta = client.get(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{escenario['mensaje'].id}/attachments"
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 1
    assert respuesta.json()["data"][0]["mensaje_id"] == str(
        escenario["mensaje"].id
    )

    from app.services import adjuntos_mensajes

    monkeypatch.setattr(
        adjuntos_mensajes,
        "subir_a_storage",
        lambda ruta, contenido: None,
    )

    como(escenario["solicitante"])
    assert subir(client, escenario).status_code == 201

    respuesta = client.get(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{escenario['mensaje'].id}/attachments"
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()["data"]) == 1
    assert respuesta.json()["data"][0]["mensaje_id"] == str(
        escenario["mensaje"].id
    )


def test_no_consulta_adjuntos_de_usuario_ajeno(
    client, escenario
):
    como(escenario["otro"])

    respuesta = client.get(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{escenario['mensaje'].id}/attachments"
    )

    assert respuesta.status_code == 403


def test_mensaje_inexistente_devuelve_404(
    client, escenario
):
    como(escenario["solicitante"])

    respuesta = client.get(
        f"{URL}/{escenario['solicitud'].id}/messages/"
        f"{uuid.uuid4()}/attachments"
    )

    assert respuesta.status_code == 404
