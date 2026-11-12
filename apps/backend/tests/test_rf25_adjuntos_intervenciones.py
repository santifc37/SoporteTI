import uuid
from io import BytesIO

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import select, create_engine
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
    Intervencion,
    Solicitud,
    Usuario,
)
from app.services.adjuntos import ErrorImagen, convertir_a_webp


URL = "/api/v1/requests"


# ============================================================
# PRUEBAS DE CONVERSIÓN DE IMÁGENES
# ============================================================

def crear_imagen(formato="PNG", dimensiones=(800, 600)):
    imagen = Image.new("RGB", dimensiones, "red")
    buffer = BytesIO()
    imagen.save(buffer, format=formato)
    return buffer.getvalue()


def test_imagen_png_se_convierte_a_webp():
    resultado = convertir_a_webp(crear_imagen("PNG"))

    imagen = Image.open(BytesIO(resultado))

    assert imagen.format == "WEBP"
    assert imagen.size == (800, 600)


def test_imagen_grande_se_redimensiona_sin_deformarse():
    resultado = convertir_a_webp(
        crear_imagen("PNG", (2400, 1600))
    )

    imagen = Image.open(BytesIO(resultado))

    assert imagen.format == "WEBP"
    assert imagen.size == (1920, 1280)


def test_imagen_jpeg_se_convierte_a_webp():
    resultado = convertir_a_webp(crear_imagen("JPEG"))

    imagen = Image.open(BytesIO(resultado))

    assert imagen.format == "WEBP"


def test_archivo_no_imagen_es_rechazado_conversion():
    with pytest.raises(ErrorImagen):
        convertir_a_webp(b"esto no es una imagen")


def test_archivo_vacio_es_rechazado():
    with pytest.raises(ErrorImagen):
        convertir_a_webp(b"")


def test_archivo_superior_a_10_mb_es_rechazado():
    contenido = b"x" * (10 * 1024 * 1024 + 1)

    with pytest.raises(ErrorImagen):
        convertir_a_webp(contenido)


# ============================================================
# FIXTURES Y DATOS DE PRUEBA
# ============================================================

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
    solicitante = crear_usuario(db, "solicitante", "Juan")
    tecnico = crear_usuario(db, "tecnico", "Carlos")
    otro_tecnico = crear_usuario(db, "tecnico", "Luis")

    solicitud = crear_solicitud(
        db,
        solicitante,
        tecnico,
    )

    intervencion = Intervencion(
        solicitud_id=solicitud.id,
        tecnico_id=tecnico.id,
        descripcion="Se realizó mantenimiento.",
    )

    db.add(intervencion)
    db.commit()

    return {
        "solicitante": solicitante,
        "tecnico": tecnico,
        "otro_tecnico": otro_tecnico,
        "solicitud": solicitud,
        "intervencion": intervencion,
    }


def crear_archivo_png():
    imagen = Image.new("RGB", (800, 600), "red")
    buffer = BytesIO()

    imagen.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


# ============================================================
# PRUEBAS DEL ENDPOINT DE ADJUNTOS
# ============================================================

def test_tecnico_asignado_puede_adjuntar_imagen(
    client, db, escenario, monkeypatch
):
    from app.services import adjuntos

    contenido_subido = {}

    def simular_subida(ruta, contenido):
        contenido_subido["ruta"] = ruta
        contenido_subido["contenido"] = contenido

    monkeypatch.setattr(
        adjuntos,
        "subir_a_storage",
        simular_subida,
    )

    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/interventions/"
        f"{escenario['intervencion'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_archivo_png(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 201

    cuerpo = respuesta.json()

    assert cuerpo["adjunto"]["solicitud_id"] == str(
        escenario["solicitud"].id
    )
    assert cuerpo["adjunto"]["nombre_archivo"] == "evidencia.png"
    assert cuerpo["adjunto"]["tipo_archivo"] == "image/webp"

    imagen_convertida = Image.open(
        BytesIO(contenido_subido["contenido"])
    )

    assert imagen_convertida.format == "WEBP"

    adjunto = db.scalar(select(Adjunto))

    assert adjunto is not None
    assert adjunto.intervencion_id == escenario["intervencion"].id
    assert adjunto.subido_por == escenario["tecnico"].id


def test_tecnico_no_asignado_no_puede_adjuntar_imagen(
    client, escenario
):
    como(escenario["otro_tecnico"])

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/interventions/"
        f"{escenario['intervencion'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_archivo_png(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_solicitud_cerrada_no_admite_adjuntos(
    client, db, escenario
):
    escenario["solicitud"].estado = "cerrado"
    db.commit()

    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/interventions/"
        f"{escenario['intervencion'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_archivo_png(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


def test_archivo_no_imagen_es_rechazado_endpoint(
    client, escenario
):
    como(escenario["tecnico"])

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/interventions/"
        f"{escenario['intervencion'].id}/attachments",
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


@pytest.mark.parametrize(
    "rol",
    ["solicitante", "coordinador"],
)
def test_otros_roles_no_pueden_adjuntar_imagen(
    client, db, escenario, rol
):
    usuario = crear_usuario(
        db,
        rol,
        f"Usuario {rol}",
    )

    como(usuario)

    respuesta = client.post(
        f"{URL}/{escenario['solicitud'].id}/interventions/"
        f"{escenario['intervencion'].id}/attachments",
        files={
            "archivo": (
                "evidencia.png",
                crear_archivo_png(),
                "image/png",
            )
        },
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"