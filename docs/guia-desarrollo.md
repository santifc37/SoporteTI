# Guía de desarrollo y trabajo colaborativo

**Proyecto:** SoporteTI  
**Versión:** 1.0  
**Estado:** Acuerdo inicial de desarrollo

---

## 1. Propósito

Este documento establece los acuerdos técnicos y de organización entre los integrantes del proyecto SoporteTI.

Su objetivo es que ambos desarrolladores trabajen con una arquitectura común, responsabilidades claras y criterios compartidos para evitar conflictos durante el desarrollo y la integración del código.

Este documento complementa:

- `docs/requisitos.md`: define qué debe hacer el sistema.
- `docs/diseno.md`: define la arquitectura y las decisiones de diseño.
- `docs/guia-desarrollo.md`: define cómo se organizará y desarrollará el trabajo.

## 2. Distribución de responsabilidades

El desarrollo se dividirá por módulos funcionales y roles del sistema. Cada integrante será responsable tanto del backend como del frontend de sus módulos.

### 2.1. Integrante 1: módulo coordinador

Responsable del desarrollo de las funcionalidades correspondientes al coordinador.

**Backend:**
- Gestión de usuarios.
- Creación y administración de cuentas.
- Gestión de categorías.
- Evaluación de solicitudes.
- Asignación y reasignación de técnicos.
- Gestión de prioridades.
- Cierre de solicitudes.
- Consultas generales y estadísticas.

**Frontend:**
- Panel principal del coordinador.
- Gestión de usuarios.
- Administración de categorías.
- Bandeja general de solicitudes.
- Evaluación y asignación de solicitudes.
- Seguimiento y cierre de solicitudes.
- Visualización de estadísticas.

**Responsabilidad adicional:**
- Desarrollo del backend correspondiente al módulo del solicitante.

### 2.2. Integrante 2: módulo técnico

Responsable del desarrollo de las funcionalidades correspondientes al técnico.

**Backend:**
- Consulta de solicitudes asignadas.
- Registro de intervenciones técnicas.
- Solicitudes de información al solicitante.
- Registro de soluciones.
- Consulta de información necesaria para atender los casos.
- Funcionalidades relacionadas con la atención técnica.

**Frontend:**
- Panel principal del técnico.
- Listado de solicitudes asignadas.
- Vista de detalle de las solicitudes.
- Registro de intervenciones.
- Registro de soluciones.
- Comunicación con el solicitante.
- Seguimiento de solicitudes.

**Responsabilidad adicional:**
- Desarrollo del frontend correspondiente al módulo del solicitante.

### 2.3. Módulo del solicitante

El módulo del solicitante será desarrollado entre ambos integrantes.

| Área | Responsable |
|---|---|
| Backend | Integrante 1 |
| Frontend | Integrante 2 |

**Funcionalidades contempladas:**
- Acceso a la plataforma.
- Creación de solicitudes.
- Consulta de solicitudes propias.
- Seguimiento del estado de las solicitudes.
- Consulta del historial.
- Comunicación con el personal de soporte.
- Envío de archivos adjuntos permitidos.
- Cancelación de solicitudes cuando corresponda.

### 2.4. Funcionalidades compartidas

Las siguientes funcionalidades afectan a varios módulos y requieren acuerdos entre ambos integrantes:

- Autenticación y autorización.
- Administración de roles y permisos.
- Estructura de la base de datos.
- Contratos de los endpoints de la API.
- Conversación entre solicitante y personal de soporte.
- Historial de cambios.
- Almacenamiento de archivos.
- Notificaciones.
- Integración entre frontend y backend.
- Pruebas de integración.

Ambos integrantes deberán acordar el comportamiento de estas funcionalidades antes de implementarlas.

La responsabilidad de implementar cada tarea compartida se establecerá al momento de planificarla. Una tarea tendrá un responsable principal, aunque ambos participen en su definición y revisión.

---

## 3. Arquitectura del proyecto

Se utilizará una arquitectura cliente-servidor:

- **Frontend:** React con TypeScript.
- **Backend:** FastAPI con Python.
- **Base de datos:** PostgreSQL mediante Supabase.
- **Almacenamiento de archivos:** Supabase Storage.
- **Control de versiones:** Git y GitHub.

La comunicación entre frontend y backend se realizará mediante una API REST.

El frontend no deberá conectarse directamente a la base de datos para ejecutar operaciones de negocio. Las operaciones se realizarán a través del backend.

## 4. Estructura del proyecto

Se utilizará una estructura común para que ambos integrantes trabajen sobre la misma organización de archivos.

```text
SoporteTI/
│
├── apps/
│   │
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── coordinador/
│   │   │   │   ├── tecnico/
│   │   │   │   ├── solicitante/
│   │   │   │   └── autenticacion/
│   │   │   │
│   │   │   ├── core/
│   │   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── main.py
│   │   │
│   │   ├── tests/
│   │   ├── alembic/
│   │   └── requirements.txt
│   │
│   └── frontend/
│       ├── src/
│       │   ├── modules/
│       │   │   ├── coordinador/
│       │   │   ├── tecnico/
│       │   │   └── solicitante/
│       │   │
│       │   ├── components/
│       │   ├── layouts/
│       │   ├── services/
│       │   ├── hooks/
│       │   ├── routes/
│       │   ├── types/
│       │   └── main.tsx
│       │
│       └── package.json
│
├── docs/
│   ├── requisitos.md
│   ├── diseno.md
│   ├── guia-desarrollo.md
│   ├── trazabilidad.md
│   └── pruebas.md
│
├── evidencias/
│   └── entrevista/
│
├── README.md
└── .gitignore
```

Esta estructura es la referencia inicial. Si durante el desarrollo se necesita modificarla, ambos integrantes deberán acordar el cambio y actualizar la documentación.

## 5. Acuerdos técnicos compartidos

### 5.1. Backend

- Se utilizará FastAPI para construir la API REST.
- Las rutas se organizarán por módulos funcionales.
- Los modelos representarán las entidades de la base de datos.
- Los esquemas definirán los datos de entrada y salida.
- Los servicios contendrán la lógica de negocio.
- Las rutas no deberán concentrar toda la lógica de negocio.
- Las validaciones de permisos se realizarán en el backend.

### 5.2. Frontend

- Se utilizará React con TypeScript.
- Las interfaces se organizarán por módulos y roles.
- Los componentes reutilizables se ubicarán en `components/`.
- Las llamadas a la API se centralizarán en `services/`.
- Los tipos compartidos se definirán en `types/`.
- La navegación y protección de rutas se organizarán en `routes/`.

### 5.3. Base de datos

- Se utilizará una única base de datos compartida en Supabase.
- Ambos integrantes deberán trabajar con el mismo esquema.
- No se crearán tablas duplicadas para representar una misma entidad.
- Los cambios en tablas, relaciones, restricciones e índices deberán acordarse.
- Los cambios estructurales se registrarán mediante migraciones de Alembic.
- Ningún integrante deberá modificar unilateralmente el esquema compartido.

### 5.4. Contratos de la API

Antes de desarrollar una funcionalidad que conecte frontend y backend, se deberán acordar:

1. Método HTTP.
2. Ruta del endpoint.
3. Parámetros necesarios.
4. Estructura del cuerpo de la petición.
5. Estructura de la respuesta.
6. Posibles errores.
7. Permisos necesarios.

Ejemplo de referencia:

```http
POST /api/v1/solicitudes
```

Petición:

```json
{
  "titulo": "Problema con el equipo",
  "descripcion": "El computador no inicia",
  "categoria_id": 1,
  "prioridad": "media"
}
```

El ejemplo es ilustrativo. Los contratos definitivos deberán corresponder a los requisitos y al diseño aprobado.

Los contratos acordados deberán documentarse para que ambos integrantes puedan desarrollar e integrar sus respectivas partes sin depender de suposiciones.

### 5.5. Funcionalidades compartidas

Se deberán respetar los siguientes acuerdos:

- La autenticación será común para todos los roles.
- Los permisos se comprobarán en el backend.
- El solicitante solo podrá consultar y modificar sus propias solicitudes, según las reglas del sistema.
- El técnico solo tendrá acceso operativo a las solicitudes que tenga asignadas.
- El coordinador tendrá acceso a la administración general.
- La conversación, las intervenciones técnicas y el historial de cambios serán elementos diferentes.
- Los archivos adjuntos respetarán las restricciones establecidas en los requisitos.

---

## 6. Organización del trabajo con Git y GitHub

Se utilizará un flujo de trabajo basado en ramas y Pull Requests.

### 6.1. Rama principal

La rama `main` contendrá la versión integrada y estable del proyecto.

No se desarrollarán funcionalidades directamente sobre `main`.

### 6.2. Ramas de funcionalidades

Cada integrante creará ramas independientes para trabajar en sus funcionalidades.

Se utilizará la siguiente convención:

| Tipo | Convención | Ejemplo |
|---|---|---|
| Funcionalidad | `feature/nombre` | `feature/gestion-usuarios` |
| Corrección | `fix/nombre` | `fix/validacion-login` |
| Documentación | `docs/nombre` | `docs/contratos-api` |
| Refactorización | `refactor/nombre` | `refactor/servicios` |

Una rama deberá partir de la última versión integrada de `main`.

### 6.3. Flujo de trabajo

Para desarrollar una funcionalidad se seguirá este procedimiento:

1. Actualizar la rama `main` local.
2. Crear una rama nueva desde `main`.
3. Desarrollar la funcionalidad correspondiente.
4. Ejecutar las pruebas necesarias.
5. Revisar los archivos modificados.
6. Realizar uno o varios commits.
7. Subir la rama a GitHub.
8. Crear un Pull Request hacia `main`.
9. Revisar los cambios y resolver observaciones.
10. Integrar la funcionalidad cuando esté aprobada.

Ejemplo:

```bash
git switch main
git pull origin main

git switch -c feature/gestion-usuarios
```

Después de desarrollar:

```bash
git status
git add .
git diff --staged
git commit -m "feat: implementar gestion de usuarios"
git push -u origin feature/gestion-usuarios
```

Antes de integrar una funcionalidad, se deberá verificar que no introduzca errores en las funcionalidades existentes.

### 6.4. Reglas para trabajar en paralelo

- Cada integrante trabajará preferiblemente en archivos correspondientes a su módulo.
- No se deberán modificar archivos compartidos sin coordinarlo previamente.
- Si ambos necesitan modificar un mismo archivo, deberán acordar cómo dividir el trabajo.
- Los cambios en `main` deberán incorporarse a las ramas de trabajo antes de completar una integración cuando sea necesario.
- Los conflictos de Git deberán resolverse revisando el contenido y conservando los cambios correctos de ambos integrantes.
- No se deberán sobrescribir cambios de otro integrante sin consultarlo.
- No se integrarán funcionalidades que dependan de contratos todavía no acordados.

---

## 7. Commits

Los mensajes de commit deberán describir brevemente el cambio realizado.

Se utilizarán los siguientes prefijos:

| Prefijo | Uso |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de errores |
| `docs:` | Cambios en documentación |
| `refactor:` | Reorganización del código |
| `test:` | Incorporación o modificación de pruebas |
| `style:` | Cambios de formato sin modificar comportamiento |

Ejemplos:

```text
feat: crear solicitudes
feat: implementar asignacion de tecnicos
fix: corregir validacion de permisos
docs: actualizar contratos de la API
test: agregar pruebas de cierre de solicitudes
```

Cada commit deberá representar un cambio comprensible y relacionado con su mensaje.

---

## 8. Pull Requests

Los Pull Requests serán el mecanismo de integración de las funcionalidades.

Cada Pull Request deberá incluir:

- Nombre claro de la funcionalidad.
- Descripción de lo implementado.
- Módulo afectado.
- Archivos o componentes principales modificados.
- Pruebas realizadas.
- Cambios en base de datos o contratos de API, si existen.

El otro integrante deberá revisar los cambios antes de integrarlos.

No se deberá aprobar automáticamente un Pull Request sin revisar su contenido.

---

## 9. Pruebas e integración

Cada integrante será responsable de probar las funcionalidades que desarrolla.

Se tendrán en cuenta tres niveles:

**Pruebas unitarias:**
- Validaciones.
- Servicios.
- Reglas de negocio.
- Funciones individuales.

**Pruebas de integración:**
- Comunicación entre frontend y backend.
- Consultas a la base de datos.
- Validación de permisos.
- Operaciones que involucren varios módulos.

**Pruebas funcionales:**
- Creación y seguimiento de solicitudes.
- Evaluación y asignación.
- Atención técnica.
- Comunicación entre usuarios.
- Cierre y cancelación.

Las pruebas deberán documentarse en `docs/pruebas.md` y relacionarse con los requisitos correspondientes.

---

## 10. Cambios en los acuerdos

Si durante el desarrollo se identifica la necesidad de cambiar:

- La estructura de carpetas.
- Los contratos de la API.
- Los modelos de datos.
- Las responsabilidades.
- Las reglas de integración.
- Las decisiones arquitectónicas.

Ambos integrantes deberán revisar y aprobar el cambio.

Una vez acordado, se actualizará este documento o el documento técnico correspondiente.

---

## 11. Principio general de colaboración

Aunque cada integrante tenga módulos asignados, el proyecto se considera un único sistema.

Por lo tanto:

- Ningún módulo deberá desarrollarse ignorando el funcionamiento de los demás.
- Ambos integrantes deberán conocer la arquitectura general.
- Las decisiones que afecten a todo el sistema deberán compartirse.
- El código deberá mantener criterios consistentes de organización, nombres y validaciones.
- La integración se realizará progresivamente y no únicamente al final del proyecto.

**El objetivo es que cada integrante pueda desarrollar sus funcionalidades de manera independiente, pero que el resultado final funcione como una sola aplicación coherente.**