# SoporteTI

Sistema web para la gestión de solicitudes de soporte de tecnologías de la información. Permite registrar, evaluar, clasificar, asignar y atender solicitudes, mantener la comunicación entre los participantes y conservar la trazabilidad de cada caso.

**Asignatura:** Aplicaciones y Servicios Web  
**Institución:** Instituto Tecnológico Metropolitano (ITM)  
**Repositorio:** https://github.com/santifc37/SoporteTI

---

## 1. Descripción del sistema

SoporteTI busca centralizar el proceso de atención de incidentes y solicitudes de soporte tecnológico de una institución.

El sistema contempla tres roles:

- **Solicitante:** registra solicitudes, consulta su estado, participa en conversaciones, responde peticiones de información y consulta el resultado de la atención.
- **Técnico:** consulta sus solicitudes asignadas, registra intervenciones, solicita información adicional y documenta las soluciones.
- **Coordinador:** administra usuarios y categorías, evalúa solicitudes, asigna técnicos, supervisa la atención, revisa soluciones, cierra solicitudes y consulta estadísticas.

El sistema aplica permisos en el backend para restringir las operaciones según el rol y la relación del usuario con cada solicitud.

## 2. Alcance y requisitos

El proyecto contempla:

- Autenticación y control de acceso por roles.
- Administración de usuarios y datos de contacto.
- Registro y consulta de solicitudes.
- Evaluación, clasificación y asignación de solicitudes.
- Actualización controlada de estados.
- Registro y consulta de intervenciones técnicas.
- Solicitud y respuesta de información adicional.
- Registro de soluciones y cierre de solicitudes.
- Conversaciones y mensajes asociados a solicitudes.
- Adjuntos en solicitudes, mensajes e intervenciones.
- Notificaciones internas.
- Historial de cambios.
- Estadísticas para coordinación.

No se incluyen notificaciones por correo, SMS o WhatsApp, chat mediante WebSockets ni recuperación automática de contraseñas mediante servicios externos.

**Documentación:**
- [Requisitos funcionales y no funcionales](docs/requisitos.md).
- [Diseño de la solución](docs/diseno.md).
- [Contrato de la API](docs/contrato-api.md).
- [Guía de desarrollo](docs/guia-desarrollo.md).
- [Matriz de trazabilidad](docs/trazabilidad.md).

## 3. Arquitectura y tecnologías

La solución utiliza una arquitectura cliente-servidor:

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Frontend | React, TypeScript y Vite | Interfaz de usuario y consumo de la API. |
| Backend | Python y FastAPI | API REST, reglas de negocio y autorización. |
| Base de datos | PostgreSQL | Persistencia de usuarios, solicitudes y demás registros. |
| Plataforma de datos | Supabase | Servicio PostgreSQL. |
| Almacenamiento | Supabase Storage | Almacenamiento privado de archivos. |
| ORM | SQLAlchemy | Acceso y persistencia de datos. |
| Migraciones | Alembic | Evolución del esquema de base de datos. |
| Pruebas | pytest | Validación automatizada del backend. |

### Estructura principal

```text
SoporteTI/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── .env.example
│   │   └── requirements.txt
│   └── frontend/
├── docs/
├── evidencias/
├── proyecto2.md
└── README.md
```

El código fuente del frontend se encuentra actualmente en las ramas `feature/frontend-base` y `feature/frontend-solicitudes`; su integración en `feature/backend-integrado` está pendiente.

## 4. Configuración del entorno

### 4.1. Requisitos previos

- Git.
- Python.
- Node.js y npm para el frontend.
- Acceso al proyecto de Supabase.
- Bucket privado de Supabase Storage llamado `soporteti-adjuntos`.

### 4.2. Configuración del backend

Desde la raíz del repositorio:

```powershell
cd apps/backend
```

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crear el archivo de configuración:

```powershell
Copy-Item .env.example .env
```

Configurar las variables necesarias en `.env`:

```env
DATABASE_URL=postgresql://...

SUPABASE_URL=https://TU_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=TU_SERVICE_ROLE_KEY
SUPABASE_STORAGE_BUCKET=soporteti-adjuntos

SESSION_DURATION_HOURS=8
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

La variable `DATABASE_URL` corresponde a la conexión PostgreSQL. Las variables `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` se utilizan para acceder al almacenamiento.

**Seguridad:**
- No subir el archivo `.env` al repositorio.
- No exponer la clave `SUPABASE_SERVICE_ROLE_KEY` en el frontend.
- Mantener privado el bucket de adjuntos.
- Utilizar datos ficticios en las demostraciones.

### 4.3. Migraciones de base de datos

Desde `apps/backend`, con el entorno virtual activado:

```powershell
alembic upgrade head
```

Las migraciones se encuentran en:

```text
apps/backend/alembic/versions/
```

### 4.4. Ejecutar el backend

```powershell
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva estará disponible en:

```text
http://127.0.0.1:8000/docs
```

## 5. Servicios web implementados

La API utiliza el prefijo `/api/v1`.

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/login` | Inicio de sesión. |
| POST | `/api/v1/logout` | Cierre de sesión. |
| GET | `/api/v1/me` | Consulta del usuario autenticado. |
| POST | `/api/v1/change-password` | Cambio de contraseña. |
| GET | `/api/v1/users` | Consulta de usuarios. |
| POST | `/api/v1/users` | Creación de usuarios. |
| PATCH | `/api/v1/users/{id}` | Actualización de usuarios. |
| GET | `/api/v1/categories` | Consulta de categorías. |
| GET | `/api/v1/requests` | Consulta de solicitudes. |
| POST | `/api/v1/requests` | Creación de solicitudes. |
| GET | `/api/v1/requests/{id}` | Consulta del detalle de una solicitud. |
| PATCH | `/api/v1/requests/{id}/status` | Actualización del estado. |
| POST | `/api/v1/requests/{id}/assignments` | Asignación o reasignación de técnicos. |
| GET | `/api/v1/requests/{id}/assignments` | Consulta de asignaciones. |
| POST | `/api/v1/requests/{id}/cancel` | Cancelación de una solicitud. |
| POST | `/api/v1/requests/{id}/close` | Cierre de una solicitud. |
| POST | `/api/v1/requests/{id}/resolve` | Registro de una solución. |
| GET | `/api/v1/requests/{id}/interventions` | Consulta de intervenciones. |
| POST | `/api/v1/requests/{id}/messages` | Envío de mensajes. |
| GET | `/api/v1/requests/{id}/messages` | Consulta de mensajes. |
| POST | `/api/v1/requests/{id}/messages/{message_id}/attachments` | Adjuntos en mensajes. |
| GET | `/api/v1/requests/{id}/messages/{message_id}/attachments` | Consulta de adjuntos de mensajes. |
| POST | `/api/v1/requests/{id}/interventions/{intervention_id}/attachments` | Adjuntos en intervenciones. |
| GET | `/api/v1/requests/{id}/attachments` | Consulta de adjuntos de solicitudes. |
| GET | `/api/v1/attachments/{id}/download` | Descarga de adjuntos. |
| GET | `/api/v1/requests/{id}/history` | Consulta del historial de cambios. |
| GET | `/api/v1/notifications` | Consulta de notificaciones internas. |
| PATCH | `/api/v1/notifications/read-all` | Marcar notificaciones como leídas. |
| PATCH | `/api/v1/notifications/{id}/read` | Marcar una notificación como leída. |
| GET | `/api/v1/statistics` | Consulta de estadísticas. |
| GET | `/api/v1/health` | Verificación del backend. |
| GET | `/api/v1/health/db` | Verificación de conexión con la base de datos. |

Los permisos de cada operación dependen del rol autenticado y de las reglas definidas para cada solicitud.

La especificación completa de parámetros, cuerpos de petición, respuestas y errores se encuentra en [docs/contrato-api.md](docs/contrato-api.md).

## 6. Archivos adjuntos

Los adjuntos se procesan desde el backend y se almacenan en Supabase Storage.

El servicio de procesamiento de imágenes contempla:

- Validación del contenido real del archivo.
- Conversión a formato WebP.
- Corrección de orientación cuando existe información EXIF.
- Redimensionamiento de imágenes cuando es necesario.
- Almacenamiento privado.
- Registro de metadatos en PostgreSQL.
- Validación de permisos y estado de la solicitud.

Los adjuntos están asociados a solicitudes, mensajes o intervenciones, según la operación utilizada.

## 7. Pruebas y evidencias

### 7.1. Pruebas automatizadas del backend

Desde `apps/backend`, con el entorno virtual activado:

Ejecutar todas las pruebas:

```powershell
python -m pytest -q
```

Ejecutar las pruebas de un requisito específico:

```powershell
python -m pytest tests/test_rf24_adjuntos_mensajes.py -v
```

Los archivos de pruebas se encuentran en:

```text
apps/backend/tests/
```

Las pruebas cubren autenticación, permisos, usuarios, solicitudes, asignaciones, intervenciones, mensajes, adjuntos, notificaciones, historial y estadísticas.

### 7.2. Pruebas funcionales del proyecto

La guía del proyecto exige documentar 12 pruebas funcionales reproducibles, incluyendo casos exitosos, entradas inválidas, permisos, persistencia, integridad e integración entre interfaz, API y base de datos.

**Documento pendiente de consolidación:** `docs/pruebas.md`.

Las evidencias de ejecución deberán conservarse en la carpeta `evidencias/`.

### 7.3. Matriz de trazabilidad

La relación entre condiciones de aceptación, requisitos, implementación, Pull Requests y pruebas se documenta en:

[docs/trazabilidad.md](docs/trazabilidad.md).

## 8. Organización del desarrollo

El desarrollo se organiza por módulos y requisitos funcionales.

- **Integrante 1:** módulo coordinador y backend del solicitante.
- **Integrante 2:** módulo técnico y frontend del solicitante.
- **Trabajo compartido:** autenticación, sesiones, modelo de datos, contrato de API, conversaciones e integración.

Cada requisito funcional se desarrolla en una rama independiente y se integra mediante Pull Requests.

Los cambios deben respetar los requisitos, el diseño, el modelo de datos y el contrato de la API.

## 9. Estado y limitaciones

El backend integrado contiene módulos para los requisitos funcionales RF-01 a RF-29, incluyendo autenticación, usuarios, solicitudes, atención técnica, conversaciones, adjuntos, notificaciones, historial y estadísticas.

Para considerar el proyecto completo todavía se debe:

- Integrar el código fuente del frontend con la rama del backend.
- Consolidar las 12 pruebas funcionales documentadas y sus evidencias.
- Actualizar la matriz de trazabilidad con las implementaciones y pruebas reales.
- Armonizar las restricciones documentadas de los adjuntos con la implementación.
- Verificar el flujo completo desde la interfaz hasta la persistencia.

El alcance no contempla notificaciones externas por correo, SMS o WhatsApp, ni comunicación en tiempo real mediante WebSockets.

## 10. Documentación complementaria

- [Guía principal del proyecto](proyecto2.md).
- [Requisitos](docs/requisitos.md).
- [Diseño](docs/diseno.md).
- [Modelo entidad-relación](docs/MER.md).
- [Contrato de API](docs/contrato-api.md).
- [Guía de desarrollo](docs/guia-desarrollo.md).
- [Trazabilidad](docs/trazabilidad.md).
