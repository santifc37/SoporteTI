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

El backend aplica controles de acceso para restringir las operaciones según el rol y la relación del usuario con cada solicitud.

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

### Documentación

- [Requisitos funcionales y no funcionales](docs/requisitos.md).
- [Diseño de la solución](docs/diseno.md).
- [Contrato de la API](docs/contrato-api.md).
- [Guía de desarrollo](docs/guia-desarrollo.md).
- [Matriz de trazabilidad](docs/trazabilidad.md).
- [Modelo entidad-relación](docs/MER.md).
- [Guía de usuarios](docs/usuarios.md).

## 3. Arquitectura y tecnologías

La solución utiliza una arquitectura cliente-servidor:

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Frontend | React, TypeScript y Vite | Interfaz de usuario y consumo de la API. |
| Backend | Python y FastAPI | API REST, reglas de negocio y autorización. |
| Base de datos | PostgreSQL | Persistencia de usuarios, solicitudes y demás registros. |
| Almacenamiento | Disco local (`apps/backend/storage/`) | Almacenamiento privado de archivos adjuntos. |
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
│   │   ├── scripts/
│   │   ├── storage/          # adjuntos locales (no se versiona)
│   │   ├── tests/
│   │   ├── .env.example
│   │   └── requirements.txt
│   └── frontend/
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── vite.config.ts
├── docs/
├── evidencias/
├── proyecto2.md
└── README.md
```

La carpeta `apps/backend/storage/` se crea automáticamente al subir el primer adjunto y está excluida de Git.

## 4. Configuración del entorno local

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

### 4.2. Configuración de PostgreSQL

Crear una base de datos local llamada:

```text
soporteti_local
```

Por ejemplo, desde PowerShell:

```powershell
psql -U postgres -c "CREATE DATABASE soporteti_local;"
```

La conexión local utiliza PostgreSQL en `localhost`, puerto `5432`.

Ejemplo de conexión:

```text
postgresql+psycopg://postgres:CONTRASEÑA@localhost:5432/soporteti_local
```

La contraseña debe corresponder a la configurada durante la instalación de PostgreSQL. Si contiene caracteres especiales (`@`, `#`, `/`), deben escribirse codificados (por ejemplo, `@` como `%40`).

### 4.3. Configuración del backend

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

Crear el archivo de configuración local a partir del ejemplo:

```powershell
Copy-Item .env.example .env.local
```

Editar `apps/backend/.env.local` y configurar las variables:

```env
DATABASE_URL=postgresql+psycopg://postgres:CONTRASEÑA@localhost:5432/soporteti_local

SESSION_DURATION_HOURS=8
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

La conexión `DATABASE_URL` apunta a PostgreSQL local. Los archivos adjuntos se guardan en `apps/backend/storage/`, por lo que no se necesitan variables adicionales para el almacenamiento.

**Importante:**

- El archivo `.env.local` contiene información privada y no debe subirse al repositorio.
- La carpeta `apps/backend/storage/` contiene archivos privados y no debe subirse al repositorio (ya está en `.gitignore`).
- Utilizar datos ficticios en las demostraciones.

### 4.4. Selección del entorno local

El backend utiliza la variable `APP_ENV` para seleccionar el archivo de configuración:

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

Este comando crea o actualiza las tablas de la base de datos local según las migraciones disponibles.

### 4.6. Ejecutar el backend

Desde `apps/backend`, con el entorno virtual activado:

```powershell
$env:APP_ENV = "local"
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de Swagger estará disponible en:

```text
http://127.0.0.1:8000/docs
```

## 5. Configuración del frontend

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

El frontend utiliza `VITE_API_URL` para determinar la dirección de la API.

La configuración de Vite utiliza un proxy local que redirige las solicitudes `/api` hacia:

```text
http://127.0.0.1:8000
```

Por esta razón, el frontend puede comunicarse con el backend sin configurar una dirección externa durante el desarrollo local.

### Ejecutar el frontend

Desde `apps/frontend`:

```powershell
npm run dev
```

La interfaz estará disponible en:

```text
http://localhost:5173
```

Para utilizar el sistema local deben estar ejecutándose simultáneamente el backend y el frontend.

## 6. Creación de usuarios locales

El proyecto dispone de un script para crear usuarios directamente en la base de datos seleccionada.

Desde `apps/backend`, con el entorno virtual activado:

```powershell
$env:APP_ENV = "local"
```

Ejemplo de creación de un usuario coordinador:

```powershell
python -m scripts.crear_usuario Admin Local admin.local@soporteti.com coordinador
```

Ejemplo de creación de un técnico:

```powershell
python -m scripts.crear_usuario Tecnico Local tecnico.local@soporteti.com tecnico
```

Ejemplo de creación de un solicitante:

```powershell
python -m scripts.crear_usuario Solicitante Local solicitante.local@soporteti.com solicitante
```

El script solicita la contraseña de forma interactiva y la almacena utilizando el mecanismo de hash definido por el backend.

Los roles disponibles son:

- `solicitante`
- `tecnico`
- `coordinador`

Para más información, consultar [docs/usuarios.md](docs/usuarios.md).

## 7. Servicios web y API

La API utiliza el prefijo:

```text
/api/v1
```

La documentación interactiva de los servicios se puede consultar desde Swagger:

```text
http://127.0.0.1:8000/docs
```

La especificación de rutas, métodos HTTP, parámetros, cuerpos de petición, respuestas, permisos y errores se encuentra en:

[docs/contrato-api.md](docs/contrato-api.md).

Los permisos de cada operación dependen del rol autenticado y de las reglas definidas para cada solicitud.

## 8. Archivos adjuntos

Los adjuntos se procesan desde el backend y se almacenan en el disco local, dentro de `apps/backend/storage/`. Sus metadatos y relaciones se conservan en PostgreSQL.

El procesamiento de imágenes contempla:

- Validación del contenido real del archivo.
- Conversión a formato WebP.
- Corrección de orientación cuando existe información EXIF.
- Redimensionamiento de imágenes cuando es necesario.
- Almacenamiento privado en disco local.
- Registro de metadatos en PostgreSQL.
- Validación de permisos y estado de la solicitud.

Los adjuntos pueden asociarse a solicitudes, mensajes o intervenciones, según la operación utilizada.

### Descarga de adjuntos

Los archivos no se exponen públicamente. Las respuestas de la API incluyen, en el campo `url`, una ruta relativa al endpoint autenticado:

```text
/api/v1/attachments/{id}/download
```

Antes de entregar el archivo, el backend valida la sesión del usuario y sus permisos sobre la solicitud, el mensaje o la intervención a la que pertenece el adjunto. Por esta razón, la descarga debe realizarse con la sesión activa del usuario.

### Consideraciones

- `apps/backend/storage/` no se versiona; para conservar los adjuntos debe incluirse en las copias de seguridad del equipo o servidor.
- Los adjuntos que se hayan guardado anteriormente en Supabase Storage no se migran automáticamente. Para conservarlos, deben copiarse a `apps/backend/storage/` respetando la ruta registrada en la base de datos (`ruta_storage`).

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

Las pruebas automatizadas permiten validar los diferentes módulos y reglas de negocio implementados en el backend. Utilizan SQLite en memoria y simulan la lectura y escritura de adjuntos, por lo que no requieren PostgreSQL ni archivos reales en `storage/`.

### 9.2. Pruebas funcionales del proyecto

Las pruebas funcionales deben documentar escenarios reproducibles que permitan verificar:

- Casos exitosos.
- Entradas inválidas.
- Permisos según el rol.
- Persistencia de la información.
- Integridad de los datos.
- Integración entre interfaz, API y base de datos.

Las evidencias de ejecución deben conservarse en:

```text
evidencias/
```

### 9.3. Matriz de trazabilidad

La relación entre condiciones de aceptación, requisitos funcionales, implementación, Pull Requests y pruebas se documenta en:

[docs/trazabilidad.md](docs/trazabilidad.md).

## 10. Organización del desarrollo

El desarrollo se organiza por módulos y requisitos funcionales.

- **Integrante 1:** módulo coordinador y backend del solicitante.
- **Integrante 2:** módulo técnico y frontend del solicitante.
- **Trabajo compartido:** autenticación, sesiones, modelo de datos, contrato de API, conversaciones e integración.

Cada requisito funcional se desarrolla en una rama independiente y se integra mediante Pull Requests, siguiendo el flujo de trabajo definido para el proyecto.

Los cambios deben respetar los requisitos, el diseño, el modelo de datos y el contrato de la API.

## 11. Estado del entorno y consideraciones

El entorno local permite ejecutar el backend y el frontend utilizando únicamente PostgreSQL y el disco del equipo, sin depender de servicios externos como Supabase.

Los archivos de configuración locales (`.env.local`) y la carpeta `apps/backend/storage/` no deben incluirse en los commits.

El despliegue en producción y sus variables de entorno deben configurarse de manera independiente al entorno local. En un despliegue, el directorio `storage/` debe residir en un volumen persistente y respaldado.

El alcance no contempla notificaciones externas por correo, SMS o WhatsApp, ni comunicación en tiempo real mediante WebSockets.

## 12. Documentación complementaria

- [Guía principal del proyecto](proyecto2.md).
- [Requisitos](docs/requisitos.md).
- [Diseño](docs/diseno.md).
- [Modelo entidad-relación](docs/MER.md).
- [Contrato de API](docs/contrato-api.md).
- [Guía de desarrollo](docs/guia-desarrollo.md).
- [Guía de usuarios](docs/usuarios.md).
- [Trazabilidad](docs/trazabilidad.md).