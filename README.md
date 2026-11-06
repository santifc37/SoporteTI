# SoporteTI# Requisitos — Mesa de Servicios de Soporte Tecnológico (PF-02)

**Curso:** Aplicaciones y Servicios Web  
**Institución:** ITM – Institución Universitaria  
**Versión:** 1.1  
**Fecha:** 06-11-2026  
**Proyecto:** Sistema web para la gestión de solicitudes de soporte tecnológico.

---

## 1. Descripción del problema

Actualmente, la atención de solicitudes de soporte tecnológico puede generar dificultades para llevar un control organizado de los problemas reportados, conocer quién está encargado de atenderlos, consultar su estado y conservar un historial de las actividades realizadas.

Por esta razón, se propone desarrollar una aplicación web de mesa de servicios que permita registrar, administrar, asignar, atender y hacer seguimiento a las solicitudes de soporte tecnológico de una institución.

La plataforma permitirá mantener una comunicación entre los solicitantes y el personal de soporte, conservar el historial de cada solicitud y facilitar la supervisión de los casos por parte del coordinador.

## 2. Objetivo del sistema

Desarrollar una aplicación web que centralice la gestión de solicitudes de soporte tecnológico, permitiendo a los usuarios reportar problemas, consultar su estado y comunicarse con el personal encargado de atenderlos.

El sistema también permitirá al personal técnico gestionar las solicitudes asignadas y al coordinador administrar los usuarios, asignaciones, prioridades y cierres.

## 3. Alcance del proyecto

### 3.1. Funcionalidades incluidas

El sistema permitirá:

- Iniciar sesión según el rol asignado.
- Administrar las cuentas de los usuarios.
- Registrar solicitudes de soporte tecnológico.
- Adjuntar imágenes y archivos como evidencia.
- Clasificar y evaluar las solicitudes.
- Asignar y reasignar técnicos.
- Establecer prioridades.
- Consultar el estado de las solicitudes.
- Gestionar la atención y resolución de los casos.
- Mantener conversaciones entre solicitantes y personal de soporte.
- Registrar intervenciones técnicas internas.
- Conservar el historial de cambios y actividades.
- Consultar los resultados de las solicitudes.
- Cerrar solicitudes mediante autorización del coordinador.
- Consultar estadísticas y un tablero de seguimiento.
- Enviar notificaciones por correo electrónico cuando corresponda al medio de contacto seleccionado.

### 3.2. Funcionalidades fuera del alcance

No se contempla inicialmente:

- Ejecutar directamente las reparaciones o soluciones técnicas.
- Acceder remotamente a los equipos de los usuarios.
- Monitorear automáticamente redes o dispositivos.
- Integrarse con directorios institucionales.
- Integrar WhatsApp u otras plataformas externas de mensajería.
- Implementar acuerdos de niveles de servicio (SLA).
- Implementar alertas automáticas de incumplimiento de tiempos de atención.
- Permitir el registro público de usuarios sin intervención del coordinador.
- Reabrir solicitudes que ya hayan sido cerradas.
- Procesar respuestas de correo electrónico para incorporarlas automáticamente a las conversaciones de la plataforma.

---

## 4. Levantamiento de información

### 4.1. Técnica utilizada

Se realizó una entrevista mediante chat con el docente, quien asumió el papel de representante institucional para identificar las necesidades de una mesa de servicios de soporte tecnológico.

La información obtenida permitió identificar los actores, las funcionalidades principales, las reglas de negocio y el flujo de atención de las solicitudes.

### 4.2. Hallazgos de la entrevista

A partir de la entrevista se identificaron los siguientes aspectos:

1. **Actores:** se identificaron solicitantes (personal docente y administrativo), entre tres y cinco técnicos y un coordinador.
2. **Información de las solicitudes:** se determinó que deben incluir el nombre del solicitante, medio de contacto, descripción del problema, evidencia opcional y un identificador del equipo cuando corresponda.
3. **Prioridades:** el coordinador será responsable de establecer la prioridad según el impacto y la urgencia.
4. **Asignaciones:** el coordinador asignará y podrá reasignar los casos. Los técnicos solamente podrán gestionar las solicitudes que tengan asignadas.
5. **Estados:** se estableció un flujo de estados para controlar el ciclo de vida de las solicitudes.
6. **Intervenciones:** se requiere conservar un registro de las actividades realizadas por el personal técnico.
7. **Resolución:** el técnico registrará el resultado de la atención y la explicación de la solución.
8. **Cierre:** el coordinador será responsable de revisar y cerrar las solicitudes resueltas.
9. **Historial:** se conservará el historial de las solicitudes y sus actividades.
10. **Comunicación:** se incorporará un mecanismo de comunicación entre el solicitante y el personal de soporte.
11. **Visibilidad:** se diferenciará la información que puede consultar el solicitante de las notas internas del personal de soporte.
12. **Tablero:** el coordinador tendrá una vista general para supervisar las solicitudes.
13. **Evaluación:** se contemplará la consulta del resultado de la atención por parte del solicitante.

Cuando una decisión no quedó definida expresamente durante la entrevista, se documentó como una decisión de diseño o supuesto pendiente de validación.

---

## 5. Actores del sistema

El sistema contará con tres roles principales.

### 5.1. Solicitante

Es el usuario que necesita asistencia tecnológica y registra solicitudes en la plataforma.

Podrá:

- Iniciar sesión con las credenciales creadas por el coordinador.
- Registrar nuevas solicitudes.
- Adjuntar imágenes y archivos permitidos.
- Consultar únicamente sus propias solicitudes.
- Consultar el estado de cada solicitud.
- Consultar el técnico asignado, cuando exista.
- Enviar y recibir mensajes durante todo el período de atención de una solicitud abierta.
- Responder solicitudes de información realizadas por el técnico.
- Consultar el historial de conversaciones.
- Consultar el resultado de la atención.
- Cancelar una solicitud cuando se encuentre en los estados permitidos.
- Consultar las solicitudes cerradas sin modificarlas.

No podrá:

- Asignar técnicos.
- Modificar prioridades.
- Consultar solicitudes de otros usuarios.
- Consultar intervenciones internas.
- Modificar solicitudes cerradas.
- Enviar nuevos mensajes en solicitudes cerradas.

### 5.2. Técnico

Es el encargado de atender las solicitudes que le sean asignadas.

Podrá:

- Iniciar sesión.
- Consultar las solicitudes que tenga asignadas.
- Consultar la información de cada solicitud asignada.
- Comunicarse con el solicitante mediante la conversación de la solicitud.
- Solicitar información adicional.
- Registrar intervenciones técnicas.
- Agregar notas internas.
- Consultar el historial de atención.
- Cambiar los estados permitidos según el flujo definido.
- Registrar la resolución y su explicación.

No podrá:

- Asignarse solicitudes a sí mismo.
- Asignar solicitudes a otros técnicos.
- Modificar la prioridad establecida por el coordinador.
- Consultar solicitudes que no tenga asignadas.
- Cerrar solicitudes.
- Modificar o eliminar intervenciones ya registradas.

### 5.3. Coordinador

Es el responsable de administrar y supervisar el funcionamiento de la mesa de servicios.

Podrá:

- Iniciar sesión.
- Crear cuentas de solicitantes, técnicos y otros coordinadores, según los roles autorizados.
- Modificar y desactivar cuentas.
- Asignar roles a los usuarios.
- Consultar todas las solicitudes.
- Evaluar solicitudes.
- Establecer prioridades.
- Asignar y reasignar técnicos.
- Consultar las conversaciones de las solicitudes.
- Consultar intervenciones internas.
- Supervisar el historial de atención.
- Cerrar solicitudes resueltas.
- Cerrar solicitudes que no procedan o sean duplicadas, según las reglas establecidas.
- Consultar estadísticas y el tablero general.
- Filtrar solicitudes por diferentes criterios.

El coordinador será el único rol autorizado para realizar asignaciones, establecer prioridades y cerrar solicitudes.

---

## 6. Requisitos funcionales

### RF-01. Inicio de sesión y control de acceso

El sistema permitirá que los usuarios ingresen mediante correo electrónico y contraseña.

El acceso estará condicionado por el rol asignado: solicitante, técnico o coordinador.

El sistema deberá restringir las funcionalidades y la información según los permisos de cada rol.

Las cuentas serán creadas y administradas por el coordinador. No existirá un registro público de usuarios.

### RF-02. Registro de solicitudes

El sistema permitirá que los solicitantes registren nuevas solicitudes de soporte tecnológico.

El formulario deberá incluir:

- Nombre del solicitante.
- Medio de contacto seleccionado.
- Información de contacto correspondiente al medio seleccionado.
- Tipo de solicitud.
- Categoría.
- Sede o ubicación donde ocurre el problema.
- Descripción del problema.
- Identificador o placa del equipo, cuando corresponda.
- Evidencia opcional mediante archivos adjuntos.

La descripción deberá tener una extensión mínima de 20 caracteres.

El sistema validará los campos obligatorios y rechazará la información que no cumpla las condiciones establecidas.

Al registrar correctamente una solicitud, se generará un número único y consecutivo y su estado inicial será `Registrado`.

La fecha y hora de creación serán generadas automáticamente.

### RF-03. Adjuntar evidencias

El sistema permitirá adjuntar imágenes como evidencia de una solicitud.

Inicialmente se admitirán archivos PNG y JPG con un tamaño máximo de 5 MB por archivo.

El sistema validará el formato y el tamaño antes de aceptar los archivos.

Las evidencias podrán consultarse desde el detalle de la solicitud, respetando los permisos de cada rol.

### RF-04. Consulta de solicitudes por el solicitante

El sistema permitirá al solicitante consultar un listado de sus propias solicitudes.

Podrá acceder al detalle de cada caso y consultar:

- Número de solicitud.
- Fecha de creación.
- Tipo y categoría.
- Descripción.
- Estado actual.
- Prioridad, cuando haya sido establecida.
- Técnico asignado, cuando exista.
- Conversación asociada.
- Historial visible.
- Resultado de la atención, cuando esté disponible.

El sistema impedirá consultar solicitudes pertenecientes a otros usuarios.

### RF-05. Evaluación y priorización

El sistema permitirá al coordinador evaluar las solicitudes registradas y establecer su prioridad.

Se utilizarán tres niveles:

- **Baja:** el problema afecta a un usuario y existe una alternativa para continuar las actividades.
- **Media:** el problema afecta a varios usuarios o dificulta actividades importantes.
- **Alta:** el problema interrumpe una actividad institucional importante o afecta a un número significativo de usuarios.

La prioridad deberá establecerse antes de realizar la asignación del técnico.

El coordinador también podrá cerrar solicitudes durante la evaluación cuando sean duplicadas o no procedan, registrando la justificación correspondiente.

### RF-06. Asignación y reasignación de técnicos

El sistema permitirá al coordinador asignar un técnico a una solicitud evaluada.

La asignación requerirá que la solicitud tenga una prioridad definida.

El sistema registrará:

- Técnico asignado.
- Fecha y hora de asignación.
- Usuario que realizó la asignación.

El coordinador podrá reasignar una solicitud a otro técnico.

Toda reasignación deberá registrar el técnico anterior, el nuevo técnico, la fecha, la hora y el motivo.

El técnico asignado podrá consultar la solicitud desde su panel de trabajo.

### RF-07. Acceso de los técnicos a las solicitudes

El sistema permitirá que cada técnico consulte y gestione únicamente las solicitudes que tenga asignadas.

Si un técnico intenta acceder a una solicitud asignada a otro técnico, el sistema deberá denegar el acceso.

El coordinador podrá consultar todas las solicitudes, independientemente del técnico asignado.

### RF-08. Registro de intervenciones técnicas

El sistema permitirá que los técnicos registren las actividades realizadas durante la atención de una solicitud.

Cada intervención deberá contener:

- Identificador de la solicitud.
- Técnico responsable.
- Fecha y hora de registro.
- Descripción de la actividad realizada.
- Tipo de intervención.
- Visibilidad de la intervención: interna o visible para el solicitante.
- Archivos adjuntos opcionales, cuando corresponda.

Las intervenciones registradas no podrán modificarse ni eliminarse.

Cuando exista un error, deberá agregarse una nueva intervención que documente la corrección.

Las intervenciones internas solamente podrán ser consultadas por el personal autorizado.

### RF-09. Solicitud de información adicional

El sistema permitirá que el técnico solicite información adicional al solicitante durante la atención de un caso.

Cuando el técnico solicite información, la solicitud podrá pasar al estado `En espera`.

El solicitante podrá responder mediante la conversación asociada a la solicitud.

La respuesta del solicitante no deberá modificar automáticamente el estado del caso. El técnico podrá actualizarlo cuando corresponda.

### RF-10. Historial de solicitudes

El sistema conservará un historial cronológico de las actividades realizadas en cada solicitud.

Se registrarán, entre otros:

- Cambios de estado.
- Asignaciones.
- Reasignaciones.
- Intervenciones.
- Solicitudes de información.
- Resoluciones.
- Cierres.
- Cancelaciones.

Cada registro deberá conservar la fecha, hora y usuario responsable.

El solicitante solamente podrá consultar los registros autorizados para su rol.

### RF-11. Resolución de solicitudes

El sistema permitirá que el técnico registre la resolución de una solicitud cuando haya terminado la atención.

Para registrar la resolución será obligatorio incluir:

- Resultado de la atención.
- Explicación de la solución o motivo correspondiente.
- Fecha y hora de resolución.
- Técnico responsable.

Los resultados contemplados serán:

- Solucionado.
- Duplicado.
- No procede.

Cuando el técnico marque una solicitud como resuelta, su estado pasará a `Resuelto`.

La resolución quedará pendiente de revisión y cierre por parte del coordinador.

### RF-12. Cierre de solicitudes

El sistema permitirá que únicamente el coordinador cierre solicitudes.

Una solicitud solamente podrá cerrarse cuando se encuentre en estado `Resuelto`, salvo los cierres por duplicidad, cancelación o no procedencia permitidos durante las etapas anteriores.

El coordinador deberá registrar el motivo y la explicación del cierre.

Si el coordinador considera que la solución registrada por el técnico no es suficiente, podrá devolver la solicitud al estado `En atención`, registrando el motivo.

Una vez cerrada una solicitud:

- No podrá modificarse.
- No podrá reabrirse.
- No permitirá nuevos mensajes.
- No permitirá nuevas intervenciones.
- Su información y su historial permanecerán disponibles para consulta.

Si se presenta un nuevo problema, deberá registrarse una nueva solicitud.

### RF-13. Consulta de resultados

El sistema permitirá que el solicitante consulte el resultado de la atención cuando una solicitud se encuentre en estado `Resuelto` o `Cerrado`.

La información visible incluirá:

- Resultado de la atención.
- Explicación de la solución.
- Fecha de resolución.
- Fecha de cierre, cuando corresponda.
- Motivo del cierre, cuando corresponda.

No se mostrarán intervenciones internas ni información restringida.

### RF-14. Tablero de control del coordinador

El sistema dispondrá de un tablero para que el coordinador supervise las solicitudes.

El tablero mostrará:

- Cantidad total de solicitudes.
- Cantidad de solicitudes por estado.
- Cantidad de solicitudes por prioridad.
- Solicitudes pendientes de asignación.
- Solicitudes asignadas por técnico.
- Solicitudes resueltas.
- Solicitudes cerradas.

El coordinador podrá filtrar las solicitudes por:

- Número de solicitud.
- Fecha.
- Estado.
- Prioridad.
- Técnico asignado.
- Categoría.

El tablero será exclusivo del coordinador.

### RF-15. Cancelación de solicitudes

El sistema permitirá que el solicitante cancele una solicitud cuando se encuentre en estado `Registrado` o `En evaluación`.

La cancelación deberá registrarse en el historial y el caso pasará a estado `Cerrado`, con el motivo `Cancelado por el usuario`.

Una solicitud que ya haya sido asignada no podrá ser cancelada directamente por el solicitante.

### RF-16. Administración de categorías

El sistema permitirá que el coordinador administre las categorías utilizadas para clasificar las solicitudes.

Las categorías iniciales serán:

- Equipos.
- Conectividad.
- Software.
- Plataformas institucionales.

El coordinador podrá administrar las categorías según las necesidades de la institución.

### RF-17. Administración de usuarios

El sistema permitirá que el coordinador cree, consulte, modifique y desactive cuentas de usuario.

Cada cuenta tendrá un rol asignado y los datos necesarios para su identificación y acceso.

El sistema no permitirá que usuarios sin autorización creen cuentas ni modifiquen los roles de otros usuarios.

Las cuentas desactivadas no podrán iniciar sesión.

### RF-18. Búsqueda y filtrado de solicitudes

El sistema permitirá buscar y filtrar solicitudes según los permisos del usuario.

Los criterios de búsqueda incluirán número de solicitud, fecha, estado, prioridad, categoría y técnico asignado, según el rol.

Los solicitantes solamente podrán buscar entre sus propias solicitudes.

### RF-19. Consulta por número de solicitud

El sistema permitirá consultar una solicitud mediante su número único.

Antes de mostrar la información, deberá verificar que el usuario tenga permisos para acceder al caso.

### RF-20. Estadísticas de gestión

El sistema permitirá al coordinador consultar estadísticas de las solicitudes por período, estado, prioridad y técnico responsable.

Las estadísticas servirán para analizar el volumen de solicitudes y el comportamiento general de la atención.

### RF-21. Registro de cambios

El sistema conservará un registro de los cambios importantes realizados sobre cada solicitud.

Se incluirán los cambios de estado, asignaciones, reasignaciones, cancelaciones, resoluciones y cierres.

Cada cambio deberá identificar al usuario responsable y la fecha y hora de realización.

### RF-22. Consulta de solicitudes cerradas

El sistema permitirá consultar las solicitudes cerradas y su información histórica.

La consulta respetará los permisos establecidos para cada rol.

Las solicitudes cerradas no podrán modificarse ni reabrirse.

### RF-23. Comunicación entre solicitante y personal de soporte

El sistema permitirá el intercambio de mensajes entre el solicitante y el personal de soporte durante todo el período de atención de una solicitud abierta.

La comunicación estará asociada al número de solicitud y permitirá que el solicitante y el técnico asignado intercambien información sin depender de que el técnico haya solicitado previamente información adicional.

El coordinador podrá consultar las conversaciones para supervisar la atención.

### RF-24. Historial de conversaciones

El sistema conservará los mensajes de cada solicitud en orden cronológico.

Cada mensaje deberá registrar:

- Identificador de la solicitud.
- Autor del mensaje.
- Contenido.
- Fecha y hora de envío.
- Archivos adjuntos, cuando corresponda.

El historial de conversación estará disponible para consulta según los permisos de cada rol.

### RF-25. Comunicación durante el estado En espera

El sistema permitirá que el solicitante y el personal de soporte intercambien mensajes incluso cuando la solicitud se encuentre en estado `En espera`.

El envío de un mensaje no modificará automáticamente el estado de la solicitud.

El técnico será responsable de actualizar el estado cuando corresponda.

### RF-26. Restricción de comunicación después del cierre

Cuando una solicitud pase al estado `Cerrado`, el sistema impedirá el envío de nuevos mensajes y la modificación de los mensajes existentes.

La conversación permanecerá disponible para consulta como parte del historial de la solicitud.

### RF-27. Notificaciones por correo electrónico

El sistema permitirá enviar notificaciones relacionadas con las solicitudes cuando el solicitante haya seleccionado el correo electrónico como medio de contacto.

Las notificaciones podrán informar sobre:

- Registro de una nueva solicitud.
- Asignación de un técnico.
- Cambios relevantes en el estado.
- Nuevos mensajes.
- Solicitudes de información.
- Resolución y cierre.

El correo electrónico funcionará como medio de notificación. La conversación y el historial completo se gestionarán dentro de la plataforma.

### RF-28. Consulta de conversaciones por el solicitante

El sistema permitirá que el solicitante consulte desde el detalle de cada solicitud los mensajes enviados y recibidos durante la atención.

No podrá consultar conversaciones pertenecientes a otros usuarios ni intervenciones internas del personal de soporte.

---

## 7. Reglas de negocio

**RN-01.** Toda solicitud deberá tener un número único y consecutivo generado automáticamente.

**RN-02.** Toda solicitud deberá estar asociada a un solicitante, un tipo y una categoría.

**RN-03.** Las categorías iniciales serán equipos, conectividad, software y plataformas institucionales.

**RN-04.** La prioridad solamente podrá ser establecida por el coordinador.

**RN-05.** Una solicitud no podrá asignarse a un técnico si no tiene prioridad definida.

**RN-06.** Cada solicitud tendrá como máximo un técnico responsable de la asignación actual.

**RN-07.** Toda asignación o reasignación deberá quedar registrada en el historial.

**RN-08.** Los solicitantes solamente podrán consultar sus propias solicitudes.

**RN-09.** Los técnicos solamente podrán consultar las solicitudes que tengan asignadas.

**RN-10.** El coordinador podrá consultar todas las solicitudes.

**RN-11.** Los cambios de estado deberán respetar el flujo definido para el sistema.

**RN-12.** Las intervenciones técnicas registradas no podrán editarse ni eliminarse. Los errores se corregirán mediante un nuevo registro.

**RN-13.** Los casos no podrán eliminarse físicamente del sistema una vez registrados. Su historial deberá conservarse.

**RN-14.** El técnico deberá registrar un resultado y una explicación antes de marcar una solicitud como resuelta.

**RN-15.** El cierre de una solicitud será responsabilidad exclusiva del coordinador, excepto que el sistema registre una cancelación realizada por el solicitante según las condiciones permitidas.

**RN-16.** Toda solicitud cerrada será inmutable y no podrá reabrirse. Si se presenta un nuevo problema, deberá crearse otra solicitud.

**RN-17.** El solicitante no podrá consultar intervenciones internas del personal de soporte.

**RN-18.** Cuando el técnico solicite información adicional, la solicitud podrá pasar a estado `En espera`.

**RN-19.** El solicitante podrá enviar mensajes durante toda la atención de una solicitud abierta, incluso cuando se encuentre en estado `En espera`.

**RN-20.** El envío de mensajes no cambiará automáticamente el estado de la solicitud.

**RN-21.** Una solicitud cerrada no permitirá nuevos mensajes, modificaciones ni intervenciones.

**RN-22.** El solicitante podrá consultar el resultado de la atención cuando la solicitud se encuentre en estado `Resuelto` o `Cerrado`.

**RN-23.** El coordinador será responsable de crear las cuentas y asignar los roles de los usuarios.

**RN-24.** Las cuentas desactivadas no podrán iniciar sesión.

**RN-25.** El medio de contacto seleccionado determinará qué información de contacto será obligatoria.

**RN-26.** Cuando el medio de contacto seleccionado sea el correo electrónico, el sistema podrá utilizarlo para enviar notificaciones relacionadas con la solicitud.

**RN-27.** Los mensajes de conversación y las intervenciones técnicas serán registros diferentes y tendrán reglas de visibilidad independientes.

**RN-28.** Los cambios importantes de una solicitud deberán registrar el usuario responsable, la fecha y la hora.

**RN-29.** Los usuarios no podrán ejecutar operaciones que no estén autorizadas para su rol.

**RN-30.** Una solicitud que haya sido asignada no podrá ser cancelada directamente por el solicitante.

---

## 8. Estados de las solicitudes

El sistema manejará los siguientes estados:

| Estado | Descripción |
|---|---|
| Registrado | La solicitud fue creada y está pendiente de evaluación. |
| En evaluación | El coordinador está revisando el caso y definiendo su prioridad. |
| Asignado | La solicitud tiene un técnico responsable. |
| En atención | El técnico está trabajando en la solicitud. |
| En espera | La atención está pendiente de información u otra condición necesaria. |
| Resuelto | El técnico registró una solución y está pendiente de revisión del coordinador. |
| Cerrado | La solicitud terminó su ciclo de atención y no admite modificaciones. |

### 8.1. Transiciones permitidas

| Estado inicial | Estado final | Responsable | Condición |
|---|---|---|---|
| Nuevo | Registrado | Solicitante | Registro correcto de la solicitud. |
| Registrado | En evaluación | Coordinador | Inicio de la evaluación. |
| En evaluación | Asignado | Coordinador | Prioridad definida y técnico asignado. |
| En evaluación | Cerrado | Coordinador | Solicitud duplicada o no procedente. |
| Registrado | Cerrado | Solicitante | Cancelación permitida. |
| En evaluación | Cerrado | Solicitante | Cancelación permitida. |
| Asignado | En atención | Técnico | Inicio de la atención. |
| En atención | En espera | Técnico | Solicitud de información adicional. |
| En espera | En atención | Técnico | Reanudación de la atención. |
| En atención | Resuelto | Técnico | Registro de resultado y explicación. |
| Resuelto | Cerrado | Coordinador | Aprobación de la resolución. |
| Resuelto | En atención | Coordinador | Rechazo de la solución con justificación. |

**Nota:** `Nuevo` representa el evento previo al registro y no un estado persistente. El estado inicial almacenado será `Registrado`.

### 8.2. Condiciones adicionales de los estados

- Una solicitud en estado `En espera` podrá recibir mensajes del solicitante.
- La recepción de un mensaje no cambiará automáticamente el estado.
- El técnico decidirá cuándo reanudar la atención.
- Una solicitud en estado `Resuelto` estará pendiente de revisión del coordinador.
- Una solicitud en estado `Cerrado` no podrá reabrirse.
- Las solicitudes canceladas, duplicadas o no procedentes deberán conservar su motivo de cierre.

---

## 9. Comunicación y gestión de mensajes

### 9.1. Comunicación dentro de la plataforma

La plataforma será el medio principal para la comunicación entre solicitantes y personal de soporte.

Cada solicitud tendrá una sección de conversación desde la cual se podrán enviar y consultar mensajes.

Los mensajes estarán asociados a una solicitud específica y se mostrarán en orden cronológico.

### 9.2. Participantes de la conversación

- El solicitante podrá comunicarse con el técnico asignado.
- El técnico asignado podrá responder al solicitante.
- El coordinador podrá consultar las conversaciones de todas las solicitudes.
- Los mensajes no podrán ser consultados por usuarios que no tengan autorización.

### 9.3. Diferencia entre conversación e intervención técnica

El sistema diferenciará dos tipos de registros:

**Mensajes de conversación:**

Son comunicaciones entre el solicitante y el personal de soporte. Su finalidad es compartir información, hacer preguntas y comunicar novedades.

**Intervenciones técnicas:**

Son registros de las actividades realizadas por el técnico durante la atención. Podrán ser internas o visibles para el solicitante, según su clasificación.

Ambos registros deberán conservar su propio historial y respetar los permisos de acceso.

### 9.4. Comunicación por correo electrónico

Cuando el solicitante seleccione el correo electrónico como medio de contacto, el sistema podrá utilizarlo para enviar notificaciones.

El correo electrónico no reemplazará la conversación dentro de la plataforma.

El solicitante deberá ingresar a la plataforma para consultar el historial completo y continuar la conversación.

---

## 10. Requisitos no funcionales

### RNF-01. Seguridad y autorización

El sistema deberá validar los permisos de cada usuario en el servidor. No será suficiente ocultar opciones en la interfaz.

### RNF-02. Protección de credenciales

Las contraseñas deberán almacenarse utilizando mecanismos seguros de protección, evitando guardarlas en texto plano.

### RNF-03. Integridad de la información

La base de datos deberá mantener la integridad referencial entre usuarios, solicitudes, asignaciones, mensajes e intervenciones.

### RNF-04. Disponibilidad de la información

El sistema deberá conservar las solicitudes y sus historiales, evitando la pérdida de información durante el ciclo de atención.

### RNF-05. Compatibilidad

La aplicación deberá funcionar correctamente en versiones actuales de los navegadores Google Chrome, Microsoft Edge y Mozilla Firefox.

### RNF-06. Adaptabilidad

La interfaz deberá adaptarse a diferentes resoluciones de pantalla, incluyendo computadores, tabletas y dispositivos móviles.

### RNF-07. Usabilidad

La interfaz deberá ser clara, organizada y fácil de utilizar. Los mensajes de error deberán indicar qué ocurrió y cómo corregirlo cuando sea posible.

### RNF-08. Validación de datos

El sistema deberá validar los datos tanto en el cliente como en el servidor para evitar información incompleta o inválida.

### RNF-09. Protección de información

El sistema no deberá exponer contraseñas, tokens, credenciales ni información interna en las respuestas de la API.

### RNF-10. Rendimiento

Las operaciones principales deberán responder en un tiempo objetivo máximo de tres segundos bajo condiciones normales de uso y carga.

### RNF-11. Mantenibilidad

El código deberá organizarse en módulos y componentes que faciliten su mantenimiento y evolución.

### RNF-12. Idioma

La interfaz de usuario estará desarrollada en español.

### RNF-13. Registro de actividades

Las acciones importantes deberán quedar registradas para permitir la trazabilidad de las operaciones realizadas.

---

## 11. Supuestos y decisiones de diseño pendientes de validación

Los siguientes puntos corresponden a decisiones adoptadas para completar los aspectos que no quedaron totalmente definidos durante el levantamiento de información.

**S-01.** Se adopta el flujo de estados descrito en este documento para controlar el ciclo de vida de las solicitudes.

**S-02.** El técnico será responsable de registrar la resolución y el coordinador de revisar y cerrar la solicitud.

**S-03.** El solicitante podrá cancelar solicitudes únicamente cuando estén en estado `Registrado` o `En evaluación`.

**S-04.** Las intervenciones internas no serán visibles para los solicitantes.

**S-05.** El resultado de la atención podrá ser consultado por el solicitante desde el estado `Resuelto`.

**S-06.** El coordinador podrá cerrar solicitudes duplicadas o no procedentes durante la evaluación, registrando la justificación.

**S-07.** El medio de contacto será seleccionado por el solicitante y la información correspondiente será obligatoria según la opción elegida.

**S-08.** El coordinador podrá devolver una solicitud del estado `Resuelto` al estado `En atención` cuando rechace la solución, siempre que registre el motivo.

**S-09.** El coordinador será responsable de crear las cuentas y asignar los roles de todos los usuarios.

**S-10.** Las solicitudes cerradas no podrán reabrirse. Para un nuevo problema se deberá registrar otra solicitud.

**S-11.** La plataforma será el medio principal de comunicación entre el solicitante y el personal de soporte.

**S-12.** El solicitante podrá enviar mensajes durante toda la atención de una solicitud abierta, incluso cuando esté en estado `En espera`.

**S-13.** El envío de mensajes no cambiará automáticamente el estado de la solicitud.

**S-14.** Los mensajes de conversación, las intervenciones técnicas y el historial de cambios serán registros independientes.

**S-15.** Cuando el solicitante seleccione el correo electrónico como medio de contacto, se utilizará para las notificaciones relacionadas con su solicitud.

**S-16.** Una vez cerrada la solicitud, la conversación permanecerá disponible para consulta, pero no se podrán enviar nuevos mensajes.

---

## 12. Criterios generales de aceptación

Los siguientes criterios permitirán comprobar que las funcionalidades principales cumplen con los requisitos establecidos.

| Requisito relacionado | Criterio de aceptación |
|---|---|
| RF-01 | Un usuario podrá iniciar sesión y acceder únicamente a las funcionalidades correspondientes a su rol. |
| RF-02 | Una solicitud válida se registrará correctamente y recibirá un número único. |
| RF-03 | El sistema aceptará archivos permitidos y rechazará formatos o tamaños no autorizados. |
| RF-04 | Un solicitante podrá consultar sus solicitudes, pero no las de otros usuarios. |
| RF-05 | El coordinador podrá establecer la prioridad y el sistema impedirá asignar sin ella. |
| RF-06 | El sistema registrará las asignaciones y reasignaciones con sus responsables y motivos. |
| RF-07 | Un técnico no podrá consultar solicitudes asignadas a otros técnicos. |
| RF-08 | Las intervenciones quedarán registradas y no podrán modificarse ni eliminarse. |
| RF-09 | El técnico podrá solicitar información y el solicitante podrá responder. |
| RF-10 | El historial mostrará las actividades en orden cronológico y respetará los permisos. |
| RF-11 | El sistema impedirá resolver una solicitud sin resultado y explicación. |
| RF-12 | Un técnico no podrá cerrar solicitudes y una solicitud cerrada no podrá modificarse. |
| RF-13 | El solicitante podrá consultar el resultado de la atención. |
| RF-14 | El coordinador podrá consultar estadísticas y filtrar solicitudes. |
| RF-15 | El solicitante solamente podrá cancelar solicitudes en los estados permitidos. |
| RF-17 | El coordinador podrá crear cuentas y asignar roles. |
| RF-19 | El sistema verificará los permisos antes de mostrar una solicitud consultada por número. |
| RF-23 | El solicitante y el técnico podrán intercambiar mensajes durante toda la atención. |
| RF-25 | El solicitante podrá enviar mensajes cuando el caso esté en espera, sin cambiar automáticamente su estado. |
| RF-26 | Una solicitud cerrada no permitirá nuevos mensajes. |
| RF-27 | El sistema podrá enviar notificaciones por correo cuando corresponda al medio de contacto seleccionado. |

---

## 13. Trazabilidad de requisitos

La matriz de trazabilidad relacionará cada requisito funcional con su implementación y las pruebas correspondientes.

Se completará durante las etapas de diseño, desarrollo y pruebas del proyecto.

Como mínimo, deberá contener:

| Código | Requisito | Módulo del sistema | Prueba asociada | Estado |
|---|---|---|---|---|
| RF-01 | Inicio de sesión y roles | Autenticación | Prueba de acceso por rol | Pendiente |
| RF-02 | Registro de solicitudes | Solicitudes | Prueba de registro | Pendiente |
| RF-05 | Evaluación y prioridad | Gestión de solicitudes | Prueba de priorización | Pendiente |
| RF-06 | Asignación de técnicos | Asignaciones | Prueba de asignación | Pendiente |
| RF-08 | Intervenciones técnicas | Atención | Prueba de registro de intervención | Pendiente |
| RF-12 | Cierre de solicitudes | Gestión de solicitudes | Prueba de cierre y permisos | Pendiente |
| RF-14 | Tablero de control | Panel del coordinador | Prueba de estadísticas | Pendiente |
| RF-17 | Administración de usuarios | Usuarios | Prueba de creación de cuentas | Pendiente |
| RF-23 | Comunicación | Conversaciones | Prueba de envío y recepción de mensajes | Pendiente |
| RF-26 | Restricción después del cierre | Conversaciones | Prueba de bloqueo de mensajes | Pendiente |
| RF-27 | Notificaciones por correo | Notificaciones | Prueba de envío de correo | Pendiente |

La matriz se ampliará para incluir todos los requisitos y sus pruebas correspondientes.

---

**Fin del documento.**