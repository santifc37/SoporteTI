# Pruebas funcionales — SoporteTI

## 1. Objetivo

Este documento contiene los escenarios de prueba funcionales del proyecto SoporteTI, de acuerdo con los requisitos establecidos en `proyecto2.md`, Actividad 6.

Las pruebas tienen como objetivo verificar el registro y la gestión de casos de soporte, las consultas, los permisos de acceso, el historial de intervenciones, el cierre de solicitudes, la persistencia de la información y la integración entre el frontend, la API REST y la base de datos.

Las pruebas se ejecutarán manualmente mediante la interfaz web y, cuando corresponda, mediante solicitudes HTTP.

## 2. Alcance

Se contemplan doce escenarios funcionales:

1. Registro válido de un caso de soporte.
2. Registro de un caso con datos inválidos.
3. Consulta de un caso existente.
4. Consulta de un caso inexistente.
5. Gestión de un caso por personal autorizado.
6. Intento de gestión por un actor no autorizado.
7. Consulta del estado y responsable de un caso.
8. Consulta del historial de intervenciones.
9. Cierre de un caso y consulta del resultado.
10. Consulta consolidada de coordinación.
11. Verificación de persistencia e integridad de las relaciones.
12. Verificación de integración entre frontend, API y base de datos.

## 3. Condiciones generales de ejecución

- La aplicación y sus servicios deben encontrarse disponibles.
- La base de datos debe estar accesible.
- Deben existir cuentas de los roles necesarios para cada escenario.
- Se utilizarán datos de prueba identificables.
- Las pruebas se realizarán respetando los permisos definidos para cada rol.
- Cada escenario deberá ejecutarse y documentarse individualmente.
- Las evidencias deberán permitir verificar el resultado obtenido.

## 4. Registro de resultados

Para cada prueba se utilizará el siguiente formato:

- **Estado:** Pendiente, Aprobada o Fallida.
- **Resultado obtenido:** descripción de lo que ocurrió realmente.
- **Método HTTP:** método utilizado, cuando aplique.
- **Código HTTP:** respuesta recibida, cuando aplique.
- **Evidencia:** nombre o ruta de la captura, registro o evidencia correspondiente.

Ninguna prueba se considerará aprobada hasta que haya sido ejecutada y su resultado haya sido verificado.

---

## 5. Escenarios de prueba

### PF-01. Registro válido de un caso de soporte

**Requisito asociado:** RF-06.

**Criterio de aceptación:** CA-01.

**Precondiciones:**
- La aplicación está disponible.
- Existe un usuario solicitante autenticado.
- El usuario tiene acceso al formulario de registro de solicitudes.

**Pasos de ejecución:**
1. Iniciar sesión con una cuenta de solicitante.
2. Acceder al formulario de creación de solicitudes.
3. Ingresar la información obligatoria del caso.
4. Confirmar el registro.
5. Consultar el caso creado.

**Datos de entrada:**
- Tipo de solicitud válido.
- Descripción del problema.
- Ubicación o información requerida por el formulario.
- Datos adicionales obligatorios según el tipo de solicitud.

**Resultado esperado:**
- El sistema acepta el registro.
- La solicitud queda almacenada en la base de datos.
- Se asigna un identificador al caso.
- La solicitud inicia en estado `Registrado`.
- El solicitante puede consultar el caso creado.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-02. Registro de un caso con datos inválidos

**Requisito asociado:** RF-06.

**Criterio de aceptación:** CA-01.

**Precondiciones:**
- La aplicación está disponible.
- Existe un usuario solicitante autenticado.

**Pasos de ejecución:**
1. Acceder al formulario de creación de solicitudes.
2. Dejar vacío un campo obligatorio o ingresar un dato inválido.
3. Intentar registrar la solicitud.
4. Verificar el mensaje presentado por el sistema.
5. Comprobar que no se haya creado un caso incorrecto.

**Datos de entrada:**
- Descripción vacía o dato obligatorio inválido.

**Resultado esperado:**
- El sistema rechaza el registro.
- Se informa qué dato debe corregirse.
- No se almacena una solicitud con información inválida.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-03. Consulta de un caso existente

**Requisito asociado:** RF-07.

**Criterios de aceptación:** CA-01 y CA-03.

**Precondiciones:**
- Existe una solicitud registrada.
- El usuario que realiza la consulta tiene permisos para acceder al caso.

**Pasos de ejecución:**
1. Iniciar sesión con un usuario autorizado.
2. Acceder al módulo de consulta de solicitudes.
3. Buscar una solicitud existente mediante su identificador.
4. Abrir el resultado.
5. Verificar la información presentada.

**Datos de entrada:**
- Identificador de una solicitud existente.

**Resultado esperado:**
- El sistema encuentra la solicitud.
- Presenta la información correspondiente al caso.
- Los datos mostrados coinciden con los almacenados.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-04. Consulta de un caso inexistente

**Requisito asociado:** RF-07.

**Criterio de aceptación:** CA-03.

**Precondiciones:**
- La aplicación está disponible.
- Existe un usuario autorizado para realizar consultas.

**Pasos de ejecución:**
1. Iniciar sesión.
2. Acceder al módulo de consulta.
3. Ingresar un identificador que no corresponda a ninguna solicitud registrada.
4. Ejecutar la búsqueda.
5. Verificar la respuesta del sistema.

**Datos de entrada:**
- Identificador inexistente.

**Resultado esperado:**
- El sistema no devuelve una solicitud inexistente.
- Presenta un mensaje o respuesta controlada indicando que no se encontró el caso.
- No expone información de otros registros.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-05. Gestión de un caso por personal autorizado

**Requisitos asociados:** RF-09, RF-10, RF-11, RF-12 y RF-14.

**Criterio de aceptación:** CA-02.

**Precondiciones:**
- Existe una solicitud registrada.
- Existe una cuenta de coordinador autenticada.
- El coordinador tiene permisos para gestionar solicitudes.

**Pasos de ejecución:**
1. Iniciar sesión como coordinador.
2. Acceder a la solicitud existente.
3. Realizar una acción de gestión permitida, como evaluar, clasificar, asignar un técnico o actualizar el estado.
4. Confirmar la operación.
5. Consultar nuevamente la solicitud.
6. Verificar que el cambio haya quedado registrado.

**Datos de entrada:**
- Identificador de la solicitud.
- Categoría, prioridad, técnico o estado válido, según la operación seleccionada.

**Resultado esperado:**
- El sistema permite la operación autorizada.
- La información del caso se actualiza correctamente.
- Se conserva la relación con el responsable correspondiente.
- Los cambios quedan almacenados.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-06. Intento de gestión por un actor no autorizado

**Requisitos asociados:** RF-02 y RF-09 a RF-14, según la operación evaluada.

**Criterio de aceptación:** CA-02.

**Precondiciones:**
- Existe una solicitud sobre la que se intentará realizar una operación restringida.
- Existe una cuenta sin permisos para ejecutar esa operación.

**Pasos de ejecución:**
1. Iniciar sesión con un usuario que no tenga autorización para gestionar el caso.
2. Intentar acceder a la operación restringida.
3. Intentar ejecutar la modificación mediante la interfaz o la solicitud HTTP correspondiente.
4. Verificar la respuesta del sistema.
5. Consultar el caso para comprobar que no haya sufrido modificaciones no autorizadas.

**Datos de entrada:**
- Identificador de la solicitud.
- Usuario sin permisos para la operación.
- Datos de modificación de prueba.

**Resultado esperado:**
- El sistema bloquea la operación.
- Devuelve una respuesta de acceso no autorizado o prohibido, según corresponda.
- No modifica la información del caso.
- No expone información restringida.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-07. Consulta del estado y responsable de un caso

**Requisitos asociados:** RF-07, RF-11, RF-12, RF-13 y RF-14.

**Criterio de aceptación:** CA-03.

**Precondiciones:**
- Existe una solicitud con un estado registrado.
- La solicitud tiene un responsable asignado cuando corresponda.
- El usuario tiene permisos para consultar la información.

**Pasos de ejecución:**
1. Iniciar sesión con un usuario autorizado.
2. Consultar la solicitud.
3. Identificar el estado actual.
4. Identificar el responsable de atención.
5. Comparar la información presentada con los registros almacenados.

**Datos de entrada:**
- Identificador de una solicitud existente.

**Resultado esperado:**
- El sistema presenta el estado correcto.
- Identifica al responsable correspondiente.
- La información coincide con las asignaciones y los cambios registrados.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-08. Consulta del historial de intervenciones

**Requisitos asociados:** RF-16, RF-17 y RF-21.

**Criterio de aceptación:** CA-04.

**Precondiciones:**
- Existe una solicitud con intervenciones registradas.
- El usuario tiene permisos para consultar las intervenciones correspondientes.

**Pasos de ejecución:**
1. Iniciar sesión con un usuario autorizado.
2. Acceder a una solicitud que tenga intervenciones.
3. Consultar el historial de intervenciones.
4. Verificar el contenido, autor y fecha de los registros.
5. Comprobar que se respeten las reglas de visibilidad.

**Datos de entrada:**
- Identificador de una solicitud con intervenciones registradas.

**Resultado esperado:**
- El sistema presenta las intervenciones asociadas al caso.
- Se conserva la información de cada intervención.
- Se respeta la visibilidad según el rol y los permisos del usuario.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-09. Cierre de un caso y consulta del resultado

**Requisitos asociados:** RF-07, RF-19 y RF-20.

**Criterio de aceptación:** CA-05.

**Precondiciones:**
- Existe una solicitud que puede ser resuelta y cerrada.
- El técnico asignado ha registrado la solución cuando corresponda.
- Existe un coordinador autorizado para realizar el cierre.

**Pasos de ejecución:**
1. Consultar la solicitud.
2. Verificar que tenga una solución registrada.
3. Iniciar sesión como coordinador.
4. Revisar la solución.
5. Confirmar el cierre de la solicitud.
6. Consultar nuevamente el caso.
7. Verificar que el resultado permanezca disponible.

**Datos de entrada:**
- Identificador de la solicitud resuelta.
- Confirmación de cierre por solución.

**Resultado esperado:**
- La solicitud cambia a estado `Cerrado`.
- Se conserva el tipo de cierre y la información correspondiente.
- El resultado de la atención permanece disponible para consulta autorizada.
- No se permiten nuevas operaciones que estén prohibidas para solicitudes cerradas.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-10. Consulta consolidada de coordinación

**Requisito asociado:** RF-29.

**Criterio de aceptación:** CA-06.

**Precondiciones:**
- Existe una cuenta de coordinador autenticada.
- Hay varias solicitudes registradas.
- Existen solicitudes con diferentes estados o responsables.

**Pasos de ejecución:**
1. Iniciar sesión como coordinador.
2. Acceder al módulo de estadísticas o consulta consolidada.
3. Consultar la información general de las solicitudes.
4. Verificar los resultados presentados.
5. Comparar los datos con los registros existentes.

**Datos de entrada:**
- Conjunto de solicitudes registradas en el sistema.

**Resultado esperado:**
- El coordinador puede consultar información consolidada.
- Los datos corresponden con los registros existentes.
- La información se presenta de acuerdo con los criterios de agrupación implementados.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-11. Verificación de persistencia e integridad de las relaciones

**Requisitos asociados:** RF-06, RF-16 y RF-17.

**Criterios de aceptación:** CA-01, CA-02 y CA-04.

**Precondiciones:**
- La aplicación y la base de datos están disponibles.
- Existe una solicitud registrada.
- Existen registros relacionados, como solicitante, responsable e intervenciones, cuando correspondan.

**Pasos de ejecución:**
1. Registrar o seleccionar una solicitud de prueba.
2. Consultar la información mediante la aplicación.
3. Verificar los registros relacionados en la base de datos.
4. Consultar las intervenciones asociadas al caso, si existen.
5. Comparar los identificadores y las relaciones entre los registros.
6. Volver a consultar la solicitud para verificar que la información persista.

**Datos de entrada:**
- Identificador de una solicitud.
- Registros relacionados con la solicitud.

**Resultado esperado:**
- La información permanece almacenada después de finalizar la operación.
- Las relaciones entre la solicitud y sus registros asociados son consistentes.
- No se presentan relaciones inválidas ni pérdida de información.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar, cuando aplique.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

### PF-12. Verificación de integración entre frontend, API y base de datos

**Requisitos asociados:** RF-06 y requisitos relacionados con la consulta y gestión del caso.

**Criterios de aceptación:** CA-01 a CA-06.

**Precondiciones:**
- El frontend está disponible.
- La API REST está disponible.
- La base de datos está accesible.
- Existe una cuenta de usuario autorizada.

**Pasos de ejecución:**
1. Abrir la aplicación web.
2. Iniciar sesión.
3. Registrar un caso de soporte desde la interfaz.
4. Verificar que el frontend envíe la solicitud a la API.
5. Verificar que la API procese y almacene la información en la base de datos.
6. Consultar el caso desde la aplicación.
7. Verificar que la información recuperada corresponda con la registrada.
8. Comprobar que las respuestas y mensajes de la aplicación sean coherentes con el resultado de las operaciones.

**Datos de entrada:**
- Credenciales válidas.
- Información válida de una solicitud de prueba.

**Resultado esperado:**
- El frontend se comunica correctamente con la API.
- La API procesa las operaciones y se comunica con la base de datos.
- La información queda almacenada.
- La aplicación puede recuperar y presentar la información registrada.
- No se presentan errores de integración durante el flujo probado.

**Resultado obtenido:** Pendiente de ejecución.

**Método HTTP y código de respuesta:** Pendiente de registrar.

**Estado:** Pendiente.

**Evidencia:** Pendiente de adjuntar.

---

## 6. Resumen de resultados

El siguiente resumen se actualizará después de ejecutar las doce pruebas.

| Estado | Cantidad |
|---|---:|
| Aprobadas | 0 |
| Fallidas | 0 |
| Pendientes | 12 |
| **Total** | **12** |

## 7. Ubicación de evidencias

Las evidencias de las pruebas funcionales se almacenarán en:

`evidencias/pruebas/`

Se recomienda identificar cada archivo mediante el código de la prueba correspondiente.

Ejemplos de nombres:

- `PF-01-registro-valido.png`
- `PF-02-registro-invalido.png`
- `PF-03-consulta-existente.png`
- `PF-04-consulta-inexistente.png`
- `PF-05-gestion-autorizada.png`
- `PF-06-gestion-no-autorizada.png`
- `PF-07-estado-responsable.png`
- `PF-08-historial-intervenciones.png`
- `PF-09-cierre-resultado.png`
- `PF-10-consolidado-coordinacion.png`
- `PF-11-persistencia-integridad.png`
- `PF-12-integracion-completa.png`

Los nombres son una convención propuesta. Cada evidencia deberá corresponder a una ejecución real.

## 8. Consideraciones finales

Las pruebas funcionales de este documento se ejecutarán manualmente y sus resultados se registrarán de acuerdo con lo observado.

Las pruebas automatizadas existentes en el backend constituyen evidencia técnica complementaria, pero no reemplazan los escenarios funcionales exigidos en `proyecto2.md`.

La ejecución, los resultados y las evidencias deberán mantenerse actualizados para facilitar la validación del proyecto y su sustentación.