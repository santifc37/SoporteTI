# Contrato de la API — SoporteTI

**Versión:** 1.0  
**Estado:** Contrato propuesto para iniciar el desarrollo  
**Proyecto:** SoporteTI  
**Asignatura:** Aplicaciones y Servicios Web  
**Institución:** Instituto Tecnológico Metropolitano (ITM)

---

## 1. Objetivo

Este documento establece el contrato de comunicación entre el frontend y el backend de SoporteTI.

Define las rutas, métodos HTTP, parámetros, estructuras de petición, respuestas, permisos y reglas que deberán respetarse durante el desarrollo.

Su propósito es permitir que los integrantes trabajen en paralelo sobre los módulos de coordinador, técnico y solicitante, manteniendo una integración consistente.

Este contrato complementa:

- `docs/requisitos.md`
- `docs/diseno.md`
- `docs/guia-desarrollo.md`

Los cambios que afecten rutas, nombres de campos, estructuras de respuesta, permisos o reglas de negocio deberán acordarse entre los integrantes y reflejarse en este documento antes de implementarse.

## 2. Convenciones generales

### 2.1. URL base y versión

Todas las rutas estarán bajo el prefijo:

```text
/api/v1
```

La URL completa dependerá del entorno donde se encuentre desplegado el backend.

### 2.2. Métodos HTTP

| Método | Utilización |
|---|---|
| GET | Consultar información. |
| POST | Crear recursos o ejecutar operaciones. |
| PATCH | Modificar parcialmente un recurso. |
| DELETE | No se utilizará para eliminar solicitudes ni registros históricos. |

### 2.3. Formato de intercambio

- Las peticiones y respuestas utilizarán JSON.
- Los nombres de los campos utilizarán `snake_case`.
- Las fechas se transmitirán en formato ISO 8601 con zona horaria.
- Los identificadores serán UUID.
- Los valores numéricos deberán enviarse como números JSON, no como cadenas.
- Los campos opcionales podrán omitirse o enviarse como `null`, según corresponda.
- Los recursos históricos no podrán eliminarse mediante las operaciones normales de la API.

### 2.4. Convenciones de nombres

Las rutas utilizarán nombres en inglés y en plural para los recursos.

Ejemplos:

```text
/api/v1/users
/api/v1/requests
/api/v1/categories
/api/v1/interventions
```

Los campos JSON utilizarán nombres en español, manteniendo coherencia con el modelo de datos del proyecto.

### 2.5. Identificadores

Los recursos principales utilizarán identificadores UUID.

Ejemplo:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

El número legible de una solicitud será independiente de su UUID.

---

## 3. Roles y autorización

La API reconocerá tres roles:

| Valor | Descripción |
|---|---|
| `solicitante` | Usuario que registra y consulta sus solicitudes. |
| `tecnico` | Personal encargado de atender solicitudes asignadas. |
| `coordinador` | Usuario encargado de administrar y supervisar el sistema. |

### 3.1. Matriz general de permisos

| Operación | Solicitante | Técnico asignado | Coordinador |
|---|---:|---:|---:|
| Iniciar y cerrar sesión | Sí | Sí | Sí |
| Consultar sus propios datos | Sí | Sí | Sí |
| Consultar usuarios | No | No | Sí |
| Crear usuarios | No | No | Sí |
| Modificar usuarios | Solo datos propios permitidos | Solo datos propios permitidos | Sí |
| Gestionar categorías | No | No | Sí |
| Crear solicitudes | Sí | No | No |
| Consultar solicitudes | Propias | Asignadas actualmente | Todas |
| Clasificar solicitudes | No | No | Sí |
| Modificar prioridad | No | No | Sí |
| Asignar técnicos | No | No | Sí |
| Reasignar técnicos | No | No | Sí |
| Cambiar estados permitidos | No | Sí | Sí, según transición |
| Cancelar solicitudes | Propias y en estados permitidos | No | No |
| Registrar intervenciones | No | Sí | No |
| Solicitar información adicional | No | Sí | Sí |
| Responder peticiones de información | Sí, en solicitudes propias | No | No |
| Enviar mensajes | Sí, en solicitudes propias | Sí, en solicitudes asignadas | Sí |
| Registrar soluciones | No | Sí | No |
| Cerrar solicitudes | No | No | Sí |
| Consultar historial | Propias | Asignadas actualmente | Todas |
| Consultar estadísticas | No | No | Sí |

### 3.2. Reglas de autorización por solicitud

El backend deberá verificar la relación del usuario con cada solicitud.

**Solicitante:**
- Solo puede acceder a solicitudes donde sea el propietario.
- Puede consultar el historial y la conversación de sus solicitudes.
- Puede cancelar solicitudes propias cuando el estado lo permita.
- No puede consultar intervenciones internas.

**Técnico:**
- Solo puede acceder operativamente a solicitudes que tenga asignadas actualmente.
- Puede registrar intervenciones, solicitar información y enviar mensajes.
- Al ser reasignado un caso, pierde el acceso operativo a esa solicitud.
- No puede consultar intervenciones internas de solicitudes que ya no tenga asignadas.

**Coordinador:**
- Puede consultar todas las solicitudes.
- Puede administrar usuarios y categorías.
- Puede evaluar, clasificar, asignar y reasignar solicitudes.
- Puede participar en las conversaciones.
- Puede revisar soluciones y cerrar solicitudes.

Una solicitud cerrada conservará su información, conversación e historial. Los usuarios autorizados podrán consultarlos, pero no realizar nuevas operaciones de atención.

---

## 4. Autenticación y sesiones

La autenticación se realizará mediante sesiones gestionadas por el backend.

Se utilizará una cookie protegida para identificar al usuario autenticado.

El frontend no deberá almacenar contraseñas, tokens de sesión ni credenciales administrativas de Supabase.

### 4.1. Iniciar sesión

**Método:** `POST`

**Ruta:**

```text
/api/v1/auth/login
```

**Permisos:** Público.

**Petición:**

```json
{
  "correo": "usuario@organizacion.com",
  "contrasena": "MiContrasena123"
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Inicio de sesión exitoso",
  "usuario": {
    "id": "uuid",
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo": "usuario@organizacion.com",
    "rol": "solicitante"
  }
}
```

El backend establecerá la cookie de sesión mediante los encabezados HTTP correspondientes.

Si las credenciales son incorrectas, devolverá `401 Unauthorized`.

### 4.2. Cerrar sesión

**Método:** `POST`

**Ruta:**

```text
/api/v1/auth/logout
```

**Permisos:** Usuario autenticado.

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Sesión cerrada correctamente"
}
```

El backend invalidará la sesión y eliminará la cookie correspondiente.

### 4.3. Consultar usuario autenticado

**Método:** `GET`

**Ruta:**

```text
/api/v1/auth/me
```

**Permisos:** Usuario autenticado.

**Respuesta:** `200 OK`

```json
{
  "usuario": {
    "id": "uuid",
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo": "usuario@organizacion.com",
    "rol": "solicitante",
    "activo": true
  }
}
```

Si no existe una sesión válida, devolverá `401 Unauthorized`.

### 4.4. Cambio de contraseña

**Método:** `POST`

**Ruta:**

```text
/api/v1/auth/change-password
```

**Permisos:** Usuario autenticado.

**Petición:**

```json
{
  "contrasena_actual": "ContrasenaAnterior",
  "contrasena_nueva": "ContrasenaNueva123"
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Contraseña actualizada correctamente"
}
```

El backend deberá comprobar la contraseña actual antes de actualizar el hash almacenado.

El procedimiento de recuperación de contraseña mediante verificación externa se implementará cuando se defina y configure el servicio necesario para realizarlo. No se permitirá recuperar una cuenta únicamente proporcionando un correo electrónico.

---

## 5. Usuarios

### 5.1. Consultar usuarios

**Método:** `GET`

**Ruta:**

```text
/api/v1/users
```

**Permisos:** Coordinador.

**Parámetros opcionales:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `rol` | string | Filtrar por rol. |
| `activo` | boolean | Filtrar por estado de la cuenta. |
| `busqueda` | string | Buscar por nombre o correo. |
| `page` | integer | Página solicitada. |
| `limit` | integer | Cantidad de resultados. |

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "nombre": "Juan",
      "apellido": "Pérez",
      "correo": "juan@organizacion.com",
      "rol": "tecnico",
      "activo": true,
      "medio_contacto_preferido": "correo",
      "telefono": "3001234567",
      "fecha_creacion": "2026-11-06T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

### 5.2. Consultar un usuario

**Método:** `GET`

**Ruta:**

```text
/api/v1/users/{id}
```

**Permisos:** Coordinador.

**Respuesta:** `200 OK`

```json
{
  "id": "uuid",
  "nombre": "Juan",
  "apellido": "Pérez",
  "correo": "juan@organizacion.com",
  "rol": "tecnico",
  "activo": true,
  "medio_contacto_preferido": "correo",
  "telefono": "3001234567",
  "fecha_creacion": "2026-11-06T10:00:00Z",
  "fecha_actualizacion": "2026-11-06T10:00:00Z"
}
```

### 5.3. Crear usuario

**Método:** `POST`

**Ruta:**

```text
/api/v1/users
```

**Permisos:** Coordinador.

**Petición:**

```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "correo": "juan@organizacion.com",
  "contrasena": "Contrasena123",
  "rol": "tecnico",
  "medio_contacto_preferido": "correo",
  "telefono": "3001234567"
}
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Usuario creado correctamente",
  "usuario": {
    "id": "uuid",
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo": "juan@organizacion.com",
    "rol": "tecnico",
    "activo": true
  }
}
```

Reglas:
- El correo debe ser único.
- La contraseña deberá cumplir las políticas de seguridad.
- El rol debe ser uno de los valores permitidos.
- La cuenta se creará activa por defecto.
- La contraseña nunca deberá devolverse en las respuestas.

### 5.4. Modificar usuario

**Método:** `PATCH`

**Ruta:**

```text
/api/v1/users/{id}
```

**Permisos:**
- El coordinador puede modificar los datos administrativos de cualquier usuario.
- Un usuario puede modificar sus propios datos de contacto permitidos.

**Petición de ejemplo:**

```json
{
  "nombre": "Juan Carlos",
  "telefono": "3009876543",
  "medio_contacto_preferido": "telefono"
}
```

El coordinador también podrá modificar los campos administrativos permitidos:

```json
{
  "rol": "tecnico",
  "activo": false
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Usuario actualizado correctamente",
  "usuario": {
    "id": "uuid",
    "nombre": "Juan Carlos",
    "apellido": "Pérez",
    "correo": "juan@organizacion.com",
    "rol": "tecnico",
    "activo": true
  }
}
```

Reglas:
- No se permitirá modificar directamente el identificador.
- No se permitirá modificar el hash de contraseña mediante esta ruta.
- Desactivar una cuenta impedirá iniciar nuevas sesiones y acceder a operaciones protegidas.
- Un usuario no podrá cambiar su propio rol ni activar su propia cuenta.

---

## 6. Categorías

### 6.1. Consultar categorías

**Método:** `GET`

**Ruta:**

```text
/api/v1/categories
```

**Permisos:** Usuarios autenticados.

**Parámetros opcionales:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `activa` | boolean | Filtrar categorías activas o inactivas. |
| `busqueda` | string | Buscar por nombre. |
| `page` | integer | Página solicitada. |
| `limit` | integer | Cantidad de resultados. |

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "nombre": "Hardware",
      "descripcion": "Problemas relacionados con componentes físicos",
      "activa": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

### 6.2. Crear categoría

**Método:** `POST`

**Ruta:**

```text
/api/v1/categories
```

**Permisos:** Coordinador.

**Petición:**

```json
{
  "nombre": "Hardware",
  "descripcion": "Problemas relacionados con componentes físicos"
}
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Categoría creada correctamente",
  "categoria": {
    "id": "uuid",
    "nombre": "Hardware",
    "descripcion": "Problemas relacionados con componentes físicos",
    "activa": true
  }
}
```

### 6.3. Modificar categoría

**Método:** `PATCH`

**Ruta:**

```text
/api/v1/categories/{id}
```

**Permisos:** Coordinador.

**Petición:**

```json
{
  "nombre": "Hardware y periféricos",
  "descripcion": "Problemas de equipos y dispositivos",
  "activa": true
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Categoría actualizada correctamente",
  "categoria": {
    "id": "uuid",
    "nombre": "Hardware y periféricos",
    "descripcion": "Problemas de equipos y dispositivos",
    "activa": true
  }
}
```

Las categorías utilizadas por solicitudes existentes no se eliminarán físicamente. Para retirarlas del uso se cambiará su estado a inactivo.

---

## 7. Solicitudes

### 7.1. Consultar solicitudes

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests
```

**Permisos:**
- Solicitante: únicamente sus solicitudes.
- Técnico: únicamente las solicitudes asignadas actualmente.
- Coordinador: todas las solicitudes.

**Parámetros opcionales:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `estado` | string | Filtrar por estado. |
| `prioridad` | string | Filtrar por prioridad. |
| `categoria_id` | UUID | Filtrar por categoría. |
| `tipo` | string | `incidente` o `requerimiento`. |
| `solicitante_id` | UUID | Filtrar por solicitante. |
| `tecnico_id` | UUID | Filtrar por técnico asignado. |
| `fecha_desde` | datetime | Fecha inicial. |
| `fecha_hasta` | datetime | Fecha final. |
| `tipo_cierre` | string | Filtrar por tipo de cierre. |
| `busqueda` | string | Buscar por número o título. |
| `page` | integer | Página solicitada. |
| `limit` | integer | Cantidad de resultados. |

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "numero": "ST-000001",
      "titulo": "Equipo no enciende",
      "tipo": "incidente",
      "prioridad": "alta",
      "estado": "en_atencion",
      "categoria": {
        "id": "uuid",
        "nombre": "Hardware"
      },
      "solicitante": {
        "id": "uuid",
        "nombre": "Juan Pérez"
      },
      "tecnico_asignado": {
        "id": "uuid",
        "nombre": "Carlos Gómez"
      },
      "fecha_creacion": "2026-11-06T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

El backend aplicará los permisos antes de devolver los resultados. No será responsabilidad exclusiva del frontend filtrar los registros.

### 7.2. Crear solicitud

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests
```

**Permisos:** Solicitante.

**Petición:**

```json
{
  "titulo": "Equipo no enciende",
  "descripcion": "El computador no enciende al presionar el botón de encendido.",
  "tipo": "incidente",
  "categoria_id": "uuid",
  "ubicacion": "Oficina administrativa",
  "placa_equipo": "EQ-001",
  "medio_contacto": "correo",
  "dato_contacto": "juan@organizacion.com"
}
```

Los siguientes campos son obligatorios:
- `titulo`
- `descripcion`
- `tipo`
- `ubicacion`
- `medio_contacto`
- `dato_contacto`

`categoria_id` y `placa_equipo` podrán ser nulos cuando no correspondan.

El solicitante se obtendrá de la sesión autenticada. No se aceptará `solicitante_id` enviado por el frontend como fuente de autorización.

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Solicitud creada correctamente",
  "solicitud": {
    "id": "uuid",
    "numero": "ST-000001",
    "titulo": "Equipo no enciende",
    "descripcion": "El computador no enciende al presionar el botón de encendido.",
    "tipo": "incidente",
    "prioridad": null,
    "estado": "registrado",
    "solicitante_id": "uuid",
    "categoria_id": "uuid",
    "fecha_creacion": "2026-11-06T10:00:00Z"
  }
}
```

Reglas:
- El estado inicial será `registrado`.
- La prioridad será establecida por el coordinador durante la evaluación.
- El solicitante se asociará automáticamente a la sesión.
- La creación deberá quedar registrada en el historial.

### 7.3. Consultar detalle de solicitud

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}
```

**Permisos:**
- Solicitante propietario.
- Técnico asignado actualmente.
- Coordinador.

**Respuesta:** `200 OK`

```json
{
  "id": "uuid",
  "numero": "ST-000001",
  "titulo": "Equipo no enciende",
  "descripcion": "El computador no enciende.",
  "tipo": "incidente",
  "prioridad": "alta",
  "estado": "en_atencion",
  "ubicacion": "Oficina administrativa",
  "placa_equipo": "EQ-001",
  "medio_contacto": "correo",
  "dato_contacto": "juan@organizacion.com",
  "solicitante": {
    "id": "uuid",
    "nombre": "Juan Pérez"
  },
  "categoria": {
    "id": "uuid",
    "nombre": "Hardware"
  },
  "tecnico_asignado": {
    "id": "uuid",
    "nombre": "Carlos Gómez"
  },
  "tipo_cierre": null,
  "motivo_cierre": null,
  "solucion_final": null,
  "fecha_creacion": "2026-11-06T10:00:00Z",
  "fecha_actualizacion": "2026-11-06T11:00:00Z",
  "fecha_cierre": null
}
```

Los datos relacionados se devolverán de acuerdo con los permisos del usuario.

### 7.4. Modificar clasificación y prioridad

**Método:** `PATCH`

**Ruta:**

```text
/api/v1/requests/{id}
```

**Permisos:** Coordinador.

**Petición:**

```json
{
  "categoria_id": "uuid",
  "prioridad": "alta"
}
```

Los campos podrán enviarse individualmente o juntos.

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Solicitud actualizada correctamente",
  "solicitud": {
    "id": "uuid",
    "numero": "ST-000001",
    "categoria_id": "uuid",
    "prioridad": "alta",
    "estado": "en_evaluacion"
  }
}
```

Reglas:
- Solo se podrán modificar los campos permitidos para esta operación.
- Las prioridades válidas serán `baja`, `media` y `alta`.
- Los cambios deberán quedar registrados en el historial.
- No se permitirá modificar solicitudes cerradas.
- Los datos de creación, propietario y cierre no podrán modificarse por esta ruta.

---

## 8. Evaluación y estados

Los valores internos utilizados por la API serán:

| Valor API | Nombre mostrado |
|---|---|
| `registrado` | Registrado |
| `en_evaluacion` | En evaluación |
| `asignado` | Asignado |
| `en_atencion` | En atención |
| `en_espera` | En espera |
| `resuelto` | Resuelto |
| `cerrado` | Cerrado |

### 8.1. Cambiar estado

**Método:** `PATCH`

**Ruta:**

```text
/api/v1/requests/{id}/status
```

**Permisos:** Coordinador o técnico asignado, dependiendo de la transición.

**Petición:**

```json
{
  "estado": "en_atencion"
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Estado actualizado correctamente",
  "solicitud": {
    "id": "uuid",
    "estado_anterior": "asignado",
    "estado_actual": "en_atencion",
    "fecha_actualizacion": "2026-11-06T12:00:00Z"
  }
}
```

Esta ruta solo permitirá las transiciones normales definidas en los requisitos:

| Estado actual | Estado siguiente | Responsable |
|---|---|---|
| `registrado` | `en_evaluacion` | Coordinador |
| `asignado` | `en_atencion` | Técnico asignado |
| `en_atencion` | `en_espera` | Técnico asignado |
| `en_espera` | `en_atencion` | Técnico asignado |

Las transiciones de cierre y resolución se realizarán mediante sus rutas específicas.

El backend rechazará cualquier transición no permitida con `409 Conflict`.

---

## 9. Asignaciones

### 9.1. Asignar o reasignar técnico

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/assignments
```

**Permisos:** Coordinador.

**Petición:**

```json
{
  "tecnico_id": "uuid",
  "observacion": "Asignación inicial del caso"
}
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Técnico asignado correctamente",
  "asignacion": {
    "id": "uuid",
    "solicitud_id": "uuid",
    "tecnico_id": "uuid",
    "asignado_por": "uuid",
    "fecha_asignacion": "2026-11-06T12:00:00Z",
    "fecha_finalizacion": null,
    "observacion": "Asignación inicial del caso"
  },
  "estado_solicitud": "asignado"
}
```

Reglas:
- El técnico debe existir y estar activo.
- La primera asignación se realizará sobre una solicitud en `en_evaluacion`.
- La primera asignación cambiará el estado a `asignado`.
- Una reasignación finalizará la asignación anterior y creará una nueva.
- Solo podrá existir una asignación activa por solicitud.
- La reasignación no borrará el historial de asignaciones.
- La reasignación no cambiará automáticamente el estado de una solicitud que ya se encuentre en atención o espera.
- El técnico anterior perderá el acceso operativo después de la reasignación.
- La operación y el cambio de responsable deberán registrarse en el historial.

### 9.2. Consultar asignaciones de una solicitud

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}/assignments
```

**Permisos:**
- Coordinador.
- Técnico actualmente asignado.
- Solicitante propietario, para consultar el responsable actual.

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "tecnico_id": "uuid",
      "tecnico_nombre": "Carlos Gómez",
      "asignado_por": "uuid",
      "fecha_asignacion": "2026-11-06T12:00:00Z",
      "fecha_finalizacion": null,
      "observacion": "Asignación inicial del caso"
    }
  ]
}
```

El solicitante solo recibirá la información del responsable actual, no información administrativa interna de las asignaciones anteriores.

---

## 10. Intervenciones técnicas

### 10.1. Registrar intervención

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/interventions
```

**Permisos:** Técnico asignado actualmente.

**Petición:**

```json
{
  "descripcion": "Se revisó la conexión eléctrica del equipo.",
  "diagnostico": "El cable de alimentación presenta daños.",
  "solucion": null,
  "visibilidad": "solicitante"
}
```

Valores permitidos para `visibilidad`:
- `interna`
- `solicitante`

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Intervención registrada correctamente",
  "intervencion": {
    "id": "uuid",
    "solicitud_id": "uuid",
    "tecnico_id": "uuid",
    "descripcion": "Se revisó la conexión eléctrica del equipo.",
    "diagnostico": "El cable de alimentación presenta daños.",
    "solucion": null,
    "visibilidad": "solicitante",
    "fecha_registro": "2026-11-06T13:00:00Z"
  }
}
```

Reglas:
- La descripción es obligatoria.
- El técnico se obtiene de la sesión autenticada.
- La solicitud debe estar asignada actualmente al técnico.
- No se permitirán intervenciones en solicitudes cerradas.
- Las intervenciones internas no serán visibles para el solicitante.

### 10.2. Consultar intervenciones

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}/interventions
```

**Permisos:**
- Solicitante propietario: únicamente intervenciones visibles.
- Técnico asignado: intervenciones de su solicitud asignada.
- Coordinador: todas las intervenciones.

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "tecnico_id": "uuid",
      "tecnico_nombre": "Carlos Gómez",
      "descripcion": "Se revisó la conexión eléctrica del equipo.",
      "diagnostico": "El cable presenta daños.",
      "solucion": null,
      "visibilidad": "solicitante",
      "fecha_registro": "2026-11-06T13:00:00Z"
    }
  ]
}
```

Las intervenciones se devolverán en orden cronológico.

---

## 11. Solicitudes de información adicional

### 11.1. Crear petición de información

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/information-requests
```

**Permisos:**
- Técnico asignado actualmente.
- Coordinador.

**Petición:**

```json
{
  "contenido": "Por favor, indique si el equipo presenta alguna luz al conectarlo."
}
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Solicitud de información registrada correctamente",
  "solicitud_informacion": {
    "id": "uuid",
    "solicitud_id": "uuid",
    "solicitado_por": "uuid",
    "contenido": "Por favor, indique si el equipo presenta alguna luz al conectarlo.",
    "estado": "pendiente",
    "fecha_solicitud": "2026-11-06T13:30:00Z"
  }
}
```

Reglas:
- El contenido es obligatorio.
- La petición deberá asociarse a una solicitud abierta.
- El autor se obtendrá de la sesión.
- La petición no cambiará automáticamente el estado.
- Si la atención debe quedar detenida, el técnico realizará por separado la transición a `en_espera`.

### 11.2. Consultar peticiones de información

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}/information-requests
```

**Permisos:**
- Solicitante propietario.
- Técnico asignado actualmente.
- Coordinador.

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "contenido": "Por favor, indique si el equipo presenta alguna luz al conectarlo.",
      "estado": "pendiente",
      "solicitado_por": {
        "id": "uuid",
        "nombre": "Carlos Gómez",
        "rol": "tecnico"
      },
      "fecha_solicitud": "2026-11-06T13:30:00Z",
      "respuesta": null
    }
  ]
}
```

### 11.3. Responder petición de información

**Método:** `POST`

**Ruta:**

```text
/api/v1/information-requests/{id}/responses
```

**Permisos:** Solicitante propietario de la solicitud relacionada.

**Petición:**

```json
{
  "contenido": "Sí, el equipo enciende una luz roja al conectarlo."
}
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Respuesta registrada correctamente",
  "respuesta": {
    "id": "uuid",
    "solicitud_informacion_id": "uuid",
    "respondido_por": "uuid",
    "contenido": "Sí, el equipo enciende una luz roja al conectarlo.",
    "fecha_respuesta": "2026-11-06T14:00:00Z"
  }
}
```

Reglas:
- La petición debe pertenecer a una solicitud del usuario autenticado.
- La petición debe encontrarse pendiente.
- Solo se admitirá una respuesta principal por petición.
- Al responder, la petición pasará a estado `respondida`.
- La respuesta no cambiará automáticamente el estado de la solicitud.
- No se permitirán respuestas en solicitudes cerradas.

---

## 12. Conversación y mensajes

### 12.1. Consultar mensajes

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}/messages
```

**Permisos:**
- Solicitante propietario.
- Técnico asignado actualmente.
- Coordinador.

**Parámetros opcionales:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `page` | integer | Página solicitada. |
| `limit` | integer | Cantidad de mensajes. |
| `desde` | datetime | Consultar mensajes posteriores a una fecha. |

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "solicitud_id": "uuid",
      "remitente": {
        "id": "uuid",
        "nombre": "Juan Pérez",
        "rol": "solicitante"
      },
      "contenido": "El equipo sigue sin encender.",
      "fecha_envio": "2026-11-06T14:10:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

Los mensajes deberán devolverse en orden cronológico.

### 12.2. Enviar mensaje

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/messages
```

**Permisos:**
- Solicitante propietario.
- Técnico asignado actualmente.
- Coordinador.

**Petición:**

```json
{
  "contenido": "El equipo sigue sin encender."
}
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Mensaje enviado correctamente",
  "data": {
    "id": "uuid",
    "solicitud_id": "uuid",
    "remitente_id": "uuid",
    "contenido": "El equipo sigue sin encender.",
    "fecha_envio": "2026-11-06T14:10:00Z"
  }
}
```

Reglas:
- El contenido es obligatorio.
- El remitente se obtiene de la sesión.
- No se permitirá enviar mensajes en solicitudes cerradas.
- El técnico debe estar asignado actualmente.
- Enviar un mensaje no modificará el estado de la solicitud.
- Los mensajes no reemplazan las intervenciones ni las peticiones de información.

La primera versión utilizará consultas REST para actualizar la conversación. No se utilizarán WebSockets.

---

## 13. Registro de soluciones y cierre

### 13.1. Registrar solución

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/resolve
```

**Permisos:** Técnico asignado actualmente.

**Petición:**

```json
{
  "solucion": "Se reemplazó el cable de alimentación y se comprobó el funcionamiento del equipo."
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Solución registrada correctamente",
  "solicitud": {
    "id": "uuid",
    "estado_anterior": "en_atencion",
    "estado_actual": "resuelto",
    "solucion_final": "Se reemplazó el cable de alimentación y se comprobó el funcionamiento del equipo.",
    "fecha_actualizacion": "2026-11-06T15:00:00Z"
  }
}
```

Reglas:
- La solución es obligatoria.
- Solo el técnico asignado puede registrar la solución.
- La solicitud debe estar en `en_atencion` o `en_espera`.
- El registro cambiará el estado a `resuelto`.
- La solución deberá quedar registrada en el historial.
- El técnico no podrá cerrar la solicitud.

### 13.2. Cerrar solicitud

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/close
```

**Permisos:** Coordinador.

Esta operación contempla el cierre por solución o por causa administrativa.

**Petición para cierre por solución:**

```json
{
  "tipo_cierre": "solucion"
}
```

**Petición para cierre administrativo:**

```json
{
  "tipo_cierre": "administrativo",
  "motivo_cierre": "La solicitud no corresponde a los servicios prestados por el área de soporte."
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Solicitud cerrada correctamente",
  "solicitud": {
    "id": "uuid",
    "estado_anterior": "resuelto",
    "estado_actual": "cerrado",
    "tipo_cierre": "solucion",
    "motivo_cierre": null,
    "cerrado_por": "uuid",
    "fecha_cierre": "2026-11-06T16:00:00Z"
  }
}
```

Reglas:
- El cierre por solución solo se permitirá desde `resuelto`.
- El cierre administrativo solo se permitirá desde `en_evaluacion`.
- El cierre administrativo exige un motivo.
- El tipo de cierre deberá ser `solucion` o `administrativo`.
- El responsable y la fecha de cierre se obtendrán del backend.
- El cierre deberá quedar registrado en el historial.
- Una solicitud cerrada no podrá reabrirse.

### 13.3. Cancelar solicitud

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/cancel
```

**Permisos:** Solicitante propietario.

**Petición:**

```json
{
  "motivo": "Ya no necesito asistencia para este problema."
}
```

**Respuesta:** `200 OK`

```json
{
  "mensaje": "Solicitud cancelada correctamente",
  "solicitud": {
    "id": "uuid",
    "estado_anterior": "registrado",
    "estado_actual": "cerrado",
    "tipo_cierre": "cancelacion",
    "motivo_cierre": "Ya no necesito asistencia para este problema.",
    "cerrado_por": "uuid",
    "fecha_cierre": "2026-11-06T16:00:00Z"
  }
}
```

Reglas:
- Solo se permitirá cancelar solicitudes propias.
- La solicitud deberá estar en `registrado` o `en_evaluacion`.
- El motivo será obligatorio.
- El tipo de cierre será `cancelacion`.
- La cancelación quedará registrada en el historial.

---

## 14. Historial de cambios

### 14.1. Consultar historial

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}/history
```

**Permisos:**
- Solicitante propietario.
- Técnico actualmente asignado.
- Coordinador.

**Parámetros opcionales:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `page` | integer | Página solicitada. |
| `limit` | integer | Cantidad de registros. |

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "solicitud_id": "uuid",
      "usuario": {
        "id": "uuid",
        "nombre": "Carlos Gómez",
        "rol": "coordinador"
      },
      "tipo_cambio": "cambio_estado",
      "valor_anterior": "registrado",
      "valor_nuevo": "en_evaluacion",
      "observacion": "Inicio de evaluación",
      "fecha_cambio": "2026-11-06T11:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

Reglas:
- El historial se conservará de forma permanente según las reglas de retención del proyecto.
- Los usuarios no podrán modificar ni eliminar registros históricos mediante la API.
- Los cambios importantes deberán registrarse junto con el usuario responsable y la fecha.
- La consulta del historial no se confundirá con la consulta de mensajes ni de intervenciones.

---

## 15. Archivos adjuntos

Los archivos se almacenarán en Supabase Storage mediante el backend.

Se utilizará un bucket privado.

### 15.1. Adjuntar imagen a solicitud

**Método:** `POST`

**Ruta:**

```text
/api/v1/requests/{id}/attachments
```

**Permisos:**
- Solicitante propietario.
- Técnico asignado actualmente.
- Coordinador.

**Formato:** `multipart/form-data`

**Campo:**

```text
archivo: imagen.png
```

**Respuesta:** `201 Created`

```json
{
  "mensaje": "Archivo adjuntado correctamente",
  "adjunto": {
    "id": "uuid",
    "solicitud_id": "uuid",
    "nombre_archivo": "imagen.png",
    "tipo_archivo": "image/png",
    "tamano": 204800,
    "fecha_subida": "2026-11-06T16:30:00Z"
  }
}
```

Reglas:
- Se permitirán PNG, JPG y JPEG.
- El tamaño máximo será de 5 MB por archivo.
- El backend validará el contenido real del archivo, no solamente su extensión.
- El archivo se almacenará en un bucket privado.
- Se guardarán los metadatos en PostgreSQL.
- No se permitirán adjuntos en solicitudes cerradas.
- El usuario deberá tener acceso a la solicitud.
- La ruta interna de Storage no se expondrá como enlace público.

### 15.2. Consultar adjuntos de una solicitud

**Método:** `GET`

**Ruta:**

```text
/api/v1/requests/{id}/attachments
```

**Permisos:**
- Solicitante propietario.
- Técnico asignado actualmente.
- Coordinador.

**Respuesta:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "nombre_archivo": "imagen.png",
      "tipo_archivo": "image/png",
      "tamano": 204800,
      "subido_por": "uuid",
      "fecha_subida": "2026-11-06T16:30:00Z"
    }
  ]
}
```

### 15.3. Consultar o descargar archivo

**Método:** `GET`

**Ruta:**

```text
/api/v1/attachments/{id}/download
```

**Permisos:** Usuarios autorizados para consultar la solicitud relacionada.

**Respuesta:** Archivo binario o redirección/enlace temporal autorizado, según la implementación de Storage.

El backend deberá validar los permisos antes de proporcionar acceso al archivo.

### 15.4. Adjuntos en mensajes e intervenciones

Los adjuntos asociados a mensajes e intervenciones corresponden a funcionalidades complementarias de prioridad baja.

Si se implementan, utilizarán rutas específicas:

```text
POST /api/v1/requests/{id}/messages/{message_id}/attachments
POST /api/v1/requests/{id}/interventions/{intervention_id}/attachments
```

Estas operaciones deberán respetar los mismos límites de formato, tamaño y autorización definidos para los adjuntos.

No son necesarias para cerrar los primeros flujos principales.

---

## 16. Estadísticas

### 16.1. Consultar estadísticas

**Método:** `GET`

**Ruta:**

```text
/api/v1/statistics
```

**Permisos:** Coordinador.

**Parámetros opcionales:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `fecha_desde` | datetime | Fecha inicial del periodo. |
| `fecha_hasta` | datetime | Fecha final del periodo. |

**Respuesta:** `200 OK`

```json
{
  "total_solicitudes": 100,
  "por_estado": {
    "registrado": 10,
    "en_evaluacion": 15,
    "asignado": 20,
    "en_atencion": 25,
    "en_espera": 10,
    "resuelto": 10,
    "cerrado": 10
  },
  "por_prioridad": {
    "baja": 30,
    "media": 40,
    "alta": 30
  },
  "por_categoria": [
    {
      "categoria_id": "uuid",
      "nombre": "Hardware",
      "cantidad": 40
    }
  ],
  "tiempo_promedio_atencion": null
}
```

Reglas:
- Los resultados se calcularán a partir de los registros existentes.
- El tiempo promedio solo se devolverá cuando exista información suficiente para calcularlo.
- El módulo será exclusivo del coordinador.
- Los filtros de fechas deberán aplicarse de forma consistente a los indicadores.

---

## 17. Paginación y filtros

Los endpoints de consulta que devuelvan colecciones utilizarán paginación cuando corresponda.

Parámetros generales:

| Parámetro | Tipo | Valor predeterminado |
|---|---|---|
| `page` | integer | 1 |
| `limit` | integer | 20 |

Reglas:
- `page` debe ser mayor o igual a 1.
- `limit` debe ser mayor o igual a 1.
- El límite máximo será de 100 registros por petición.
- Los resultados deberán mantener un orden estable.
- Los listados deberán devolver el objeto `pagination`.

Estructura:

```json
{
  "page": 1,
  "limit": 20,
  "total": 50,
  "total_pages": 3
}
```

Si no existen resultados, `data` será un arreglo vacío y `total` será 0.

Los filtros no podrán ampliar los permisos del usuario. Por ejemplo, un técnico no podrá consultar solicitudes de otro técnico enviando su identificador en `tecnico_id`.

---

## 18. Formato general de errores

Todas las respuestas de error utilizarán una estructura consistente.

**Ejemplo:**

```json
{
  "error": {
    "codigo": "SOLICITUD_NO_ENCONTRADA",
    "mensaje": "No se encontró la solicitud solicitada.",
    "detalles": null
  }
}
```

Cuando existan errores de validación:

```json
{
  "error": {
    "codigo": "ERROR_VALIDACION",
    "mensaje": "Los datos enviados no son válidos.",
    "detalles": [
      {
        "campo": "titulo",
        "mensaje": "El título es obligatorio."
      }
    ]
  }
}
```

### 18.1. Códigos HTTP

| Código | Significado | Uso |
|---|---|---|
| `200` | OK | Consulta u operación exitosa. |
| `201` | Created | Recurso creado correctamente. |
| `204` | No Content | Operación exitosa sin contenido de respuesta. |
| `400` | Bad Request | Petición incorrecta. |
| `401` | Unauthorized | Usuario no autenticado o credenciales incorrectas. |
| `403` | Forbidden | Usuario autenticado sin permisos. |
| `404` | Not Found | Recurso inexistente o no accesible. |
| `409` | Conflict | Operación incompatible con el estado actual. |
| `413` | Payload Too Large | Archivo superior al tamaño permitido. |
| `415` | Unsupported Media Type | Formato de archivo no permitido. |
| `422` | Unprocessable Entity | Error de validación de datos. |
| `500` | Internal Server Error | Error interno del backend. |

### 18.2. Códigos de error funcionales

Se utilizarán códigos descriptivos para identificar los errores más frecuentes.

| Código | Situación |
|---|---|
| `CREDENCIALES_INVALIDAS` | Correo o contraseña incorrectos. |
| `SESION_NO_VALIDA` | Sesión inexistente o vencida. |
| `USUARIO_INACTIVO` | Cuenta desactivada. |
| `PERMISO_DENEGADO` | El usuario no puede realizar la operación. |
| `RECURSO_NO_ENCONTRADO` | El recurso no existe o no es accesible. |
| `CORREO_DUPLICADO` | Ya existe una cuenta con ese correo. |
| `CATEGORIA_DUPLICADA` | Ya existe una categoría con ese nombre. |
| `ESTADO_NO_PERMITIDO` | La transición de estado no está permitida. |
| `SOLICITUD_CERRADA` | Se intenta modificar una solicitud cerrada. |
| `TECNICO_NO_VALIDO` | El técnico no existe o está inactivo. |
| `PETICION_YA_RESPONDIDA` | La petición de información ya tiene respuesta. |
| `ARCHIVO_NO_VALIDO` | El archivo no corresponde a un formato permitido. |
| `ARCHIVO_DEMASIADO_GRANDE` | El archivo supera los 5 MB. |
| `CONFLICTO_CONCURRENCIA` | La solicitud fue modificada por otra operación simultánea. |

Los mensajes de error no deberán revelar contraseñas, hashes, claves privadas, rutas internas ni detalles técnicos sensibles.

---

## 19. Reglas de integridad y concurrencia

El backend deberá garantizar que las operaciones relacionadas se ejecuten de manera consistente.

Se aplicarán las siguientes reglas:

1. La creación de una solicitud y su registro inicial en el historial deberán formar parte de una operación consistente.
2. Una asignación deberá actualizar la relación activa y conservar las asignaciones anteriores.
3. Un cambio de estado deberá registrarse en el historial.
4. Una reasignación deberá finalizar la asignación anterior y crear la nueva.
5. Una solución deberá guardarse junto con el cambio a `resuelto`.
6. Un cierre deberá guardar el tipo, responsable, fecha y motivo cuando corresponda.
7. Una cancelación deberá guardar el motivo y el tipo de cierre.
8. Los archivos deberán validarse antes de registrar sus metadatos.
9. Las solicitudes cerradas no admitirán nuevas operaciones de atención.
10. Las operaciones deberán comprobar el estado actual antes de modificarlo.

Si dos usuarios intentan modificar simultáneamente una solicitud y una operación deja de ser válida por el cambio previo, el backend devolverá `409 Conflict` sin realizar modificaciones parciales.

---

## 20. Seguridad

Las siguientes condiciones serán obligatorias:

- Todas las operaciones protegidas requerirán una sesión válida.
- Los permisos se validarán en el backend.
- Las contraseñas se almacenarán mediante hash seguro.
- Las cookies de sesión utilizarán los atributos de seguridad definidos en el diseño.
- Las credenciales de Supabase permanecerán exclusivamente en el backend.
- Las operaciones que utilicen cookies deberán aplicar protección CSRF cuando corresponda.
- Los archivos se almacenarán en un bucket privado.
- Las solicitudes cerradas serán de solo consulta.
- Los errores no expondrán información sensible.
- Las operaciones importantes quedarán registradas en el historial.

---

## 21. Convenciones para el desarrollo paralelo

Para evitar incompatibilidades entre los integrantes, se establecen los siguientes acuerdos.

### 21.1. Responsabilidades funcionales

**Integrante 1:**
- Módulo coordinador: frontend y backend.
- Backend del módulo solicitante.

**Integrante 2:**
- Módulo técnico: frontend y backend.
- Frontend del módulo solicitante.

**Trabajo compartido:**
- Autenticación y sesiones.
- Modelo de datos y relaciones.
- Contrato de API.
- Conversaciones.
- Integración entre módulos.
- Pruebas de integración.

### 21.2. Acuerdos obligatorios

Ambos integrantes deberán respetar:

1. Las rutas y métodos definidos en este documento.
2. Los nombres y tipos de los campos JSON.
3. Los valores permitidos para roles, estados, prioridades y tipos de cierre.
4. Los permisos definidos para cada operación.
5. La estructura de las respuestas.
6. La estructura general de errores.
7. Las reglas de transición de estados.
8. Los identificadores UUID.
9. Los formatos de fecha.
10. Las reglas de paginación.

Cada integrante tendrá autonomía para organizar internamente los archivos y funciones de su módulo, siempre que respete el contrato compartido.

### 21.3. Cambios al contrato

Si durante el desarrollo se necesita cambiar una ruta, campo, respuesta o permiso:

1. Se informa al otro integrante.
2. Se revisa el impacto sobre el frontend y backend.
3. Se acuerda el cambio.
4. Se actualiza este documento.
5. Se implementa el cambio en las ramas correspondientes.

No se deberán modificar unilateralmente contratos compartidos.

---

## 22. Orden de implementación

La API se desarrollará siguiendo los flujos verticales definidos en `docs/diseno.md`.

| Orden | Flujo | Endpoints principales |
|---|---|---|
| 1 | Autenticación y roles | `/auth/*`, `/users` |
| 2 | Registro y consulta de solicitudes | `/requests` |
| 3 | Evaluación y asignación | `/requests/{id}`, `/status`, `/assignments` |
| 4 | Atención técnica | `/interventions`, `/information-requests`, `/history` |
| 5 | Resolución y cierre | `/resolve`, `/close`, `/cancel` |
| 6 | Consolidado del coordinador | `/statistics` |

Después de completar los flujos principales se podrán implementar las funcionalidades complementarias:

- Adjuntos en mensajes e intervenciones.
- Recuperación de contraseña mediante verificación externa.
- Notificaciones por correo.
- Mejoras de estadísticas.
- Actualización de conversaciones en tiempo real.

Los adjuntos de imágenes en solicitudes y el mecanismo básico de solicitud y respuesta de información adicional forman parte del alcance funcional y no deberán confundirse con las mejoras posteriores.

---

## 23. Relación con los requisitos

| Requisitos | Operaciones principales |
|---|---|
| RF-01 y RF-02 | `/auth/login`, `/auth/logout`, `/auth/me` y autorización por roles. |
| RF-03 y RF-05 | `/users` y `/users/{id}`. |
| RF-04 | `/auth/change-password` y futura recuperación verificada. |
| RF-06, RF-07 y RF-08 | `/requests` y `/requests/{id}/attachments`. |
| RF-09 y RF-10 | `/requests/{id}` y `/requests/{id}/status`. |
| RF-11 y RF-12 | `/requests/{id}/assignments`. |
| RF-13 y RF-14 | `/requests` y `/requests/{id}/status`. |
| RF-15 | `/requests/{id}/cancel`. |
| RF-16, RF-17 y RF-21 | `/requests/{id}/interventions`. |
| RF-18 | `/information-requests` y `/responses`. |
| RF-19 | `/requests/{id}/resolve`. |
| RF-20 | `/requests/{id}/close`. |
| RF-22, RF-23 y RF-26 | `/requests/{id}/messages`. |
| RF-24 y RF-25 | Rutas complementarias de adjuntos. |
| RF-27 | Notificaciones, cuando se implemente el servicio correspondiente. |
| RF-28 | `/requests/{id}/history`. |
| RF-29 | `/statistics`. |

Este contrato deberá mantenerse alineado con los requisitos y el diseño técnico durante todo el desarrollo.

---

**Fin del documento.**