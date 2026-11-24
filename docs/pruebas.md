# Pruebas funcionales — SoporteTI

## 1. Objetivo

Este documento define y registra las pruebas funcionales de SoporteTI para verificar el comportamiento de la aplicación, sus servicios web, las reglas de negocio y la persistencia de la información.

Las pruebas permiten comprobar el cumplimiento de los requisitos funcionales y de las seis condiciones de aceptación establecidas en `proyecto2.md`.

La ejecución se realizará mediante Swagger UI (`/docs`), la interfaz web y las consultas necesarias a la base de datos.

Este documento corresponde a las pruebas funcionales de la entrega académica. No debe confundirse con las pruebas automatizadas del backend ejecutadas mediante pytest.

## 2. Alcance

De acuerdo con la Actividad 6 de `proyecto2.md`, se deben realizar doce pruebas funcionales.

| ID | Prueba | Criterio de aceptación |
|---|---|---|
| PF-01 | Registro válido de un caso de soporte. | CA-01 |
| PF-02 | Registro de un caso con datos inválidos. | CA-01 |
| PF-03 | Consulta de un caso existente. | CA-01, CA-03 y CA-05 |
| PF-04 | Consulta de un caso inexistente. | CA-03 |
| PF-05 | Gestión de un caso por personal autorizado. | CA-02 |
| PF-06 | Intento de gestión por un actor no autorizado. | CA-02 |
| PF-07 | Consulta del estado y responsable de un caso. | CA-03 |
| PF-08 | Consulta del historial de intervenciones. | CA-04 |
| PF-09 | Cierre de un caso y consulta del resultado. | CA-05 |
| PF-10 | Consulta consolidada de coordinación. | CA-06 |
| PF-11 | Verificación de persistencia e integridad de relaciones. | CA-01, CA-02 y CA-04 |
| PF-12 | Verificación de integración entre interfaz, API y base de datos. | CA-01 a CA-06 |

Las pruebas abarcan los siguientes aspectos:

- Registro y consulta de solicitudes.
- Validación de datos.
- Autorización de operaciones según el rol.
- Evaluación y gestión de solicitudes.
- Consulta de estados y responsables.
- Registro y consulta de intervenciones.
- Cierre y consulta de resultados.
- Consulta consolidada de coordinación.
- Persistencia e integridad de la información.
- Integración entre frontend, backend y base de datos.

## 3. Preparación del entorno

Antes de ejecutar las pruebas se deben cumplir las siguientes condiciones:

1. Tener el backend configurado y en ejecución.
2. Tener disponible la instancia de PostgreSQL utilizada por el entorno local.
3. Tener aplicadas las migraciones de base de datos correspondientes.
4. Abrir la documentación interactiva de la API en `http://127.0.0.1:8000/docs`.
5. Si la prueba requiere la interfaz web, tener también el frontend en ejecución y conectado al backend.
6. Disponer de cuentas de prueba para los roles solicitante, técnico y coordinador.
7. Contar con solicitudes de prueba en los estados necesarios para cada escenario.
8. Utilizar información ficticia para los usuarios, solicitudes y demás registros.

### 3.1. Datos de prueba

Se utilizarán los siguientes actores ficticios:

| Actor | Rol | Uso |
|---|---|---|
| Usuario Solicitante A | Solicitante | Registrar y consultar sus solicitudes. |
| Usuario Solicitante B | Solicitante | Comprobar las restricciones de acceso a solicitudes ajenas. |
| Usuario Técnico A | Técnico | Consultar solicitudes asignadas y registrar intervenciones. |
| Usuario Técnico B | Técnico | Comprobar asignaciones y reasignaciones. |
| Usuario Coordinador A | Coordinador | Evaluar, gestionar, asignar y supervisar solicitudes. |

Los datos de prueba deberán ser ficticios. Las contraseñas, tokens y credenciales reales no se deben registrar en este documento ni en las evidencias.

### 3.2. Herramientas de ejecución

Las pruebas podrán utilizar:

- Swagger UI para ejecutar operaciones de la API REST.
- La interfaz web para comprobar los flujos desde la perspectiva de los usuarios.
- PostgreSQL para verificar la persistencia y las relaciones entre registros.
- Capturas de pantalla y registros de respuestas HTTP como evidencia.

Los endpoints concretos se deben consultar en la documentación interactiva de la API. No se deben asumir rutas o métodos HTTP que no estén publicados por la implementación actual.

### 3.3. Registro de resultados

Cada prueba tendrá uno de los siguientes estados:

- **Pendiente:** todavía no se ha ejecutado.
- **Aprobada:** el resultado obtenido coincide con el resultado esperado.
- **Fallida:** el resultado obtenido no coincide con el esperado.
- **Bloqueada:** no se pudo ejecutar por una dependencia o problema del entorno.

Las pruebas solo se marcarán como aprobadas después de su ejecución y comprobación.

---

## 4. Casos de prueba

### PF-01. Registro válido de un caso de soporte

**Criterio de aceptación:** CA-01.

**Requisito relacionado:** RF-06.

**Objetivo:** comprobar que un solicitante puede registrar un incidente o requerimiento de soporte con información válida y que el sistema conserva el caso.

**Precondiciones:**

- El backend está en ejecución.
- La base de datos está disponible.
- Existe una cuenta activa de solicitante.
- El solicitante inició sesión.
- Se dispone de los datos necesarios para registrar una solicitud.

**Datos de entrada:**

- Asunto o título.
- Descripción del problema.
- Tipo de solicitud.
- Categoría, cuando corresponda.
- Ubicación.
- Identificador del equipo, cuando corresponda.
- Información de contacto requerida.

**Pasos:**

1. Iniciar sesión como solicitante.
2. Abrir el formulario de creación de solicitudes o la operación correspondiente de la API.
3. Completar los campos obligatorios con información válida.
4. Enviar la solicitud.
5. Comprobar la respuesta del sistema.
6. Consultar las solicitudes del usuario.
7. Recuperar el detalle de la solicitud recién creada.

**Resultado esperado:**

- El sistema registra correctamente la solicitud.
- La solicitud queda asociada al solicitante autenticado.
- Se asigna el estado inicial `Registrado`.
- Se conserva la fecha de creación.
- La solicitud puede recuperarse posteriormente.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Captura del registro, respuesta de la API y consulta posterior de la solicitud.

---

### PF-02. Registro de un caso con datos inválidos

**Criterio de aceptación:** CA-01.

**Requisito relacionado:** RF-06.

**Objetivo:** comprobar que el sistema valida la información recibida y rechaza solicitudes con datos obligatorios ausentes o inválidos.

**Precondiciones:**

- El backend está en ejecución.
- La base de datos está disponible.
- Existe una cuenta activa de solicitante.
- El solicitante inició sesión.

**Datos de entrada:**

Se realizarán diferentes intentos utilizando:

- Asunto vacío.
- Descripción vacía.
- Tipo de solicitud inválido.
- Datos con formato incorrecto.
- Identificador del equipo ausente cuando sea obligatorio para el caso.

**Pasos:**

1. Iniciar sesión como solicitante.
2. Abrir el formulario de creación de solicitudes o la operación correspondiente.
3. Enviar una solicitud sin completar un campo obligatorio.
4. Comprobar la respuesta del sistema.
5. Repetir la operación utilizando un valor inválido.
6. Consultar las solicitudes del usuario.
7. Verificar que los intentos rechazados no hayan generado registros incorrectos.

**Resultado esperado:**

- El sistema rechaza los datos inválidos.
- La respuesta informa el error de validación.
- No se registra una solicitud incompleta o incorrecta.
- Los registros existentes no se modifican como consecuencia de los intentos rechazados.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas de los datos inválidos, respuestas de validación y consulta de solicitudes.

---

### PF-03. Consulta de un caso existente

**Criterios de aceptación:** CA-01, CA-03 y CA-05.

**Requisitos relacionados:** RF-07, RF-13, RF-19 y RF-20.

**Objetivo:** comprobar que el sistema permite recuperar una solicitud existente y presentar la información correspondiente según los permisos del usuario.

**Precondiciones:**

- Existe una solicitud previamente registrada.
- La solicitud tiene un identificador válido.
- Se dispone de las cuentas necesarias para consultar la información.
- La solicitud tiene información almacenada que puede recuperarse.

**Datos de entrada:**

- Identificador de una solicitud existente.
- Cuenta del solicitante propietario.
- Cuenta del técnico asignado, cuando corresponda.
- Cuenta del coordinador.

**Pasos:**

1. Iniciar sesión como solicitante propietario.
2. Consultar el listado de sus solicitudes.
3. Seleccionar una solicitud existente.
4. Consultar su información detallada.
5. Comprobar que los datos coinciden con los registrados.
6. Iniciar sesión como coordinador.
7. Consultar la misma solicitud.
8. Verificar que la información corresponde al mismo registro.

**Resultado esperado:**

- El sistema recupera la solicitud existente.
- La información presentada coincide con los datos almacenados.
- El solicitante puede consultar sus propias solicitudes.
- El coordinador puede consultar las solicitudes dentro de su ámbito de gestión.
- Los permisos se aplican de acuerdo con el rol del usuario.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas del listado y detalle de la solicitud desde los roles utilizados.

---

### PF-04. Consulta de un caso inexistente

**Criterio de aceptación:** CA-03.

**Requisito relacionado:** RF-07.

**Objetivo:** comprobar que el sistema maneja correctamente las consultas de solicitudes que no existen.

**Precondiciones:**

- El backend está en ejecución.
- Existe una cuenta autenticada con permisos para consultar solicitudes.
- Se dispone de un identificador que no corresponde a ninguna solicitud registrada.

**Datos de entrada:**

- Identificador inexistente de una solicitud.

**Pasos:**

1. Iniciar sesión con una cuenta autorizada.
2. Abrir la operación de consulta de una solicitud por identificador.
3. Enviar un identificador que no exista en la base de datos.
4. Comprobar la respuesta del sistema.
5. Verificar que no se presenta información de otra solicitud.

**Resultado esperado:**

- El sistema informa que la solicitud no existe.
- Se devuelve una respuesta de error controlada.
- No se presentan datos de otros registros.
- La operación no modifica la información almacenada.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Captura de la solicitud HTTP y de la respuesta obtenida.

---

### PF-05. Gestión de un caso por personal autorizado

**Criterio de aceptación:** CA-02.

**Requisitos relacionados:** RF-09, RF-10, RF-11, RF-12 y RF-14.

**Objetivo:** comprobar que el personal autorizado puede realizar las operaciones de evaluación, clasificación, asignación y gestión de una solicitud, respetando las reglas del sistema.

**Precondiciones:**

- Existe una solicitud registrada.
- La solicitud se encuentra en un estado que permite su evaluación.
- Existe una cuenta activa de coordinador.
- Existen técnicos activos para realizar la asignación.

**Datos de entrada:**

- Identificador de la solicitud.
- Categoría válida.
- Prioridad válida.
- Técnico seleccionado.
- Estado permitido para la operación correspondiente.

**Pasos:**

1. Iniciar sesión como coordinador.
2. Consultar una solicitud pendiente de evaluación.
3. Ejecutar la evaluación de la solicitud.
4. Establecer una categoría y prioridad válidas.
5. Guardar los cambios.
6. Asignar la solicitud a un técnico.
7. Consultar nuevamente el detalle de la solicitud.
8. Verificar que el responsable, la clasificación y la prioridad se hayan actualizado.
9. Consultar el historial de cambios, cuando corresponda.

**Resultado esperado:**

- El coordinador puede evaluar la solicitud.
- La clasificación y prioridad quedan almacenadas.
- La asignación queda asociada a la solicitud y al técnico responsable.
- Las operaciones se registran de acuerdo con las reglas del sistema.
- Los cambios pueden recuperarse posteriormente.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas de la evaluación, clasificación, asignación y consulta posterior de la solicitud.

---

### PF-06. Intento de gestión por un actor no autorizado

**Criterio de aceptación:** CA-02.

**Requisito relacionado:** RF-02.

**Objetivo:** verificar que el sistema impide que un usuario realice operaciones de gestión que no están permitidas para su rol.

**Precondiciones:**

- Existen cuentas activas de solicitante y técnico.
- Existe una solicitud sobre la que se pueden realizar operaciones administrativas.
- Las cuentas utilizadas tienen sesiones válidas.

**Datos de entrada:**

- Sesión de solicitante.
- Sesión de técnico.
- Identificador de una solicitud.
- Operaciones administrativas que requieren permisos de coordinación.

**Pasos:**

1. Iniciar sesión como solicitante.
2. Intentar realizar una operación exclusiva del coordinador, como asignar un técnico o modificar la prioridad.
3. Comprobar que el sistema rechaza la operación.
4. Iniciar sesión como técnico.
5. Intentar ejecutar una operación exclusiva del coordinador.
6. Comprobar que el sistema rechaza la operación.
7. Consultar nuevamente la solicitud.
8. Verificar que los intentos no autorizados no hayan modificado su información.

**Resultado esperado:**

- Los usuarios sin permisos no pueden ejecutar operaciones administrativas.
- El backend rechaza las solicitudes no autorizadas.
- La información de la solicitud permanece sin cambios.
- La protección se aplica aunque se invoque directamente la API y no se utilice la interfaz.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas de las operaciones rechazadas y de la consulta posterior de la solicitud.

---

### PF-07. Consulta del estado y responsable de un caso

**Criterio de aceptación:** CA-03.

**Requisitos relacionados:** RF-07, RF-11, RF-12, RF-13 y RF-14.

**Objetivo:** comprobar que el sistema presenta el estado actual de una solicitud y permite identificar al responsable de su atención.

**Precondiciones:**

- Existe una solicitud registrada.
- La solicitud tiene un técnico asignado.
- Se dispone de una cuenta de solicitante y una cuenta de coordinador.
- La solicitud puede consultarse según los permisos de cada usuario.

**Datos de entrada:**

- Identificador de la solicitud.
- Estado actual.
- Identificador del técnico responsable.

**Pasos:**

1. Iniciar sesión como coordinador.
2. Consultar la solicitud.
3. Verificar el estado y el técnico responsable.
4. Iniciar sesión como técnico asignado.
5. Consultar la solicitud desde su listado de asignaciones.
6. Iniciar sesión como solicitante propietario.
7. Consultar el estado de su solicitud.
8. Comparar la información presentada con los registros existentes.
9. Si se realiza un cambio de estado permitido, consultar nuevamente la solicitud y verificar la actualización.

**Resultado esperado:**

- El estado presentado corresponde al estado almacenado.
- El responsable identificado corresponde a la asignación vigente.
- La información se presenta de acuerdo con los permisos de cada rol.
- Los cambios autorizados de estado se reflejan en las consultas posteriores.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas de las consultas realizadas desde los roles correspondientes.

---

### PF-08. Consulta del historial de intervenciones

**Criterio de aceptación:** CA-04.

**Requisitos relacionados:** RF-16, RF-17 y RF-21.

**Objetivo:** comprobar que el sistema conserva las intervenciones realizadas durante la atención de una solicitud y permite consultarlas respetando las reglas de visibilidad.

**Precondiciones:**

- Existe una solicitud con intervenciones registradas.
- Las intervenciones están asociadas a la solicitud y a sus responsables.
- Se dispone de cuentas de solicitante, técnico y coordinador.

**Datos de entrada:**

- Identificador de la solicitud.
- Intervenciones registradas.
- Clasificación de visibilidad de las intervenciones.

**Pasos:**

1. Iniciar sesión como técnico autorizado.
2. Consultar una solicitud asignada.
3. Abrir el historial de intervenciones.
4. Verificar que las intervenciones registradas aparecen asociadas al caso.
5. Iniciar sesión como coordinador.
6. Consultar el historial de la misma solicitud.
7. Iniciar sesión como solicitante propietario.
8. Consultar las intervenciones visibles para el solicitante.
9. Comprobar que las intervenciones internas no se muestran al solicitante.

**Resultado esperado:**

- Las intervenciones permanecen almacenadas.
- Las intervenciones se relacionan con la solicitud correspondiente.
- Se conserva la información del responsable y la fecha.
- La consulta respeta el orden y la información disponible.
- Las intervenciones internas solo pueden consultarse por el personal autorizado.
- El solicitante únicamente puede consultar las intervenciones visibles para su rol.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas del historial consultado desde los diferentes roles.

---

### PF-09. Cierre de un caso y consulta del resultado

**Criterio de aceptación:** CA-05.

**Requisitos relacionados:** RF-07, RF-19 y RF-20.

**Objetivo:** comprobar que una solicitud puede cerrarse después de registrar la solución y que el solicitante puede consultar el resultado de la atención.

**Precondiciones:**

- Existe una solicitud asignada a un técnico.
- La solicitud se encuentra en un estado que permite registrar una solución.
- Existe una cuenta activa de técnico.
- Existe una cuenta activa de coordinador.
- Existe una cuenta de solicitante propietario.

**Datos de entrada:**

- Identificador de la solicitud.
- Descripción de la solución.
- Tipo de cierre correspondiente.
- Información adicional requerida para el cierre.

**Pasos:**

1. Iniciar sesión como técnico asignado.
2. Consultar la solicitud.
3. Registrar la solución aplicada.
4. Verificar que la solicitud pasa al estado `Resuelto`, de acuerdo con las reglas de transición.
5. Iniciar sesión como coordinador.
6. Consultar la solicitud resuelta.
7. Revisar la solución registrada.
8. Ejecutar el cierre de la solicitud.
9. Consultar nuevamente el estado de la solicitud.
10. Iniciar sesión como solicitante propietario.
11. Consultar el resultado y la finalización del caso.

**Resultado esperado:**

- El técnico puede registrar la solución de una solicitud asignada.
- La solución queda almacenada y asociada al caso.
- El coordinador puede revisar y cerrar la solicitud.
- La solicitud queda en estado `Cerrado`.
- Se conserva la información correspondiente al cierre.
- El solicitante puede consultar el resultado de la atención después del cierre.
- La solicitud cerrada conserva su información histórica para consulta autorizada.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas del registro de solución, cierre y consulta del resultado por parte del solicitante.

---

### PF-10. Consulta consolidada de coordinación

**Criterio de aceptación:** CA-06.

**Requisito relacionado:** RF-29.

**Objetivo:** comprobar que el coordinador puede consultar información consolidada de varias solicitudes, incluyendo sus estados y responsables.

**Precondiciones:**

- Existen varias solicitudes registradas.
- Las solicitudes tienen diferentes estados.
- Existen solicitudes asignadas a diferentes técnicos.
- Existe una cuenta activa de coordinador.

**Datos de entrada:**

- Conjunto de solicitudes de prueba.
- Estados de las solicitudes.
- Técnicos responsables.
- Información estadística disponible en el sistema.

**Pasos:**

1. Iniciar sesión como coordinador.
2. Abrir la consulta de estadísticas o información consolidada.
3. Consultar la información general de las solicitudes.
4. Verificar la información agrupada por estado.
5. Consultar los responsables de las solicitudes, cuando la funcionalidad lo permita.
6. Comparar los resultados con los registros existentes.
7. Comprobar que los datos presentados corresponden a las solicitudes almacenadas.

**Resultado esperado:**

- El coordinador puede consultar información de varios casos.
- Se presentan los estados correspondientes.
- Se puede identificar a los responsables de los casos.
- Los datos consolidados coinciden con la información almacenada.
- La consulta está restringida a los roles autorizados.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Captura de la consulta consolidada y de los registros utilizados para comprobar sus resultados.

---

### PF-11. Verificación de persistencia e integridad de relaciones

**Criterios de aceptación:** CA-01, CA-02 y CA-04.

**Requisitos relacionados:** RF-06, RF-11, RF-12, RF-16, RF-17 y RF-28.

**Objetivo:** comprobar que los registros del sistema se conservan en la base de datos y mantienen correctamente sus relaciones.

**Precondiciones:**

- PostgreSQL está disponible.
- El backend está conectado a la base de datos.
- Existen solicitudes, usuarios, asignaciones e intervenciones de prueba.
- Se dispone de acceso autorizado para consultar la información de la base de datos.

**Datos de entrada:**

- Una solicitud registrada.
- El usuario solicitante.
- El técnico responsable.
- Una asignación.
- Una o varias intervenciones.
- Registros del historial relacionados con las operaciones realizadas.

**Pasos:**

1. Registrar una solicitud desde la aplicación.
2. Consultar la solicitud mediante la API.
3. Verificar que el registro existe en la base de datos.
4. Comprobar que la solicitud está relacionada con el solicitante correcto.
5. Asignar la solicitud a un técnico.
6. Verificar que la asignación se conserva correctamente.
7. Registrar una intervención.
8. Consultar la intervención mediante la API.
9. Verificar que la intervención está relacionada con la solicitud y el responsable correspondiente.
10. Consultar los registros del historial relacionados con las operaciones realizadas.
11. Comparar los datos obtenidos desde la aplicación con los almacenados en PostgreSQL.

**Resultado esperado:**

- Las solicitudes se conservan después de registrarse.
- Las relaciones entre solicitudes y solicitantes son correctas.
- Las asignaciones conservan la relación con el técnico correspondiente.
- Las intervenciones quedan asociadas a la solicitud y al responsable.
- El historial conserva los cambios que deben registrarse.
- No se presentan relaciones inconsistentes o registros huérfanos.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas de las consultas de la API y de las verificaciones realizadas en PostgreSQL.

---

### PF-12. Verificación de integración entre interfaz, API y base de datos

**Criterios de aceptación:** CA-01, CA-02, CA-03, CA-04, CA-05 y CA-06.

**Requisitos relacionados:** RF-01, RF-02, RF-06, RF-07, RF-09, RF-10, RF-11, RF-13, RF-14, RF-16, RF-19, RF-20 y RF-29.

**Objetivo:** comprobar que la interfaz web, la API REST y la base de datos trabajan de forma integrada durante un flujo de atención de soporte.

**Precondiciones:**

- El frontend está en ejecución.
- El backend está en ejecución.
- PostgreSQL está disponible.
- El frontend está configurado para comunicarse con el backend.
- Existen cuentas activas de solicitante, técnico y coordinador.

**Datos de entrada:**

- Credenciales de los usuarios de prueba.
- Información válida para registrar una solicitud.
- Categoría y prioridad válidas.
- Técnico responsable.
- Descripción de una intervención.
- Descripción de una solución.

**Pasos:**

1. Abrir la interfaz web.
2. Iniciar sesión como solicitante.
3. Registrar una solicitud desde el frontend.
4. Comprobar que la interfaz muestra el resultado de la operación.
5. Verificar que la API recibió y procesó la solicitud.
6. Consultar la base de datos y comprobar que el registro existe.
7. Iniciar sesión como coordinador.
8. Consultar y evaluar la solicitud.
9. Asignarla a un técnico.
10. Iniciar sesión como técnico.
11. Consultar la solicitud asignada.
12. Registrar una intervención.
13. Registrar la solución cuando corresponda.
14. Iniciar sesión como coordinador y cerrar la solicitud.
15. Iniciar sesión como solicitante y consultar el resultado.
16. Consultar la información consolidada desde la cuenta de coordinador.

**Resultado esperado:**

- El frontend se comunica correctamente con el backend.
- La API procesa las operaciones y aplica las reglas de negocio.
- PostgreSQL conserva los registros y sus relaciones.
- Los cambios realizados se reflejan en las consultas posteriores.
- Los roles pueden realizar las operaciones autorizadas.
- El flujo completo mantiene la coherencia de la información.
- El resultado final puede consultarse desde la interfaz.

**Resultado obtenido:** Pendiente de ejecución.

**Estado:** Pendiente.

**Evidencia:** Capturas de las operaciones realizadas desde el frontend, respuestas de la API y verificaciones de persistencia en PostgreSQL.

---

## 5. Resumen de ejecución

Esta tabla se actualizará después de ejecutar las pruebas funcionales.

| ID | Prueba | Estado | Evidencia |
|---|---|---|---|
| PF-01 | Registro válido de un caso de soporte | Pendiente | Por adjuntar |
| PF-02 | Registro de un caso con datos inválidos | Pendiente | Por adjuntar |
| PF-03 | Consulta de un caso existente | Pendiente | Por adjuntar |
| PF-04 | Consulta de un caso inexistente | Pendiente | Por adjuntar |
| PF-05 | Gestión de un caso por personal autorizado | Pendiente | Por adjuntar |
| PF-06 | Intento de gestión por un actor no autorizado | Pendiente | Por adjuntar |
| PF-07 | Consulta del estado y responsable de un caso | Pendiente | Por adjuntar |
| PF-08 | Consulta del historial de intervenciones | Pendiente | Por adjuntar |
| PF-09 | Cierre de un caso y consulta del resultado | Pendiente | Por adjuntar |
| PF-10 | Consulta consolidada de coordinación | Pendiente | Por adjuntar |
| PF-11 | Verificación de persistencia e integridad de relaciones | Pendiente | Por adjuntar |
| PF-12 | Verificación de integración entre interfaz, API y base de datos | Pendiente | Por adjuntar |

### 5.1. Contadores

Los siguientes valores representan el estado inicial del plan de pruebas, no resultados de una ejecución.

| Indicador | Cantidad |
|---|---:|
| Total de pruebas | 12 |
| Aprobadas | 0 |
| Fallidas | 0 |
| Bloqueadas | 0 |
| Pendientes | 12 |

Los contadores deberán actualizarse únicamente con resultados reales de ejecución.

## 6. Evidencias

Las capturas y registros de las pruebas se conservarán en la carpeta `evidencias/`.

Se propone la siguiente estructura:

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

Cada carpeta debe contener evidencia suficiente para identificar:

- La prueba ejecutada.
- El usuario o rol utilizado.
- La operación realizada.
- Los datos relevantes de entrada.
- El resultado obtenido.
- La fecha de ejecución.

Las evidencias pueden incluir capturas de la interfaz, solicitudes y respuestas HTTP, registros de ejecución y consultas de PostgreSQL.

Se deben ocultar contraseñas, tokens, claves y datos personales reales.

## 7. Relación con la matriz de trazabilidad

Los resultados de este documento complementan la matriz definida en `docs/trazabilidad.md`.

La relación entre las pruebas funcionales y las condiciones de aceptación es:

| Condición de aceptación | Pruebas relacionadas |
|---|---|
| CA-01. Registro de casos de soporte | PF-01, PF-02, PF-03, PF-11 y PF-12 |
| CA-02. Evaluación y gestión de casos | PF-05, PF-06, PF-11 y PF-12 |
| CA-03. Consulta del estado y responsable | PF-03, PF-04, PF-07 y PF-12 |
| CA-04. Historial de intervenciones | PF-08, PF-11 y PF-12 |
| CA-05. Consulta del resultado y finalización | PF-03, PF-09 y PF-12 |
| CA-06. Consulta consolidada de coordinación | PF-10 y PF-12 |

Una condición de aceptación no se marcará como demostrada únicamente porque exista un endpoint o una prueba automatizada.

Se debe comprobar el flujo funcional correspondiente y conservar evidencia reproducible.

## 8. Control de cambios

| Versión | Descripción |
|---|---|
| 1.0 | Creación del documento con los casos de prueba funcionales iniciales. |
| 2.0 | Ajuste de las doce pruebas funcionales para alinearlas con la Actividad 6 de `proyecto2.md` y las condiciones de aceptación CA-01 a CA-06. |