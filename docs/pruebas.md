# Pruebas funcionales — SoporteTI

## 1. Objetivo

Este documento registra las pruebas funcionales de SoporteTI para verificar el comportamiento de la aplicación, sus servicios web, las reglas de negocio y la persistencia de la información.

Las pruebas se relacionan con los requisitos funcionales y las seis condiciones de aceptación definidas en `proyecto2.md`.

Se ejecutarán manualmente mediante Swagger UI (`/docs`), la interfaz web y las consultas necesarias a la base de datos. No se exige automatizar estas pruebas con pytest, Postman CLI, Newman ni herramientas de integración continua.

## 2. Alcance

Se documentan las 12 pruebas funcionales previstas en `docs/requisitos.md`:

| ID | Prueba | Condición de aceptación |
|---|---|---|
| PF-01 | Inicio de sesión con credenciales válidas e inválidas | CA-01 |
| PF-02 | Acceso a funcionalidades según el rol | CA-01 |
| PF-03 | Creación de usuarios por el coordinador | CA-01 |
| PF-04 | Registro de una solicitud por un solicitante | CA-02 |
| PF-05 | Consulta de solicitudes según el rol | CA-02 |
| PF-06 | Evaluación, clasificación y prioridad | CA-03 |
| PF-07 | Asignación y reasignación de técnicos | CA-03 |
| PF-08 | Registro de intervención técnica | CA-04 |
| PF-09 | Solicitud y respuesta de información adicional | CA-04 |
| PF-10 | Registro de solución y cierre | CA-05 |
| PF-11 | Cancelación y cierre administrativo | CA-05 |
| PF-12 | Consulta del consolidado del coordinador | CA-06 |

## 3. Preparación del entorno

Antes de ejecutar las pruebas:

1. Tener el backend configurado y en ejecución.
2. Tener disponible la base de datos configurada para la aplicación.
3. Abrir la documentación interactiva de la API en `http://127.0.0.1:8000/docs`.
4. Si se realizan pruebas desde la interfaz, tener también el frontend en ejecución y conectado al backend.
5. Disponer de cuentas de prueba para los roles solicitante, técnico y coordinador.
6. Utilizar información ficticia para las solicitudes, usuarios y demás registros.

### 3.1. Datos de prueba

Se utilizarán los siguientes actores ficticios:

| Actor | Rol | Uso |
|---|---|---|
| Usuario Solicitante A | Solicitante | Crear y consultar sus solicitudes. |
| Usuario Solicitante B | Solicitante | Comprobar restricciones de acceso a solicitudes ajenas. |
| Usuario Técnico A | Técnico | Consultar casos asignados y registrar actuaciones. |
| Usuario Técnico B | Técnico | Comprobar asignaciones y reasignaciones. |
| Usuario Coordinador A | Coordinador | Administrar usuarios, evaluar, asignar y cerrar solicitudes. |

Los nombres, correos y contraseñas utilizados durante la ejecución deben ser datos ficticios. Las credenciales reales no se deben registrar en este documento.

### 3.2. Registro de resultados

Cada prueba tendrá uno de estos estados:

- **Pendiente:** todavía no se ha ejecutado.
- **Aprobada:** el resultado obtenido coincide con el resultado esperado.
- **Fallida:** el resultado obtenido no coincide con el esperado.
- **Bloqueada:** no se pudo ejecutar por una dependencia o problema del entorno.

Las pruebas solo se marcarán como aprobadas después de su ejecución y comprobación.

---

## 4. Casos de prueba

### PF-01. Inicio de sesión con credenciales válidas e inválidas

**Condición de aceptación:** CA-01.  
**Requisito relacionado:** RF-01.  
**Objetivo:** comprobar que un usuario registrado puede iniciar sesión y que el sistema rechaza credenciales incorrectas.

**Precondiciones:**
- El backend está en ejecución.
- Existe una cuenta de prueba activa.
- Se conoce la contraseña de la cuenta de prueba.

**Datos de entrada:**
- Correo y contraseña válidos.
- Correo existente con contraseña incorrecta.
- Correo no registrado.

**Pasos:**
1. Abrir Swagger UI o la pantalla de inicio de sesión.
2. Ejecutar el inicio de sesión con credenciales válidas.
3. Comprobar que el acceso se realiza correctamente.
4. Ejecutar nuevamente el inicio de sesión con una contraseña incorrecta.
5. Intentar iniciar sesión con un correo no registrado.
6. Comprobar que los intentos inválidos no permiten acceder al sistema.

**Resultado esperado:**
- Las credenciales válidas permiten iniciar sesión.
- El sistema establece la sesión correspondiente.
- Las credenciales incorrectas son rechazadas con una respuesta controlada.
- No se expone información sensible en los mensajes de error.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Captura del inicio de sesión exitoso y de las respuestas de los intentos inválidos.

---

### PF-02. Acceso a funcionalidades según el rol

**Condición de aceptación:** CA-01.  
**Requisito relacionado:** RF-02.  
**Objetivo:** verificar que los permisos se apliquen según el rol del usuario autenticado.

**Precondiciones:**
- Existen cuentas de solicitante, técnico y coordinador.
- Las tres cuentas pueden iniciar sesión.
- Se dispone de las operaciones protegidas de la API.

**Datos de entrada:**
- Sesión del solicitante.
- Sesión del técnico.
- Sesión del coordinador.

**Pasos:**
1. Iniciar sesión como solicitante.
2. Consultar las operaciones permitidas para ese rol.
3. Intentar ejecutar una operación exclusiva del coordinador.
4. Cerrar sesión e iniciar como técnico.
5. Intentar consultar o modificar información que no corresponda a sus permisos.
6. Iniciar sesión como coordinador.
7. Comprobar el acceso a las operaciones administrativas autorizadas.

**Resultado esperado:**
- Cada rol puede ejecutar únicamente las operaciones permitidas.
- Las operaciones no autorizadas son rechazadas.
- El backend aplica los permisos aunque se invoquen directamente los endpoints sin utilizar la interfaz.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Capturas de las operaciones permitidas y rechazadas para cada rol.

---

### PF-03. Creación de usuarios por el coordinador

**Condición de aceptación:** CA-01.  
**Requisito relacionado:** RF-03.  
**Objetivo:** comprobar que el coordinador puede registrar usuarios con sus datos y rol correspondiente.

**Precondiciones:**
- Existe una cuenta de coordinador.
- El coordinador inició sesión.
- No existe previamente el correo que se utilizará.

**Datos de entrada:**
- Nombre: Usuario de prueba.
- Correo: una dirección ficticia no registrada.
- Rol: técnico o solicitante.
- Los demás datos obligatorios definidos por el sistema.

**Pasos:**
1. Iniciar sesión como coordinador.
2. Abrir la operación de creación de usuarios.
3. Registrar un usuario con datos válidos.
4. Consultar el listado de usuarios.
5. Verificar que el usuario creado aparece con el rol asignado.
6. Intentar crear otro usuario con datos inválidos o con un correo duplicado.
7. Comprobar que el sistema rechaza el registro incorrecto.

**Resultado esperado:**
- El coordinador puede crear usuarios con datos válidos.
- El usuario queda almacenado y puede recuperarse.
- El rol asignado corresponde al enviado.
- Los datos inválidos o duplicados son rechazados.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Captura del registro exitoso y de la consulta del usuario creado.

---

### PF-04. Registro de una solicitud por un solicitante

**Condición de aceptación:** CA-02.  
**Requisito relacionado:** RF-06.  
**Objetivo:** comprobar que un solicitante puede registrar una solicitud con la información obligatoria y que esta queda persistida.

**Precondiciones:**
- Existe una cuenta de solicitante.
- El solicitante inició sesión.
- Existen las categorías y los datos requeridos por el formulario.

**Datos de entrada:**
- Tipo de solicitud.
- Descripción del incidente o necesidad.
- Ubicación.
- Datos de contacto.
- Identificador del equipo, cuando corresponda.

**Pasos:**
1. Iniciar sesión como solicitante.
2. Abrir la operación de creación de solicitudes o el formulario correspondiente.
3. Enviar una solicitud con todos los datos obligatorios.
4. Comprobar la respuesta del sistema.
5. Consultar las solicitudes del usuario.
6. Recuperar el detalle de la solicitud recién creada.
7. Intentar registrar otra solicitud omitiendo un dato obligatorio.

**Resultado esperado:**
- La solicitud válida se registra correctamente.
- Se asigna el estado inicial definido por el sistema (`Registrado`).
- La solicitud puede recuperarse posteriormente.
- Los datos obligatorios faltantes generan una respuesta de validación y no se guarda una solicitud incompleta.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Captura de la creación, respuesta de la API y consulta posterior del registro.

---

### PF-05. Consulta de solicitudes según el rol

**Condición de aceptación:** CA-02.  
**Requisitos relacionados:** RF-07 y RF-13.  
**Objetivo:** verificar que cada rol consulte únicamente el conjunto de solicitudes permitido.

**Precondiciones:**
- Existen solicitudes de distintos solicitantes.
- Existen solicitudes asignadas a diferentes técnicos.
- Hay cuentas de los tres roles.

**Datos de entrada:**
- Cuenta de solicitante A.
- Cuenta de solicitante B.
- Cuenta de técnico A.
- Cuenta de coordinador.

**Pasos:**
1. Iniciar sesión como solicitante A.
2. Consultar el listado de solicitudes.
3. Verificar que aparecen sus propias solicitudes.
4. Intentar consultar una solicitud perteneciente al solicitante B.
5. Iniciar sesión como técnico A.
6. Consultar sus solicitudes asignadas.
7. Comprobar que no aparecen solicitudes asignadas exclusivamente a otro técnico.
8. Iniciar sesión como coordinador.
9. Consultar el listado general de solicitudes.

**Resultado esperado:**
- El solicitante consulta sus propias solicitudes.
- El técnico consulta las solicitudes que tiene asignadas.
- El coordinador puede consultar las solicitudes dentro de su ámbito de gestión.
- Los intentos de acceso a solicitudes ajenas sin autorización son rechazados.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Capturas de los listados y de los intentos de acceso no autorizado.

---

### PF-06. Evaluación, clasificación y prioridad

**Condición de aceptación:** CA-03.  
**Requisitos relacionados:** RF-09 y RF-10.  
**Objetivo:** comprobar que el coordinador puede evaluar una solicitud y establecer su clasificación y prioridad.

**Precondiciones:**
- Existe una solicitud registrada y pendiente de evaluación.
- El coordinador inició sesión.
- Existen categorías disponibles.

**Datos de entrada:**
- Solicitud existente.
- Categoría válida.
- Prioridad válida.
- Datos de evaluación requeridos por el sistema.

**Pasos:**
1. Iniciar sesión como coordinador.
2. Consultar una solicitud pendiente de evaluación.
3. Ejecutar la operación de evaluación.
4. Asignar una categoría y una prioridad válidas.
5. Consultar nuevamente el detalle de la solicitud.
6. Comprobar que los datos se conservaron.
7. Intentar enviar una categoría o prioridad inválida.

**Resultado esperado:**
- El coordinador puede evaluar y clasificar la solicitud.
- La categoría y prioridad quedan asociadas al caso.
- Los cambios se pueden consultar posteriormente.
- Los valores inválidos son rechazados.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Captura de la evaluación y del detalle actualizado de la solicitud.

---

### PF-07. Asignación y reasignación de técnicos

**Condición de aceptación:** CA-03.  
**Requisitos relacionados:** RF-11 y RF-12.  
**Objetivo:** comprobar que el coordinador puede asignar una solicitud a un técnico y reasignarla cuando sea necesario.

**Precondiciones:**
- Existe una solicitud evaluada.
- Existen al menos dos técnicos activos.
- El coordinador inició sesión.

**Datos de entrada:**
- Identificador de la solicitud.
- Identificador del técnico A.
- Identificador del técnico B.

**Pasos:**
1. Iniciar sesión como coordinador.
2. Seleccionar una solicitud que pueda asignarse.
3. Asignarla al técnico A.
4. Consultar los datos de la asignación.
5. Reasignar la solicitud al técnico B.
6. Consultar nuevamente el responsable actual.
7. Consultar el historial de asignaciones.
8. Iniciar sesión como cada técnico y comprobar las solicitudes que tiene asignadas.

**Resultado esperado:**
- La asignación inicial queda registrada.
- La reasignación actualiza el responsable.
- Se conserva la información histórica de las asignaciones.
- El técnico B puede consultar la solicitud asignada y el técnico A deja de verla como asignación vigente, según las reglas del sistema.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Capturas de la asignación inicial, la reasignación y la consulta de responsables.

---

### PF-08. Registro de intervención técnica

**Condición de aceptación:** CA-04.  
**Requisitos relacionados:** RF-16, RF-17 y RF-21.  
**Objetivo:** comprobar que el técnico asignado puede registrar una intervención y que esta queda asociada a la solicitud.

**Precondiciones:**
- Existe una solicitud asignada al técnico A.
- El técnico A inició sesión.
- La solicitud se encuentra en un estado que permite registrar intervenciones.

**Datos de entrada:**
- Identificador de la solicitud.
- Descripción de la intervención.
- Información adicional solicitada por el formulario, cuando corresponda.

**Pasos:**
1. Iniciar sesión como técnico A.
2. Consultar las solicitudes asignadas.
3. Abrir el detalle de una solicitud.
4. Registrar una intervención con información válida.
5. Consultar nuevamente las intervenciones de la solicitud.
6. Comprobar que la intervención aparece asociada al caso y al técnico.
7. Intentar consultar la intervención desde una cuenta sin permisos.

**Resultado esperado:**
- El técnico asignado puede registrar la intervención.
- La intervención queda persistida y vinculada a la solicitud y al responsable.
- La consulta respeta las reglas de visibilidad.
- Los usuarios no autorizados no pueden consultar información restringida.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Captura del registro y de la consulta de la intervención.

---

### PF-09. Solicitud y respuesta de información adicional

**Condición de aceptación:** CA-04.  
**Requisito relacionado:** RF-18.  
**Objetivo:** verificar que el personal autorizado puede solicitar información adicional y que el solicitante puede responder.

**Precondiciones:**
- Existe una solicitud asignada.
- El técnico o coordinador tiene acceso autorizado.
- El solicitante propietario de la solicitud puede iniciar sesión.

**Datos de entrada:**
- Solicitud existente.
- Pregunta o descripción de la información requerida.
- Respuesta del solicitante.

**Pasos:**
1. Iniciar sesión como técnico asignado o coordinador autorizado.
2. Abrir la solicitud correspondiente.
3. Registrar una petición de información adicional.
4. Consultar las peticiones asociadas a la solicitud.
5. Cerrar sesión e iniciar como solicitante propietario.
6. Consultar la petición recibida.
7. Registrar una respuesta.
8. Consultar nuevamente la petición y verificar que la respuesta quedó asociada.

**Resultado esperado:**
- El personal autorizado puede registrar una petición.
- El solicitante propietario puede consultar y responder la petición.
- La respuesta queda vinculada a la petición y a la solicitud.
- Los usuarios ajenos no pueden responder o consultar información sin autorización.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Capturas de la petición, su consulta y la respuesta registrada.

---

### PF-10. Registro de solución y cierre

**Condición de aceptación:** CA-05.  
**Requisitos relacionados:** RF-19 y RF-20.  
**Objetivo:** comprobar que el técnico puede documentar la solución y que el coordinador puede revisar y cerrar la solicitud.

**Precondiciones:**
- Existe una solicitud en atención.
- La solicitud está asignada a un técnico.
- El técnico y el coordinador tienen cuentas activas.

**Datos de entrada:**
- Identificador de la solicitud.
- Descripción de la solución.
- Información de cierre requerida por el sistema.

**Pasos:**
1. Iniciar sesión como técnico asignado.
2. Abrir la solicitud.
3. Registrar la solución con una descripción válida.
4. Consultar el detalle y verificar que la solución quedó registrada.
5. Iniciar sesión como coordinador.
6. Consultar la solicitud resuelta.
7. Revisar la información de la solución.
8. Ejecutar el cierre permitido.
9. Consultar nuevamente la solicitud y verificar su estado final.
10. Iniciar sesión como solicitante propietario y consultar el resultado.

**Resultado esperado:**
- El técnico puede registrar la solución de la solicitud asignada.
- El coordinador puede revisar la solución y cerrar la solicitud conforme a las reglas.
- El estado final y el resultado de atención quedan persistidos.
- El solicitante puede consultar el resultado de su caso cerrado.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Capturas del registro de solución, cierre y consulta del resultado por el solicitante.

---

### PF-11. Cancelación y cierre administrativo

**Condición de aceptación:** CA-05.  
**Requisitos relacionados:** RF-15 y RF-20.  
**Objetivo:** comprobar que la cancelación y el cierre administrativo respetan los permisos, estados y motivos establecidos.

**Precondiciones:**
- Existen solicitudes en estados que permitan probar los diferentes escenarios.
- Hay cuentas de solicitante y coordinador.
- Se conocen las reglas de cancelación y cierre definidas en el sistema.

**Datos de entrada:**
- Solicitud cancelable por el solicitante.
- Solicitud que pueda recibir cierre administrativo.
- Motivo correspondiente, cuando sea obligatorio.

**Pasos:**
1. Iniciar sesión como solicitante propietario.
2. Seleccionar una solicitud cuyo estado permita cancelación.
3. Ejecutar la cancelación con la información requerida.
4. Consultar el estado actualizado.
5. Iniciar sesión como coordinador.
6. Seleccionar una solicitud que cumpla las condiciones para cierre administrativo.
7. Registrar el motivo requerido y ejecutar el cierre.
8. Consultar el estado final y el historial.
9. Intentar realizar una operación no permitida sobre una solicitud cerrada.

**Resultado esperado:**
- El solicitante puede cancelar únicamente las solicitudes permitidas.
- El coordinador puede realizar cierres administrativos justificados y autorizados.
- Los motivos y cambios quedan registrados cuando corresponda.
- Una solicitud cerrada no admite nuevas operaciones operativas no permitidas.
- La información histórica permanece disponible para consulta autorizada.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Capturas de la cancelación, cierre administrativo, historial y rechazo de una operación no permitida.

---

### PF-12. Consulta del consolidado del coordinador

**Condición de aceptación:** CA-06.  
**Requisito relacionado:** RF-29.  
**Objetivo:** comprobar que el coordinador puede consultar información consolidada sobre las solicitudes y su atención.

**Precondiciones:**
- Existen varias solicitudes registradas.
- Las solicitudes tienen diferentes estados, prioridades y categorías.
- Existen solicitudes asignadas a diferentes técnicos.
- El coordinador inició sesión.

**Datos de entrada:**
- Solicitudes de prueba con diferentes estados.
- Diferentes categorías y prioridades.
- Responsables asignados.

**Pasos:**
1. Iniciar sesión como coordinador.
2. Abrir la consulta de estadísticas o consolidado.
3. Consultar la información general de solicitudes.
4. Comprobar los datos agrupados por estado.
5. Verificar los datos de categorías, prioridades y responsables cuando estén disponibles.
6. Comparar los resultados con las solicitudes registradas.
7. Intentar consultar la información desde un rol que no tenga permisos de coordinación.

**Resultado esperado:**
- El coordinador puede consultar información consolidada de varias solicitudes.
- Las cantidades y agrupaciones corresponden a los datos almacenados.
- Los datos de estado, prioridad, categoría y responsables son coherentes con los registros existentes.
- Los usuarios sin permisos no pueden acceder a la consulta restringida.

**Resultado obtenido:** Pendiente de ejecución.  
**Estado:** Pendiente.  
**Evidencia:** Captura del consolidado y de la comparación con las solicitudes registradas.

---

## 5. Resumen de ejecución

Esta tabla se actualizará después de ejecutar las pruebas.

| ID | Prueba | Estado | Evidencia |
|---|---|---|---|
| PF-01 | Inicio de sesión | Pendiente | Por adjuntar |
| PF-02 | Acceso según el rol | Pendiente | Por adjuntar |
| PF-03 | Creación de usuarios | Pendiente | Por adjuntar |
| PF-04 | Registro de solicitudes | Pendiente | Por adjuntar |
| PF-05 | Consulta según el rol | Pendiente | Por adjuntar |
| PF-06 | Evaluación y clasificación | Pendiente | Por adjuntar |
| PF-07 | Asignación y reasignación | Pendiente | Por adjuntar |
| PF-08 | Registro de intervención | Pendiente | Por adjuntar |
| PF-09 | Solicitud y respuesta de información | Pendiente | Por adjuntar |
| PF-10 | Registro de solución y cierre | Pendiente | Por adjuntar |
| PF-11 | Cancelación y cierre administrativo | Pendiente | Por adjuntar |
| PF-12 | Consolidado del coordinador | Pendiente | Por adjuntar |

**Total de pruebas:** 12  
**Aprobadas:** 0  
**Fallidas:** 0  
**Bloqueadas:** 0  
**Pendientes:** 12

Los contadores se actualizarán únicamente con los resultados reales de ejecución.

## 6. Evidencias

Las capturas y registros de las pruebas se conservarán en la siguiente estructura:

```text
evidencias/
├── PF-01/
├── PF-02/
├── PF-03/
├── PF-04/
├── PF-05/
├── PF-06/
├── PF-07/
├── PF-08/
├── PF-09/
├── PF-10/
├── PF-11/
└── PF-12/
```

Cada carpeta debe contener evidencia suficiente para identificar la operación ejecutada y su resultado. Se deben ocultar contraseñas, tokens, claves y datos personales reales.

## 7. Relación con la matriz de trazabilidad

Los resultados de este documento complementan `docs/trazabilidad.md`.

Una condición de aceptación no se marcará como demostrada únicamente porque exista un endpoint o una prueba automatizada. Se debe comprobar el flujo funcional correspondiente y conservar evidencia reproducible.

La matriz de trazabilidad deberá actualizarse cuando las pruebas se ejecuten, indicando los identificadores PF correspondientes, el resultado y la evidencia disponible.

## 8. Control de cambios

| Versión | Descripción |
|---|---|
| 1.0 | Creación del documento con los 12 casos de prueba funcionales definidos para el proyecto. |
