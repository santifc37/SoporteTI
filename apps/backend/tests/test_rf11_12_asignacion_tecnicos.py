"""Pruebas de RF-11 (asignación) y RF-12 (reasignación) de técnicos.

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
from app.models import Asignacion, Base, Solicitud, Usuario
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


def crear_usuario(db, rol, nombre, activo=True):
    usuario = Usuario(
        nombre=nombre,
        apellido="Prueba",
        correo=f"{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
        activo=activo,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, estado="en_evaluacion"):
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


def activas(db, solicitud):
    return db.scalars(
        select(Asignacion).where(
            Asignacion.solicitud_id == solicitud.id,
            Asignacion.fecha_finalizacion.is_(None),
        )
    ).all()


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
        "laura": crear_usuario(db, "solicitante", "Laura"),
        "pedro": crear_usuario(db, "solicitante", "Pedro"),
        "carlos": crear_usuario(db, "tecnico", "Carlos"),
        "luis": crear_usuario(db, "tecnico", "Luis"),
        "coordinador": crear_usuario(db, "coordinador", "Marta"),
    }


def asignar(client, solicitud, tecnico, observacion=None):
    cuerpo = {"tecnico_id": str(tecnico.id)}
    if observacion is not None:
        cuerpo["observacion"] = observacion
    return client.post(f"{URL}/{solicitud.id}/assignments", json=cuerpo)


# ============================ RF-11: asignación ============================


def test_coordinador_asigna_un_tecnico(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    respuesta = asignar(client, solicitud, e["carlos"], "Asignación inicial del caso")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Técnico asignado correctamente"
    assert cuerpo["estado_solicitud"] == "asignado"
    a = cuerpo["asignacion"]
    assert a["tecnico_id"] == str(e["carlos"].id)
    assert a["asignado_por"] == str(e["coordinador"].id)
    assert a["fecha_finalizacion"] is None
    assert a["observacion"] == "Asignación inicial del caso"


def test_la_asignacion_cambia_el_estado_y_queda_en_el_historial(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    asignar(client, solicitud, e["carlos"])

    db.refresh(solicitud)
    assert solicitud.estado == "asignado"
    assert solicitud.version == 2
    [asignacion] = historial(db, solicitud, "asignacion")
    assert asignacion.valor_nuevo == "Carlos Prueba"
    [estado] = historial(db, solicitud, "cambio_estado")
    assert (estado.valor_anterior, estado.valor_nuevo) == ("en_evaluacion", "asignado")


@pytest.mark.parametrize("estado", ["registrado", "resuelto"])
def test_primera_asignacion_solo_en_evaluacion(client, db, e, estado):
    solicitud = crear_solicitud(db, e["laura"], estado=estado)
    como(e["coordinador"])

    respuesta = asignar(client, solicitud, e["carlos"])

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "ESTADO_NO_PERMITIDO"
    assert activas(db, solicitud) == []


def test_no_se_asigna_una_solicitud_cerrada(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], estado="cerrado")
    como(e["coordinador"])

    respuesta = asignar(client, solicitud, e["carlos"])

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"


@pytest.mark.parametrize("caso", ["inexistente", "no_es_tecnico", "inactivo"])
def test_tecnico_no_valido_devuelve_422(client, db, e, caso):
    solicitud = crear_solicitud(db, e["laura"])
    if caso == "inexistente":
        tecnico_id = uuid.uuid4()
    elif caso == "no_es_tecnico":
        tecnico_id = e["pedro"].id
    else:
        tecnico_id = crear_usuario(db, "tecnico", "Inactivo", activo=False).id
    como(e["coordinador"])

    respuesta = client.post(
        f"{URL}/{solicitud.id}/assignments", json={"tecnico_id": str(tecnico_id)}
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "TECNICO_NO_VALIDO"
    db.refresh(solicitud)
    assert solicitud.estado == "en_evaluacion"
    assert activas(db, solicitud) == []


@pytest.mark.parametrize(
    "cuerpo",
    [{}, {"tecnico_id": "no-uuid"}, {"tecnico_id": str(uuid.uuid4()), "estado": "asignado"}],
)
def test_datos_invalidos_devuelven_422(client, db, e, cuerpo):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    assert client.post(f"{URL}/{solicitud.id}/assignments", json=cuerpo).status_code == 422


@pytest.mark.parametrize("rol", ["laura", "carlos"])
def test_solo_el_coordinador_asigna(client, db, e, rol):
    solicitud = crear_solicitud(db, e["laura"])
    como(e[rol])

    respuesta = asignar(client, solicitud, e["carlos"])

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"
    assert activas(db, solicitud) == []


def test_asignar_solicitud_inexistente_devuelve_404(client, e):
    como(e["coordinador"])

    respuesta = client.post(
        f"{URL}/{uuid.uuid4()}/assignments", json={"tecnico_id": str(e["carlos"].id)}
    )

    assert respuesta.status_code == 404


def test_asignar_sin_sesion_devuelve_401(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])

    assert asignar(client, solicitud, e["carlos"]).status_code == 401


# =========================== RF-12: reasignación ===========================


def test_reasignar_finaliza_la_anterior_y_crea_una_nueva(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"])

    respuesta = asignar(client, solicitud, e["luis"], "Carlos está de vacaciones")

    assert respuesta.status_code == 201
    [activa] = activas(db, solicitud)
    assert activa.tecnico_id == e["luis"].id
    todas = db.scalars(select(Asignacion).where(Asignacion.solicitud_id == solicitud.id)).all()
    assert len(todas) == 2  # la anterior se conserva como historial


def test_reasignar_queda_en_el_historial(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"])

    asignar(client, solicitud, e["luis"], "Carga de trabajo")

    [registro] = historial(db, solicitud, "reasignacion")
    assert (registro.valor_anterior, registro.valor_nuevo) == ("Carlos Prueba", "Luis Prueba")
    assert registro.observacion == "Carga de trabajo"


@pytest.mark.parametrize("estado", ["asignado", "en_atencion", "en_espera"])
def test_reasignar_no_cambia_el_estado(client, db, e, estado):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"])
    solicitud.estado = estado
    db.commit()

    respuesta = asignar(client, solicitud, e["luis"])

    assert respuesta.status_code == 201
    assert respuesta.json()["estado_solicitud"] == estado


def test_reasignar_al_mismo_tecnico_devuelve_409(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"])

    respuesta = asignar(client, solicitud, e["carlos"])

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "TECNICO_YA_ASIGNADO"
    assert len(activas(db, solicitud)) == 1


def test_no_se_reasigna_una_solicitud_resuelta(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"])
    solicitud.estado = "resuelto"
    db.commit()

    assert asignar(client, solicitud, e["luis"]).status_code == 409
    assert activas(db, solicitud)[0].tecnico_id == e["carlos"].id


def test_el_tecnico_anterior_pierde_el_acceso(client, db, e):
    """RN-14: tras la reasignación solo el técnico nuevo accede a la solicitud."""
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"])
    asignar(client, solicitud, e["luis"])

    como(e["carlos"])
    assert client.get(f"{URL}/{solicitud.id}").status_code == 403
    assert client.get(URL).json()["data"] == []

    como(e["luis"])
    assert client.get(f"{URL}/{solicitud.id}").status_code == 200


# ===================== consulta del historial de asignaciones =====================


def preparar_reasignada(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["coordinador"])
    asignar(client, solicitud, e["carlos"], "Inicial")
    asignar(client, solicitud, e["luis"], "Reasignación")
    return solicitud


def test_coordinador_ve_todo_el_historial_en_orden(client, db, e):
    solicitud = preparar_reasignada(client, db, e)
    como(e["coordinador"])

    datos = client.get(f"{URL}/{solicitud.id}/assignments").json()["data"]

    assert [a["tecnico_nombre"] for a in datos] == ["Carlos Prueba", "Luis Prueba"]
    assert datos[0]["fecha_finalizacion"] is not None
    assert datos[1]["fecha_finalizacion"] is None
    assert datos[0]["observacion"] == "Inicial"


def test_tecnico_actual_ve_el_historial(client, db, e):
    solicitud = preparar_reasignada(client, db, e)
    como(e["luis"])

    assert len(client.get(f"{URL}/{solicitud.id}/assignments").json()["data"]) == 2


def test_tecnico_anterior_no_ve_el_historial(client, db, e):
    solicitud = preparar_reasignada(client, db, e)
    como(e["carlos"])

    assert client.get(f"{URL}/{solicitud.id}/assignments").status_code == 403


def test_solicitante_solo_ve_el_responsable_actual(client, db, e):
    solicitud = preparar_reasignada(client, db, e)
    como(e["laura"])

    datos = client.get(f"{URL}/{solicitud.id}/assignments").json()["data"]

    assert len(datos) == 1
    assert datos[0]["tecnico_nombre"] == "Luis Prueba"
    assert datos[0]["asignado_por"] is None
    assert datos[0]["observacion"] is None


def test_solicitante_sin_tecnico_asignado(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["laura"])

    respuesta = client.get(f"{URL}/{solicitud.id}/assignments")

    assert respuesta.status_code == 200
    assert respuesta.json()["data"] == []


def test_otro_solicitante_no_ve_las_asignaciones(client, db, e):
    solicitud = preparar_reasignada(client, db, e)
    como(e["pedro"])

    assert client.get(f"{URL}/{solicitud.id}/assignments").status_code == 403


def test_historial_de_solicitud_inexistente_devuelve_404(client, e):
    como(e["coordinador"])

    assert client.get(f"{URL}/{uuid.uuid4()}/assignments").status_code == 404


# ============================ flujo de punta a punta ============================


def test_flujo_asignar_y_el_tecnico_inicia_la_atencion(client, db, e):
    """Evaluación → asignación → el técnico inicia la atención (RF-14 de Santiago)."""
    solicitud = crear_solicitud(db, e["laura"], estado="registrado")
    como(e["coordinador"])
    assert client.patch(f"{URL}/{solicitud.id}/status", json={"estado": "en_evaluacion"}).status_code == 200
    assert asignar(client, solicitud, e["carlos"]).status_code == 201

    como(e["carlos"])
    respuesta = client.patch(f"{URL}/{solicitud.id}/status", json={"estado": "en_atencion"})

    assert respuesta.status_code == 200
    assert respuesta.json()["solicitud"]["estado_actual"] == "en_atencion"

    como(e["laura"])
    detalle = client.get(f"{URL}/{solicitud.id}").json()
    assert detalle["estado"] == "en_atencion"
    assert detalle["tecnico_asignado"]["nombre"] == "Carlos Prueba"
