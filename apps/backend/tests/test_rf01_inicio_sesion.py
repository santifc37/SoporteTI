"""Pruebas de RF-01 (inicio y cierre de sesión) y RNF-04 (hash de contraseñas).

Usan SQLite en memoria; no tocan Supabase.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import SESSION_COOKIE_NAME
from app.core.security import (
    hash_password,
    hash_session_token,
    password_needs_rehash,
    verify_password,
)
from app.database.session import get_db
from app.main import app
from app.models import Base, Sesion, Usuario

LOGIN = "/api/v1/auth/login"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/auth/me"
CONTRASENA = "Contrasena123"


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


@pytest.fixture()
def usuario(db):
    u = Usuario(
        nombre="Juan",
        apellido="Pérez",
        correo="Juan@Organizacion.com",
        password_hash=hash_password(CONTRASENA),
        rol="tecnico",
    )
    db.add(u)
    db.commit()
    return u


def iniciar(client, correo="juan@organizacion.com", contrasena=CONTRASENA):
    return client.post(LOGIN, json={"correo": correo, "contrasena": contrasena})


# ----------------------------- inicio de sesión ------------------------------


def test_login_correcto_devuelve_usuario_y_cookie(client, usuario):
    respuesta = iniciar(client)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Inicio de sesión exitoso"
    assert cuerpo["usuario"] == {
        "id": str(usuario.id),
        "nombre": "Juan",
        "apellido": "Pérez",
        "correo": "Juan@Organizacion.com",
        "rol": "tecnico",
    }
    assert SESSION_COOKIE_NAME in respuesta.cookies


def test_la_respuesta_no_expone_contrasena_ni_hash(client, usuario):
    texto = iniciar(client).text

    assert CONTRASENA not in texto
    assert "password" not in texto
    assert usuario.password_hash not in texto


def test_cookie_es_httponly_con_samesite_y_duracion(client, usuario):
    cabecera = iniciar(client).headers["set-cookie"].lower()

    assert "httponly" in cabecera
    assert "samesite=lax" in cabecera
    assert "max-age=28800" in cabecera  # 8 horas por defecto
    assert "secure" not in cabecera  # solo con SESSION_COOKIE_SECURE=true


def test_cookie_secure_se_activa_por_configuracion(client, usuario, monkeypatch):
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")

    assert "secure" in iniciar(client).headers["set-cookie"].lower()


def test_en_la_base_solo_se_guarda_el_hash_del_token(client, db, usuario):
    token = iniciar(client).cookies[SESSION_COOKIE_NAME]

    sesion = db.scalar(select(Sesion))
    assert sesion.token_hash != token
    assert sesion.token_hash == hash_session_token(token)
    assert len(sesion.token_hash) == 64
    assert sesion.usuario_id == usuario.id
    assert sesion.revocada is False


def test_el_correo_no_distingue_mayusculas(client, usuario):
    assert iniciar(client, correo="  JUAN@ORGANIZACION.COM ").status_code == 200


def test_contrasena_incorrecta_devuelve_401(client, usuario):
    respuesta = iniciar(client, contrasena="otra")

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"
    assert SESSION_COOKIE_NAME not in respuesta.cookies


def test_correo_inexistente_da_el_mismo_error_que_contrasena_incorrecta(client, usuario):
    inexistente = iniciar(client, correo="nadie@organizacion.com")
    incorrecta = iniciar(client, contrasena="otra")

    assert inexistente.status_code == incorrecta.status_code == 401
    assert inexistente.json() == incorrecta.json()


def test_cuenta_desactivada_no_puede_iniciar_sesion(client, db, usuario):
    usuario.activo = False
    db.commit()

    respuesta = iniciar(client)

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "USUARIO_INACTIVO"
    assert db.scalar(select(Sesion)) is None


def test_cuenta_desactivada_con_contrasena_incorrecta_no_revela_su_estado(client, db, usuario):
    usuario.activo = False
    db.commit()

    respuesta = iniciar(client, contrasena="otra")

    assert respuesta.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


@pytest.mark.parametrize("cuerpo", [{}, {"correo": "a@b.com"}, {"contrasena": "x"}])
def test_login_con_campos_faltantes_devuelve_422(client, cuerpo):
    assert client.post(LOGIN, json=cuerpo).status_code == 422


# ----------------------------- usuario autenticado ---------------------------


def test_me_con_sesion_valida(client, usuario):
    iniciar(client)

    respuesta = client.get(ME)

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["correo"] == "Juan@Organizacion.com"
    assert respuesta.json()["usuario"]["activo"] is True


def test_me_sin_sesion_devuelve_401(client):
    respuesta = client.get(ME)

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "SESION_NO_VALIDA"


def test_me_con_token_inventado_devuelve_401(client, usuario):
    client.cookies.set(SESSION_COOKIE_NAME, "token-inventado")

    assert client.get(ME).status_code == 401


def test_sesion_vencida_devuelve_401(client, db, usuario):
    iniciar(client)
    sesion = db.scalar(select(Sesion))
    sesion.fecha_expiracion = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()

    assert client.get(ME).status_code == 401


def test_sesion_revocada_devuelve_401(client, db, usuario):
    iniciar(client)
    sesion = db.scalar(select(Sesion))
    sesion.revocada = True
    db.commit()

    assert client.get(ME).status_code == 401


def test_desactivar_la_cuenta_invalida_la_sesion_abierta(client, db, usuario):
    iniciar(client)
    usuario.activo = False
    db.commit()

    respuesta = client.get(ME)

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "USUARIO_INACTIVO"


# ------------------------------ cierre de sesión -----------------------------


def test_logout_revoca_la_sesion_aunque_se_reutilice_el_token(client, db, usuario):
    token = iniciar(client).cookies[SESSION_COOKIE_NAME]

    respuesta = client.post(LOGOUT)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"mensaje": "Sesión cerrada correctamente"}
    assert db.scalar(select(Sesion)).revocada is True

    # Aunque alguien conserve el token, ya no sirve.
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE_NAME, token)
    assert client.get(ME).status_code == 401


def test_logout_elimina_la_cookie(client, usuario):
    iniciar(client)

    cabecera = client.post(LOGOUT).headers["set-cookie"].lower()

    assert SESSION_COOKIE_NAME in cabecera
    assert "max-age=0" in cabecera


def test_logout_sin_sesion_devuelve_401(client):
    assert client.post(LOGOUT).status_code == 401


def test_cerrar_una_sesion_no_afecta_a_las_otras(client, db, usuario):
    primera = TestClient(app)
    iniciar(primera)
    iniciar(client)

    client.post(LOGOUT)

    assert primera.get(ME).status_code == 200


# ----------------------- hash de contraseñas y tokens (RNF-04) ---------------


def test_el_hash_no_es_la_contrasena_y_es_distinto_cada_vez():
    primero, segundo = hash_password(CONTRASENA), hash_password(CONTRASENA)

    assert CONTRASENA not in primero
    assert primero.startswith("$argon2id$")
    assert primero != segundo


def test_verificar_contrasena():
    hash_guardado = hash_password(CONTRASENA)

    assert verify_password(CONTRASENA, hash_guardado) is True
    assert verify_password("otra", hash_guardado) is False
    assert verify_password(CONTRASENA, "no-es-un-hash") is False
    assert password_needs_rehash(hash_guardado) is False


def test_hash_del_token_es_determinista():
    assert hash_session_token("abc") == hash_session_token("abc")
    assert hash_session_token("abc") != hash_session_token("abd")


def test_cada_login_genera_un_token_distinto(client, usuario):
    primero = iniciar(client).cookies[SESSION_COOKIE_NAME]
    segundo = iniciar(TestClient(app)).cookies[SESSION_COOKIE_NAME]

    assert primero != segundo
    assert uuid.UUID(str(usuario.id))  # el id sigue siendo un UUID válido
