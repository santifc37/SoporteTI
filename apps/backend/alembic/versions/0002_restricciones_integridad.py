"""Restricciones de integridad estables (MER.md 3.1)

Agrega a la base de datos solo las reglas baratas y que no suelen cambiar:
  - CHECK de valores controlados (rol, tipo, prioridad, estado, tipo de cierre,
    visibilidad y estado de las peticiones de informacion).
  - CHECK de adjuntos: pertenece a un mensaje o a una intervencion, no a ambos.
  - Trigger que vuelve inmutable la tabla historial_cambios.

Las demas reglas (transiciones de estado, RN-35, datos de contacto, tipo y
tamano de adjuntos, valores de tipo_cambio) se validan en el backend.

Revision ID: 0002_restricciones_integridad
Revises: 0001_esquema_inicial
Create Date: 2026-11-08
"""

from alembic import op

# Identificadores de la revision usados por Alembic.
revision = "0002_restricciones_integridad"
down_revision = "0001_esquema_inicial"
branch_labels = None
depends_on = None


# (tabla, nombre de la restriccion, condicion)
# Las columnas que aceptan NULL (prioridad, tipo_cierre) pasan el CHECK con
# NULL, porque en SQL una condicion NULL no se considera violada.
CHECKS = [
    ("usuarios", "ck_usuarios_rol",
     "rol IN ('solicitante', 'tecnico', 'coordinador')"),
    ("solicitudes", "ck_solicitudes_tipo",
     "tipo IN ('incidente', 'requerimiento')"),
    ("solicitudes", "ck_solicitudes_prioridad",
     "prioridad IN ('baja', 'media', 'alta')"),
    ("solicitudes", "ck_solicitudes_estado",
     "estado IN ('registrado', 'en_evaluacion', 'asignado', 'en_atencion', "
     "'en_espera', 'resuelto', 'cerrado')"),
    ("solicitudes", "ck_solicitudes_tipo_cierre",
     "tipo_cierre IN ('solucion', 'cancelacion', 'administrativo')"),
    ("intervenciones", "ck_intervenciones_visibilidad",
     "visibilidad IN ('interna', 'solicitante')"),
    ("solicitudes_informacion", "ck_solicitudes_informacion_estado",
     "estado IN ('pendiente', 'respondida')"),
    # Con ambos NULL el adjunto queda ligado solo a la solicitud.
    ("adjuntos", "ck_adjuntos_un_solo_origen",
     "num_nonnulls(mensaje_id, intervencion_id) <= 1"),
]


# ---------------------------------------------------------------------------
# historial_cambios inmutable
# ---------------------------------------------------------------------------

TRIGGERS = [
    """
    CREATE FUNCTION fn_historial_inmutable() RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'historial_cambios es inmutable: no se permite %', TG_OP
            USING ERRCODE = 'integrity_constraint_violation';
    END;
    $$ LANGUAGE plpgsql
    """,
    """
    CREATE TRIGGER tg_historial_inmutable
        BEFORE UPDATE OR DELETE ON historial_cambios
        FOR EACH ROW EXECUTE FUNCTION fn_historial_inmutable()
    """,
    # TRUNCATE no dispara triggers por fila; se bloquea con uno por sentencia.
    """
    CREATE TRIGGER tg_historial_inmutable_truncate
        BEFORE TRUNCATE ON historial_cambios
        FOR EACH STATEMENT EXECUTE FUNCTION fn_historial_inmutable()
    """,
]


def upgrade() -> None:
    for tabla, nombre, condicion in CHECKS:
        op.execute(f"ALTER TABLE {tabla} ADD CONSTRAINT {nombre} CHECK ({condicion})")
    for sentencia in TRIGGERS:
        op.execute(sentencia)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS tg_historial_inmutable_truncate ON historial_cambios")
    op.execute("DROP TRIGGER IF EXISTS tg_historial_inmutable ON historial_cambios")
    op.execute("DROP FUNCTION IF EXISTS fn_historial_inmutable()")
    for tabla, nombre, _ in reversed(CHECKS):
        op.execute(f"ALTER TABLE {tabla} DROP CONSTRAINT IF EXISTS {nombre}")
