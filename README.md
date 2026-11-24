# SoporteTI

Sistema web para la gestiÃ³n de solicitudes de soporte de tecnologÃ­as de la informaciÃ³n. Permite registrar, evaluar, clasificar, asignar y atender solicitudes, mantener la comunicaciÃ³n entre los participantes y conservar la trazabilidad de cada caso.

**Asignatura:** Aplicaciones y Servicios Web  
**InstituciÃ³n:** Instituto TecnolÃ³gico Metropolitano (ITM)  
**Repositorio:** https://github.com/santifc37/SoporteTI

---

## 1. DescripciÃ³n del sistema

SoporteTI busca centralizar el proceso de atenciÃ³n de incidentes y solicitudes de soporte tecnolÃ³gico de una instituciÃ³n.

El sistema contempla tres roles:

- **Solicitante:** registra solicitudes, consulta su estado, participa en conversaciones, responde peticiones de informaciÃ³n y consulta el resultado de la atenciÃ³n.
- **TÃ©cnico:** consulta sus solicitudes asignadas, registra intervenciones, solicita informaciÃ³n adicional y documenta las soluciones.
- **Coordinador:** administra usuarios y categorÃ­as, evalÃºa solicitudes, asigna tÃ©cnicos, supervisa la atenciÃ³n, revisa soluciones, cierra solicitudes y consulta estadÃ­sticas.

El backend aplica controles de acceso para restringir las operaciones segÃºn el rol y la relaciÃ³n del usuario con cada solicitud.

## 2. Alcance y requisitos

El proyecto contempla:

- AutenticaciÃ³n y control de acceso por roles.
- AdministraciÃ³n de usuarios y datos de contacto.
- Registro y consulta de solicitudes.
- EvaluaciÃ³n, clasificaciÃ³n y asignaciÃ³n de solicitudes.
- ActualizaciÃ³n controlada de estados.
- Registro y consulta de intervenciones tÃ©cnicas.
- Solicitud y respuesta de informaciÃ³n adicional.
- Registro de soluciones y cierre de solicitudes.
- Conversaciones y mensajes asociados a solicitudes.
- Adjuntos en solicitudes, mensajes e intervenciones.
- Notificaciones internas.
- Historial de cambios.
- EstadÃ­sticas para coordinaciÃ³n.

No se incluyen notificaciones por correo, SMS o WhatsApp, chat mediante WebSockets ni recuperaciÃ³n automÃ¡tica de contraseÃ±as mediante servicios externos.

### DocumentaciÃ³n

- [Requisitos funcionales y no funcionales](docs/requisitos.md).
- [DiseÃ±o de la soluciÃ³n](docs/diseno.md).
- [Contrato de la API](docs/contrato-api.md).
- [GuÃ­a de desarrollo](docs/guia-desarrollo.md).
- [Matriz de trazabilidad](docs/trazabilidad.md).
- [Modelo entidad-relaciÃ³n](docs/MER.md).

## 3. Arquitectura y tecnologÃ­as

La soluciÃ³n utiliza una arquitectura cliente-servidor:

| Componente | TecnologÃ­a | Responsabilidad |
|---|---|---|
| Frontend | React, TypeScript y Vite | Interfaz de usuario y consumo de la API. |
| Backend | Python y FastAPI | API REST, reglas de negocio y autorizaciÃ³n. |
| Base de datos | PostgreSQL | Persistencia de usuarios, solicitudes y demÃ¡s registros. |
| Almacenamiento | Disco local (`apps/backend/storage/`) | Almacenamiento privado de archivos adjuntos. |
| ORM | SQLAlchemy | Acceso y persistencia de datos. |
| Migraciones | Alembic | EvoluciÃ³n del esquema de base de datos. |
| Pruebas | pytest | ValidaciÃ³n automatizada del backend. |

### Estructura principal

```text
SoporteTI/
â”œâ”€â”€ apps/
â”‚   â”œâ”€â”€ backend/
â”‚   â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”‚   â”œâ”€â”€ database/
â”‚   â”‚   â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”‚   â”œâ”€â”€ schemas/
â”‚   â”‚   â”‚   â””â”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ alembic/
â”‚   â”‚   â”œâ”€â”€ scripts/
â”‚   â”‚   â”œâ”€â”€ storage/          # adjuntos locales (no se versiona)
â”‚   â”‚   â”œâ”€â”€ tests/
â”‚   â”‚   â”œâ”€â”€ .env.example
â”‚   â”‚   â””â”€â”€ requirements.txt
â”‚   â””â”€â”€ frontend/
â”‚       â”œâ”€â”€ src/
â”‚       â”œâ”€â”€ public/
â”‚       â”œâ”€â”€ package.json
â”‚       â””â”€â”€ vite.config.ts
â”œâ”€â”€ docs/
â”œâ”€â”€ evidencias/
â”œâ”€â”€ proyecto2.md
â””â”€â”€ README.md
```

La carpeta `apps/backend/storage/` se crea automÃ¡ticamente al subir el primer adjunto y estÃ¡ excluida de Git.

## 4. ConfiguraciÃ³n del entorno local

El entorno de desarrollo local utiliza:

- PostgreSQL instalado en el equipo.
- Una base de datos local llamada `soporteti_local`.
- FastAPI como servidor backend.
- React y Vite como frontend.
- El disco local para los archivos adjuntos.

No se requiere ninguna cuenta ni servicio externo.

### 4.1. Requisitos previos

- Git.
- Python.
- Node.js y npm.
- PostgreSQL.

### 4.2. ConfiguraciÃ³n de PostgreSQL

Crear una base de datos local llamada:

```text
soporteti_local
```

Por ejemplo, desde PowerShell:

```powershell
psql -U postgres -c "CREATE DATABASE soporteti_local;"
```

La conexiÃ³n local utiliza PostgreSQL en `localhost`, puerto `5432`.

Ejemplo de conexiÃ³n:

```text
postgresql+psycopg://postgres:CONTRASEÃ‘A@localhost:5432/soporteti_local
```

La contraseÃ±a debe corresponder a la configurada durante la instalaciÃ³n de PostgreSQL. Si contiene caracteres especiales (`@`, `#`, `/`), deben escribirse codificados (por ejemplo, `@` como `%40`).

### 4.3. ConfiguraciÃ³n del backend

Desde la raÃ­z del repositorio:

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

Crear el archivo de configuraciÃ³n local a partir del ejemplo:

```powershell
Copy-Item .env.example .env.local
```

Editar `apps/backend/.env.local` y configurar las variables:

```env
DATABASE_URL=postgresql+psycopg://postgres:CONTRASEÃ‘A@localhost:5432/soporteti_local

SESSION_DURATION_HOURS=8
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

La conexiÃ³n `DATABASE_URL` apunta a PostgreSQL local. Los archivos adjuntos se guardan en `apps/backend/storage/`, por lo que no se necesitan variables adicionales para el almacenamiento.

**Importante:**

- El archivo `.env.local` contiene informaciÃ³n privada y no debe subirse al repositorio.
- La carpeta `apps/backend/storage/` contiene archivos privados y no debe subirse al repositorio (ya estÃ¡ en `.gitignore`).
- Utilizar datos ficticios en las demostraciones.

### 4.4. SelecciÃ³n del entorno local

El backend utiliza la variable `APP_ENV` para seleccionar el archivo de configuraciÃ³n:

| Valor | Archivo utilizado |
|---|---|
| `local` | `.env.local` |
| Otro valor o valor predeterminado | `.env` |

Antes de ejecutar los comandos del backend, seleccionar el entorno local:

```powershell
$env:APP_ENV = "local"
```

Este comando debe ejecutarse en cada nueva terminal de PowerShell que se utilice para trabajar con el backend.

### 4.5. Migraciones de la base de datos

Desde `apps/backend`, con el entorno virtual activado y `APP_ENV` configurado como `local`:

```powershell
alembic upgrade head
```

Las migraciones se encuentran en:

```text
apps/backend/alembic/versions/
```

Este comando crea o actualiza las tablas de la base de datos local segÃºn las migraciones disponibles.

### 4.6. Ejecutar el backend

Desde `apps/backend`, con el entorno virtual activado:

```powershell
$env:APP_ENV = "local"
uvicorn app.main:app --reload
```

La API estarÃ¡ disponible en:

```text
http://127.0.0.1:8000
```

La documentaciÃ³n interactiva de Swagger estarÃ¡ disponible en:

```text
http://127.0.0.1:8000/docs
```

## 5. ConfiguraciÃ³n del frontend

Abrir una segunda terminal de PowerShell y ubicarse en:

```powershell
cd apps/frontend
```

Instalar las dependencias:

```powershell
npm install
```

Crear el archivo local de variables de entorno:

```powershell
@"
VITE_API_URL=/api/v1
"@ | Set-Content .env.local
```

El frontend utiliza `VITE_API_URL` para determinar la direcciÃ³n de la API.

La configuraciÃ³n de Vite utiliza un proxy local que redirige las solicitudes `/api` hacia:

```text
http://127.0.0.1:8000
```

Por esta razÃ³n, el frontend puede comunicarse con el backend sin configurar una direcciÃ³n externa durante el desarrollo local.

### Ejecutar el frontend

Desde `apps/frontend`:

```powershell
npm run dev
```

La interfaz estarÃ¡ disponible en:

```text
http://localhost:5173
```

Para utilizar el sistema local deben estar ejecutÃ¡ndose simultÃ¡neamente el backend y el frontend.

## 6. CreaciÃ³n de usuarios locales

El proyecto dispone de un script para crear usuarios directamente en la base de datos seleccionada.

Desde `apps/backend`, con el entorno virtual activado:

```powershell
$env:APP_ENV = "local"
```

Ejemplo de creaciÃ³n de un usuario coordinador:

```powershell
python -m scripts.crear_usuario Admin Local coordinador@coordinador.com coordinador
```

Ejemplo de creaciÃ³n de un tÃ©cnico:

```powershell
python -m scripts.crear_usuario Tecnico Local tecnico@tecnico.com tecnico
```

Ejemplo de creaciÃ³n de un solicitante:

```powershell
python -m scripts.crear_usuario Solicitante Local solicitante@solicitante.com solicitante
```

El script solicita la contraseÃ±a de forma interactiva y la almacena utilizando el mecanismo de hash definido por el backend.

Los roles disponibles son:

- `solicitante`
- `tecnico`
- `coordinador`

Los usuarios se crean mediante el script 'apps/backend/scripts/crear_usuario.py'. Consulta la secciÃ³n de creaciÃ³n de usuarios de esta guÃ­a.

## 7. Servicios web y API

La API utiliza el prefijo:

```text
/api/v1
```

La documentaciÃ³n interactiva de los servicios se puede consultar desde Swagger:

```text
http://127.0.0.1:8000/docs
```

La especificaciÃ³n de rutas, mÃ©todos HTTP, parÃ¡metros, cuerpos de peticiÃ³n, respuestas, permisos y errores se encuentra en:

[docs/contrato-api.md](docs/contrato-api.md).

Los permisos de cada operaciÃ³n dependen del rol autenticado y de las reglas definidas para cada solicitud.

## 8. Archivos adjuntos

Los adjuntos se procesan desde el backend y se almacenan en el disco local, dentro de `apps/backend/storage/`. Sus metadatos y relaciones se conservan en PostgreSQL.

El procesamiento de imÃ¡genes contempla:

- ValidaciÃ³n del contenido real del archivo.
- ConversiÃ³n a formato WebP.
- CorrecciÃ³n de orientaciÃ³n cuando existe informaciÃ³n EXIF.
- Redimensionamiento de imÃ¡genes cuando es necesario.
- Almacenamiento privado en disco local.
- Registro de metadatos en PostgreSQL.
- ValidaciÃ³n de permisos y estado de la solicitud.

Los adjuntos pueden asociarse a solicitudes, mensajes o intervenciones, segÃºn la operaciÃ³n utilizada.

### Descarga de adjuntos

Los archivos no se exponen pÃºblicamente. Las respuestas de la API incluyen, en el campo `url`, una ruta relativa al endpoint autenticado:

```text
/api/v1/attachments/{id}/download
```

Antes de entregar el archivo, el backend valida la sesiÃ³n del usuario y sus permisos sobre la solicitud, el mensaje o la intervenciÃ³n a la que pertenece el adjunto. Por esta razÃ³n, la descarga debe realizarse con la sesiÃ³n activa del usuario.

### Consideraciones

- `apps/backend/storage/` no se versiona; para conservar los adjuntos debe incluirse en las copias de seguridad del equipo o servidor.
- Los adjuntos que se hayan guardado anteriormente en Supabase Storage no se migran automÃ¡ticamente. Para conservarlos, deben copiarse a `apps/backend/storage/` respetando la ruta registrada en la base de datos (`ruta_storage`).

## 9. Pruebas y evidencias

### 9.1. Pruebas automatizadas del backend

Desde `apps/backend`, con el entorno virtual activado:

Ejecutar todas las pruebas:

```powershell
python -m pytest -q
```

Ejecutar las pruebas con mayor detalle:

```powershell
python -m pytest -v
```

Los archivos de pruebas se encuentran en:

```text
apps/backend/tests/
```

Las pruebas automatizadas permiten validar los diferentes mÃ³dulos y reglas de negocio implementados en el backend. Utilizan SQLite en memoria y simulan la lectura y escritura de adjuntos, por lo que no requieren PostgreSQL ni archivos reales en `storage/`.

### 9.2. Pruebas funcionales del proyecto

Las pruebas funcionales deben documentar escenarios reproducibles que permitan verificar:

- Casos exitosos.
- Entradas invÃ¡lidas.
- Permisos segÃºn el rol.
- Persistencia de la informaciÃ³n.
- Integridad de los datos.
- IntegraciÃ³n entre interfaz, API y base de datos.

Las evidencias de ejecuciÃ³n deben conservarse en:

```text
evidencias/
```

### 9.3. Matriz de trazabilidad

La relaciÃ³n entre condiciones de aceptaciÃ³n, requisitos funcionales, implementaciÃ³n, Pull Requests y pruebas se documenta en:

[docs/trazabilidad.md](docs/trazabilidad.md).

## 10. OrganizaciÃ³n del desarrollo

El desarrollo se organiza por mÃ³dulos y requisitos funcionales.

- **Integrante 1:** mÃ³dulo coordinador y backend del solicitante.
- **Integrante 2:** mÃ³dulo tÃ©cnico y frontend del solicitante.
- **Trabajo compartido:** autenticaciÃ³n, sesiones, modelo de datos, contrato de API, conversaciones e integraciÃ³n.

Cada requisito funcional se desarrolla en una rama independiente y se integra mediante Pull Requests, siguiendo el flujo de trabajo definido para el proyecto.

Los cambios deben respetar los requisitos, el diseÃ±o, el modelo de datos y el contrato de la API.

## 11. Estado del entorno y consideraciones

El entorno local permite ejecutar el backend y el frontend utilizando Ãºnicamente PostgreSQL y el disco del equipo, sin depender de servicios externos como Supabase.

Los archivos de configuraciÃ³n locales (`.env.local`) y la carpeta `apps/backend/storage/` no deben incluirse en los commits.

El despliegue en producciÃ³n y sus variables de entorno deben configurarse de manera independiente al entorno local. En un despliegue, el directorio `storage/` debe residir en un volumen persistente y respaldado.

El alcance no contempla notificaciones externas por correo, SMS o WhatsApp, ni comunicaciÃ³n en tiempo real mediante WebSockets.

## 12. DocumentaciÃ³n complementaria

- [GuÃ­a principal del proyecto](proyecto2.md).
- [Requisitos](docs/requisitos.md).
- [DiseÃ±o](docs/diseno.md).
- [Modelo entidad-relaciÃ³n](docs/MER.md).
- [Contrato de API](docs/contrato-api.md).
- [GuÃ­a de desarrollo](docs/guia-desarrollo.md).
- [Trazabilidad](docs/trazabilidad.md).
- [Trazabilidad](docs/trazabilidad.md).
