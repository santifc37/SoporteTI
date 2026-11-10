# SoporteTI

Sistema web para la gestión de solicitudes de soporte de tecnologías de la información (TI). Permite registrar, evaluar, asignar, atender y cerrar casos de soporte, conservando la información de las intervenciones y facilitando el seguimiento por parte de los usuarios y la coordinación.

## 1. Información general

| Campo | Descripción |
|---|---|
| Proyecto | SoporteTI |
| Tipo de aplicación | Aplicación web cliente-servidor |
| Backend | Python y FastAPI |
| Frontend | React y TypeScript |
| Base de datos | PostgreSQL mediante Supabase |
| Repositorio | [GitHub - SoporteTI](https://github.com/santifc37/SoporteTI) |

El sistema contempla tres actores principales:

- **Solicitante:** registra solicitudes y consulta su estado y resultado.
- **Técnico:** atiende los casos asignados, registra intervenciones y soluciones.
- **Coordinador:** evalúa solicitudes, gestiona asignaciones, supervisa la atención y realiza cierres.

## 2. Descripción y alcance del sistema

El proyecto busca centralizar el proceso de soporte tecnológico de una institución. La solución permite mantener información organizada de los casos desde su registro hasta su resolución o cierre.

El alcance comprende:

- Registro de incidentes y requerimientos de soporte.
- Evaluación, clasificación y priorización de solicitudes.
- Asignación y seguimiento de responsables.
- Consulta del estado de los casos.
- Registro y consulta de intervenciones técnicas.
- Solicitudes de información adicional.
- Registro de soluciones y cierre de solicitudes.
- Conservación del historial de cambios.
- Consulta consolidada de información para coordinación.

El sistema se concentra en la gestión del proceso de soporte. No pretende sustituir herramientas de acceso remoto, monitoreo de infraestructura ni servicios externos de comunicación.

### 2.1. Criterios de aceptación

| Criterio | Condición |
|---|---|
| CA-01 | Un usuario puede reportar un incidente o solicitar soporte tecnológico. |
| CA-02 | El personal autorizado puede evaluar y gestionar el caso. |
| CA-03 | Es posible identificar el responsable y consultar el estado del caso. |
| CA-04 | El sistema conserva el historial de intervenciones de soporte. |
| CA-05 | El usuario puede consultar el resultado y la finalización de su caso. |
| CA-06 | La coordinación puede consultar información consolidada sobre la atención. |

La especificación detallada se encuentra en [`docs/requisitos.md`](docs/requisitos.md).

## 3. Requisitos y documentación

La documentación complementaria se encuentra en `docs/`:

| Documento | Contenido |
|---|---|
| [`docs/requisitos.md`](docs/requisitos.md) | Requisitos funcionales, no funcionales, reglas de negocio y criterios de aceptación. |
| [`docs/diseno.md`](docs/diseno.md) | Arquitectura, diseño técnico y decisiones de implementación. |
| [`docs/MER.md`](docs/MER.md) | Modelo entidad-relación de la base de datos. |
| [`docs/contrato-api.md`](docs/contrato-api.md) | Contrato de comunicación y especificación de servicios web. |
| [`docs/guia-desarrollo.md`](docs/guia-desarrollo.md) | Organización y convenciones de desarrollo. |
| [`docs/trazabilidad.md`](docs/trazabilidad.md) | Correspondencia entre criterios, requisitos, implementación, Pull Requests y pruebas. |
| [`docs/pruebas.md`](docs/pruebas.md) | Escenarios y registro de las doce pruebas funcionales manuales. |

También se conserva el registro de entrevista y las evidencias correspondientes en las carpetas de `evidencias/`.

## 4. Arquitectura y tecnologías

### 4.1. Arquitectura

La aplicación utiliza una arquitectura cliente-servidor:

1. El frontend presenta las interfaces y recibe las acciones de los usuarios.
2. El frontend consume los servicios mediante solicitudes HTTP.
3. El backend valida las solicitudes, aplica reglas de negocio y controla los permisos.
4. El backend consulta y modifica la información persistida en PostgreSQL.
5. La respuesta de la API se presenta en la interfaz web.

```text
Usuario
   |
   v
Frontend (React + TypeScript + Vite)
   |
   | HTTP / JSON
   v
Backend (Python + FastAPI)
   |
   | SQLAlchemy
   v
PostgreSQL (Supabase)

Backend
   |
   v
Supabase Storage
(archivos adjuntos)
```

### 4.2. Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Frontend | React 19 |
| Lenguaje frontend | TypeScript |
| Herramienta de desarrollo frontend | Vite |
| Estilos | Tailwind CSS |
| Navegación | React Router |
| Backend | Python |
| Framework API | FastAPI |
| ORM | SQLAlchemy |
| Migraciones | Alembic |
| Base de datos | PostgreSQL |
| Plataforma de base de datos | Supabase |
| Almacenamiento de archivos | Supabase Storage |
| Procesamiento de imágenes | Pillow y pillow-heif |
| Cliente HTTP del backend | HTTPX |
| Recepción de archivos | python-multipart |
| Pruebas automatizadas complementarias | pytest |

## 5. Estructura del repositorio

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
│       ├── src/
│       ├── public/
│       ├── .env.example
│       ├── package.json
│       └── vite.config.ts
├── docs/
├── evidencias/
│   └── entrevista/
├── README.md
└── proyecto2.md
```

## 6. Configuración del entorno

### 6.1. Requisitos previos

- Git.
- Python.
- Node.js y npm.
- Acceso al proyecto de Supabase.
- Un navegador web moderno.

### 6.2. Clonar el repositorio

```powershell
git clone https://github.com/santifc37/SoporteTI.git
cd SoporteTI
```

### 6.3. Configurar el backend

Desde la raíz del repositorio:

```powershell
cd apps/backend
```

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crear el archivo de configuración:

```powershell
Copy-Item .env.example .env
```

Configurar las variables:

```env
DATABASE_URL=postgresql://...
SESSION_DURATION_HOURS=8
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`DATABASE_URL` debe contener la cadena de conexión PostgreSQL del proyecto de Supabase.

Para la funcionalidad de almacenamiento de imágenes RF-25 también se requieren las variables:

```env
SUPABASE_URL=https://TU_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=TU_SERVICE_ROLE_KEY
SUPABASE_STORAGE_BUCKET=soporteti-adjuntos
```

El bucket `soporteti-adjuntos` debe existir y permanecer privado.

### 6.4. Configurar el frontend

Desde la raíz del repositorio:

```powershell
cd apps/frontend
```

Instalar dependencias:

```powershell
npm install
```

Crear el archivo de variables de entorno:

```powershell
Copy-Item .env.example .env
```

La configuración de desarrollo utiliza:

```env
VITE_API_URL=/api/v1
```

El archivo `vite.config.ts` configura un proxy que redirige las solicitudes `/api` hacia `http://localhost:8000`.

## 7. Ejecución de la aplicación

Se deben iniciar el backend y el frontend en terminales independientes.

### 7.1. Iniciar el backend

Desde `apps/backend`, con el entorno virtual activado:

```powershell
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

### 7.2. Iniciar el frontend

Desde `apps/frontend`:

```powershell
npm run dev
```

Vite mostrará la dirección local donde se encuentra disponible la aplicación. Normalmente:

```text
http://localhost:5173
```

### 7.3. Documentación interactiva de la API

FastAPI proporciona Swagger UI:

```text
http://127.0.0.1:8000/docs
```

También se puede consultar el esquema OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

## 8. Base de datos y persistencia

La aplicación utiliza PostgreSQL mediante Supabase.

El backend accede a los datos mediante SQLAlchemy. Las migraciones de estructura se encuentran en:

```text
apps/backend/alembic/versions/
```

Las migraciones permiten mantener el esquema de la base de datos versionado y reproducible.

Para los archivos adjuntos:

- Los metadatos se conservan en PostgreSQL.
- Los archivos se almacenan en Supabase Storage.
- El bucket es privado.
- El backend valida los permisos antes de almacenar los archivos.
- La ruta interna de almacenamiento no se expone como enlace público.

Las relaciones y restricciones de integridad se describen en el modelo entidad-relación y en la documentación de diseño.

## 9. Servicios web implementados

La API utiliza el prefijo:

```text
/api/v1
```

Los siguientes endpoints corresponden a rutas identificadas en el código del backend de esta versión:

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Verificación básica de funcionamiento de la API. |
| GET | `/api/v1/health` | Verificación del servicio. |
| GET | `/api/v1/health/db` | Verificación de conexión con la base de datos. |
| POST | `/api/v1/auth/login` | Inicio de sesión. |
| POST | `/api/v1/auth/logout` | Cierre de sesión. |
| GET | `/api/v1/auth/me` | Consulta de la sesión actual. |
| GET | `/api/v1/requests` | Consulta de solicitudes según los permisos implementados. |
| PATCH | `/api/v1/requests/{solicitud_id}/status` | Actualización del estado por el técnico autorizado. |
| POST | `/api/v1/requests/{solicitud_id}/interventions` | Registro de intervención técnica. |
| GET | `/api/v1/requests/{solicitud_id}/interventions` | Consulta de intervenciones. |
| POST | `/api/v1/requests/{solicitud_id}/information-requests` | Solicitud de información adicional. |
| POST | `/api/v1/requests/{solicitud_id}/resolve` | Registro de solución. |
| POST | `/api/v1/requests/{solicitud_id}/interventions/{intervencion_id}/attachments` | Adjuntar imagen a una intervención. |

Los endpoints y permisos deben verificarse en el código y en la documentación interactiva de la API. La especificación de comunicación se encuentra en [`docs/contrato-api.md`](docs/contrato-api.md).

### 9.1. Respuestas HTTP y validaciones

La API utiliza códigos HTTP para comunicar los resultados de las operaciones, entre ellos:

| Código | Significado |
|---|---|
| 200 | Operación exitosa. |
| 201 | Recurso creado. |
| 401 | Usuario no autenticado. |
| 403 | Operación no autorizada. |
| 404 | Recurso no encontrado. |
| 409 | Conflicto con el estado del recurso. |
| 422 | Error de validación. |
| 500 | Error interno del servidor. |

Las validaciones se realizan en el backend para evitar que solicitudes inválidas o no autorizadas modifiquen la información.

## 10. Adjuntos en intervenciones técnicas (RF-25)

El backend permite que el técnico asignado adjunte imágenes a las intervenciones de una solicitud abierta.

Características implementadas:

- Recibe imágenes reconocidas por Pillow y pillow-heif, incluyendo formatos como PNG, JPEG y HEIC/HEIF.
- Acepta archivos de entrada de hasta 10 MB.
- Valida el contenido real del archivo.
- Rechaza archivos vacíos o que no puedan procesarse como imágenes.
- Corrige la orientación cuando las imágenes contienen información EXIF.
- Redimensiona imágenes que superan los 1920 píxeles de ancho o alto, conservando la proporción.
- Convierte las imágenes a WebP con calidad del 80 %.
- Almacena los archivos convertidos en un bucket privado de Supabase Storage.
- Registra los metadatos en PostgreSQL.
- Asocia el adjunto con la solicitud, intervención y técnico.
- Impide adjuntar imágenes a solicitudes cerradas.
- Restringe la operación al técnico con asignación activa.
- Si falla el registro en la base de datos, intenta eliminar el archivo previamente almacenado.

**Endpoint:**

```text
POST /api/v1/requests/{solicitud_id}/interventions/{intervencion_id}/attachments
```

La solicitud utiliza `multipart/form-data` y recibe el archivo mediante el campo `archivo`.

## 11. Pruebas funcionales y evidencias

El proyecto contempla doce escenarios de pruebas funcionales manuales, de acuerdo con la Actividad 6 de `proyecto2.md`.

| ID | Escenario | Estado |
|---|---|---|
| PF-01 | Registro válido de un caso de soporte | Pendiente |
| PF-02 | Registro de un caso con datos inválidos | Pendiente |
| PF-03 | Consulta de un caso existente | Pendiente |
| PF-04 | Consulta de un caso inexistente | Pendiente |
| PF-05 | Gestión por personal autorizado | Pendiente |
| PF-06 | Intento de gestión por actor no autorizado | Pendiente |
| PF-07 | Consulta del estado y responsable | Pendiente |
| PF-08 | Consulta del historial de intervenciones | Pendiente |
| PF-09 | Cierre de un caso y consulta del resultado | Pendiente |
| PF-10 | Consulta consolidada de coordinación | Pendiente |
| PF-11 | Persistencia e integridad de las relaciones | Pendiente |
| PF-12 | Integración frontend, API y base de datos | Pendiente |

Los pasos, precondiciones, datos de entrada, resultados esperados y espacios para registrar resultados obtenidos se encuentran en [`docs/pruebas.md`](docs/pruebas.md).

Las evidencias de ejecución se almacenarán en:

```text
evidencias/pruebas/
```

Las pruebas no se marcarán como aprobadas hasta que hayan sido ejecutadas y verificadas. Se conservarán capturas de pantalla, solicitudes HTTP, respuestas y registros que permitan reproducir los escenarios.

### 11.1. Pruebas automatizadas complementarias

El backend cuenta con pruebas implementadas mediante pytest en:

```text
apps/backend/tests/
```

Para ejecutarlas, desde `apps/backend` y con el entorno virtual activado:

```powershell
python -m pytest -q
```

Estas pruebas automatizadas son complementarias y no sustituyen los doce escenarios funcionales manuales exigidos por la guía del proyecto.

## 12. Control de versiones y trabajo colaborativo

El desarrollo se organiza mediante Git y GitHub.

Se utilizan ramas independientes para desarrollar requisitos o funcionalidades, commits descriptivos y Pull Requests para documentar la integración de cambios.

Cada Pull Request debe permitir identificar:

- Propósito del cambio.
- Archivos y funcionalidades modificadas.
- Requisitos relacionados.
- Validaciones o pruebas realizadas.
- Resultado de la revisión e integración.

El historial verificable de ramas, commits y Pull Requests se encuentra en el repositorio:

[Consultar repositorio y Pull Requests en GitHub](https://github.com/santifc37/SoporteTI)

Los aportes individuales deben respaldarse mediante el historial de GitHub y las contribuciones registradas en los Pull Requests.

## 13. Seguridad y configuración de secretos

- Las credenciales reales no deben incluirse en el repositorio.
- Los archivos `.env` deben permanecer fuera del control de versiones.
- Los archivos `.env.example` deben contener únicamente nombres de variables y valores de ejemplo.
- La clave `SUPABASE_SERVICE_ROLE_KEY` debe utilizarse exclusivamente desde el backend.
- El bucket de adjuntos debe permanecer privado.
- Los permisos se deben validar en el servidor.
- Los mensajes de error no deben exponer credenciales ni información sensible.

## 14. Conclusiones y limitaciones

SoporteTI integra una interfaz web, una API REST y una base de datos relacional para gestionar solicitudes de soporte tecnológico.

El cumplimiento de las condiciones de aceptación debe comprobarse mediante los flujos funcionales y las pruebas documentadas. Los resultados de las pruebas y las evidencias se actualizarán a medida que se ejecuten los escenarios.

Las funcionalidades pendientes, restricciones técnicas y limitaciones verificadas deberán registrarse en este documento y en la matriz de trazabilidad, evitando declarar como completada una función que no haya sido implementada y comprobada.