"""Pruebas de RF-20 (cierre por solución y administrativo) y RF-15 (cancelación).

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


def crear_usuario(db, rol, nombre):
    usuario = Usuario(
        nombre=nombre,
        apellido="Prueba",
        correo=f"{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, estado, **campos):
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
        "estado": estado,
        "version": 1,
    }
    datos.update(campos)
    solicitud = Solicitud(**datos)
    db.add(solicitud)
    db.commit()
    return solicitud


def resuelta(db, e):
    """Solicitud resuelta por el técnico, lista para el cierre por solución."""
    solicitud = crear_solicitud(
        db,
        e["laura"],
        "resuelto",
        solucion_final="Se reemplazó el cable de poder.",
        resuelto_por=e["carlos"].id,
    )
    db.add(Asignacion(solicitud_id=solicitud.id, tecnico_id=e["carlos"].id, asignado_por=e["coordinador"].id))
    db.commit()
    return solicitud


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
        "coordinador": crear_usuario(db, "coordinador", "Marta"),
    }


def cerrar(client, solicitud, cuerpo):
    return client.post(f"{URL}/{solicitud.id}/close", json=cuerpo)


def cancelar(client, solicitud, motivo="Ya no necesito asistencia."):
    return client.post(f"{URL}/{solicitud.id}/cancel", json={"motivo": motivo})


# ========================= RF-20: cierre por solución =========================


def test_coordinador_cierra_por_solucion(client, db, e):
    solicitud = resuelta(db, e)
    como(e["coordinador"])

    respuesta = cerrar(client, solicitud, {"tipo_cierre": "solucion"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Solicitud cerrada correctamente"
    s = cuerpo["solicitud"]
    assert (s["estado_anterior"], s["estado_actual"]) == ("resuelto", "cerrado")
    assert s["tipo_cierre"] == "solucion"
    assert s["cerrado_por"] == str(e["coordinador"].id)
    assert s["fecha_cierre"] is not None
    db.refresh(solicitud)
    assert solicitud.estado == "cerrado"
    assert solicitud.version == 2


def test_cierre_por_solucion_queda_en_el_historial(client, db, e):
    solicitud = resuelta(db, e)
    como(e["coordinador"])

    cerrar(client, solicitud, {"tipo_cierre": "solucion"})

    [registro] = historial(db, solicitud, "cierre_solucion")
    assert (registro.valor_anterior, registro.valor_nuevo) == ("resuelto", "cerrado")
    assert registro.usuario_id == e["coordinador"].id


@pytest.mark.parametrize("estado", ["registrado", "en_evaluacion", "asignado", "en_atencion", "en_espera"])
def test_solo_se_cierra_por_solucion_una_resuelta(client, db, e, estado):
    solicitud = crear_solicitud(db, e["laura"], estado)
    como(e["coordinador"])

    respuesta = cerrar(client, solicitud, {"tipo_cierre": "solucion"})

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "ESTADO_NO_PERMITIDO"
    db.refresh(solicitud)
    assert solicitud.estado == estado


# ========================= RF-20: cierre administrativo ========================


def test_cierre_administrativo_con_motivo(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["coordinador"])

    respuesta = cerrar(
        client,
        solicitud,
        {"tipo_cierre": "administrativo", "motivo_cierre": "No corresponde al área de soporte."},
    )

    assert respuesta.status_code == 200
    s = respuesta.json()["solicitud"]
    assert s["tipo_cierre"] == "administrativo"
    assert s["motivo_cierre"] == "No corresponde al área de soporte."
    [registro] = historial(db, solicitud, "cierre_administrativo")
    assert registro.observacion == "No corresponde al área de soporte."


@pytest.mark.parametrize("motivo", [None, "", "   "])
def test_cierre_administrativo_exige_motivo(client, db, e, motivo):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["coordinador"])

    cuerpo = {"tipo_cierre": "administrativo"}
    if motivo is not None:
        cuerpo["motivo_cierre"] = motivo

    assert cerrar(client, solicitud, cuerpo).status_code == 422
    db.refresh(solicitud)
    assert solicitud.estado == "en_evaluacion"


@pytest.mark.parametrize("estado", ["registrado", "asignado", "resuelto"])
def test_cierre_administrativo_solo_en_evaluacion(client, db, e, estado):
    solicitud = crear_solicitud(db, e["laura"], estado)
    como(e["coordinador"])

    respuesta = cerrar(
        client, solicitud, {"tipo_cierre": "administrativo", "motivo_cierre": "Motivo"}
    )

    assert respuesta.status_code == 409


@pytest.mark.parametrize(
    "cuerpo",
    [{}, {"tipo_cierre": "cancelacion", "motivo_cierre": "x"}, {"tipo_cierre": "otro"},
     {"tipo_cierre": "solucion", "estado": "cerrado"}],
)
def test_datos_de_cierre_invalidos_devuelven_422(client, db, e, cuerpo):
    solicitud = resuelta(db, e)
    como(e["coordinador"])

    assert cerrar(client, solicitud, cuerpo).status_code == 422
    db.refresh(solicitud)
    assert solicitud.estado == "resuelto"


@pytest.mark.parametrize("rol", ["laura", "carlos"])
def test_solo_el_coordinador_cierra(client, db, e, rol):
    solicitud = resuelta(db, e)
    como(e[rol])

    respuesta = cerrar(client, solicitud, {"tipo_cierre": "solucion"})

    assert respuesta.status_code == 403
    db.refresh(solicitud)
    assert solicitud.estado == "resuelto"


def test_cerrar_solicitud_inexistente_devuelve_404(client, e):
    como(e["coordinador"])

    respuesta = client.post(f"{URL}/{uuid.uuid4()}/close", json={"tipo_cierre": "solucion"})

    assert respuesta.status_code == 404


# ============================== RF-15: cancelación ==============================


@pytest.mark.parametrize("estado", ["registrado", "en_evaluacion"])
def test_solicitante_cancela_su_solicitud(client, db, e, estado):
    solicitud = crear_solicitud(db, e["laura"], estado)
    como(e["laura"])

    respuesta = cancelar(client, solicitud)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Solicitud cancelada correctamente"
    s = cuerpo["solicitud"]
    assert (s["estado_anterior"], s["estado_actual"]) == (estado, "cerrado")
    assert s["tipo_cierre"] == "cancelacion"
    assert s["motivo_cierre"] == "Ya no necesito asistencia."
    assert s["cerrado_por"] == str(e["laura"].id)


def test_cancelacion_queda_en_el_historial(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e["laura"])

    cancelar(client, solicitud, "Se solucionó solo.")

    [registro] = historial(db, solicitud, "cancelacion")
    assert registro.usuario_id == e["laura"].id
    assert registro.observacion == "Se solucionó solo."


@pytest.mark.parametrize("estado", ["asignado", "en_atencion", "en_espera", "resuelto"])
def test_no_se_cancela_despues_de_la_evaluacion(client, db, e, estado):
    solicitud = crear_solicitud(db, e["laura"], estado)
    como(e["laura"])

    respuesta = cancelar(client, solicitud)

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "ESTADO_NO_PERMITIDO"
    db.refresh(solicitud)
    assert solicitud.estado == estado


@pytest.mark.parametrize("cuerpo", [{}, {"motivo": ""}, {"motivo": "   "}, {"motivo": "x" * 1001}])
def test_cancelacion_exige_motivo(client, db, e, cuerpo):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e["laura"])

    assert client.post(f"{URL}/{solicitud.id}/cancel", json=cuerpo).status_code == 422
    db.refresh(solicitud)
    assert solicitud.estado == "registrado"


def test_no_se_cancela_una_solicitud_ajena(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e["pedro"])

    respuesta = cancelar(client, solicitud)

    assert respuesta.status_code == 403
    db.refresh(solicitud)
    assert solicitud.estado == "registrado"


@pytest.mark.parametrize("rol", ["carlos", "coordinador"])
def test_solo_el_solicitante_cancela(client, db, e, rol):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e[rol])

    assert cancelar(client, solicitud).status_code == 403


def test_cancelar_solicitud_inexistente_devuelve_404(client, e):
    como(e["laura"])

    respuesta = client.post(f"{URL}/{uuid.uuid4()}/cancel", json={"motivo": "x"})

    assert respuesta.status_code == 404


def test_sin_sesion_devuelve_401(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "registrado")

    assert cancelar(client, solicitud).status_code == 401
    assert cerrar(client, solicitud, {"tipo_cierre": "solucion"}).status_code == 401


# =========================== solicitud ya cerrada ===========================


def test_una_solicitud_cerrada_no_se_vuelve_a_cerrar_ni_cancelar(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["laura"])
    assert cancelar(client, solicitud).status_code == 200

    como(e["coordinador"])
    respuesta = cerrar(client, solicitud, {"tipo_cierre": "administrativo", "motivo_cierre": "x"})
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "SOLICITUD_CERRADA"

    como(e["laura"])
    assert cancelar(client, solicitud).json()["error"]["codigo"] == "SOLICITUD_CERRADA"


def test_una_solicitud_cerrada_no_se_reabre(client, db, e):
    """RN-21: ninguna operación devuelve una solicitud cerrada a otro estado."""
    solicitud = resuelta(db, e)
    como(e["coordinador"])
    cerrar(client, solicitud, {"tipo_cierre": "solucion"})

    assert client.patch(f"{URL}/{solicitud.id}/status", json={"estado": "en_evaluacion"}).status_code == 409
    assert client.patch(f"{URL}/{solicitud.id}", json={"prioridad": "alta"}).status_code == 409
    assert client.post(
        f"{URL}/{solicitud.id}/assignments", json={"tecnico_id": str(e["carlos"].id)}
    ).status_code == 409
    db.refresh(solicitud)
    assert solicitud.estado == "cerrado"


# ============================ CA-05: consulta del resultado ============================


def test_el_solicitante_consulta_el_resultado_de_su_caso_cerrado(client, db, e):
    """CA-05: el usuario puede consultar el resultado y la finalización de su caso."""
    solicitud = resuelta(db, e)
    como(e["coordinador"])
    cerrar(client, solicitud, {"tipo_cierre": "solucion"})

    como(e["laura"])
    detalle = client.get(f"{URL}/{solicitud.id}").json()

    assert detalle["estado"] == "cerrado"
    assert detalle["tipo_cierre"] == "solucion"
    assert detalle["solucion_final"] == "Se reemplazó el cable de poder."
    assert detalle["fecha_cierre"] is not None
