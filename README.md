# SoporteTI

Sistema web para la gestión de solicitudes de soporte de tecnologías de la información (TI). Permite registrar, clasificar, asignar y atender solicitudes, así como mantener la comunicación y trazabilidad de cada caso.

## 1. Documentación del proyecto

La documentación detallada se encuentra en la carpeta `docs/`:

| Documento | Contenido |
|---|---|
| `requisitos.md` | Requisitos y funcionalidades del sistema. |
| `diseno.md` | Arquitectura y decisiones técnicas. |
| `MER.md` | Modelo entidad-relación de la base de datos. |
| `contrato-api.md` | Contratos de los endpoints de la API. |
| `guia-desarrollo.md` | Guía para organizar y desarrollar el proyecto. |
| `trazabilidad.md` | Relación entre requisitos, implementación y pruebas. |
| `pruebas.md` | Plan y documentación de pruebas. |

## 2. Tecnologías

- **Backend:** Python y FastAPI.
- **Frontend:** React y TypeScript.
- **Base de datos:** PostgreSQL mediante Supabase.
- **ORM:** SQLAlchemy.
- **Migraciones:** Alembic.
- **Almacenamiento de archivos:** Supabase Storage.
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
│   │   │   └── main.py
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

La estructura de cada aplicación podrá ampliarse a medida que se implementen los módulos funcionales.

## 4. Configuración del backend

### Requisitos previos

- Python instalado.
- Acceso al proyecto de Supabase.
- Git.

### 4.1. Ubicarse en el backend

Desde la raíz del repositorio:

```powershell
cd apps/backend
```

### 4.2. Crear el entorno virtual

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4.3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4. Configurar las variables de entorno

Crear el archivo `.env` a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Configurar en `.env` los valores correspondientes al proyecto de Supabase:

```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:CONTRASENA@HOST:5432/postgres

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

La URL de conexión se obtiene desde la opción **Connect** del proyecto de Supabase, utilizando el Session Pooler.

**Importante:** el archivo `.env` contiene credenciales y no debe subirse al repositorio. Se debe utilizar `.env.example` como referencia.

## 5. Ejecución del backend

Desde `apps/backend`, con el entorno virtual activado:

```powershell
uvicorn app.main:app --reload
```

El servidor estará disponible en:

```text
http://127.0.0.1:8000
```

### 5.1. Endpoints iniciales

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Información básica de la API. |
| GET | `/api/v1/health` | Comprueba que la API esté funcionando. |
| GET | `/api/v1/health/db` | Comprueba la conexión con PostgreSQL. |

### 5.2. Documentación interactiva

FastAPI genera automáticamente la documentación de los endpoints mediante Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 6. Ejecución de pruebas

Desde `apps/backend`, con el entorno virtual activado:

```powershell
python -m pytest -q
```

Las pruebas verifican las respuestas básicas de la API.

## 7. Base de datos

El esquema inicial de la base de datos se encuentra definido mediante migraciones de Alembic en:

```text
apps/backend/alembic/versions/
```

Las migraciones existentes establecen la estructura inicial y sus restricciones de integridad.

Cualquier modificación posterior del esquema debe gestionarse mediante nuevas migraciones, evitando alterar migraciones que ya hayan sido aplicadas.

## 8. Organización del desarrollo

El proyecto se desarrolla mediante módulos funcionales para los roles de:

- Solicitante.
- Técnico.
- Coordinador.

La implementación debe respetar el modelo entidad-relación, los requisitos aprobados y el contrato de la API.

Los cambios se desarrollan en ramas independientes y se integran a `main` mediante Pull Requests.

## 9. Estado del proyecto

La base inicial del backend permite iniciar FastAPI, comprobar la disponibilidad de la API y verificar la conexión con la base de datos.

Los módulos funcionales y sus respectivas interfaces se implementarán progresivamente siguiendo la documentación del proyecto.
