"""Esquema inicial de SoporteTI

Crea las tablas de docs/MER.md (v1.2) con sus claves primarias y foraneas,
campos unicos, secuencia del numero de solicitud e indices recomendados.

Las restricciones CHECK y el trigger del historial inmutable (MER.md 3.1)
se agregaran en una migracion posterior.

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-11-07
"""

from alembic import op

# Identificadores de la revision usados por Alembic.
revision = "0001_esquema_inicial"
down_revision = None
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------
# Se usa SQL explicito para que la estructura sea facil de comparar con
# docs/MER.md y de revisar en el Pull Request.
# - gen_random_uuid() viene incluido en PostgreSQL 13+ (Supabase ya lo tiene).
# - Todas las claves foraneas usan ON DELETE RESTRICT: no se eliminan
#   registros de negocio (MER.md, seccion 2).

TABLAS = [
    # ----------------------------- usuarios --------------------------------
    """
    CREATE TABLE usuarios (
        id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nombre                    VARCHAR(100) NOT NULL,
        apellido                  VARCHAR(100) NOT NULL,
        correo                    VARCHAR(255) NOT NULL,
        password_hash             VARCHAR(255) NOT NULL,
        rol                       VARCHAR(20)  NOT NULL,
        activo                    BOOLEAN      NOT NULL DEFAULT TRUE,
        medio_contacto_preferido  VARCHAR(20)  NOT NULL DEFAULT 'correo',
        telefono                  VARCHAR(20),
        fecha_creacion            TIMESTAMPTZ  NOT NULL DEFAULT now(),
        fecha_actualizacion       TIMESTAMPTZ  NOT NULL DEFAULT now()
    )
    """,
    # El correo es unico sin importar mayusculas/minusculas.
    "CREATE UNIQUE INDEX uq_usuarios_correo ON usuarios (lower(correo))",

    # ----------------------------- sesiones --------------------------------
    """
    CREATE TABLE sesiones (
        id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        usuario_id        UUID         NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        token_hash        VARCHAR(255) NOT NULL UNIQUE,
        fecha_creacion    TIMESTAMPTZ  NOT NULL DEFAULT now(),
        fecha_expiracion  TIMESTAMPTZ  NOT NULL,
        revocada          BOOLEAN      NOT NULL DEFAULT FALSE
    )
    """,
    "CREATE INDEX ix_sesiones_usuario_activas ON sesiones (usuario_id) WHERE revocada = FALSE",

    # ---------------------------- categorias -------------------------------
    """
    CREATE TABLE categorias (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nombre          VARCHAR(100) NOT NULL,
        descripcion     TEXT,
        activa          BOOLEAN      NOT NULL DEFAULT TRUE,
        fecha_creacion  TIMESTAMPTZ  NOT NULL DEFAULT now()
    )
    """,
    "CREATE UNIQUE INDEX uq_categorias_nombre ON categorias (lower(nombre))",

    # ---------------------------- solicitudes ------------------------------
    # Numero legible ST-000001, ST-000002, ... generado por la base de datos.
    "CREATE SEQUENCE solicitudes_numero_seq START 1",
    """
    CREATE TABLE solicitudes (
        id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        numero               VARCHAR(20)  NOT NULL UNIQUE
                             DEFAULT 'ST-' || lpad(nextval('solicitudes_numero_seq')::text, 6, '0'),
        titulo               VARCHAR(200) NOT NULL,
        descripcion          TEXT         NOT NULL,
        tipo                 VARCHAR(20)  NOT NULL,
        solicitante_id       UUID         NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        categoria_id         UUID         REFERENCES categorias (id) ON DELETE RESTRICT,
        prioridad            VARCHAR(10),
        estado               VARCHAR(20)  NOT NULL DEFAULT 'registrado',
        ubicacion            VARCHAR(200) NOT NULL,
        placa_equipo         VARCHAR(50),
        medio_contacto       VARCHAR(20)  NOT NULL,
        dato_contacto        VARCHAR(255) NOT NULL,
        solucion_final       TEXT,
        resuelto_por         UUID         REFERENCES usuarios (id) ON DELETE RESTRICT,
        fecha_resolucion     TIMESTAMPTZ,
        tipo_cierre          VARCHAR(20),
        motivo_cierre        TEXT,
        cerrado_por          UUID         REFERENCES usuarios (id) ON DELETE RESTRICT,
        fecha_cierre         TIMESTAMPTZ,
        version              INTEGER      NOT NULL DEFAULT 1,
        fecha_creacion       TIMESTAMPTZ  NOT NULL DEFAULT now(),
        fecha_actualizacion  TIMESTAMPTZ  NOT NULL DEFAULT now()
    )
    """,
    "ALTER SEQUENCE solicitudes_numero_seq OWNED BY solicitudes.numero",
    "CREATE INDEX ix_solicitudes_solicitante ON solicitudes (solicitante_id, fecha_creacion DESC)",
    "CREATE INDEX ix_solicitudes_estado_prioridad ON solicitudes (estado, prioridad)",
    "CREATE INDEX ix_solicitudes_categoria ON solicitudes (categoria_id)",

    # --------------------------- asignaciones ------------------------------
    """
    CREATE TABLE asignaciones (
        id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id        UUID        NOT NULL REFERENCES solicitudes (id) ON DELETE RESTRICT,
        tecnico_id          UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        asignado_por        UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        observacion         TEXT,
        fecha_asignacion    TIMESTAMPTZ NOT NULL DEFAULT now(),
        fecha_finalizacion  TIMESTAMPTZ
    )
    """,
    # Solo una asignacion activa (fecha_finalizacion NULL) por solicitud.
    """
    CREATE UNIQUE INDEX uq_asignacion_activa
        ON asignaciones (solicitud_id) WHERE fecha_finalizacion IS NULL
    """,
    """
    CREATE INDEX ix_asignaciones_tecnico_activas
        ON asignaciones (tecnico_id) WHERE fecha_finalizacion IS NULL
    """,
    "CREATE INDEX ix_asignaciones_solicitud ON asignaciones (solicitud_id, fecha_asignacion)",

    # ----------------------------- mensajes --------------------------------
    """
    CREATE TABLE mensajes (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id  UUID        NOT NULL REFERENCES solicitudes (id) ON DELETE RESTRICT,
        remitente_id  UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        contenido     TEXT        NOT NULL,
        fecha_envio   TIMESTAMPTZ NOT NULL DEFAULT now(),

        -- Permite que los adjuntos verifiquen que el mensaje es de la misma solicitud.
        CONSTRAINT uq_mensajes_solicitud UNIQUE (solicitud_id, id)
    )
    """,
    "CREATE INDEX ix_mensajes_solicitud ON mensajes (solicitud_id, fecha_envio)",

    # --------------------- solicitudes_informacion -------------------------
    """
    CREATE TABLE solicitudes_informacion (
        id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id     UUID        NOT NULL REFERENCES solicitudes (id) ON DELETE RESTRICT,
        solicitado_por   UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        contenido        TEXT        NOT NULL,
        estado           VARCHAR(20) NOT NULL DEFAULT 'pendiente',
        fecha_solicitud  TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE INDEX ix_solicitudes_informacion_solicitud
        ON solicitudes_informacion (solicitud_id, estado)
    """,

    # ---------------------- respuestas_informacion -------------------------
    """
    CREATE TABLE respuestas_informacion (
        id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_informacion_id  UUID        NOT NULL UNIQUE
                                  REFERENCES solicitudes_informacion (id) ON DELETE RESTRICT,
        respondido_por            UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        contenido                 TEXT        NOT NULL,
        fecha_respuesta           TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,

    # -------------------------- intervenciones -----------------------------
    """
    CREATE TABLE intervenciones (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id    UUID        NOT NULL REFERENCES solicitudes (id) ON DELETE RESTRICT,
        tecnico_id      UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        descripcion     TEXT        NOT NULL,
        diagnostico     TEXT,
        visibilidad     VARCHAR(20) NOT NULL DEFAULT 'interna',
        fecha_registro  TIMESTAMPTZ NOT NULL DEFAULT now(),

        -- Permite que los adjuntos verifiquen que la intervencion es de la misma solicitud.
        CONSTRAINT uq_intervenciones_solicitud UNIQUE (solicitud_id, id)
    )
    """,
    "CREATE INDEX ix_intervenciones_solicitud ON intervenciones (solicitud_id, fecha_registro)",

    # ------------------------- historial_cambios ---------------------------
    """
    CREATE TABLE historial_cambios (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id    UUID        NOT NULL REFERENCES solicitudes (id) ON DELETE RESTRICT,
        usuario_id      UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        tipo_cambio     VARCHAR(30) NOT NULL,
        valor_anterior  TEXT,
        valor_nuevo     TEXT,
        observacion     TEXT,
        fecha_cambio    TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX ix_historial_solicitud ON historial_cambios (solicitud_id, fecha_cambio)",

    # ----------------------------- adjuntos --------------------------------
    # Las claves compuestas garantizan que el mensaje o la intervencion
    # pertenezcan a la misma solicitud del adjunto (MER.md 3.1).
    """
    CREATE TABLE adjuntos (
        id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        solicitud_id     UUID         NOT NULL REFERENCES solicitudes (id) ON DELETE RESTRICT,
        mensaje_id       UUID,
        intervencion_id  UUID,
        subido_por       UUID         NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        nombre_archivo   VARCHAR(255) NOT NULL,
        ruta_storage     VARCHAR(500) NOT NULL UNIQUE,
        tipo_archivo     VARCHAR(50)  NOT NULL,
        tamano           BIGINT       NOT NULL,
        fecha_subida     TIMESTAMPTZ  NOT NULL DEFAULT now(),

        CONSTRAINT fk_adjuntos_mensaje
            FOREIGN KEY (solicitud_id, mensaje_id)
            REFERENCES mensajes (solicitud_id, id) ON DELETE RESTRICT,
        CONSTRAINT fk_adjuntos_intervencion
            FOREIGN KEY (solicitud_id, intervencion_id)
            REFERENCES intervenciones (solicitud_id, id) ON DELETE RESTRICT
    )
    """,
    "CREATE INDEX ix_adjuntos_solicitud ON adjuntos (solicitud_id)",

    # -------------------------- notificaciones -----------------------------
    # Solo internas a la plataforma; implementacion en una fase posterior.
    """
    CREATE TABLE notificaciones (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        usuario_id      UUID        NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
        solicitud_id    UUID        REFERENCES solicitudes (id) ON DELETE RESTRICT,
        tipo            VARCHAR(50) NOT NULL,
        contenido       TEXT        NOT NULL,
        leida           BOOLEAN     NOT NULL DEFAULT FALSE,
        fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX ix_notificaciones_usuario ON notificaciones (usuario_id, leida)",
]


# ---------------------------------------------------------------------------
# fecha_actualizacion automatica
# ---------------------------------------------------------------------------

TRIGGERS = [
    """
    CREATE FUNCTION fn_actualizar_fecha_actualizacion() RETURNS trigger AS $$
    BEGIN
        NEW.fecha_actualizacion := now();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql
    """,
    """
    CREATE TRIGGER tg_usuarios_fecha_actualizacion
        BEFORE UPDATE ON usuarios
        FOR EACH ROW EXECUTE FUNCTION fn_actualizar_fecha_actualizacion()
    """,
    """
    CREATE TRIGGER tg_solicitudes_fecha_actualizacion
        BEFORE UPDATE ON solicitudes
        FOR EACH ROW EXECUTE FUNCTION fn_actualizar_fecha_actualizacion()
    """,
]


# ---------------------------------------------------------------------------
# Seguridad en Supabase
# ---------------------------------------------------------------------------
# Supabase expone las tablas del esquema public por su API REST (anon key).
# Activar RLS sin politicas bloquea ese acceso directo: solo el backend
# (conectado como el usuario propietario de las tablas) puede leer y escribir.

TABLAS_CON_RLS = [
    "usuarios", "sesiones", "categorias", "solicitudes", "asignaciones",
    "mensajes", "solicitudes_informacion", "respuestas_informacion",
    "intervenciones", "historial_cambios", "adjuntos", "notificaciones",
]


def upgrade() -> None:
    for sentencia in TABLAS + TRIGGERS:
        op.execute(sentencia)
    for tabla in TABLAS_CON_RLS:
        op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    # Orden inverso a las dependencias de claves foraneas.
    for tabla in [
        "notificaciones", "adjuntos", "historial_cambios", "intervenciones",
        "respuestas_informacion", "solicitudes_informacion", "mensajes",
        "asignaciones", "solicitudes", "categorias", "sesiones", "usuarios",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {tabla}")
    op.execute("DROP SEQUENCE IF EXISTS solicitudes_numero_seq")
    op.execute("DROP FUNCTION IF EXISTS fn_actualizar_fecha_actualizacion()")
