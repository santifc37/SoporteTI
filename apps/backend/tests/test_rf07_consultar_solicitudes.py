"""Pruebas de RF-07: consulta de solicitudes por solicitante y coordinador,
y detalle de una solicitud (contrato-api.md §7.1 y §7.3).

La consulta del técnico (RF-13) se prueba en test_rf13_solicitudes_asignadas.py.
Usan SQLite en memoria; no tocan Supabase. La sesión se simula con `como()`.
"""

import itertools
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.security import hash_password
from app.database.session import get_db
from app.main import app
from app.models import Asignacion, Base, Categoria, Solicitud, Usuario

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


def crear_usuario(db, rol, nombre="Ana", apellido="Pérez"):
    usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        correo=f"{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Contrasena123"),
        rol=rol,
    )
    db.add(usuario)
    db.commit()
    return usuario


def crear_solicitud(db, solicitante, tecnico=None, *, activa=True, **campos):
    """Crea una solicitud y, si se indica técnico, su asignación."""
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
        "estado": "registrado",
        "fecha_creacion": datetime(2026, 11, 1) + timedelta(minutes=n),
    }
    datos.update(campos)
    solicitud = Solicitud(**datos)
    db.add(solicitud)
    db.commit()

    if tecnico is not None:
        db.add(
            Asignacion(
                solicitud_id=solicitud.id,
                tecnico_id=tecnico.id,
                asignado_por=tecnico.id,
                fecha_finalizacion=None if activa else datetime(2026, 11, 2),
            )
        )
        db.commit()
    return solicitud


@pytest.fixture()
def e(db):
    """Escenario con un usuario de cada rol, más un segundo solicitante y técnico."""
    return {
        "laura": crear_usuario(db, "solicitante", "Laura", "Docente"),
        "pedro": crear_usuario(db, "solicitante", "Pedro", "Admin"),
        "carlos": crear_usuario(db, "tecnico", "Carlos", "Gómez"),
        "luis": crear_usuario(db, "tecnico", "Luis", "Díaz"),
        "coordinador": crear_usuario(db, "coordinador", "Marta", "Ruiz"),
    }


def ids(respuesta) -> list[str]:
    return [s["id"] for s in respuesta.json()["data"]]


# --------------------------------- solicitante --------------------------------


def test_solicitante_ve_solo_sus_solicitudes(client, db, e):
    propia = crear_solicitud(db, e["laura"])
    crear_solicitud(db, e["pedro"])
    como(e["laura"])

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert ids(respuesta) == [str(propia.id)]
    assert respuesta.json()["pagination"]["total"] == 1


def test_solicitante_no_ve_ajenas_enviando_otro_solicitante_id(client, db, e):
    """Los filtros no amplían permisos (contrato §17)."""
    propia = crear_solicitud(db, e["laura"])
    crear_solicitud(db, e["pedro"])
    como(e["laura"])

    respuesta = client.get(URL, params={"solicitante_id": str(e["pedro"].id)})

    assert ids(respuesta) == [str(propia.id)]


def test_solicitante_ve_el_tecnico_asignado_y_el_estado(client, db, e):
    crear_solicitud(db, e["laura"], e["carlos"], estado="en_atencion")
    como(e["laura"])

    item = client.get(URL).json()["data"][0]

    assert item["estado"] == "en_atencion"
    assert item["tecnico_asignado"]["nombre"] == "Carlos Gómez"
    assert item["solicitante"]["nombre"] == "Laura Docente"


def test_solicitante_filtra_por_estado(client, db, e):
    crear_solicitud(db, e["laura"], estado="registrado")
    cerrada = crear_solicitud(db, e["laura"], estado="cerrado")
    como(e["laura"])

    assert ids(client.get(URL, params={"estado": "cerrado"})) == [str(cerrada.id)]


def test_solicitante_sin_solicitudes(client, e):
    como(e["laura"])

    cuerpo = client.get(URL).json()

    assert cuerpo["data"] == []
    assert cuerpo["pagination"]["total"] == 0


# --------------------------------- coordinador --------------------------------


def test_coordinador_ve_todas_ordenadas_de_la_mas_reciente(client, db, e):
    primera = crear_solicitud(db, e["laura"])
    segunda = crear_solicitud(db, e["pedro"], e["carlos"])
    tercera = crear_solicitud(db, e["laura"], e["luis"])
    como(e["coordinador"])

    respuesta = client.get(URL)

    assert ids(respuesta) == [str(tercera.id), str(segunda.id), str(primera.id)]
    assert respuesta.json()["pagination"]["total"] == 3


def test_solicitud_sin_asignar_muestra_tecnico_nulo(client, db, e):
    crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    item = client.get(URL).json()["data"][0]

    assert item["tecnico_asignado"] is None
    assert item["categoria"] is None


def test_respuesta_sigue_el_contrato(client, db, e):
    categoria = Categoria(nombre="Hardware")
    db.add(categoria)
    db.commit()
    crear_solicitud(db, e["laura"], e["carlos"], categoria_id=categoria.id, prioridad="alta")
    como(e["coordinador"])

    item = client.get(URL).json()["data"][0]

    assert set(item) == {
        "id", "numero", "titulo", "tipo", "prioridad", "estado",
        "categoria", "solicitante", "tecnico_asignado", "fecha_creacion",
    }
    assert item["categoria"] == {"id": str(categoria.id), "nombre": "Hardware"}
    assert item["prioridad"] == "alta"


def test_solo_cuenta_la_asignacion_activa(client, db, e):
    """Tras una reasignación se muestra el técnico nuevo, no el anterior."""
    solicitud = crear_solicitud(db, e["laura"], e["carlos"], activa=False)
    db.add(Asignacion(solicitud_id=solicitud.id, tecnico_id=e["luis"].id, asignado_por=e["coordinador"].id))
    db.commit()
    como(e["coordinador"])

    respuesta = client.get(URL)

    assert respuesta.json()["pagination"]["total"] == 1
    assert respuesta.json()["data"][0]["tecnico_asignado"]["nombre"] == "Luis Díaz"


def test_coordinador_filtra_por_tecnico(client, db, e):
    de_carlos = crear_solicitud(db, e["laura"], e["carlos"])
    crear_solicitud(db, e["laura"], e["luis"])
    crear_solicitud(db, e["laura"], e["carlos"], activa=False)  # ya no es suya
    crear_solicitud(db, e["pedro"])
    como(e["coordinador"])

    respuesta = client.get(URL, params={"tecnico_id": str(e["carlos"].id)})

    assert ids(respuesta) == [str(de_carlos.id)]
    assert respuesta.json()["pagination"]["total"] == 1


def test_coordinador_filtra_por_solicitante(client, db, e):
    de_pedro = crear_solicitud(db, e["pedro"])
    crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    assert ids(client.get(URL, params={"solicitante_id": str(e["pedro"].id)})) == [str(de_pedro.id)]


def test_coordinador_filtra_por_tipo_de_cierre(client, db, e):
    crear_solicitud(db, e["laura"], estado="cerrado", tipo_cierre="solucion")
    cancelada = crear_solicitud(db, e["laura"], estado="cerrado", tipo_cierre="cancelacion")
    crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    assert ids(client.get(URL, params={"tipo_cierre": "cancelacion"})) == [str(cancelada.id)]


def test_coordinador_filtra_por_estado_prioridad_y_busqueda(client, db, e):
    crear_solicitud(db, e["laura"], estado="registrado", prioridad="baja", titulo="Impresora")
    objetivo = crear_solicitud(db, e["pedro"], estado="en_evaluacion", prioridad="alta", titulo="Monitor roto")
    como(e["coordinador"])

    assert ids(client.get(URL, params={"estado": "en_evaluacion"})) == [str(objetivo.id)]
    assert ids(client.get(URL, params={"prioridad": "alta"})) == [str(objetivo.id)]
    assert ids(client.get(URL, params={"busqueda": "MONITOR"})) == [str(objetivo.id)]
    assert ids(client.get(URL, params={"busqueda": objetivo.numero})) == [str(objetivo.id)]


def test_coordinador_paginacion(client, db, e):
    for _ in range(25):
        crear_solicitud(db, e["laura"])
    como(e["coordinador"])

    pagina_3 = client.get(URL, params={"page": 3, "limit": 10}).json()

    assert len(pagina_3["data"]) == 5
    assert pagina_3["pagination"] == {"page": 3, "limit": 10, "total": 25, "total_pages": 3}


@pytest.mark.parametrize(
    "params",
    [{"tipo_cierre": "otro"}, {"tecnico_id": "no-uuid"}, {"estado": "inventado"}, {"limit": 101}],
)
def test_filtros_invalidos_devuelven_422(client, e, params):
    como(e["coordinador"])

    assert client.get(URL, params=params).status_code == 422


def test_listado_sin_sesion_devuelve_401(client):
    assert client.get(URL).status_code == 401


# ----------------------------------- detalle ----------------------------------


def test_detalle_para_el_solicitante_propietario(client, db, e):
    categoria = Categoria(nombre="Redes")
    db.add(categoria)
    db.commit()
    solicitud = crear_solicitud(
        db, e["laura"], e["carlos"], categoria_id=categoria.id, placa_equipo="EQ-001"
    )
    como(e["laura"])

    respuesta = client.get(f"{URL}/{solicitud.id}")

    assert respuesta.status_code == 200
    d = respuesta.json()
    assert d["id"] == str(solicitud.id)
    assert d["descripcion"] == "Descripción"
    assert d["ubicacion"] == "Oficina"
    assert d["placa_equipo"] == "EQ-001"
    assert d["solicitante"]["nombre"] == "Laura Docente"
    assert d["categoria"]["nombre"] == "Redes"
    assert d["tecnico_asignado"]["nombre"] == "Carlos Gómez"
    assert d["tipo_cierre"] is None


def test_detalle_de_solicitud_cerrada_muestra_el_resultado(client, db, e):
    """CA-05: el solicitante puede consultar el resultado de su caso cerrado."""
    solicitud = crear_solicitud(
        db,
        e["laura"],
        estado="cerrado",
        solucion_final="Se reemplazó el cable de poder.",
        tipo_cierre="solucion",
        cerrado_por=e["coordinador"].id,
        fecha_cierre=datetime(2026, 11, 5),
    )
    como(e["laura"])

    d = client.get(f"{URL}/{solicitud.id}").json()

    assert d["estado"] == "cerrado"
    assert d["tipo_cierre"] == "solucion"
    assert d["solucion_final"] == "Se reemplazó el cable de poder."
    assert d["fecha_cierre"] is not None


def test_otro_solicitante_no_ve_el_detalle(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])
    como(e["pedro"])

    respuesta = client.get(f"{URL}/{solicitud.id}")

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_tecnico_asignado_ve_el_detalle(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], e["carlos"])
    como(e["carlos"])

    assert client.get(f"{URL}/{solicitud.id}").status_code == 200


def test_tecnico_no_asignado_no_ve_el_detalle(client, db, e):
    solicitud = crear_solicitud(db, e["laura"], e["carlos"])
    como(e["luis"])

    assert client.get(f"{URL}/{solicitud.id}").status_code == 403


def test_tecnico_reasignado_pierde_el_acceso(client, db, e):
    """RN-14: el técnico anterior pierde el acceso tras la reasignación."""
    solicitud = crear_solicitud(db, e["laura"], e["carlos"], activa=False)
    db.add(Asignacion(solicitud_id=solicitud.id, tecnico_id=e["luis"].id, asignado_por=e["coordinador"].id))
    db.commit()

    como(e["carlos"])
    assert client.get(f"{URL}/{solicitud.id}").status_code == 403

    como(e["luis"])
    assert client.get(f"{URL}/{solicitud.id}").status_code == 200


def test_coordinador_ve_cualquier_detalle(client, db, e):
    solicitud = crear_solicitud(db, e["pedro"])
    como(e["coordinador"])

    respuesta = client.get(f"{URL}/{solicitud.id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["tecnico_asignado"] is None


def test_detalle_de_solicitud_inexistente_devuelve_404(client, e):
    como(e["coordinador"])

    respuesta = client.get(f"{URL}/{uuid.uuid4()}")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_detalle_con_id_invalido_devuelve_422(client, e):
    como(e["coordinador"])

    assert client.get(f"{URL}/no-es-un-uuid").status_code == 422


def test_detalle_sin_sesion_devuelve_401(client, db, e):
    solicitud = crear_solicitud(db, e["laura"])

    assert client.get(f"{URL}/{solicitud.id}").status_code == 401
