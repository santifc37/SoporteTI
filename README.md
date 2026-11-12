
# SoporteTI

Sistema web para la gestión de solicitudes de soporte de tecnologías de la información (TI). Permite centralizar el registro, clasificación, asignación y atención de solicitudes, así como mantener la comunicación y trazabilidad de cada caso.

## 1. Documentación del proyecto

La documentación detallada se encuentra en la carpeta `docs/`:

| Documento | Contenido |
|---|---|
| `docs/requisitos.md` | Requisitos funcionales y no funcionales. |
| `docs/diseno.md` | Arquitectura y decisiones técnicas. |
| `docs/MER.md` | Modelo entidad-relación de la base de datos. |
| `docs/contrato-api.md` | Contratos de los endpoints de la API. |
| `docs/guia-desarrollo.md` | Guía para organizar y desarrollar el proyecto. |
| `docs/trazabilidad.md` | Relación entre requisitos, implementación y pruebas. |

## 2. Tecnologías

- **Backend:** Python y FastAPI.
- **Frontend:** React y TypeScript.
- **Base de datos:** PostgreSQL mediante Supabase.
- **ORM:** SQLAlchemy.
- **Migraciones:** Alembic.
- **Almacenamiento de archivos:** Supabase Storage.
- **Procesamiento de imágenes:** Pillow y pillow-heif.
- **Recepción de archivos:** python-multipart.
- **Comunicación HTTP:** HTTPX.
- **Pruebas:** pytest.

## 3. Estructura del repositorio

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
│   │   ├── alembic.ini
│   │   └── requirements.txt
│   └── frontend/
├── docs/
├── evidencias/
└── README.md
```

## 4. Funcionalidades del sistema

SoporteTI contempla tres roles principales:

- **Solicitante:** registra solicitudes, consulta su estado, participa en conversaciones y responde solicitudes de información.
- **Técnico:** consulta sus solicitudes asignadas, registra intervenciones, diagnósticos y soluciones, y participa en la atención.
- **Coordinador:** administra y supervisa las solicitudes, gestiona asignaciones, revisa soluciones y realiza cierres.

### 4.1. Gestión y seguimiento de solicitudes

El sistema contempla funcionalidades para:

- Registrar y consultar solicitudes.
- Clasificar solicitudes y establecer prioridades.
- Asignar y reasignar técnicos.
- Controlar las transiciones de estado.
- Registrar intervenciones técnicas.
- Diferenciar intervenciones internas de las visibles para el solicitante.
- Solicitar información adicional y registrar las respuestas.
- Registrar soluciones.
- Consultar intervenciones respetando los permisos.
- Mantener conversaciones y mensajes asociados a las solicitudes.
- Conservar la trazabilidad de las actividades realizadas.

### 4.2. Adjuntos en intervenciones técnicas (RF-25)

El backend permite que el técnico asignado adjunte imágenes a las intervenciones de una solicitud abierta.

Características:

- Recibe imágenes en formatos compatibles con Pillow y pillow-heif, incluyendo PNG, JPEG y HEIC.
- Acepta archivos de entrada de hasta 10 MB.
- Valida el contenido real del archivo.
- Corrige la orientación de las imágenes cuando contienen información EXIF.
- Redimensiona las imágenes que superan los 1920 píxeles de ancho o alto, conservando su proporción.
- Convierte automáticamente las imágenes a WebP con calidad del 80 %.
- Almacena los archivos convertidos en un bucket privado de Supabase Storage.
- Registra los metadatos en PostgreSQL, asociados a la solicitud, intervención y técnico.
- Evita exponer públicamente la ruta interna de almacenamiento.
- Si falla el registro en la base de datos, intenta eliminar el archivo previamente almacenado para evitar archivos huérfanos.

**Endpoint implementado:**

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/requests/{solicitud_id}/interventions/{intervencion_id}/attachments` | Adjunta una imagen a una intervención. |

La solicitud utiliza `multipart/form-data` y recibe el archivo mediante el campo `archivo`.

La operación está restringida al técnico asignado y no permite adjuntar imágenes a solicitudes cerradas.

## 5. Configuración del backend

### Requisitos previos

- Python instalado.
- Git.
- Acceso al proyecto de Supabase.
- Un bucket privado de Supabase Storage llamado `soporteti-adjuntos`.

### 5.1. Ubicarse en el backend

Desde la raíz del repositorio:

```powershell
cd apps/backend
```

### 5.2. Crear el entorno virtual

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5.3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Entre las dependencias utilizadas se encuentran Pillow, pillow-heif, python-multipart y HTTPX.

### 5.4. Configurar las variables de entorno

Crear el archivo `.env` a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Configurar las variables necesarias:

```env
# Conexión a PostgreSQL de Supabase
DATABASE_URL=postgresql://...

# Supabase Storage
SUPABASE_URL=https://TU_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=TU_SERVICE_ROLE_KEY
SUPABASE_STORAGE_BUCKET=soporteti-adjuntos

# Sesiones
SESSION_DURATION_HOURS=8
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax

# Direcciones permitidas del frontend
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

La variable `DATABASE_URL` corresponde a la conexión PostgreSQL. `SUPABASE_URL` corresponde a la URL del proyecto de Supabase y se utiliza para acceder a Storage.

**Seguridad:**

- La clave `SUPABASE_SERVICE_ROLE_KEY` debe mantenerse exclusivamente en el backend.
- No se debe exponer esta clave al frontend.
- El archivo `.env` contiene credenciales y nunca debe subirse al repositorio.
- El bucket de adjuntos debe permanecer privado.

## 6. Ejecución del backend

Desde `apps/backend`, con el entorno virtual activado:

```powershell
uvicorn app.main:app --reload
```

El servidor estará disponible en:

```text
http://127.0.0.1:8000
```

### 6.1. Endpoints de verificación

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Información básica de la API. |
| GET | `/api/v1/health` | Comprueba que la API esté funcionando. |
| GET | `/api/v1/health/db` | Comprueba la conexión con PostgreSQL. |

### 6.2. Documentación interactiva

FastAPI genera automáticamente la documentación de los endpoints mediante Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 7. Base de datos

La base de datos utiliza PostgreSQL mediante Supabase.

El esquema se encuentra definido mediante migraciones de Alembic en:

```text
apps/backend/alembic/versions/
```

Las migraciones establecen las tablas, relaciones y restricciones de integridad del sistema.

Para los adjuntos, la tabla `adjuntos` conserva los metadatos y la ruta interna de Storage. El contenido binario de las imágenes se almacena en Supabase Storage.

Cualquier modificación posterior del esquema debe gestionarse mediante nuevas migraciones, evitando alterar migraciones que ya hayan sido aplicadas.

## 8. Ejecución de pruebas

Desde `apps/backend`, con el entorno virtual activado:

Ejecutar todas las pruebas:

```powershell
python -m pytest -q
```

Ejecutar las pruebas específicas de adjuntos en intervenciones:

```powershell
python -m pytest tests/test_rf25_adjuntos_intervenciones.py -v
```

Las pruebas de RF-25 verifican:

- Conversión de PNG y JPEG a WebP.
- Redimensionamiento conservando las proporciones.
- Rechazo de archivos inválidos y vacíos.
- Rechazo de archivos superiores a 10 MB.
- Carga de imágenes por parte del técnico asignado.
- Registro de metadatos en PostgreSQL.
- Restricción de acceso para técnicos no asignados.
- Rechazo de adjuntos en solicitudes cerradas.
- Rechazo de archivos que no son imágenes.
- Restricción de acceso para solicitantes y coordinadores.

Las pruebas de almacenamiento externo utilizan simulaciones para no depender de una conexión real con Supabase durante su ejecución.

## 9. Organización del desarrollo

El proyecto se desarrolla mediante módulos funcionales correspondientes a los roles de solicitante, técnico y coordinador.

Los cambios deben respetar:

- Los requisitos funcionales aprobados.
- El modelo entidad-relación.
- Los contratos de la API.
- Las reglas de autorización por roles.
- Las restricciones de integridad de la base de datos.

Cada requisito funcional se desarrolla en una rama independiente y se integra mediante Pull Requests, siguiendo la organización establecida para el equipo.

## 10. Estado del proyecto

El desarrollo se realiza progresivamente por requisitos funcionales.

Los avances de cada requisito, sus archivos de implementación y las pruebas correspondientes se documentan en `docs/trazabilidad.md`.

Para considerar un requisito completado se debe contar con implementación, validación mediante pruebas y la documentación correspondiente.
