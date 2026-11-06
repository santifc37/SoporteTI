# Documento de requisitos — SoporteTI

**Versión:** 1.2  
**Estado:** Requisitos definidos  
**Proyecto:** SoporteTI  
**Asignatura:** Aplicaciones y Servicios Web  
**Institución:** Instituto Tecnológico Metropolitano (ITM)

---

## 1. Descripción del proyecto

SoporteTI es una plataforma web destinada a gestionar solicitudes de soporte técnico dentro de una organización. Su propósito es centralizar la recepción, clasificación, asignación, atención y seguimiento de los problemas reportados por los usuarios.

La plataforma permitirá que los solicitantes registren problemas y consulten su estado, mientras que el personal de soporte podrá gestionar las solicitudes asignadas, documentar intervenciones y comunicarse con los solicitantes.

El coordinador tendrá acceso a la administración general del sistema, incluyendo la gestión de usuarios, asignaciones, prioridades, categorías y cierre de solicitudes.

## 2. Objetivo general

Desarrollar una plataforma web que permita gestionar de manera organizada y trazable las solicitudes de soporte técnico, facilitando la comunicación entre solicitantes, técnicos y coordinadores, y manteniendo un registro de las actividades realizadas durante la atención.

## 3. Alcance del proyecto

La primera versión de SoporteTI incluirá:

- Registro e inicio de sesión de usuarios.
- Administración de cuentas por parte del coordinador.
- Gestión de solicitudes de soporte.
- Clasificación por categorías y prioridades.
- Asignación y reasignación de solicitudes.
- Gestión de estados.
- Registro de intervenciones técnicas.
- Conversación entre el solicitante y el personal autorizado.
- Adjuntos de imágenes.
- Notificaciones por correo electrónico cuando corresponda según el medio de contacto elegido.
- Historial de cambios y seguimiento.
- Paneles de consulta y estadísticas básicas.

### 3.1 Fuera del alcance inicial

La primera versión no incluirá:

- Registro público de usuarios.
- Aplicación móvil nativa.
- Chat en tiempo real mediante WebSockets.
- Recepción y procesamiento de respuestas enviadas directamente al correo electrónico.
- Integraciones con sistemas externos de gestión empresarial.
- Gestión de inventario de equipos o repuestos.
- Automatización de diagnósticos mediante inteligencia artificial.
- Reapertura de solicitudes cerradas.

Estas funcionalidades podrán evaluarse como mejoras posteriores.

## 4. Levantamiento de información

El levantamiento de requisitos se realizó mediante la recopilación de información sobre el funcionamiento esperado de un sistema de soporte técnico.

Se identificaron las necesidades de los diferentes participantes, los procesos de atención, los mecanismos de comunicación y las restricciones que debe cumplir la plataforma.

Las evidencias del levantamiento se encuentran en `evidencias/entrevista/`.

Los requisitos se organizaron en requisitos funcionales, reglas de negocio y requisitos no funcionales.

## 5. Actores del sistema

La plataforma contará con tres roles principales.

### 5.1 Solicitante

Es la persona que necesita asistencia técnica.

Puede:

- Iniciar sesión.
- Crear solicitudes.
- Consultar sus propias solicitudes.
- Consultar el estado de sus solicitudes.
- Enviar mensajes durante la atención.
- Consultar las respuestas del personal de soporte.
- Adjuntar imágenes.
- Cancelar solicitudes en los estados permitidos.
- Consultar el historial de sus solicitudes.

No puede asignar técnicos, modificar prioridades ni cerrar solicitudes como solución.

### 5.2 Técnico

Es la persona encargada de atender los problemas asignados.

Puede:

- Consultar las solicitudes que tiene asignadas.
- Consultar la información de cada solicitud asignada.
- Registrar intervenciones técnicas.
- Cambiar el estado de una solicitud asignada cuando la transición esté permitida.
- Solicitar información adicional al solicitante.
- Participar en la conversación.
- Registrar la solución aplicada.
- Consultar el historial de atención de sus solicitudes asignadas.

No puede crear usuarios, asignar o reasignar solicitudes, modificar prioridades ni cerrar solicitudes.

### 5.3 Coordinador

Es el responsable de administrar y supervisar el sistema.

Puede:

- Consultar todas las solicitudes.
- Crear, modificar y desactivar cuentas de usuario.
- Gestionar categorías.
- Establecer prioridades.
- Evaluar solicitudes.
- Asignar y reasignar técnicos.
- Supervisar las intervenciones.
- Participar en las conversaciones.
- Revisar las soluciones registradas.
- Cerrar solicitudes.
- Consultar estadísticas e informes.
- Consultar el historial completo de las solicitudes.

## 6. Requisitos funcionales

### 6.1 Autenticación y usuarios

**RF-01. Inicio de sesión**

El sistema debe permitir que los usuarios registrados inicien sesión mediante sus credenciales.

**RF-02. Control de acceso por roles**

El sistema debe restringir las funcionalidades y la información de acuerdo con el rol del usuario autenticado: solicitante, técnico o coordinador.

**RF-03. Administración de usuarios**

El sistema debe permitir al coordinador crear, consultar, modificar y desactivar cuentas de solicitantes, técnicos y coordinadores.

No existirá un mecanismo de registro público.

**RF-04. Recuperación y cambio de contraseña**

El sistema debe proporcionar un mecanismo para recuperar o cambiar la contraseña de una cuenta, de acuerdo con el procedimiento de autenticación implementado.

**RF-05. Gestión de datos de contacto**

El sistema debe permitir almacenar y actualizar los datos de contacto del usuario, incluyendo el medio de contacto seleccionado y la información necesaria para utilizarlo.

### 6.2 Gestión de solicitudes

**RF-06. Creación de solicitudes**

El sistema debe permitir que un solicitante registre una solicitud indicando como mínimo:

- Asunto.
- Descripción del problema.
- Categoría, cuando corresponda.
- Medio de contacto preferido.
- Adjuntos opcionales.

El sistema debe registrar automáticamente la fecha de creación y el usuario solicitante.

**RF-07. Consulta de solicitudes**

El sistema debe permitir que cada solicitante consulte únicamente sus propias solicitudes.

Los técnicos podrán consultar las solicitudes que tengan asignadas y los coordinadores podrán consultar todas las solicitudes.

**RF-08. Adjuntos en solicitudes**

El sistema debe permitir adjuntar imágenes a una solicitud.

Los archivos permitidos serán PNG y JPG, con un tamaño máximo de 5 MB por archivo.

**RF-09. Evaluación de solicitudes**

El sistema debe permitir que el coordinador revise las solicitudes registradas y determine si requieren atención, necesitan información adicional o deben ser cerradas por una causa administrativa.

**RF-10. Clasificación y prioridad**

El sistema debe permitir que el coordinador establezca la categoría y prioridad de una solicitud.

Las prioridades serán configurables por el sistema y podrán incluir, como mínimo, baja, media y alta.

**RF-11. Asignación de técnicos**

El sistema debe permitir que el coordinador asigne una solicitud a un técnico disponible.

**RF-12. Reasignación de solicitudes**

El sistema debe permitir que el coordinador cambie el técnico responsable de una solicitud, conservando el registro de las asignaciones anteriores.

Después de una reasignación, el técnico anterior perderá el acceso operativo a la solicitud. El nuevo técnico asignado podrá continuar la atención.

**RF-13. Consulta de solicitudes asignadas**

El sistema debe permitir que el técnico consulte las solicitudes que se encuentran asignadas a su cuenta.

**RF-14. Actualización del estado**

El sistema debe permitir que los usuarios autorizados actualicen el estado de una solicitud de acuerdo con las transiciones permitidas.

**RF-15. Cancelación de solicitudes**

El sistema debe permitir que el solicitante cancele una solicitud cuando se encuentre en estado `Registrado` o `En evaluación`.

La cancelación cambiará el estado de la solicitud a `Cerrado` y registrará el tipo de cierre como `Cancelación`, junto con el responsable, la fecha y el motivo de la cancelación.

El solicitante no podrá cancelar solicitudes que ya estén en atención o cerradas.

### 6.3 Atención técnica

**RF-16. Registro de intervenciones**

El sistema debe permitir que el técnico asignado registre las actividades realizadas durante la atención de una solicitud.

Cada intervención deberá contener una descripción y su fecha de registro.

**RF-17. Visibilidad de intervenciones**

El sistema debe permitir distinguir las intervenciones internas de las intervenciones visibles para el solicitante.

Las intervenciones internas solo podrán ser consultadas por el personal autorizado.

**RF-18. Solicitud de información adicional**

El sistema debe permitir que el técnico solicite información adicional al solicitante cuando sea necesaria para continuar la atención.

**RF-19. Registro de solución**

El sistema debe permitir que el técnico registre la solución aplicada a una solicitud, incluyendo una descripción de las acciones realizadas y el resultado obtenido.

**RF-20. Revisión y cierre de solicitudes**

El sistema debe permitir que el coordinador revise la atención realizada y cierre la solicitud cuando corresponda.

El cierre deberá registrar el tipo de cierre y el responsable de la acción.

**RF-21. Consulta de intervenciones**

El sistema debe permitir consultar las intervenciones relacionadas con una solicitud, respetando las reglas de visibilidad y los permisos de cada rol.

### 6.4 Comunicación y seguimiento

**RF-22. Conversación asociada a solicitudes**

El sistema debe disponer de una conversación asociada a cada solicitud para permitir el intercambio de mensajes entre el solicitante y el personal de soporte autorizado.

**RF-23. Envío y consulta de mensajes**

El sistema debe permitir que el solicitante, el técnico asignado y el coordinador envíen y consulten mensajes relacionados con una solicitud.

El solicitante podrá comunicarse durante toda la atención de una solicitud abierta, incluso cuando se encuentre en estado `En espera`.

El envío de un mensaje no modificará automáticamente el estado de la solicitud.

Los técnicos que no estén asignados a la solicitud no podrán acceder a su conversación.

**RF-24. Adjuntos en mensajes**

El sistema debe permitir adjuntar imágenes a los mensajes de la conversación.

Se permitirán archivos PNG y JPG, con un tamaño máximo de 5 MB por archivo.

**RF-25. Adjuntos en intervenciones**

El sistema debe permitir adjuntar imágenes a las intervenciones técnicas.

Se permitirán archivos PNG y JPG, con un tamaño máximo de 5 MB por archivo.

**RF-26. Historial de conversación**

El sistema debe conservar los mensajes de cada solicitud en orden cronológico para permitir consultar la comunicación realizada durante su atención.

**RF-27. Notificaciones**

El sistema debe generar notificaciones relacionadas con los eventos relevantes de una solicitud.

Cuando el usuario haya seleccionado el correo electrónico como medio de contacto, el sistema podrá enviar las notificaciones correspondientes a ese correo.

El correo será un canal de notificación. Las respuestas y comunicaciones dentro de la solicitud se realizarán desde la plataforma.

**RF-28. Historial de cambios y estadísticas**

El sistema debe mantener un historial de los cambios importantes realizados en cada solicitud, incluyendo cambios de estado, prioridad, categoría, asignación, reasignación y cierre.

También debe permitir al coordinador consultar estadísticas básicas sobre las solicitudes, sus estados, prioridades, categorías y tiempos de atención.

## 7. Reglas de negocio

**RN-01.** Toda persona que utilice la plataforma debe tener una cuenta creada previamente por un coordinador.

**RN-02.** No se permitirá el registro público de usuarios.

**RN-03.** Cada usuario tendrá un único rol activo dentro del sistema: solicitante, técnico o coordinador.

**RN-04.** Un solicitante solo podrá consultar y gestionar sus propias solicitudes.

**RN-05.** Un técnico solo podrá acceder operativamente a las solicitudes que tenga asignadas.

**RN-06.** El coordinador tendrá acceso general a las solicitudes y a las funciones administrativas.

**RN-07.** Toda solicitud deberá estar asociada a un solicitante.

**RN-08.** Toda solicitud nueva deberá iniciar en estado `Registrado`.

**RN-09.** El coordinador será responsable de evaluar las solicitudes registradas.

**RN-10.** La prioridad de una solicitud será establecida por el coordinador.

**RN-11.** La asignación y reasignación de técnicos será responsabilidad exclusiva del coordinador.

**RN-12.** Una solicitud en atención deberá tener un técnico asignado.

**RN-13.** Toda reasignación deberá conservar el registro de la asignación anterior y de la nueva asignación.

**RN-14.** Cuando una solicitud sea reasignada, el técnico anterior perderá el acceso operativo a ella.

**RN-15.** El técnico asignado podrá registrar intervenciones y documentar la solución, pero no podrá cerrar la solicitud.

**RN-16.** Las intervenciones internas no podrán ser consultadas por el solicitante.

**RN-17.** Las intervenciones visibles para el solicitante podrán ser consultadas por este y por el personal autorizado.

**RN-18.** El solicitante podrá cancelar una solicitud únicamente cuando esté en estado `Registrado` o `En evaluación`.

**RN-19.** Una cancelación deberá cambiar el estado de la solicitud a `Cerrado` y registrar el tipo de cierre `Cancelación`.

**RN-20.** El coordinador será el único rol autorizado para cerrar una solicitud por finalización de la atención o por una causa administrativa.

**RN-21.** Una solicitud cerrada no podrá reabrirse. Si se presenta un nuevo problema, deberá crearse una nueva solicitud.

**RN-22.** Una solicitud cerrada no permitirá nuevos mensajes, intervenciones, adjuntos ni modificaciones operativas.

**RN-23.** El historial y la conversación de una solicitud cerrada permanecerán disponibles para consulta de los usuarios autorizados.

**RN-24.** El solicitante podrá enviar mensajes mientras la solicitud esté abierta, sin importar si se encuentra en estado `En espera`.

**RN-25.** Enviar un mensaje no cambiará automáticamente el estado de la solicitud.

**RN-26.** La conversación solo estará disponible para el solicitante propietario, el técnico actualmente asignado y los coordinadores autorizados.

**RN-27.** Los técnicos que no estén asignados a una solicitud no podrán consultar sus mensajes ni sus intervenciones internas.

**RN-28.** Los archivos adjuntos deberán ser imágenes en formato PNG o JPG y no podrán superar los 5 MB por archivo.

**RN-29.** El correo electrónico se utilizará para enviar notificaciones cuando el usuario haya seleccionado ese medio de contacto. La comunicación y las respuestas se gestionarán dentro de la plataforma.

**RN-30.** Toda modificación importante de una solicitud deberá quedar registrada en el historial, incluyendo el usuario responsable y la fecha de la acción.

## 8. Estados de las solicitudes

Las solicitudes tendrán los siguientes estados:

| Estado | Descripción |
|---|---|
| Registrado | La solicitud fue creada y está pendiente de evaluación. |
| En evaluación | El coordinador está revisando la solicitud. |
| Asignado | La solicitud tiene un técnico responsable. |
| En atención | El técnico está trabajando en el problema. |
| En espera | La atención está detenida temporalmente, por ejemplo, por falta de información. |
| Resuelto | El técnico registró una solución y está pendiente de revisión o cierre por el coordinador. |
| Cerrado | La solicitud terminó su ciclo de atención y no admite modificaciones. |

### 8.1 Transiciones permitidas

| Estado actual | Estado siguiente | Responsable |
|---|---|---|
| Registrado | En evaluación | Coordinador |
| Registrado | Cerrado (cancelación) | Solicitante |
| En evaluación | Asignado | Coordinador |
| En evaluación | Cerrado (cancelación) | Solicitante |
| En evaluación | Cerrado (cierre administrativo) | Coordinador |
| Asignado | En atención | Técnico asignado |
| En atención | En espera | Técnico asignado |
| En espera | En atención | Técnico asignado |
| En atención | Resuelto | Técnico asignado |
| En espera | Resuelto | Técnico asignado |
| Resuelto | Cerrado | Coordinador |

Las transiciones no incluidas en esta tabla no estarán permitidas.

### 8.2 Tipos de cierre

El sistema deberá diferenciar, como mínimo:

- **Solución:** la solicitud fue atendida y el problema fue resuelto.
- **Cancelación:** el solicitante decidió cancelar la solicitud antes de su atención técnica.

Cuando el coordinador realice un cierre administrativo, deberá registrar el motivo correspondiente. El tipo y motivo del cierre deberán quedar almacenados para su consulta y análisis.

## 9. Modelo de comunicación

La comunicación se realizará principalmente dentro de la plataforma.

### 9.1 Participantes

Podrán participar en la conversación:

- El solicitante propietario de la solicitud.
- El técnico actualmente asignado.
- El coordinador.

Un técnico que no esté asignado no podrá consultar ni participar en la conversación.

### 9.2 Funcionamiento

- Cada solicitud tendrá una conversación independiente.
- Los mensajes se almacenarán y podrán consultarse posteriormente.
- El solicitante podrá enviar mensajes durante toda la atención de una solicitud abierta.
- El estado `En espera` no impedirá el envío de mensajes.
- Enviar un mensaje no modificará automáticamente el estado.
- Una solicitud cerrada conservará su conversación para consulta, pero no permitirá nuevos mensajes.

### 9.3 Comunicación técnica

La primera versión utilizará solicitudes HTTP mediante una API REST para enviar y consultar mensajes.

No se implementará comunicación en tiempo real mediante WebSockets en esta versión.

La actualización de los mensajes podrá realizarse mediante nuevas consultas a la API. La comunicación en tiempo real se considera una mejora futura.

### 9.4 Notificaciones por correo

El correo electrónico se utilizará para notificar eventos relacionados con las solicitudes cuando el usuario haya seleccionado ese medio de contacto.

Las respuestas a los correos no se incorporarán automáticamente a la conversación de la plataforma.

## 10. Requisitos no funcionales

### 10.1 Usabilidad

**RNF-01.** La interfaz debe ser clara, intuitiva y fácil de utilizar para los tres roles.

**RNF-02.** La plataforma debe presentar las opciones de acuerdo con el rol del usuario.

**RNF-03.** Los formularios deben mostrar mensajes claros cuando existan errores o falten datos obligatorios.

### 10.2 Seguridad

**RNF-04.** Las contraseñas deberán almacenarse mediante mecanismos seguros de hash, nunca en texto plano.

**RNF-05.** Las rutas y operaciones protegidas deberán validar la autenticación y los permisos del usuario.

**RNF-06.** El sistema deberá impedir el acceso no autorizado a solicitudes, mensajes, intervenciones y archivos adjuntos.

**RNF-07.** Los datos sensibles y las credenciales de conexión deberán mantenerse fuera del código fuente y gestionarse mediante variables de entorno o mecanismos seguros equivalentes.

### 10.3 Rendimiento y disponibilidad

**RNF-08.** Las consultas de solicitudes deberán permitir paginación para evitar cargar grandes cantidades de registros en una sola petición.

**RNF-09.** Las operaciones habituales deberán responder en un tiempo razonable bajo las condiciones normales de uso previstas para el proyecto.

**RNF-10.** La plataforma deberá contar con una estructura que permita mantener y ampliar sus funcionalidades.

### 10.4 Compatibilidad y arquitectura

**RNF-11.** La plataforma deberá funcionar en navegadores web modernos y adaptarse a diferentes tamaños de pantalla.

**RNF-12.** El backend deberá desarrollarse utilizando Python y FastAPI.

**RNF-13.** La solución deberá separar la interfaz, la lógica de negocio y la persistencia de datos para facilitar el mantenimiento y las pruebas.

## 11. Supuestos y restricciones

### 11.1 Supuestos

**S-01.** Los usuarios tendrán acceso a un navegador web y conexión a internet.

**S-02.** El coordinador será responsable de crear las cuentas de los usuarios.

**S-03.** Los usuarios tendrán un rol asignado antes de utilizar la plataforma.

**S-04.** Los solicitantes podrán ingresar a la plataforma para registrar y consultar sus solicitudes.

**S-05.** Los técnicos atenderán únicamente las solicitudes que les hayan sido asignadas.

**S-06.** El coordinador supervisará el proceso general de atención.

**S-07.** Los usuarios proporcionarán información de contacto válida cuando corresponda.

**S-08.** El correo electrónico se utilizará como medio de notificación cuando haya sido seleccionado por el usuario.

**S-09.** Los usuarios utilizarán la plataforma para enviar y consultar los mensajes relacionados con sus solicitudes.

**S-10.** Los archivos adjuntos serán imágenes PNG o JPG que no superen los 5 MB por archivo.

### 11.2 Restricciones

**S-11.** El backend se desarrollará con FastAPI.

**S-12.** La base de datos será PostgreSQL mediante Supabase.

**S-13.** La primera versión utilizará una API REST para la comunicación entre el frontend y el backend.

**S-14.** La primera versión no implementará chat en tiempo real mediante WebSockets.

**S-15.** Las solicitudes cerradas no podrán reabrirse ni modificarse.

**S-16.** La primera versión será una aplicación web y no una aplicación móvil nativa.

## 12. Criterios generales de aceptación

El sistema se considerará funcionalmente aceptable cuando se verifique que:

1. Un usuario puede iniciar sesión y acceder únicamente a las funciones correspondientes a su rol.
2. El coordinador puede crear y administrar las cuentas.
3. Un solicitante puede registrar una solicitud y consultar su información.
4. El coordinador puede evaluar, priorizar y asignar solicitudes.
5. Un técnico puede consultar y atender las solicitudes que tiene asignadas.
6. El coordinador puede reasignar solicitudes y el técnico anterior pierde el acceso operativo.
7. El técnico puede registrar intervenciones y documentar soluciones.
8. El solicitante puede comunicarse con el personal autorizado mientras la solicitud esté abierta, incluso en estado `En espera`.
9. Los mensajes no producen cambios automáticos de estado.
10. Los archivos que no cumplan los formatos o límites establecidos son rechazados.
11. El solicitante puede cancelar una solicitud en los estados permitidos.
12. El coordinador puede revisar y cerrar una solicitud.
13. Una solicitud cerrada no admite nuevas modificaciones, mensajes ni intervenciones.
14. Las solicitudes cerradas conservan su información, conversación e historial para consulta autorizada.
15. Los cambios importantes quedan registrados en el historial.
16. Las notificaciones por correo se generan cuando corresponda según el medio de contacto seleccionado.

## 13. Matriz inicial de trazabilidad

La siguiente matriz relaciona las necesidades principales con los requisitos que permitirán implementarlas y verificarlas.

| Necesidad | Requisitos relacionados | Criterio de verificación |
|---|---|---|
| Acceso seguro a la plataforma | RF-01, RF-02, RF-03, RF-04, RNF-04 a RNF-07 | Pruebas de autenticación y permisos |
| Gestión de usuarios | RF-03, RF-05 | Pruebas de creación, modificación y desactivación |
| Registro de solicitudes | RF-06, RF-08 | Prueba de creación y carga de adjuntos |
| Consulta de solicitudes | RF-07, RF-13 | Pruebas de acceso según rol |
| Evaluación y clasificación | RF-09, RF-10 | Pruebas de evaluación y prioridad |
| Asignación y reasignación | RF-11, RF-12 | Pruebas de asignación y permisos posteriores |
| Gestión de estados | RF-14, RF-15, RN-18 a RN-23 | Pruebas de transiciones permitidas y rechazadas |
| Atención técnica | RF-16, RF-17, RF-18, RF-19, RF-21 | Pruebas de intervenciones y visibilidad |
| Cierre de solicitudes | RF-20, RN-19 a RN-23 | Pruebas de cierre y bloqueo de modificaciones |
| Comunicación | RF-22, RF-23, RF-26 | Pruebas de envío, consulta y permisos |
| Adjuntos en comunicación | RF-24, RF-25, RN-28 | Pruebas de formato y tamaño |
| Notificaciones | RF-27, RN-29 | Pruebas de envío según medio de contacto |
| Seguimiento y auditoría | RF-28, RN-13, RN-30 | Pruebas de registro del historial |
| Estadísticas | RF-28 | Pruebas de consulta de indicadores |
| Usabilidad y compatibilidad | RNF-01 a RNF-03, RNF-11 | Pruebas de interfaz y navegadores |
| Rendimiento y mantenimiento | RNF-08 a RNF-10, RNF-13 | Pruebas de consultas y revisión técnica |
| Arquitectura | RNF-12, RNF-13 | Verificación de tecnologías y separación de componentes |

La matriz se actualizará durante el desarrollo para relacionar cada requisito con los módulos implementados y los casos de prueba correspondientes.

## 14. Control de cambios

| Versión | Descripción |
|---|---|
| 1.0 | Primera organización de los requisitos del proyecto. |
| 1.1 | Ampliación de requisitos funcionales, reglas de negocio, estados y comunicación. |
| 1.2 | Unificación de reglas de adjuntos, permisos de conversación, cancelación, reasignación, cierre de solicitudes y comunicación sin tiempo real en la primera versión. |

---

**Fin del documento.**