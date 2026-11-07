# Modelo entidad-relación — SoporteTI

**Versión:** 1.1  
**Estado:** Modelo de datos revisado  
**Proyecto:** SoporteTI  
**Base de datos:** PostgreSQL (Supabase)

Este modelo desarrolla la sección 6 de `docs/diseno.md` y es coherente con `docs/requisitos.md` y `docs/contrato-api.md`. Si hay diferencias, este documento refleja la decisión más reciente del equipo.

## 1. Diagrama

```mermaid
erDiagram
    USUARIOS {
        UUID id PK
        VARCHAR nombre
        VARCHAR apellido
        VARCHAR correo UK
        VARCHAR password_hash
        VARCHAR rol "solicitante | tecnico | coordinador"
        BOOLEAN activo
        VARCHAR medio_contacto_preferido "correo | telefono"
        VARCHAR telefono "nullable"
        TIMESTAMPTZ fecha_creacion
        TIMESTAMPTZ fecha_actualizacion
    }

    SESIONES {
        UUID id PK
        UUID usuario_id FK
        VARCHAR token_hash UK
        TIMESTAMPTZ fecha_creacion
        TIMESTAMPTZ fecha_expiracion
        BOOLEAN revocada
    }

    CATEGORIAS {
        UUID id PK
        VARCHAR nombre UK
        TEXT descripcion
        BOOLEAN activa
        TIMESTAMPTZ fecha_creacion
    }

    SOLICITUDES {
        UUID id PK
        VARCHAR numero UK "ST-000001, generado por secuencia"
        VARCHAR titulo
        TEXT descripcion
        VARCHAR tipo "incidente | requerimiento"
        UUID solicitante_id FK
        UUID categoria_id FK "nullable"
        VARCHAR prioridad "baja | media | alta, nullable"
        VARCHAR estado "registrado | en_evaluacion | asignado | en_atencion | en_espera | resuelto | cerrado"
        VARCHAR ubicacion
        VARCHAR placa_equipo "nullable"
        VARCHAR medio_contacto "correo | telefono"
        VARCHAR dato_contacto
        TEXT solucion_final "nullable, unica fuente de la solucion"
        UUID resuelto_por FK "nullable"
        TIMESTAMPTZ fecha_resolucion "nullable"
        VARCHAR tipo_cierre "solucion | cancelacion | administrativo, nullable"
        TEXT motivo_cierre "nullable"
        UUID cerrado_por FK "nullable"
        TIMESTAMPTZ fecha_cierre "nullable"
        INTEGER version "bloqueo optimista"
        TIMESTAMPTZ fecha_creacion
        TIMESTAMPTZ fecha_actualizacion
    }

    ASIGNACIONES {
        UUID id PK
        UUID solicitud_id FK
        UUID tecnico_id FK
        UUID asignado_por FK
        TEXT observacion "nullable"
        TIMESTAMPTZ fecha_asignacion
        TIMESTAMPTZ fecha_finalizacion "NULL = asignacion activa"
    }

    MENSAJES {
        UUID id PK
        UUID solicitud_id FK
        UUID remitente_id FK
        TEXT contenido
        TIMESTAMPTZ fecha_envio
    }

    SOLICITUDES_INFORMACION {
        UUID id PK
        UUID solicitud_id FK
        UUID solicitado_por FK
        TEXT contenido
        VARCHAR estado "pendiente | respondida"
        TIMESTAMPTZ fecha_solicitud
    }

    RESPUESTAS_INFORMACION {
        UUID id PK
        UUID solicitud_informacion_id FK, UK
        UUID respondido_por FK
        TEXT contenido
        TIMESTAMPTZ fecha_respuesta
    }

    INTERVENCIONES {
        UUID id PK
        UUID solicitud_id FK
        UUID tecnico_id FK
        TEXT descripcion
        TEXT diagnostico "nullable"
        VARCHAR visibilidad "interna | solicitante"
        TIMESTAMPTZ fecha_registro
    }

    HISTORIAL_CAMBIOS {
        UUID id PK
        UUID solicitud_id FK
        UUID usuario_id FK
        VARCHAR tipo_cambio "creacion | cambio_estado | cambio_prioridad | cambio_categoria | asignacion | reasignacion | solucion | cierre_solucion | cierre_administrativo | cancelacion"
        TEXT valor_anterior "nullable"
        TEXT valor_nuevo "nullable"
        TEXT observacion "nullable"
        TIMESTAMPTZ fecha_cambio
    }

    ADJUNTOS {
        UUID id PK
        UUID solicitud_id FK
        UUID mensaje_id FK "nullable"
        UUID intervencion_id FK "nullable"
        UUID subido_por FK
        VARCHAR nombre_archivo
        VARCHAR ruta_storage UK
        VARCHAR tipo_archivo "image/png | image/jpeg"
        BIGINT tamano "bytes, max 5242880"
        TIMESTAMPTZ fecha_subida
    }

    NOTIFICACIONES {
        UUID id PK
        UUID usuario_id FK
        UUID solicitud_id FK "nullable"
        VARCHAR tipo "evento que origina el aviso"
        TEXT contenido
        VARCHAR canal "plataforma | correo"
        VARCHAR estado_envio "pendiente | enviada | fallida"
        BOOLEAN leida
        TIMESTAMPTZ fecha_creacion
        TIMESTAMPTZ fecha_envio "nullable"
    }

    USUARIOS ||--o{ SESIONES : inicia

    USUARIOS ||--o{ SOLICITUDES : crea
    CATEGORIAS |o--o{ SOLICITUDES : clasifica
    USUARIOS |o--o{ SOLICITUDES : resuelve
    USUARIOS |o--o{ SOLICITUDES : cierra

    SOLICITUDES ||--o{ ASIGNACIONES : tiene
    USUARIOS ||--o{ ASIGNACIONES : es_tecnico
    USUARIOS ||--o{ ASIGNACIONES : asigna

    SOLICITUDES ||--o{ MENSAJES : contiene
    USUARIOS ||--o{ MENSAJES : envia

    SOLICITUDES ||--o{ SOLICITUDES_INFORMACION : genera
    USUARIOS ||--o{ SOLICITUDES_INFORMACION : solicita
    SOLICITUDES_INFORMACION ||--o| RESPUESTAS_INFORMACION : recibe
    USUARIOS ||--o{ RESPUESTAS_INFORMACION : responde

    SOLICITUDES ||--o{ INTERVENCIONES : recibe
    USUARIOS ||--o{ INTERVENCIONES : registra

    SOLICITUDES ||--o{ HISTORIAL_CAMBIOS : registra
    USUARIOS ||--o{ HISTORIAL_CAMBIOS : ejecuta

    SOLICITUDES ||--o{ ADJUNTOS : adjunta
    MENSAJES |o--o{ ADJUNTOS : adjunta
    INTERVENCIONES |o--o{ ADJUNTOS : adjunta
    USUARIOS ||--o{ ADJUNTOS : sube

    USUARIOS ||--o{ NOTIFICACIONES : recibe
    SOLICITUDES |o--o{ NOTIFICACIONES : relaciona
```

## 2. Decisiones de modelado

**La solución tiene una sola fuente.** `solicitudes.solucion_final` guarda la solución definitiva, junto con `resuelto_por` y `fecha_resolucion`. Las intervenciones solo registran descripción y diagnóstico. El endpoint `/resolve` escribe estos tres campos y cambia el estado a `resuelto` en una misma transacción.

**Los tiempos de atención se calculan sin analizar texto.** Con `fecha_creacion`, `fecha_resolucion` y `fecha_cierre` se obtienen el tiempo hasta la resolución y el tiempo total del caso (RF-29, CA-06).

**El historial distingue cada tipo de cierre.** `cierre_solucion`, `cierre_administrativo` y `cancelacion` son valores distintos de `tipo_cambio`, como exige `diseno.md` §13.

**El técnico responsable no se duplica.** Se obtiene de la asignación con `fecha_finalizacion IS NULL`.

**Los datos de contacto de la solicitud son una copia intencional.** `medio_contacto` y `dato_contacto` pueden diferir de los de la cuenta del usuario (RF-06).

**El estado de una petición de información se actualiza solo al registrar su respuesta.** Aunque se puede deducir de la existencia de la respuesta, se conserva para consultas y filtros. Lo modifica únicamente la transacción que inserta la respuesta.

**No hay tabla de recuperación de contraseña.** La v1 permite cambiar la contraseña propia y que el coordinador la restablezca; no hay recuperación por correo o SMS.

**Las notificaciones son una fase posterior.** La tabla se mantiene en el modelo, pero su implementación no es necesaria para los flujos principales.

**No se eliminan registros de negocio.** Usuarios y categorías se desactivan (`activo`, `activa`). Todas las claves foráneas usan `ON DELETE RESTRICT`.

## 3. Reglas de integridad

Estas reglas no se ven en el diagrama. Deben implementarse en las migraciones de Alembic o en los servicios.

### 3.1. En la base de datos

| Regla | Mecanismo |
|---|---|
| Una solicitud tiene como máximo una asignación activa | Índice único parcial |
| `numero` único y sin colisiones en concurrencia | Secuencia de PostgreSQL |
| Valores controlados de rol, estado, prioridad, tipo, tipo de cierre, visibilidad, canal y estados de envío | `CHECK` |
| Una solicitud cerrada tiene tipo, responsable y fecha de cierre; la cancelación y el cierre administrativo exigen motivo; el cierre por solución exige `solucion_final` | `CHECK` (RN-35) |
| `solucion_final`, `resuelto_por` y `fecha_resolucion` se registran juntos | `CHECK` |
| Si el medio preferido es teléfono, el teléfono es obligatorio | `CHECK` |
| Un adjunto pertenece a un mensaje o a una intervención, no a ambos, y estos corresponden a la misma solicitud | `CHECK` y claves foráneas compuestas |
| Una petición de información tiene como máximo una respuesta | `UNIQUE` en `solicitud_informacion_id` |
| El historial no se modifica ni se elimina | Trigger |
| Un adjunto no supera 5 MB y es PNG o JPEG | `CHECK` en `tamano` y `tipo_archivo` |

```sql
-- Secuencia para el número legible (ST-000001)
CREATE SEQUENCE solicitudes_numero_seq;
ALTER TABLE solicitudes
  ALTER COLUMN numero SET DEFAULT 'ST-' || lpad(nextval('solicitudes_numero_seq')::text, 6, '0');

-- Una sola asignación activa por solicitud
CREATE UNIQUE INDEX uq_asignacion_activa
  ON asignaciones (solicitud_id) WHERE fecha_finalizacion IS NULL;

-- Valores controlados (ejemplos)
ALTER TABLE usuarios
  ADD CONSTRAINT ck_usuarios_rol CHECK (rol IN ('solicitante', 'tecnico', 'coordinador')),
  ADD CONSTRAINT ck_usuarios_medio CHECK (medio_contacto_preferido IN ('correo', 'telefono')),
  ADD CONSTRAINT ck_usuarios_telefono
    CHECK (medio_contacto_preferido <> 'telefono' OR telefono IS NOT NULL);

ALTER TABLE solicitudes
  ADD CONSTRAINT ck_solicitudes_tipo CHECK (tipo IN ('incidente', 'requerimiento')),
  ADD CONSTRAINT ck_solicitudes_prioridad CHECK (prioridad IN ('baja', 'media', 'alta')),
  ADD CONSTRAINT ck_solicitudes_estado CHECK (estado IN (
    'registrado', 'en_evaluacion', 'asignado', 'en_atencion', 'en_espera', 'resuelto', 'cerrado')),
  ADD CONSTRAINT ck_solicitudes_tipo_cierre
    CHECK (tipo_cierre IN ('solucion', 'cancelacion', 'administrativo'));

-- Coherencia del cierre
ALTER TABLE solicitudes ADD CONSTRAINT ck_solicitudes_cierre CHECK (
  (estado <> 'cerrado'
     AND tipo_cierre IS NULL AND motivo_cierre IS NULL
     AND cerrado_por IS NULL AND fecha_cierre IS NULL)
  OR
  (estado = 'cerrado'
     AND tipo_cierre IS NOT NULL AND cerrado_por IS NOT NULL AND fecha_cierre IS NOT NULL
     AND (tipo_cierre = 'solucion' OR motivo_cierre IS NOT NULL)
     AND (tipo_cierre <> 'solucion' OR solucion_final IS NOT NULL))
);

-- Coherencia de la resolución
ALTER TABLE solicitudes ADD CONSTRAINT ck_solicitudes_resolucion CHECK (
  (solucion_final IS NULL) = (resuelto_por IS NULL)
  AND (resuelto_por IS NULL) = (fecha_resolucion IS NULL)
);

-- Adjuntos: un solo origen y coherencia con la solicitud
ALTER TABLE mensajes
  ADD CONSTRAINT uq_mensajes_solicitud UNIQUE (solicitud_id, id);
ALTER TABLE intervenciones
  ADD CONSTRAINT uq_intervenciones_solicitud UNIQUE (solicitud_id, id);
ALTER TABLE adjuntos
  ADD CONSTRAINT ck_adjuntos_un_origen CHECK (mensaje_id IS NULL OR intervencion_id IS NULL),
  ADD CONSTRAINT ck_adjuntos_tipo CHECK (tipo_archivo IN ('image/png', 'image/jpeg')),
  ADD CONSTRAINT ck_adjuntos_tamano CHECK (tamano > 0 AND tamano <= 5242880),
  ADD CONSTRAINT fk_adjuntos_mensaje
    FOREIGN KEY (solicitud_id, mensaje_id) REFERENCES mensajes (solicitud_id, id),
  ADD CONSTRAINT fk_adjuntos_intervencion
    FOREIGN KEY (solicitud_id, intervencion_id) REFERENCES intervenciones (solicitud_id, id);

-- Historial inmutable
CREATE FUNCTION bloquear_modificacion() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'Los registros de % no pueden modificarse ni eliminarse', TG_TABLE_NAME;
END;
$$;
CREATE TRIGGER tg_historial_inmutable
  BEFORE UPDATE OR DELETE ON historial_cambios
  FOR EACH ROW EXECUTE FUNCTION bloquear_modificacion();
```

### 3.2. En el backend

Una clave foránea no puede verificar el rol del usuario ni el estado de la solicitud. Estas reglas se validan en los servicios, dentro de la misma transacción que la operación:

- `solicitudes.solicitante_id` corresponde a un usuario con rol `solicitante`.
- `asignaciones.tecnico_id` corresponde a un técnico activo y `asignado_por` a un coordinador.
- `intervenciones.tecnico_id` es el técnico asignado actualmente a la solicitud.
- `respuestas_informacion.respondido_por` es el solicitante propietario de la solicitud.
- `resuelto_por` es el técnico asignado, y `cerrado_por` es un coordinador, salvo en la cancelación, donde es el solicitante.
- Una solicitud en `asignado`, `en_atencion`, `en_espera` o `resuelto` tiene una asignación activa (RN-12).
- Las transiciones de estado siguen la matriz de `requisitos.md` §8.1.
- Una solicitud cerrada no admite nuevos mensajes, intervenciones, adjuntos ni peticiones (RN-22).
- Al desactivar un usuario o restablecer su contraseña se revocan sus sesiones.
- Cada cambio importante inserta su registro en `historial_cambios` dentro de la misma transacción (RN-30).
- La modificación concurrente de una solicitud se controla con `version`; si no coincide, se responde `409 CONFLICTO_CONCURRENCIA`.

## 4. Índices recomendados

| Tabla | Índice | Uso |
|---|---|---|
| `solicitudes` | `(solicitante_id, fecha_creacion DESC)` | Solicitudes propias |
| `solicitudes` | `(estado, prioridad)` | Bandeja y filtros del coordinador |
| `solicitudes` | `(categoria_id)` | Filtros y estadísticas |
| `asignaciones` | `(tecnico_id) WHERE fecha_finalizacion IS NULL` | Solicitudes asignadas al técnico |
| `asignaciones` | `(solicitud_id, fecha_asignacion)` | Historial de asignaciones |
| `mensajes` | `(solicitud_id, fecha_envio)` | Conversación en orden cronológico |
| `solicitudes_informacion` | `(solicitud_id, estado)` | Peticiones pendientes |
| `intervenciones` | `(solicitud_id, fecha_registro)` | Historial de intervenciones |
| `historial_cambios` | `(solicitud_id, fecha_cambio)` | Historial de una solicitud |
| `adjuntos` | `(solicitud_id)` | Adjuntos de una solicitud |
| `sesiones` | `(usuario_id) WHERE revocada = false` | Revocación de sesiones |
| `notificaciones` | `(usuario_id, leida)` | Avisos no leídos |

Las columnas con `UK` ya tienen índice único.

## 5. Cobertura de requisitos

| Criterio | Entidades principales |
|---|---|
| CA-01 Registro de casos | `solicitudes`, `usuarios`, `categorias`, `adjuntos` |
| CA-02 Evaluación y gestión | `solicitudes`, `historial_cambios` |
| CA-03 Responsable y estado | `asignaciones`, `solicitudes` |
| CA-04 Historial de intervenciones | `intervenciones`, `solicitudes_informacion`, `respuestas_informacion`, `mensajes`, `historial_cambios` |
| CA-05 Resultado y cierre | `solicitudes` (`solucion_final`, `tipo_cierre`, `motivo_cierre`, `fecha_cierre`) |
| CA-06 Consolidado | Consultas sobre `solicitudes` y `asignaciones` |