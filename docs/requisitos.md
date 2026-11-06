# Requisitos — Mesa de servicios de soporte tecnológico (PF-02)
 
| Campo | Valor |
|---|---|
| **Versión** | 1.0 |
| **Fecha** | 06-11-2026 |
| **Medio de levantamiento** | Conversación por chat con el docente, en rol de representante de la institución |
 
---
 
## 1. Alcance
 
Aplicación web para registrar y dar seguimiento a los casos de soporte tecnológico (incidentes y solicitudes) de una institución educativa, desde que se reportan hasta que se cierran, conservando el historial de intervenciones y el resultado comunicado al usuario.
 
**Incluido:** reporte, evaluación, asignación, atención, seguimiento, resolución, cierre, historial, consulta de resultado y consolidado para coordinación.
 
**Fuera del alcance** (según la guía y la conversación): solución técnica real de fallas, acceso remoto, monitoreo de redes, directorio institucional, envío de correo o WhatsApp, tiempos máximos de atención y alertas.
 
---
 
## 2. Registro de la conversación con el cliente
 
Las respuestas literales se conservan como capturas en `evidencias/entrevista/`.
 
| # | Tema | Respuesta del cliente (resumen) | Decisión |
|---|---|---|---|
| 1 | Participantes | Confirmó: docentes y administrativos reportan, 3 a 5 técnicos, 1 coordinador. | ✅ Confirmada |
| 2 | Datos del reporte | Además de lo propuesto: nombre, medio de contacto y descripción clara. Puede adjuntar imagen o captura. Si es sobre un equipo, indicar identificación o placa. El técnico debe poder pedir información adicional durante la atención. | ✏️ Ampliada. Ver RF-02, RF-03 y RF-09 |
| 3 | Prioridad | La asigna el coordinador (baja, media o alta) según impacto y urgencia. El usuario solo reporta. | ✅ Confirmada |
| 4 | Asignación | El coordinador asigna y puede reasignar. El técnico solo consulta y gestiona sus casos. El coordinador ve y supervisa todos. | ✅ Confirmada |
| 5 | Etapas del caso | Respondió "sí" a "¿cambiaría algo?", sin detallar qué cambiaría. | 🔧 Se adopta el flujo de la sección 5 (supuesto S-01) |
| 6 a 13 | Intervenciones, cierre, motivos, consolidado, visibilidad, evaluación y quién cierra | El docente indicó que el equipo puede decidirlos. | 🔧 Decisión del equipo (06-11-2026), reflejada en las secciones 3 a 6 |
 
---
 
## 3. Actores y permisos
 
| Actor | Ve | Puede hacer |
|---|---|---|
| **Solicitante** (docente o administrativo) | Solo sus casos, con estado, responsable, historial visible y resultado | Reportar, adjuntar imagen, responder solicitudes de información, cancelar su caso antes de que se asigne |
| **Técnico** | Solo los casos asignados a él | Registrar intervenciones, solicitar información al usuario, marcar el caso como Resuelto con su solución |
| **Coordinador** | Todos los casos y el consolidado | Evaluar, definir prioridad, asignar y reasignar, cerrar los casos resueltos, cerrar los que no proceden o están repetidos |
 
El técnico **no toma casos por su cuenta**: solo atiende los que el coordinador le asigna. El técnico **no cierra**: deja el caso Resuelto y el coordinador lo revisa y lo cierra.
 
---
 
## 4. Reglas de negocio
 
| ID | Regla |
|---|---|
| RN-01 | Todo caso tiene un solicitante, un tipo (incidente o solicitud), una categoría y un número consecutivo único. |
| RN-02 | Categorías: equipos, conectividad, software y plataformas institucionales. |
| RN-03 | La prioridad (baja, media, alta) solo la define el coordinador, y debe estar definida antes de asignar el caso. |
| RN-04 | Un caso tiene un solo técnico responsable a la vez. Cada reasignación queda en el historial. |
| RN-05 | El técnico solo puede ver y gestionar los casos que tiene asignados. El solicitante solo ve los suyos. |
| RN-06 | Los cambios de estado siguen las transiciones permitidas de la sección 5. No se puede saltar etapas. |
| RN-07 | Las intervenciones no se editan ni se eliminan. Un error se corrige agregando otra intervención. |
| RN-08 | Los casos no se eliminan. |
| RN-09 | Para dejar un caso Resuelto, el técnico indica el resultado (solucionado, duplicado o no procede) y escribe una explicación. |
| RN-10 | Solo el coordinador cierra un caso, después de ver que está Resuelto. Todo cierre queda con un motivo y una explicación. |
| RN-11 | Un caso cerrado no admite más cambios. Si el problema reaparece, se registra un caso nuevo. |
| RN-12 | El solicitante ve las intervenciones de su caso, salvo las que el técnico marque como internas. |
| RN-13 | Cuando el técnico solicita información, el caso pasa a "En espera" y vuelve a "En atención" cuando el solicitante responde. |
| RN-14 | Motivos de cierre: solucionado, duplicado, cancelado por el usuario, no procede. |
| RN-15 | El solicitante ve el resultado de su caso desde que está Resuelto y se mantiene visible al cerrarse. |
 
---
 
## 5. Estados y transiciones
 
Estados: **Registrado, En evaluación, Asignado, En atención, En espera, Resuelto, Cerrado.**
 
| Desde | Hacia | Quién |
|---|---|---|
| (nuevo) | Registrado | Solicitante |
| Registrado | En evaluación | Coordinador |
| En evaluación | Asignado | Coordinador (con prioridad definida y técnico elegido) |
| En evaluación | Cerrado (no procede o duplicado) | Coordinador |
| Registrado, En evaluación | Cerrado (cancelado por el usuario) | Solicitante |
| Asignado | En atención | Técnico |
| En atención | En espera | Técnico (al solicitar información) |
| En espera | En atención | Solicitante (al responder) o técnico |
| En atención | Resuelto | Técnico (con resultado y explicación) |
| Resuelto | Cerrado | Coordinador |
| Resuelto | En atención | Coordinador (si no acepta la solución; ver supuesto S-08) |
 
---
 
## 6. Requisitos funcionales e historias de usuario
 
Prioridad: **A** = obligatorio, **M** = importante, **B** = si hay tiempo.
 
| ID | Historia de usuario | Criterios de aceptación | CA | Prior. |
|---|---|---|---|---|
| RF-01 | Como usuario del sistema quiero identificarme para acceder solo a lo que me corresponde según mi rol. | Se entra con correo y contraseña de un usuario de prueba. Sin identificarse no se accede a ningún caso. Cada rol ve solo sus opciones. | Permisos | A |
| RF-02 | Como solicitante quiero reportar un incidente o solicitud para que el soporte lo atienda. | Campos obligatorios: nombre, medio de contacto (texto libre: correo, teléfono o extensión, sin validar formato), tipo, categoría, ubicación (texto libre: sede, bloque y salón) y descripción (mínimo 20 caracteres). Opcional: placa del equipo. Datos inválidos se rechazan con mensaje claro y no se guarda nada. El caso queda guardado en estado Registrado y se puede consultar. | CA-01 | A |
| RF-03 | Como solicitante quiero adjuntar una imagen para explicar mejor el problema. | Acepta imágenes PNG o JPG de hasta 5 MB. Otros archivos se rechazan. La imagen se ve en el detalle del caso. | CA-01 | M |
| RF-04 | Como solicitante quiero ver mis casos y su avance. | Lista solo mis casos con número, estado y responsable. El detalle muestra los datos del reporte. No puedo ver casos de otros. Un caso inexistente da error controlado. | CA-01, CA-03 | A |
| RF-05 | Como coordinador quiero evaluar los casos nuevos y definir su prioridad. | Puedo pasar un caso a En evaluación y fijar prioridad. Puedo cerrarlo como no procede o duplicado con explicación. Un técnico o solicitante no puede hacerlo. | CA-02 | A |
| RF-06 | Como coordinador quiero asignar y reasignar casos a un técnico. | No se puede asignar sin prioridad. El caso muestra el responsable. La reasignación queda en el historial. | CA-02, CA-03 | A |
| RF-07 | Como técnico quiero ver mis casos asignados. | Lista solo los casos asignados a mí. Intentar abrir un caso ajeno devuelve acceso denegado. | CA-02 | A |
| RF-08 | Como técnico quiero registrar lo que hago en un caso. | Puedo agregar intervenciones con descripción. Cada una guarda fecha, autor y caso. Puedo marcar una como interna. No se pueden editar ni borrar. | CA-02, CA-04 | A |
| RF-09 | Como técnico quiero pedir información adicional al solicitante. | La solicitud pasa el caso a En espera. El solicitante ve la solicitud y puede responder. Al responder, el caso vuelve a En atención. Ambos mensajes quedan en el historial. | CA-02, CA-04 | M |
| RF-10 | Como solicitante, técnico o coordinador quiero ver el historial de un caso. | Las intervenciones salen en orden cronológico con autor y fecha. El solicitante no ve las internas. | CA-04 | A |
| RF-11 | Como técnico quiero dejar un caso Resuelto con su resultado. | Exige resultado (solucionado, duplicado o no procede) y explicación. Solo el técnico responsable puede hacerlo. El caso pasa a Resuelto. | CA-02, CA-05 | A |
| RF-12 | Como coordinador quiero cerrar los casos resueltos después de revisarlos. | Solo se cierra un caso en estado Resuelto. Queda con motivo y explicación. Un caso cerrado no admite más cambios. Un técnico no puede cerrar. | CA-02, CA-05 | A |
| RF-13 | Como solicitante quiero ver el resultado de mi caso. | El detalle de un caso Resuelto o Cerrado muestra el resultado, la explicación y las fechas. | CA-05 | A |
| RF-14 | Como coordinador quiero un consolidado de la atención. | Muestra cantidad de casos por estado, lista de todos los casos con técnico y prioridad, y los casos sin asignar. Se puede filtrar por estado y por técnico. No lo ve un técnico ni un solicitante. | CA-06 | A |
| RF-15 | Como solicitante quiero cancelar mi caso si aún no se asignó. | Solo se permite en Registrado o En evaluación. Queda cerrado con motivo "cancelado por el usuario". | CA-01 | B |
 
---
 
## 7. Requisitos no funcionales
 
| ID | Requisito |
|---|---|
| RNF-01 | Las validaciones y los permisos se aplican en el servidor, no solo en la interfaz. |
| RNF-02 | Los errores se informan con mensajes claros y sin revelar información interna. |
| RNF-03 | La información se conserva en una base de datos con relaciones íntegras entre casos, usuarios e intervenciones. |
| RNF-04 | No se incluyen contraseñas ni credenciales reales en el repositorio. Se usan datos ficticios. |
| RNF-05 | La aplicación se instala y ejecuta siguiendo el README, con datos de prueba incluidos. |
| RNF-06 | La interfaz y los mensajes están en español y se usan desde un navegador de escritorio. |
| RNF-07 | Cada usuario tiene un rol (solicitante, técnico o coordinador) y se identifica con correo y contraseña. |
 
---
 
## 8. Supuestos
 
Decisiones del equipo que el cliente no confirmó de forma explícita.
 
| # | Supuesto | Riesgo si es incorrecto |
|---|---|---|
| S-01 | El flujo de estados de la sección 5 es válido (el docente respondió solo "sí" a la pregunta de cambios). | Cambiar estados o transiciones. |
| S-02 | El técnico deja el caso Resuelto sin aprobación previa y el coordinador lo cierra. | Agregar o quitar un paso de aprobación. |
| S-03 | El solicitante puede cancelar su caso antes de la asignación (RF-15). | Quitar una funcionalidad opcional. |
| S-04 | Las intervenciones internas no las ve el solicitante. | Cambiar la regla de visibilidad. |
| S-05 | El solicitante ve el resultado desde Resuelto, sin esperar al cierre. | Mostrarlo solo al cerrar. |
| S-06 | El coordinador puede cerrar casos que no proceden o están repetidos desde la evaluación. | Quitar un permiso. |
| S-07 | El medio de contacto es texto libre obligatorio (correo, teléfono o extensión), sin validar formato. | Agregar validaciones de formato. |
| S-08 | El coordinador puede devolver un caso Resuelto a En atención si no acepta la solución. | Quitar una transición. |