"""Pruebas de RF-03 (gestión de usuarios) y RF-05 (datos de contacto).

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`,
igual que en las pruebas de RF-13; una prueba usa el login real de punta a punta.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Table, Uuid, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password, verify_password
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Sesion, Usuario

URL = "/api/v1/users"
CONTRASENA = "Contrasena123"

# `asignaciones` tiene una clave foránea a `solicitudes`. Si el modelo Solicitud
# todavía no existe en esta rama, se registra una tabla mínima solo para que
# SQLite pueda crear el esquema de prueba.
if "solicitudes" not in Base.metadata.tables:
    Table("solicitudes", Base.metadata, Column("id", Uuid, primary_key=True))


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


def nuevo_usuario(db, rol="solicitante", correo=None, **extra) -> Usuario:
    u = Usuario(
        nombre=extra.pop("nombre", "Ana"),
        apellido=extra.pop("apellido", "Ruiz"),
        correo=correo or f"{uuid.uuid4().hex[:8]}@organizacion.com",
        password_hash=hash_password(CONTRASENA),
        rol=rol,
        **extra,
    )
    db.add(u)
    db.commit()
    return u


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
def coordinador(db):
    return nuevo_usuario(db, "coordinador", "coordinador@organizacion.com")


def datos_nuevo(**cambios):
    datos = {
        "nombre": "Carlos",
        "apellido": "Gómez",
        "correo": "carlos@organizacion.com",
        "contrasena": CONTRASENA,
        "rol": "tecnico",
        "medio_contacto_preferido": "correo",
        "telefono": "3001234567",
    }
    datos.update(cambios)
    return datos


# --------------------------------- permisos ----------------------------------


def test_sin_sesion_devuelve_401(client):
    assert client.get(URL).status_code == 401
    assert client.post(URL, json=datos_nuevo()).status_code == 401


@pytest.mark.parametrize("rol", ["solicitante", "tecnico"])
def test_solo_el_coordinador_administra_usuarios(client, db, rol):
    otro = nuevo_usuario(db, rol)
    como(otro)

    for respuesta in (
        client.get(URL),
        client.get(f"{URL}/{otro.id}"),
        client.post(URL, json=datos_nuevo()),
    ):
        assert respuesta.status_code == 403
        assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    assert db.scalar(select(Usuario).where(Usuario.correo == "carlos@organizacion.com")) is None


# ---------------------------------- crear ------------------------------------


def test_coordinador_crea_usuario(client, db, coordinador):
    como(coordinador)

    respuesta = client.post(URL, json=datos_nuevo())

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Usuario creado correctamente"
    assert cuerpo["usuario"]["rol"] == "tecnico"
    assert cuerpo["usuario"]["activo"] is True
    creado = db.get(Usuario, uuid.UUID(cuerpo["usuario"]["id"]))
    assert creado.telefono == "3001234567"
    assert verify_password(CONTRASENA, creado.password_hash)


def test_la_respuesta_no_expone_contrasena_ni_hash(client, coordinador):
    como(coordinador)

    texto = client.post(URL, json=datos_nuevo()).text

    assert CONTRASENA not in texto
    assert "password" not in texto
    assert "contrasena" not in texto


def test_correo_duplicado_sin_importar_mayusculas(client, coordinador):
    como(coordinador)
    client.post(URL, json=datos_nuevo())

    respuesta = client.post(URL, json=datos_nuevo(correo="  CARLOS@Organizacion.com "))

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CORREO_DUPLICADO"


@pytest.mark.parametrize(
    "cambio",
    [
        {"rol": "administrador"},
        {"correo": "no-es-un-correo"},
        {"contrasena": "corta"},
        {"nombre": "   "},
        {"medio_contacto_preferido": "telefono", "telefono": None},
        {"medio_contacto_preferido": "whatsapp"},
        {"telefono": "abc"},
        {"password_hash": "x"},  # campo no permitido
    ],
)
def test_crear_con_datos_invalidos_devuelve_422_y_no_guarda(client, db, coordinador, cambio):
    como(coordinador)

    respuesta = client.post(URL, json=datos_nuevo(**cambio))

    assert respuesta.status_code == 422
    assert db.scalar(select(Usuario).where(Usuario.rol == "tecnico")) is None


def test_crear_sin_campos_obligatorios_devuelve_422(client, coordinador):
    como(coordinador)

    assert client.post(URL, json={"nombre": "Solo nombre"}).status_code == 422


# --------------------------------- consultar ---------------------------------


def test_listar_con_paginacion(client, db, coordinador):
    for i in range(3):
        nuevo_usuario(db, "tecnico", apellido=f"Tecnico{i}")
    como(coordinador)

    respuesta = client.get(URL, params={"page": 1, "limit": 2})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["data"]) == 2
    assert cuerpo["pagination"] == {"page": 1, "limit": 2, "total": 4, "total_pages": 2}
    assert "password_hash" not in cuerpo["data"][0]
    assert set(cuerpo["data"][0]) == {
        "id", "nombre", "apellido", "correo", "rol", "activo",
        "medio_contacto_preferido", "telefono", "fecha_creacion",
    }


def test_listar_filtra_por_rol_activo_y_busqueda(client, db, coordinador):
    nuevo_usuario(db, "tecnico", nombre="Laura", correo="laura@organizacion.com")
    nuevo_usuario(db, "tecnico", nombre="Pedro", activo=False)
    nuevo_usuario(db, "solicitante", nombre="Lucía")
    como(coordinador)

    tecnicos_activos = client.get(URL, params={"rol": "tecnico", "activo": True}).json()
    busqueda = client.get(URL, params={"busqueda": "LAURA"}).json()

    assert [u["nombre"] for u in tecnicos_activos["data"]] == ["Laura"]
    assert [u["correo"] for u in busqueda["data"]] == ["laura@organizacion.com"]


def test_busqueda_trata_porcentaje_como_texto(client, db, coordinador):
    nuevo_usuario(db, "tecnico")
    como(coordinador)

    assert client.get(URL, params={"busqueda": "%"}).json()["pagination"]["total"] == 0


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"limit": 101}, {"rol": "otro"}])
def test_parametros_de_listado_invalidos_devuelven_422(client, coordinador, params):
    como(coordinador)

    assert client.get(URL, params=params).status_code == 422


def test_listado_sin_resultados(client, coordinador):
    como(coordinador)

    cuerpo = client.get(URL, params={"rol": "tecnico"}).json()

    assert cuerpo["data"] == []
    assert cuerpo["pagination"]["total"] == 0
    assert cuerpo["pagination"]["total_pages"] == 0


def test_detalle_de_usuario(client, db, coordinador):
    tecnico = nuevo_usuario(db, "tecnico")
    como(coordinador)

    respuesta = client.get(f"{URL}/{tecnico.id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == str(tecnico.id)
    assert "fecha_actualizacion" in respuesta.json()


def test_detalle_de_usuario_inexistente_devuelve_404(client, coordinador):
    como(coordinador)

    respuesta = client.get(f"{URL}/{uuid.uuid4()}")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_id_no_valido_devuelve_422(client, coordinador):
    como(coordinador)

    assert client.get(f"{URL}/no-es-un-uuid").status_code == 422


# --------------------------------- modificar ---------------------------------


def test_coordinador_modifica_datos_administrativos(client, db, coordinador):
    usuario = nuevo_usuario(db, "solicitante")
    como(coordinador)

    respuesta = client.patch(
        f"{URL}/{usuario.id}", json={"rol": "tecnico", "nombre": "Ana María"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "Usuario actualizado correctamente"
    db.refresh(usuario)
    assert (usuario.rol, usuario.nombre) == ("tecnico", "Ana María")


def test_usuario_modifica_sus_datos_de_contacto(client, db):
    usuario = nuevo_usuario(db, "solicitante")
    como(usuario)

    respuesta = client.patch(
        f"{URL}/{usuario.id}",
        json={"telefono": "3009876543", "medio_contacto_preferido": "telefono"},
    )

    assert respuesta.status_code == 200
    db.refresh(usuario)
    assert usuario.medio_contacto_preferido == "telefono"


@pytest.mark.parametrize("cambio", [{"rol": "coordinador"}, {"activo": False}, {"correo": "x@y.com"}])
def test_usuario_no_modifica_campos_administrativos_propios(client, db, cambio):
    usuario = nuevo_usuario(db, "solicitante")
    como(usuario)

    respuesta = client.patch(f"{URL}/{usuario.id}", json=cambio)

    assert respuesta.status_code == 403
    db.refresh(usuario)
    assert usuario.rol == "solicitante" and usuario.activo is True


def test_usuario_no_modifica_otras_cuentas(client, db):
    usuario = nuevo_usuario(db, "tecnico")
    otro = nuevo_usuario(db, "solicitante")
    como(usuario)

    respuesta = client.patch(f"{URL}/{otro.id}", json={"nombre": "Hackeado"})

    assert respuesta.status_code == 403
    db.refresh(otro)
    assert otro.nombre == "Ana"


def test_coordinador_no_cambia_su_propio_rol_ni_se_desactiva(client, coordinador):
    como(coordinador)

    assert client.patch(f"{URL}/{coordinador.id}", json={"rol": "tecnico"}).status_code == 403
    assert client.patch(f"{URL}/{coordinador.id}", json={"activo": False}).status_code == 403
    # Enviar el mismo valor no es un cambio.
    assert client.patch(f"{URL}/{coordinador.id}", json={"activo": True}).status_code == 200


def test_quitar_el_telefono_con_medio_telefono_devuelve_422(client, db):
    usuario = nuevo_usuario(
        db, "solicitante", medio_contacto_preferido="telefono", telefono="3001234567"
    )
    como(usuario)

    respuesta = client.patch(f"{URL}/{usuario.id}", json={"telefono": None})

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "ERROR_VALIDACION"


@pytest.mark.parametrize("cuerpo", [{"nombre": None}, {"password_hash": "x"}, {"id": str(uuid.uuid4())}])
def test_patch_rechaza_nulos_y_campos_no_permitidos(client, db, coordinador, cuerpo):
    usuario = nuevo_usuario(db, "solicitante")
    como(coordinador)

    assert client.patch(f"{URL}/{usuario.id}", json=cuerpo).status_code == 422


def test_patch_correo_duplicado(client, db, coordinador):
    nuevo_usuario(db, "tecnico", correo="ocupado@organizacion.com")
    usuario = nuevo_usuario(db, "tecnico")
    como(coordinador)

    respuesta = client.patch(f"{URL}/{usuario.id}", json={"correo": "OCUPADO@organizacion.com"})

    assert respuesta.status_code == 409


def test_patch_usuario_inexistente_devuelve_404(client, coordinador):
    como(coordinador)

    assert client.patch(f"{URL}/{uuid.uuid4()}", json={"nombre": "X"}).status_code == 404


# -------------------------------- desactivar ---------------------------------


def test_desactivar_revoca_las_sesiones_abiertas(client, db, coordinador):
    usuario = nuevo_usuario(db, "solicitante")
    db.add(
        Sesion(
            usuario_id=usuario.id,
            token_hash="a" * 64,
            fecha_expiracion=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )
    db.commit()
    como(coordinador)

    respuesta = client.patch(f"{URL}/{usuario.id}", json={"activo": False})

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["activo"] is False
    assert db.scalar(select(Sesion).where(Sesion.usuario_id == usuario.id)).revocada is True


def test_tecnico_con_asignaciones_no_se_desactiva_ni_cambia_de_rol(client, db, coordinador):
    tecnico = nuevo_usuario(db, "tecnico")
    db.add(
        Asignacion(solicitud_id=uuid.uuid4(), tecnico_id=tecnico.id, asignado_por=coordinador.id)
    )
    db.commit()
    como(coordinador)

    for cambio in ({"activo": False}, {"rol": "solicitante"}):
        respuesta = client.patch(f"{URL}/{tecnico.id}", json=cambio)
        assert respuesta.status_code == 409
        assert respuesta.json()["error"]["codigo"] == "TECNICO_CON_ASIGNACIONES"

    db.refresh(tecnico)
    assert tecnico.activo is True and tecnico.rol == "tecnico"


def test_tecnico_con_asignaciones_finalizadas_si_se_desactiva(client, db, coordinador):
    tecnico = nuevo_usuario(db, "tecnico")
    db.add(
        Asignacion(
            solicitud_id=uuid.uuid4(),
            tecnico_id=tecnico.id,
            asignado_por=coordinador.id,
            fecha_finalizacion=datetime.now(timezone.utc),
        )
    )
    db.commit()
    como(coordinador)

    assert client.patch(f"{URL}/{tecnico.id}", json={"activo": False}).status_code == 200


# ------------------------------ punta a punta --------------------------------


def test_flujo_real_coordinador_crea_cuenta_y_esta_inicia_sesion(client, db, coordinador):
    """Sin simular la sesión: login real, creación y login con la cuenta nueva."""
    login = client.post(
        "/api/v1/auth/login",
        json={"correo": "coordinador@organizacion.com", "contrasena": CONTRASENA},
    )
    assert login.status_code == 200

    assert client.post(URL, json=datos_nuevo()).status_code == 201

    otro = TestClient(app)
    respuesta = otro.post(
        "/api/v1/auth/login",
        json={"correo": "carlos@organizacion.com", "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["rol"] == "tecnico"
