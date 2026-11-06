# Documento de requisitos — SoporteTI

**Versión:** 1.3  
**Estado:** Requisitos revisados para iniciar el desarrollo  
**Proyecto:** SoporteTI  
**Asignatura:** Aplicaciones y Servicios Web  
**Institución:** Instituto Tecnológico Metropolitano (ITM)

---

## 1. Descripción del proyecto

SoporteTI es una plataforma web destinada a gestionar solicitudes de soporte técnico dentro de una organización. Su propósito es centralizar la recepción, clasificación, asignación, atención y seguimiento de los problemas reportados por los usuarios.

La plataforma permitirá que los solicitantes registren problemas relacionados con sus equipos o servicios, consulten el estado de sus solicitudes y se comuniquen con el personal de soporte. Los técnicos podrán atender los casos asignados, documentar las intervenciones y solicitar información adicional cuando sea necesario. El coordinador administrará los usuarios, evaluará las solicitudes, asignará responsables y supervisará el proceso de atención.

## 2. Objetivo general

Desarrollar una plataforma web que permita gestionar de manera organizada y trazable las solicitudes de soporte técnico, facilitando la comunicación entre solicitantes, técnicos y coordinadores, y manteniendo un registro de las actividades realizadas durante la atención.

## 3. Alcance del proyecto

La primera versión de SoporteTI incluirá:

- Inicio y cierre de sesión.
- Administración de cuentas por parte del coordinador.
- Acceso diferenciado según los roles de solicitante, técnico y coordinador.
- Registro de solicitudes de soporte con información del solicitante y del equipo.
- Clasificación por tipo, categoría y prioridad.
- Asignación y reasignación de técnicos.
- Gestión de estados de las solicitudes.
- Registro de intervenciones técnicas.
- Registro de soluciones y revisión por parte del coordinador.
- Solicitud y respuesta de información adicional.
- Comunicación mediante mensajes asociados a cada solicitud.
- Adjuntos de imágenes.
- Historial de cambios y seguimiento.
- Consulta de estadísticas básicas por parte del coordinador.

### 3.1 Fuera del alcance inicial

La primera versión no incluirá:

- Registro público de usuarios.
- Aplicación móvil nativa.
- Chat en tiempo real mediante WebSockets.
- Recepción y procesamiento automático de respuestas enviadas al correo electrónico.
- Integraciones con sistemas externos de gestión empresarial.
- Gestión de inventario de equipos o repuestos.
- Diagnósticos automáticos mediante inteligencia artificial.
- Reapertura de solicitudes cerradas.
- Conversión y optimización avanzada de imágenes antes de almacenarlas.

Estas funcionalidades podrán evaluarse como mejoras posteriores, siempre que no afecten el cumplimiento de los criterios de aceptación principales.

## 4. Levantamiento de información

El levantamiento de información se realizó mediante una conversación con el docente de la asignatura, con el propósito de identificar las necesidades del sistema, los participantes, el proceso de atención y las funcionalidades esperadas.

Las evidencias disponibles de esta conversación se encuentran en `evidencias/entrevista/`.

A partir de la información recopilada, el equipo organizó los requisitos funcionales, las reglas de negocio y los requisitos no funcionales de la plataforma.

Para mantener la trazabilidad del levantamiento:

- Las necesidades expresadas o confirmadas por el docente deben respaldarse con las evidencias de la conversación.
- Las decisiones de implementación y organización que haya tomado el equipo deben identificarse como decisiones internas del proyecto.
- No se considerará una decisión confirmada por el docente si no existe evidencia que la respalde.

## 5. Actores del sistema

La plataforma contará con tres roles principales.

### 5.1 Solicitante

Es la persona que necesita asistencia técnica.

Puede:

- Iniciar sesión.
- Crear solicitudes de soporte.
- Consultar sus propias solicitudes.
- Consultar el estado y el historial de sus solicitudes.
- Enviar mensajes durante la atención de una solicitud abierta.
- Consultar las respuestas del personal de soporte.
- Responder solicitudes de información adicional.
- Adjuntar imágenes.
- Cancelar solicitudes en los estados permitidos.

No puede asignar técnicos, modificar prioridades ni cerrar solicitudes por solución o por causas administrativas.

### 5.2 Técnico

Es la persona encargada de atender los problemas asignados.

Puede:

- Consultar las solicitudes que tiene asignadas.
- Consultar la información de cada solicitud asignada.
- Registrar intervenciones técnicas.
- Cambiar el estado de una solicitud asignada cuando la transición esté permitida.
- Solicitar información adicional al solicitante.
- Consultar y participar en la comunicación de sus solicitudes asignadas.
- Registrar diagnósticos y soluciones.
- Consultar el historial de atención de sus solicitudes asignadas.

No puede crear usuarios, asignar o reasignar solicitudes, modificar prioridades ni cerrar solicitudes.

### 5.3 Coordinador

Es el responsable de administrar y supervisar el sistema.

Puede:

- Consultar todas las solicitudes.
- Crear, modificar y desactivar cuentas de usuario.
- Gestionar categorías.
- Evaluar solicitudes.
- Establecer prioridades.
- Asignar y reasignar técnicos.
- Supervisar las intervenciones.
- Participar en las conversaciones.
- Revisar las soluciones registradas.
- Cerrar solicitudes.
- Consultar estadísticas e informes básicos.
- Consultar el historial completo de las solicitudes.

## 6. Requisitos funcionales

### Convenciones de prioridad

Los requisitos funcionales se clasifican según su importancia para la primera versión:

- **A — Alta:** necesario para cumplir los flujos principales y los criterios de aceptación.
- **M — Media:** funcionalidad complementaria que permite completar adecuadamente la operación del sistema.
- **B — Baja:** funcionalidad que puede aplazarse si el tiempo de desarrollo es insuficiente.

### 6.1 Autenticación y usuarios

**RF-01. Inicio de sesión**  
**Prioridad:** A

El sistema debe permitir que los usuarios registrados inicien sesión mediante sus credenciales.

**Criterio de aceptación:** Dado un usuario registrado, cuando ingrese credenciales válidas, el sistema permitirá el acceso y mostrará las opciones correspondientes a su rol. Si las credenciales son incorrectas, rechazará el acceso e informará el error.

**RF-02. Control de acceso por roles**  
**Prioridad:** A

El sistema debe restringir las funcionalidades y la información de acuerdo con el rol del usuario autenticado: solicitante, técnico o coordinador.

**Criterio de aceptación:** Dado un usuario autenticado, cuando intente acceder a una funcionalidad no autorizada para su rol, el sistema deberá impedir la operación, tanto desde la interfaz como desde el backend.

**RF-03. Administración de usuarios**  
**Prioridad:** A

El sistema debe permitir al coordinador crear, consultar, modificar y desactivar cuentas de solicitantes, técnicos y coordinadores.

No existirá un mecanismo de registro público.

**Criterio de aceptación:** Dado un coordinador autenticado, cuando cree una cuenta con información válida y un rol permitido, el sistema deberá registrarla. Un usuario sin permisos de coordinación no podrá realizar esta operación.

**RF-04. Recuperación y cambio de contraseña**  
**Prioridad:** M

El sistema debe proporcionar un mecanismo para cambiar la contraseña de una cuenta y recuperar el acceso mediante un procedimiento de verificación.

**Criterio de aceptación:** Dado un usuario autorizado para cambiar su contraseña, cuando proporcione los datos requeridos y una nueva contraseña válida, el sistema deberá actualizarla y permitir el acceso con la nueva credencial.

**RF-05. Gestión de datos de contacto**  
**Prioridad:** M

El sistema debe permitir almacenar y actualizar los datos de contacto de los usuarios, incluyendo nombre, medio de contacto preferido y la información necesaria para utilizarlo.

Los medios de contacto contemplados inicialmente serán correo electrónico y teléfono.

**Criterio de aceptación:** Dado un usuario con acceso a sus datos de contacto, cuando registre o actualice su información, el sistema deberá conservarla y permitir consultarla de acuerdo con los permisos correspondientes.

### 6.2 Gestión de solicitudes

**RF-06. Creación de solicitudes**  
**Prioridad:** A

El sistema debe permitir que un solicitante registre una solicitud indicando como mínimo:

- Asunto o título.
- Descripción del problema.
- Tipo de solicitud: incidente o requerimiento.
- Categoría, cuando corresponda.
- Ubicación donde se encuentra el equipo o donde ocurre el problema.
- Placa o identificador del equipo, cuando corresponda.
- Nombre del solicitante.
- Medio de contacto y dato correspondiente.
- Adjuntos opcionales de imágenes.

El sistema debe registrar automáticamente la fecha de creación, el usuario solicitante y el estado inicial.

**Criterio de aceptación:** Dado un solicitante autenticado, cuando complete los campos obligatorios y envíe el formulario, el sistema deberá crear la solicitud en estado `Registrado`, asociarla al solicitante y conservar la información proporcionada.

**RF-07. Consulta de solicitudes**  
**Prioridad:** A

El sistema debe permitir que cada solicitante consulte únicamente sus propias solicitudes.

Los técnicos podrán consultar las solicitudes que tengan asignadas y los coordinadores podrán consultar todas las solicitudes.

**Criterio de aceptación:** Dado un usuario autenticado, cuando consulte las solicitudes, el sistema deberá mostrar únicamente aquellas a las que tiene acceso según su rol y relación con cada solicitud.

**RF-08. Adjuntos en solicitudes**  
**Prioridad:** M

El sistema debe permitir adjuntar imágenes a una solicitud.

Los formatos permitidos serán PNG y JPG/JPEG, con un tamaño máximo de 5 MB por archivo.

**Criterio de aceptación:** Dada una solicitud que admite adjuntos, cuando el usuario cargue una imagen válida, el sistema deberá almacenarla y asociarla a la solicitud. Si el formato o tamaño no cumple las restricciones, deberá rechazar el archivo.

**RF-09. Evaluación de solicitudes**  
**Prioridad:** A

El sistema debe permitir que el coordinador revise las solicitudes registradas, determine si requieren atención, necesitan información adicional o deben cerrarse por una causa administrativa.

**Criterio de aceptación:** Dada una solicitud pendiente de evaluación, cuando el coordinador la revise, deberá poder continuar su proceso mediante una transición permitida, solicitar información adicional o realizar un cierre administrativo con su motivo registrado.

**RF-10. Clasificación y prioridad**  
**Prioridad:** A

El sistema debe permitir que el coordinador establezca la categoría y prioridad de una solicitud.

Las prioridades iniciales serán baja, media y alta.

**Criterio de aceptación:** Dada una solicitud que puede ser clasificada, cuando el coordinador establezca una categoría y prioridad válidas, el sistema deberá guardar los cambios y registrarlos en el historial.

**RF-11. Asignación de técnicos**  
**Prioridad:** A

El sistema debe permitir que el coordinador asigne una solicitud a un técnico.

**Criterio de aceptación:** Dada una solicitud en estado `En evaluación`, cuando el coordinador seleccione un técnico y confirme la asignación, el sistema deberá asociar al técnico con la solicitud, cambiar su estado a `Asignado` y registrar la operación.

**RF-12. Reasignación de solicitudes**  
**Prioridad:** M

El sistema debe permitir que el coordinador cambie el técnico responsable de una solicitud, conservando el registro de las asignaciones anteriores.

Después de una reasignación, el técnico anterior perderá el acceso operativo a la solicitud y el nuevo técnico podrá continuar la atención.

**Criterio de aceptación:** Dada una solicitud asignada, cuando el coordinador la reasigne a otro técnico, el sistema deberá actualizar el responsable, registrar el cambio y restringir el acceso operativo del técnico anterior.

**RF-13. Consulta de solicitudes asignadas**  
**Prioridad:** A

El sistema debe permitir que el técnico consulte las solicitudes que se encuentran asignadas a su cuenta.

**Criterio de aceptación:** Dado un técnico autenticado, cuando consulte su listado de solicitudes, el sistema deberá mostrar únicamente las solicitudes que tenga asignadas actualmente.

**RF-14. Actualización del estado**  
**Prioridad:** A

El sistema debe permitir que los usuarios autorizados actualicen el estado de una solicitud de acuerdo con las transiciones permitidas.

**Criterio de aceptación:** Dada una solicitud en un estado determinado, cuando un usuario autorizado intente cambiarlo, el sistema deberá aceptar únicamente las transiciones definidas en este documento y rechazar las demás.

**RF-15. Cancelación de solicitudes**  
**Prioridad:** M

El sistema debe permitir que el solicitante cancele una solicitud cuando se encuentre en estado `Registrado` o `En evaluación`.

La cancelación cambiará el estado a `Cerrado` y registrará el tipo de cierre `Cancelación`, junto con el responsable, la fecha y el motivo.

**Criterio de aceptación:** Dada una solicitud propia en estado `Registrado` o `En evaluación`, cuando el solicitante confirme su cancelación e indique el motivo, el sistema deberá cerrarla y registrar la operación. En otros estados, la cancelación deberá rechazarse.

### 6.3 Atención técnica

**RF-16. Registro de intervenciones**  
**Prioridad:** A

El sistema debe permitir que el técnico asignado registre las actividades realizadas durante la atención de una solicitud.

Cada intervención deberá contener una descripción y su fecha de registro.

**Criterio de aceptación:** Dada una solicitud asignada a un técnico, cuando este registre una intervención válida, el sistema deberá almacenarla asociada a la solicitud y al técnico responsable.

**RF-17. Visibilidad de intervenciones**  
**Prioridad:** M

El sistema debe permitir distinguir las intervenciones internas de las intervenciones visibles para el solicitante.

Las intervenciones internas solo podrán ser consultadas por el personal autorizado.

**Criterio de aceptación:** Dada una intervención registrada como interna, cuando el solicitante consulte la solicitud, el sistema no deberá mostrarla. Las intervenciones marcadas como visibles sí podrán consultarse según los permisos.

**RF-18. Solicitud de información adicional**  
**Prioridad:** A

El sistema debe permitir que el técnico asignado solicite información adicional al solicitante cuando sea necesaria para continuar la atención.

La solicitud de información deberá incluir un mensaje que indique claramente qué información se necesita. El solicitante podrá consultar la petición y enviar una respuesta desde la plataforma.

Cuando la atención quede pendiente de esa respuesta, la solicitud podrá pasar a estado `En espera`.

El coordinador también podrá solicitar información adicional durante la evaluación o supervisión de una solicitud.

**Criterio de aceptación:** Dada una solicitud abierta, cuando el técnico asignado o el coordinador solicite información, el sistema deberá registrar la petición y permitir que el solicitante la consulte y responda. La respuesta deberá quedar asociada a la solicitud y a la petición correspondiente.

**RF-19. Registro de solución**  
**Prioridad:** A

El sistema debe permitir que el técnico registre la solución aplicada a una solicitud, incluyendo una descripción de las acciones realizadas y el resultado obtenido.

**Criterio de aceptación:** Dada una solicitud en atención o en espera, cuando el técnico asignado registre una solución válida, el sistema deberá conservarla y permitir que la solicitud pase a estado `Resuelto`, según las transiciones permitidas.

**RF-20. Revisión y cierre de solicitudes**  
**Prioridad:** A

El sistema debe permitir que el coordinador revise la atención realizada y cierre la solicitud cuando corresponda.

El cierre deberá registrar el tipo de cierre, el motivo cuando aplique, el responsable y la fecha.

**Criterio de aceptación:** Dada una solicitud resuelta, cuando el coordinador confirme el cierre, el sistema deberá cambiarla a `Cerrado` y registrar el tipo de cierre `Solución`. Si se realiza un cierre administrativo, deberá registrar el tipo y su motivo.

**RF-21. Consulta de intervenciones**  
**Prioridad:** M

El sistema debe permitir consultar las intervenciones relacionadas con una solicitud, respetando las reglas de visibilidad y los permisos de cada rol.

**Criterio de aceptación:** Dado un usuario autorizado, cuando consulte las intervenciones de una solicitud, el sistema deberá mostrar únicamente los registros que puede consultar según su rol y la visibilidad de cada intervención.

### 6.4 Comunicación y seguimiento

**RF-22. Conversación asociada a solicitudes**  
**Prioridad:** A

El sistema debe disponer de un espacio de comunicación asociado a cada solicitud para permitir el intercambio de mensajes entre el solicitante y el personal de soporte autorizado.

**Criterio de aceptación:** Dada una solicitud abierta, cuando un participante autorizado acceda a su conversación, el sistema deberá mostrar los mensajes asociados a esa solicitud y permitir la comunicación según sus permisos.

**RF-23. Envío y consulta de mensajes**  
**Prioridad:** A

El sistema debe permitir que el solicitante, el técnico asignado y el coordinador envíen y consulten mensajes relacionados con una solicitud.

El solicitante podrá comunicarse durante toda la atención de una solicitud abierta, incluso cuando se encuentre en estado `En espera`.

El envío de un mensaje no modificará automáticamente el estado de la solicitud.

Los técnicos que no estén asignados a la solicitud no podrán acceder a su conversación.

**Criterio de aceptación:** Dada una solicitud abierta, cuando un participante autorizado envíe un mensaje, el sistema deberá almacenarlo y permitir su consulta por los demás participantes autorizados. El estado de la solicitud deberá permanecer sin cambios.

**RF-24. Adjuntos en mensajes**  
**Prioridad:** B

El sistema debe permitir adjuntar imágenes a los mensajes de la conversación.

Se permitirán archivos PNG y JPG/JPEG, con un tamaño máximo de 5 MB por archivo.

**Criterio de aceptación:** Dado un mensaje que admite adjuntos, cuando el participante cargue una imagen válida, el sistema deberá asociarla al mensaje. Los archivos que incumplan las restricciones serán rechazados.

**RF-25. Adjuntos en intervenciones**  
**Prioridad:** B

El sistema debe permitir adjuntar imágenes a las intervenciones técnicas.

Se permitirán archivos PNG y JPG/JPEG, con un tamaño máximo de 5 MB por archivo.

**Criterio de aceptación:** Dada una intervención de una solicitud asignada, cuando el técnico adjunte una imagen válida, el sistema deberá almacenarla y asociarla a la intervención correspondiente.

**RF-26. Historial de conversación**  
**Prioridad:** M

El sistema debe conservar los mensajes de cada solicitud en orden cronológico para permitir consultar la comunicación realizada durante su atención.

**Criterio de aceptación:** Dada una solicitud con mensajes registrados, cuando un participante autorizado consulte la conversación, el sistema deberá presentar los mensajes en orden cronológico, conservando su autor y fecha.

**RF-27. Notificaciones**  
**Prioridad:** B

El sistema podrá generar notificaciones relacionadas con eventos relevantes de una solicitud.

Cuando el usuario haya seleccionado el correo electrónico como medio de contacto y se encuentre configurado el servicio correspondiente, el sistema podrá enviar notificaciones a ese correo.

El correo será un canal de notificación. Las respuestas y comunicaciones dentro de la solicitud se realizarán desde la plataforma.

**Criterio de aceptación:** Dado un evento para el que exista una notificación configurada y un usuario con correo válido, cuando ocurra el evento, el sistema deberá generar la notificación correspondiente. La comunicación no dependerá de recibir respuestas por correo.

**RF-28. Historial de cambios**  
**Prioridad:** A

El sistema debe mantener un historial de los cambios importantes realizados en cada solicitud, incluyendo cambios de estado, prioridad, categoría, asignación, reasignación y cierre.

Cada registro deberá incluir el usuario responsable y la fecha de la acción.

**Criterio de aceptación:** Dada una solicitud con cambios registrados, cuando un usuario autorizado consulte su historial, el sistema deberá mostrar las operaciones realizadas, el responsable y la fecha correspondiente.

**RF-29. Consulta de estadísticas**  
**Prioridad:** B

El sistema debe permitir al coordinador consultar estadísticas básicas sobre las solicitudes, incluyendo cantidades por estado, prioridad, categoría y tiempos de atención cuando exista información suficiente para calcularlos.

**Criterio de aceptación:** Dado un coordinador autenticado y solicitudes registradas, cuando consulte las estadísticas, el sistema deberá presentar resultados calculados a partir de los registros existentes. Los demás roles no podrán acceder a este módulo.

## 7. Reglas de negocio

**RN-01.** Toda persona que utilice la plataforma debe tener una cuenta creada previamente por un coordinador.

**RN-02.** No se permitirá el registro público de usuarios.

**RN-03.** Cada usuario tendrá un único rol activo dentro del sistema: solicitante, técnico o coordinador.

**RN-04.** Un solicitante solo podrá consultar y gestionar sus propias solicitudes dentro de los permisos establecidos.

**RN-05.** Un técnico solo podrá acceder operativamente a las solicitudes que tenga asignadas actualmente.

**RN-06.** El coordinador tendrá acceso general a las solicitudes y a las funciones administrativas.

**RN-07.** Toda solicitud deberá estar asociada a un solicitante.

**RN-08.** Toda solicitud nueva deberá iniciar en estado `Registrado`.

**RN-09.** El coordinador será responsable de evaluar las solicitudes registradas.

**RN-10.** La prioridad de una solicitud será establecida por el coordinador.

**RN-11.** La asignación y reasignación de técnicos será responsabilidad exclusiva del coordinador.

**RN-12.** Una solicitud en estado `Asignado`, `En atención`, `En espera` o `Resuelto` deberá conservar la relación con el técnico responsable de su atención.

**RN-13.** Toda reasignación deberá conservar el registro de la asignación anterior y de la nueva asignación.

**RN-14.** Cuando una solicitud sea reasignada, el técnico anterior perderá el acceso operativo a ella y a su conversación.

**RN-15.** El técnico asignado podrá registrar intervenciones y documentar la solución, pero no podrá cerrar la solicitud.

**RN-16.** Las intervenciones internas no podrán ser consultadas por el solicitante.

**RN-17.** Las intervenciones visibles para el solicitante podrán ser consultadas por este y por el personal autorizado.

**RN-18.** El solicitante podrá cancelar una solicitud únicamente cuando esté en estado `Registrado` o `En evaluación`.

**RN-19.** Una cancelación deberá cambiar el estado de la solicitud a `Cerrado` y registrar el tipo de cierre `Cancelación`.

**RN-20.** El coordinador será el único rol autorizado para cerrar una solicitud por solución o por una causa administrativa.

**RN-21.** Una solicitud cerrada no podrá reabrirse. Si se presenta un nuevo problema, deberá crearse una nueva solicitud.

**RN-22.** Una solicitud cerrada no permitirá nuevos mensajes, intervenciones, adjuntos ni modificaciones operativas.

**RN-23.** El historial y la conversación de una solicitud cerrada permanecerán disponibles para consulta de los usuarios autorizados.

**RN-24.** El solicitante podrá enviar mensajes mientras la solicitud esté abierta, sin importar si se encuentra en estado `En espera`.

**RN-25.** Enviar un mensaje no cambiará automáticamente el estado de la solicitud.

**RN-26.** La conversación solo estará disponible para el solicitante propietario, el técnico actualmente asignado y los coordinadores autorizados.

**RN-27.** Los técnicos que no estén asignados a una solicitud no podrán consultar sus mensajes ni sus intervenciones internas.

**RN-28.** Los archivos adjuntos deberán ser imágenes en formato PNG o JPG/JPEG y no podrán superar los 5 MB por archivo.

**RN-29.** El correo electrónico se utilizará para enviar notificaciones cuando el usuario haya seleccionado ese medio de contacto y el servicio esté disponible.

**RN-30.** Toda modificación importante de una solicitud deberá quedar registrada en el historial, incluyendo el usuario responsable y la fecha de la acción.

**RN-31.** Los mensajes, las solicitudes de información adicional y sus respuestas no modificarán automáticamente el estado de una solicitud.

**RN-32.** Cuando una solicitud esté cerrada, su conversación y su historial permanecerán disponibles únicamente para consulta autorizada.

**RN-33.** Una solicitud de información adicional deberá quedar asociada a la solicitud y conservar su autor, fecha, contenido y respuesta, cuando exista.

**RN-34.** Los tipos de cierre permitidos serán `Solución`, `Cancelación` y `Administrativo`.

**RN-35.** Todo cierre administrativo deberá incluir un motivo que justifique la finalización de la solicitud.

**RN-36.** La placa o identificador del equipo será obligatorio únicamente cuando la solicitud esté relacionada con un equipo que pueda identificarse de esa manera.

## 8. Estados de las solicitudes

Las solicitudes tendrán los siguientes estados:

| Estado | Descripción |
|---|---|
| Registrado | La solicitud fue creada y está pendiente de evaluación. |
| En evaluación | El coordinador está revisando la solicitud. |
| Asignado | La solicitud tiene un técnico responsable, pero la atención todavía no ha comenzado. |
| En atención | El técnico está trabajando en el problema. |
| En espera | La atención está detenida temporalmente, por ejemplo, porque se necesita información adicional. |
| Resuelto | El técnico registró una solución y está pendiente de revisión o cierre por el coordinador. |
| Cerrado | La solicitud terminó su ciclo de atención y no admite nuevas operaciones. |

### 8.1 Transiciones permitidas

La siguiente tabla es la referencia única para validar los cambios de estado en el sistema.

| Estado actual | Estado siguiente | Responsable | Condición |
|---|---|---|---|
| Registrado | En evaluación | Coordinador | Inicio de evaluación. |
| Registrado | Cerrado | Solicitante | Tipo de cierre: Cancelación. |
| En evaluación | Asignado | Coordinador | Debe existir un técnico asignado. |
| En evaluación | Cerrado | Solicitante | Tipo de cierre: Cancelación. |
| En evaluación | Cerrado | Coordinador | Tipo de cierre: Administrativo y motivo obligatorio. |
| Asignado | En atención | Técnico asignado | Inicio de la atención. |
| En atención | En espera | Técnico asignado | Se requiere detener temporalmente la atención. |
| En espera | En atención | Técnico asignado | Se puede continuar la atención. |
| En atención | Resuelto | Técnico asignado | Debe registrar la solución. |
| En espera | Resuelto | Técnico asignado | Debe registrar la solución. |
| Resuelto | Cerrado | Coordinador | Tipo de cierre: Solución. |

Las transiciones no incluidas en esta tabla no estarán permitidas.

Un mensaje o una respuesta a una solicitud de información adicional no provocará por sí mismo un cambio de estado. Si la solicitud debe pasar de `En espera` a `En atención`, el técnico asignado deberá realizar esa transición.

### 8.2 Tipos de cierre

El sistema deberá diferenciar los siguientes tipos:

- **Solución:** la solicitud fue atendida y el problema fue resuelto. El cierre lo realiza el coordinador después de revisar la solución registrada por el técnico.
- **Cancelación:** el solicitante decidió cancelar la solicitud cuando todavía se encontraba en `Registrado` o `En evaluación`.
- **Administrativo:** el coordinador determinó que la solicitud debe cerrarse por una causa administrativa. Debe registrarse el motivo correspondiente.

El tipo de cierre, el responsable, la fecha y el motivo cuando aplique deberán conservarse en la información de la solicitud y en su historial.

## 9. Modelo de comunicación

La comunicación se realizará principalmente dentro de la plataforma.

### 9.1 Participantes

Podrán participar en la comunicación de una solicitud:

- El solicitante propietario.
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

### 9.3 Solicitud de información adicional

El mecanismo de solicitud de información permitirá que el técnico o el coordinador indique qué información necesita para continuar o evaluar el caso.

El funcionamiento será:

1. El técnico asignado o el coordinador registra una petición de información.
2. El sistema conserva el contenido, autor y fecha de la petición.
3. El solicitante consulta la petición desde su solicitud.
4. El solicitante envía una respuesta asociada a esa petición.
5. El personal autorizado puede consultar la respuesta y continuar el proceso.

Cuando la atención técnica quede pendiente de esa información, el técnico podrá cambiar el estado a `En espera`.

Este mecanismo no requiere implementar un chat avanzado ni WebSockets. La consulta y el envío de información se realizarán mediante la API REST.

### 9.4 Comunicación técnica

La primera versión utilizará solicitudes HTTP mediante una API REST para enviar y consultar mensajes.

No se implementará comunicación en tiempo real mediante WebSockets en esta versión.

La actualización de los mensajes podrá realizarse mediante nuevas consultas a la API. La comunicación en tiempo real se considera una mejora futura.

### 9.5 Notificaciones por correo

El correo electrónico podrá utilizarse para notificar eventos relacionados con las solicitudes cuando el usuario haya seleccionado ese medio de contacto y el servicio esté configurado.

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

### 10.3 Rendimiento y mantenimiento

**RNF-08.** Las consultas de solicitudes deberán permitir paginación para evitar cargar grandes cantidades de registros en una sola petición.

**RNF-09.** El sistema deberá validar los datos en el backend antes de crear o modificar registros, y deberá utilizar operaciones transaccionales cuando una acción afecte varias entidades relacionadas.

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

**S-08.** El correo electrónico podrá utilizarse como medio de notificación cuando haya sido seleccionado por el usuario y el servicio esté configurado.

**S-09.** Los usuarios utilizarán la plataforma para enviar y consultar los mensajes relacionados con sus solicitudes.

**S-10.** Los archivos adjuntos serán imágenes PNG o JPG/JPEG que no superen los 5 MB por archivo.

**S-11.** La placa o identificador del equipo podrá no existir para solicitudes que no estén relacionadas con un equipo identificable.

### 11.2 Restricciones

**S-12.** El backend se desarrollará con FastAPI.

**S-13.** La base de datos será PostgreSQL mediante Supabase.

**S-14.** La primera versión utilizará una API REST para la comunicación entre el frontend y el backend.

**S-15.** La primera versión no implementará chat en tiempo real mediante WebSockets.

**S-16.** Las solicitudes cerradas no podrán reabrirse ni modificarse operativamente.

**S-17.** La primera versión será una aplicación web y no una aplicación móvil nativa.

**S-18.** Los archivos adjuntos deberán almacenarse con acceso restringido a los usuarios autorizados.

## 12. Criterios de aceptación del proyecto

Los siguientes criterios agrupan los flujos principales que deberán demostrarse para considerar funcional la primera versión.

### CA-01. Autenticación y permisos

Un usuario registrado puede iniciar sesión y acceder únicamente a las funcionalidades y datos correspondientes a su rol. El coordinador puede crear cuentas y administrar usuarios.

### CA-02. Registro y consulta de solicitudes

Un solicitante puede registrar una solicitud con la información requerida, incluyendo tipo, descripción, ubicación, datos de contacto y placa del equipo cuando corresponda. Puede consultar sus propias solicitudes y su estado.

### CA-03. Evaluación, clasificación y asignación

El coordinador puede evaluar solicitudes, establecer categoría y prioridad, asignar un técnico y reasignarlo cuando sea necesario. El técnico puede consultar únicamente los casos que tiene asignados.

### CA-04. Atención técnica y seguimiento

El técnico asignado puede registrar intervenciones, solicitar información adicional, consultar las respuestas del solicitante y documentar una solución. El sistema conserva los cambios y el historial de atención.

### CA-05. Resolución y cierre

El coordinador puede revisar una solicitud resuelta y cerrarla por solución. También puede realizar cierres administrativos justificados. El solicitante puede cancelar en los estados permitidos. Una solicitud cerrada no admite nuevas operaciones, pero conserva su información para consulta autorizada.

### CA-06. Consolidado del coordinador

El coordinador puede consultar las solicitudes y obtener un consolidado básico de su estado, prioridad, categoría y tiempos de atención cuando existan datos suficientes.

## 13. Pruebas funcionales previstas

Las siguientes pruebas servirán como base para documentar las 12 pruebas funcionales exigidas en la evaluación. Sus resultados, evidencias y observaciones se registrarán en `docs/pruebas.md`.

| ID | Prueba | Resultado esperado | Criterio relacionado |
|---|---|---|---|
| PF-01 | Inicio de sesión con credenciales válidas e inválidas. | Permite el acceso con credenciales válidas y rechaza las incorrectas. | CA-01 |
| PF-02 | Acceso a funcionalidades según el rol. | Cada usuario accede únicamente a las operaciones permitidas. | CA-01 |
| PF-03 | Creación de usuarios por el coordinador. | El coordinador crea cuentas con el rol correspondiente. | CA-01 |
| PF-04 | Registro de una solicitud por un solicitante. | La solicitud se crea con los datos obligatorios y estado `Registrado`. | CA-02 |
| PF-05 | Consulta de solicitudes según el rol. | El solicitante ve las propias, el técnico las asignadas y el coordinador todas. | CA-02 |
| PF-06 | Evaluación, clasificación y prioridad. | El coordinador puede evaluar y clasificar una solicitud. | CA-03 |
| PF-07 | Asignación y reasignación de técnicos. | Se actualiza el responsable y se conserva el historial de asignaciones. | CA-03 |
| PF-08 | Registro de intervención técnica. | El técnico asignado registra una intervención y se respeta su visibilidad. | CA-04 |
| PF-09 | Solicitud y respuesta de información adicional. | El técnico o coordinador solicita información y el solicitante puede responder. | CA-04 |
| PF-10 | Registro de solución y cierre. | El técnico registra la solución y el coordinador puede cerrar la solicitud. | CA-05 |
| PF-11 | Cancelación y cierre administrativo. | Se permiten los cierres según el rol, estado y motivo correspondiente. | CA-05 |
| PF-12 | Consulta del consolidado del coordinador. | Se muestran cantidades y datos agrupados según la información registrada. | CA-06 |

## 14. Trazabilidad de requisitos y criterios de aceptación

La siguiente matriz relaciona los requisitos funcionales con los criterios principales que serán evaluados.

| Requisitos funcionales | Criterio de aceptación |
|---|---|
| RF-01, RF-02, RF-03, RF-04, RF-05 | CA-01 |
| RF-06, RF-07, RF-08 | CA-02 |
| RF-09, RF-10, RF-11, RF-12, RF-13, RF-14 | CA-03 |
| RF-16, RF-17, RF-18, RF-19, RF-21, RF-22, RF-23, RF-26, RF-28 | CA-04 |
| RF-15, RF-20, RF-24, RF-25 | CA-05 |
| RF-27, RF-29 | CA-06 |

## 15. Resultado esperado

Al finalizar el desarrollo se espera contar con una plataforma web funcional que permita gestionar el ciclo de atención de solicitudes de soporte técnico.

La solución deberá ofrecer acceso diferenciado por roles, registro y seguimiento de solicitudes, asignación de técnicos, registro de intervenciones, solicitud y respuesta de información adicional, comunicación entre participantes, consulta del historial y administración general.

El coordinador podrá supervisar el proceso y consultar un consolidado básico de las solicitudes.

La plataforma deberá conservar la información y las evidencias relacionadas con cada caso, respetando los permisos de acceso y las restricciones establecidas para las solicitudes cerradas.

La arquitectura propuesta permitirá mantener separadas la interfaz, la lógica de negocio y la persistencia de datos, facilitando el mantenimiento y la evolución futura de SoporteTI.
