"""Pruebas de RF-27: notificaciones internas de la plataforma.

Cubren la consulta y lectura (/notifications) y los eventos que las generan
(asignación, reasignación, cierre, mensajes y respuestas a peticiones).

Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
"""

import itertools
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import (
    Asignacion,
    Base,
    Notificacion,
    Solicitud,
    SolicitudInformacion,
    Usuario,
)

URL = "/api/v1/notifications"
URL_SOLICITUDES = "/api/v1/requests"
_contador = itertools.count(1)
INICIO = datetime(2026, 11, 6, 9, 0, tzinfo=timezone.utc)


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


def crear_solicitud(db, solicitante, estado="en_evaluacion", **campos):
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


def asignar(db, solicitud, tecnico, coordinador):
    db.add(
        Asignacion(
            solicitud_id=solicitud.id, tecnico_id=tecnico.id, asignado_por=coordinador.id
        )
    )
    db.commit()


def crear_notificacion(db, usuario, contenido="Aviso", leida=False, minutos=0, solicitud=None):
    notificacion = Notificacion(
        usuario_id=usuario.id,
        solicitud_id=solicitud.id if solicitud else None,
        tipo="prueba",
        contenido=contenido,
        leida=leida,
        fecha_creacion=INICIO + timedelta(minutes=minutos),
    )
    db.add(notificacion)
    db.commit()
    return notificacion


def notificaciones_de(db, usuario):
    return db.scalars(
        select(Notificacion).where(Notificacion.usuario_id == usuario.id)
    ).all()


def total(db):
    return db.scalar(select(func.count()).select_from(Notificacion))


@pytest.fixture()
def e(db):
    return {
        "laura": crear_usuario(db, "solicitante", "Laura"),
        "pedro": crear_usuario(db, "solicitante", "Pedro"),
        "carlos": crear_usuario(db, "tecnico", "Carlos"),
        "ana": crear_usuario(db, "tecnico", "Ana"),
        "coordinador": crear_usuario(db, "coordinador", "Marta"),
    }


# ======================== Consultar notificaciones ========================


def test_usuario_solo_ve_sus_notificaciones(client, db, e):
    crear_notificacion(db, e["laura"], "Para Laura")
    crear_notificacion(db, e["pedro"], "Para Pedro")

    como(e["laura"])
    datos = client.get(URL).json()["data"]
    assert [n["contenido"] for n in datos] == ["Para Laura"]


def test_formato_de_la_notificacion(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    notificacion = crear_notificacion(db, e["laura"], "Aviso", solicitud=solicitud)

    como(e["laura"])
    dato = client.get(URL).json()["data"][0]
    assert dato == {
        "id": str(notificacion.id),
        "solicitud_id": str(solicitud.id),
        "tipo": "prueba",
        "contenido": "Aviso",
        "leida": False,
        "fecha_creacion": dato["fecha_creacion"],
    }
    assert dato["fecha_creacion"].startswith("2026-11-06T09:00")


def test_orden_mas_reciente_primero(client, db, e):
    crear_notificacion(db, e["laura"], "Vieja", minutos=0)
    crear_notificacion(db, e["laura"], "Nueva", minutos=30)
    crear_notificacion(db, e["laura"], "Media", minutos=15)

    como(e["laura"])
    assert [n["contenido"] for n in client.get(URL).json()["data"]] == ["Nueva", "Media", "Vieja"]


def test_cuenta_no_leidas(client, db, e):
    crear_notificacion(db, e["laura"], leida=False)
    crear_notificacion(db, e["laura"], leida=False)
    crear_notificacion(db, e["laura"], leida=True)
    crear_notificacion(db, e["pedro"], leida=False)

    como(e["laura"])
    assert client.get(URL).json()["no_leidas"] == 2


@pytest.mark.parametrize("leida, esperado", [("false", ["No leída"]), ("true", ["Leída"])])
def test_filtro_por_leida(client, db, e, leida, esperado):
    crear_notificacion(db, e["laura"], "No leída", leida=False)
    crear_notificacion(db, e["laura"], "Leída", leida=True)

    como(e["laura"])
    datos = client.get(URL, params={"leida": leida}).json()["data"]
    assert [n["contenido"] for n in datos] == esperado


def test_paginacion(client, db, e):
    for i in range(5):
        crear_notificacion(db, e["laura"], f"n{i}", minutos=i)

    como(e["laura"])
    cuerpo = client.get(URL, params={"page": 2, "limit": 2}).json()
    assert [n["contenido"] for n in cuerpo["data"]] == ["n2", "n1"]
    assert cuerpo["pagination"] == {"page": 2, "limit": 2, "total": 5, "total_pages": 3}


def test_sin_notificaciones(client, e):
    como(e["laura"])
    assert client.get(URL).json() == {
        "data": [],
        "pagination": {"page": 1, "limit": 20, "total": 0, "total_pages": 0},
        "no_leidas": 0,
    }


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 101}, {"leida": "quizas"}])
def test_parametros_invalidos_422(client, e, params):
    como(e["laura"])
    assert client.get(URL, params=params).status_code == 422


def test_consultar_sin_sesion_401(client):
    assert client.get(URL).status_code == 401


# ======================== Marcar como leídas ========================


def test_marcar_una_como_leida(client, db, e):
    notificacion = crear_notificacion(db, e["laura"])
    como(e["laura"])
    respuesta = client.patch(f"{URL}/{notificacion.id}/read")

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "Notificación marcada como leída"
    assert respuesta.json()["notificacion"]["leida"] is True
    db.refresh(notificacion)
    assert notificacion.leida is True


def test_marcar_leida_dos_veces_no_falla(client, db, e):
    notificacion = crear_notificacion(db, e["laura"], leida=True)
    como(e["laura"])
    assert client.patch(f"{URL}/{notificacion.id}/read").status_code == 200


def test_no_se_marca_la_de_otro_usuario(client, db, e):
    ajena = crear_notificacion(db, e["pedro"])
    como(e["laura"])
    respuesta = client.patch(f"{URL}/{ajena.id}/read")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"
    db.refresh(ajena)
    assert ajena.leida is False


def test_marcar_inexistente_404(client, e):
    como(e["laura"])
    assert client.patch(f"{URL}/{uuid.uuid4()}/read").status_code == 404


def test_marcar_id_invalido_422(client, e):
    como(e["laura"])
    assert client.patch(f"{URL}/no-es-uuid/read").status_code == 422


def test_marcar_todas_como_leidas(client, db, e):
    crear_notificacion(db, e["laura"])
    crear_notificacion(db, e["laura"])
    crear_notificacion(db, e["laura"], leida=True)
    ajena = crear_notificacion(db, e["pedro"])

    como(e["laura"])
    respuesta = client.patch(f"{URL}/read-all")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"mensaje": "Notificaciones marcadas como leídas", "actualizadas": 2}
    assert client.get(URL).json()["no_leidas"] == 0

    db.refresh(ajena)
    assert ajena.leida is False


def test_marcar_todas_sin_pendientes(client, e):
    como(e["laura"])
    assert client.patch(f"{URL}/read-all").json()["actualizadas"] == 0


def test_marcar_sin_sesion_401(client, db, e):
    notificacion = crear_notificacion(db, e["laura"])
    assert client.patch(f"{URL}/{notificacion.id}/read").status_code == 401
    assert client.patch(f"{URL}/read-all").status_code == 401


# ======================== Eventos que generan notificaciones ========================


def test_asignacion_notifica_al_tecnico_y_al_solicitante(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["coordinador"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/assignments",
        json={"tecnico_id": str(e["carlos"].id)},
    )
    assert respuesta.status_code == 201

    [al_tecnico] = notificaciones_de(db, e["carlos"])
    assert al_tecnico.tipo == "asignacion"
    assert al_tecnico.solicitud_id == solicitud.id
    assert solicitud.numero in al_tecnico.contenido

    [al_solicitante] = notificaciones_de(db, e["laura"])
    assert al_solicitante.tipo == "tecnico_asignado"
    assert "Carlos Prueba" in al_solicitante.contenido

    assert notificaciones_de(db, e["coordinador"]) == []


def test_reasignacion_notifica_al_tecnico_anterior_y_al_nuevo(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_atencion")
    asignar(db, solicitud, e["carlos"], e["coordinador"])

    como(e["coordinador"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/assignments",
        json={"tecnico_id": str(e["ana"].id)},
    )
    assert respuesta.status_code == 201

    assert [n.tipo for n in notificaciones_de(db, e["carlos"])] == ["reasignacion"]
    assert [n.tipo for n in notificaciones_de(db, e["ana"])] == ["asignacion"]
    assert [n.tipo for n in notificaciones_de(db, e["laura"])] == ["tecnico_asignado"]


def test_asignacion_fallida_no_genera_notificaciones(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["coordinador"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/assignments",
        json={"tecnico_id": str(e["pedro"].id)},  # no es técnico
    )
    assert respuesta.status_code == 422
    assert total(db) == 0


def test_cierre_por_solucion_notifica_al_solicitante_y_al_tecnico(client, db, e):
    solicitud = crear_solicitud(
        db,
        e["laura"],
        "resuelto",
        solucion_final="Se cambió el cable.",
        resuelto_por=e["carlos"].id,
    )
    asignar(db, solicitud, e["carlos"], e["coordinador"])

    como(e["coordinador"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/close", json={"tipo_cierre": "solucion"}
    )
    assert respuesta.status_code == 200

    [al_solicitante] = notificaciones_de(db, e["laura"])
    assert al_solicitante.tipo == "solicitud_cerrada"
    assert "solucionada" in al_solicitante.contenido
    assert [n.tipo for n in notificaciones_de(db, e["carlos"])] == ["solicitud_cerrada"]


def test_cierre_administrativo_notifica_solo_al_solicitante(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["coordinador"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/close",
        json={"tipo_cierre": "administrativo", "motivo_cierre": "Duplicada"},
    )
    assert respuesta.status_code == 200

    [al_solicitante] = notificaciones_de(db, e["laura"])
    assert "administrativamente" in al_solicitante.contenido
    assert total(db) == 1


def test_cancelacion_no_genera_notificaciones(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e["laura"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/cancel", json={"motivo": "Ya se solucionó."}
    )
    assert respuesta.status_code == 200
    assert total(db) == 0


def test_mensaje_del_solicitante_notifica_al_tecnico(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_atencion")
    asignar(db, solicitud, e["carlos"], e["coordinador"])

    como(e["laura"])
    client.post(f"{URL_SOLICITUDES}/{solicitud.id}/messages", json={"contenido": "Hola"})

    assert [n.tipo for n in notificaciones_de(db, e["carlos"])] == ["nuevo_mensaje"]
    assert notificaciones_de(db, e["laura"]) == []


def test_mensaje_del_coordinador_notifica_a_ambos(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_atencion")
    asignar(db, solicitud, e["carlos"], e["coordinador"])

    como(e["coordinador"])
    client.post(f"{URL_SOLICITUDES}/{solicitud.id}/messages", json={"contenido": "Hola"})

    assert len(notificaciones_de(db, e["laura"])) == 1
    assert len(notificaciones_de(db, e["carlos"])) == 1
    assert notificaciones_de(db, e["coordinador"]) == []


def test_mensaje_sin_tecnico_asignado_notifica_solo_al_solicitante(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "registrado")
    como(e["coordinador"])
    client.post(f"{URL_SOLICITUDES}/{solicitud.id}/messages", json={"contenido": "Hola"})
    assert total(db) == 1
    assert len(notificaciones_de(db, e["laura"])) == 1


def test_mensaje_rechazado_no_genera_notificaciones(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "cerrado")
    como(e["laura"])
    respuesta = client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/messages", json={"contenido": "Hola"}
    )
    assert respuesta.status_code == 409
    assert total(db) == 0


def test_respuesta_a_peticion_notifica_al_tecnico(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], "en_espera")
    asignar(db, solicitud, e["carlos"], e["coordinador"])
    peticion = SolicitudInformacion(
        solicitud_id=solicitud.id,
        solicitado_por=e["carlos"].id,
        contenido="¿Tiene luz?",
        estado="pendiente",
    )
    db.add(peticion)
    db.commit()

    como(e["laura"])
    respuesta = client.post(
        f"/api/v1/information-requests/{peticion.id}/responses", json={"contenido": "Sí"}
    )
    assert respuesta.status_code == 201

    [al_tecnico] = notificaciones_de(db, e["carlos"])
    assert al_tecnico.tipo == "respuesta_informacion"
    assert al_tecnico.solicitud_id == solicitud.id


def test_notificacion_generada_se_consulta_y_se_marca(client, db, e):
    """Flujo completo: un evento genera el aviso, el usuario lo ve y lo marca."""
    solicitud = crear_solicitud(db, e["laura"], "en_evaluacion")
    como(e["coordinador"])
    client.post(
        f"{URL_SOLICITUDES}/{solicitud.id}/assignments",
        json={"tecnico_id": str(e["carlos"].id)},
    )

    como(e["carlos"])
    cuerpo = client.get(URL).json()
    assert cuerpo["no_leidas"] == 1
    notificacion_id = cuerpo["data"][0]["id"]

    assert client.patch(f"{URL}/{notificacion_id}/read").status_code == 200
    assert client.get(URL).json()["no_leidas"] == 0
