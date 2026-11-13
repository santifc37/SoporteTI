
"""Pruebas de RF-04: cambio y restablecimiento de contraseñas."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.config import SESSION_COOKIE_NAME
from app.core.security import hash_password, verify_password
from app.database.session import get_db
from app.main import app
from app.models import Base, Sesion, Usuario

AUTH = "/api/v1/auth"
USERS = "/api/v1/users"
CONTRASENA = "Contrasena123"
TEMPORAL = "Temporal123"


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


def nuevo_usuario(db, rol="solicitante", correo=None):
    usuario = Usuario(
        nombre="Ana",
        apellido="Ruiz",
        correo=correo or f"{uuid.uuid4().hex}@organizacion.com",
        password_hash=hash_password(CONTRASENA),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def como(usuario):
    app.dependency_overrides[get_current_user] = lambda: UsuarioActual(
        id=usuario.id,
        rol=usuario.rol,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        activo=usuario.activo,
        sesion_id=uuid.uuid4(),
    )


def crear_sesion(db, usuario):
    sesion = Sesion(
        usuario_id=usuario.id,
        token_hash=uuid.uuid4().hex + uuid.uuid4().hex,
        fecha_expiracion=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(sesion)
    db.commit()
    return sesion


def login(client, usuario, contrasena=CONTRASENA):
    return client.post(
        f"{AUTH}/login",
        json={"correo": usuario.correo, "contrasena": contrasena},
    )


# ----------------------------- cambio de contraseña --------------------------


def test_usuario_cambia_su_contrasena_correctamente(client, db):
    usuario = nuevo_usuario(db, "tecnico")
    assert login(client, usuario).status_code == 200

    respuesta = client.post(
        f"{AUTH}/change-password",
        json={
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "NuevaClave123",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Contraseña actualizada correctamente"
    }

    db.refresh(usuario)
    assert verify_password("NuevaClave123", usuario.password_hash)
    assert not verify_password(CONTRASENA, usuario.password_hash)

    # La sesión actual continúa activa.
    assert client.get(f"{AUTH}/me").status_code == 200


def test_cambiar_contrasena_revoca_las_otras_sesiones(client, db):
    usuario = nuevo_usuario(db, "tecnico")
    otra_sesion = crear_sesion(db, usuario)

    assert login(client, usuario).status_code == 200

    respuesta = client.post(
        f"{AUTH}/change-password",
        json={
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "NuevaClave123",
        },
    )

    assert respuesta.status_code == 200
    db.refresh(otra_sesion)
    assert otra_sesion.revocada is True


def test_contrasena_anterior_deja_de_permitir_el_login(client, db):
    usuario = nuevo_usuario(db)

    assert login(client, usuario).status_code == 200
    client.post(
        f"{AUTH}/change-password",
        json={
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "NuevaClave123",
        },
    )

    otro_cliente = TestClient(app)
    assert login(otro_cliente, usuario, CONTRASENA).status_code == 401
    assert login(otro_cliente, usuario, "NuevaClave123").status_code == 200


def test_contrasena_actual_incorrecta_no_modifica_el_hash(client, db):
    usuario = nuevo_usuario(db)
    assert login(client, usuario).status_code == 200
    hash_original = usuario.password_hash

    respuesta = client.post(
        f"{AUTH}/change-password",
        json={
            "contrasena_actual": "Incorrecta123",
            "contrasena_nueva": "NuevaClave123",
        },
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "CONTRASENA_ACTUAL_INCORRECTA"
    db.refresh(usuario)
    assert usuario.password_hash == hash_original


def test_cambiar_contrasena_sin_sesion_devuelve_401(client):
    respuesta = client.post(
        f"{AUTH}/change-password",
        json={
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "NuevaClave123",
        },
    )

    assert respuesta.status_code == 401


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"contrasena_actual": CONTRASENA},
        {"contrasena_nueva": "NuevaClave123"},
        {
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "corta",
        },
        {
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": CONTRASENA,
        },
        {
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "NuevaClave123",
            "rol": "coordinador",
        },
    ],
)
def test_cambio_rechaza_datos_invalidos(client, db, cuerpo):
    usuario = nuevo_usuario(db)
    assert login(client, usuario).status_code == 200

    respuesta = client.post(f"{AUTH}/change-password", json=cuerpo)

    assert respuesta.status_code == 422


def test_respuesta_de_cambio_no_expone_contrasenas_ni_hash(client, db):
    usuario = nuevo_usuario(db)
    assert login(client, usuario).status_code == 200

    respuesta = client.post(
        f"{AUTH}/change-password",
        json={
            "contrasena_actual": CONTRASENA,
            "contrasena_nueva": "NuevaClave123",
        },
    )

    assert CONTRASENA not in respuesta.text
    assert "NuevaClave123" not in respuesta.text
    assert usuario.password_hash not in respuesta.text


# -------------------------- restablecimiento de contraseña -------------------


def test_coordinador_restablece_contrasena_de_usuario(client, db):
    coordinador = nuevo_usuario(db, "coordinador")
    usuario = nuevo_usuario(db, "tecnico")
    como(coordinador)

    respuesta = client.post(
        f"{USERS}/{usuario.id}/reset-password",
        json={"contrasena_temporal": TEMPORAL},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Contraseña restablecida correctamente"
    }

    db.refresh(usuario)
    assert verify_password(TEMPORAL, usuario.password_hash)
    assert not verify_password(CONTRASENA, usuario.password_hash)


def test_restablecimiento_revoca_todas_las_sesiones(client, db):
    coordinador = nuevo_usuario(db, "coordinador")
    usuario = nuevo_usuario(db, "tecnico")
    primera = crear_sesion(db, usuario)
    segunda = crear_sesion(db, usuario)
    como(coordinador)

    respuesta = client.post(
        f"{USERS}/{usuario.id}/reset-password",
        json={"contrasena_temporal": TEMPORAL},
    )

    assert respuesta.status_code == 200
    db.refresh(primera)
    db.refresh(segunda)
    assert primera.revocada is True
    assert segunda.revocada is True


@pytest.mark.parametrize("rol", ["tecnico", "solicitante"])
def test_usuario_no_coordinador_no_puede_restablecer_contrasena(
    client, db, rol
):
    actor = nuevo_usuario(db, rol)
    objetivo = nuevo_usuario(db, "tecnico")
    hash_original = objetivo.password_hash
    como(actor)

    respuesta = client.post(
        f"{USERS}/{objetivo.id}/reset-password",
        json={"contrasena_temporal": TEMPORAL},
    )

    assert respuesta.status_code == 403
    db.refresh(objetivo)
    assert objetivo.password_hash == hash_original


def test_restablecer_sin_sesion_devuelve_401(client, db):
    usuario = nuevo_usuario(db, "tecnico")

    respuesta = client.post(
        f"{USERS}/{usuario.id}/reset-password",
        json={"contrasena_temporal": TEMPORAL},
    )

    assert respuesta.status_code == 401


def test_restablecer_usuario_inexistente_devuelve_404(client, db):
    coordinador = nuevo_usuario(db, "coordinador")
    como(coordinador)

    respuesta = client.post(
        f"{USERS}/{uuid.uuid4()}/reset-password",
        json={"contrasena_temporal": TEMPORAL},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"contrasena_temporal": "corta"},
        {"contrasena_temporal": TEMPORAL, "rol": "coordinador"},
    ],
)
def test_restablecer_rechaza_datos_invalidos(client, db, cuerpo):
    coordinador = nuevo_usuario(db, "coordinador")
    usuario = nuevo_usuario(db, "tecnico")
    como(coordinador)

    respuesta = client.post(
        f"{USERS}/{usuario.id}/reset-password",
        json=cuerpo,
    )

    assert respuesta.status_code == 422


def test_respuesta_de_restablecimiento_no_expone_contrasena_ni_hash(
    client, db
):
    coordinador = nuevo_usuario(db, "coordinador")
    usuario = nuevo_usuario(db, "tecnico")
    como(coordinador)

    respuesta = client.post(
        f"{USERS}/{usuario.id}/reset-password",
        json={"contrasena_temporal": TEMPORAL},
    )

    assert TEMPORAL not in respuesta.text
    assert usuario.password_hash not in respuesta.text
    assert "password_hash" not in respuesta.text
