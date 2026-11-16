# Matriz de trazabilidad — SoporteTI

## 1. Objetivo

Esta matriz relaciona las seis condiciones de aceptación establecidas en `proyecto2.md` con los requisitos funcionales, los componentes del sistema, las pruebas automatizadas y la evidencia de integración.

La matriz permite identificar qué funcionalidades contribuyen al cumplimiento de cada condición y qué validaciones hacen falta para demostrar el funcionamiento completo del sistema.

### 1.1. Estados utilizados

- **Implementado:** existe código correspondiente en la rama integrada.
- **Prueba automatizada:** existe un archivo de pruebas para validar el comportamiento del requisito.
- **Pendiente de evidencia funcional:** falta documentar la demostración reproducible y su evidencia.
- **Pendiente de integración:** el componente todavía no está integrado en la rama que se está evaluando.

La existencia de código o pruebas automatizadas no significa, por sí sola, que una condición de aceptación esté completamente demostrada.

## 2. Matriz de trazabilidad

| Condición de aceptación | Requisitos funcionales relacionados | Implementación (rutas principales) | Pruebas automatizadas | Estado |
|---|---|---|---|---|
| **CA-01. Reportar un incidente o solicitar soporte tecnológico.** Se debe registrar un caso de forma persistente y poder recuperarlo. | RF-01, RF-02, RF-06, RF-07, RF-08. | `app/api/auth.py`, `app/api/solicitudes.py`, `app/api/usuarios.py`; servicios `autenticacion.py`, `solicitudes.py`, `adjuntos_solicitudes.py`; modelos `usuario.py`, `solicitud.py`, `adjunto.py`. | `test_rf01_inicio_sesion.py`, `test_rf06_crear_solicitud.py`, `test_rf07_consultar_solicitudes.py`, `test_rf08_adjuntos_solicitudes.py`. | Implementado y con pruebas automatizadas. Pendiente documentar la demostración funcional completa. |
| **CA-02. El personal autorizado puede evaluar y gestionar el caso.** Las actuaciones deben quedar asociadas al caso y al responsable correspondiente. | RF-02, RF-03, RF-04, RF-05, RF-09, RF-10, RF-11, RF-12, RF-15, RF-16, RF-18, RF-19, RF-20. | `app/api/usuarios.py`, `app/api/categorias.py`, `app/api/asignaciones.py`, `app/api/solicitudes.py`, `app/api/cierres.py`, `app/api/peticiones_informacion.py`; servicios `usuarios.py`, `categorias.py`, `asignaciones.py`, `solicitudes.py`, `intervenciones.py`, `solicitudes_informacion.py`, `cierres.py`. Modelos `usuario.py`, `solicitud.py`, `asignacion.py`, `intervencion.py`, `solicitud_informacion.py`, `respuesta_informacion.py`. | `test_rf03_gestion_usuarios.py`, `test_rf04_cambio_restablecimiento_contrasena.py`, `test_rf09_evaluacion_clasificacion.py`, `test_rf11_12_asignacion_tecnicos.py`, `test_rf15_20_cancelacion_cierre.py`, `test_rf16_registrar_intervenciones.py`, `test_rf18_solicitar_informacion.py`, `test_rf18_responder_informacion.py`, `test_rf19_registrar_solucion.py`. | Implementado y con pruebas automatizadas. Pendiente documentar la demostración funcional del proceso de gestión. |
| **CA-03. Identificar al responsable y consultar el estado del caso durante su atención.** Se deben recuperar datos coherentes de responsable y estado. | RF-02, RF-07, RF-11, RF-12, RF-13, RF-14, RF-17, RF-21. | `app/api/asignaciones.py`, `app/api/solicitudes.py`; servicios `asignaciones.py`, `solicitudes.py`, `intervenciones.py`; modelos `asignacion.py`, `solicitud.py`, `usuario.py`, `historial_cambio.py`; esquemas `asignacion.py`, `solicitud.py`. | `test_rf07_consultar_solicitudes.py`, `test_rf11_12_asignacion_tecnicos.py`, `test_rf13_solicitudes_asignadas.py`, `test_rf14_actualizar_estado.py`, `test_rf17_visibilidad_intervenciones.py`. | Implementado y con pruebas automatizadas. Pendiente documentar la comprobación conjunta de responsable y estado. |
| **CA-04. Conservar el historial de intervenciones de soporte.** Se deben consultar las actuaciones realizadas sobre un caso en su secuencia correspondiente. | RF-16, RF-17, RF-18, RF-19, RF-21, RF-22, RF-23, RF-24, RF-25, RF-26, RF-28. | `app/api/solicitudes.py`, `app/api/mensajes.py`, `app/api/peticiones_informacion.py`, `app/api/historial.py`; servicios `intervenciones.py`, `mensajes.py`, `solicitudes_informacion.py`, `adjuntos_mensajes.py`, `adjuntos.py`, `historial.py`; modelos `intervencion.py`, `mensaje.py`, `adjunto.py`, `historial_cambio.py`. | `test_rf16_registrar_intervenciones.py`, `test_rf17_visibilidad_intervenciones.py`, `test_rf18_solicitar_informacion.py`, `test_rf18_responder_informacion.py`, `test_rf19_registrar_solucion.py`, `test_rf22_23_26_mensajes.py`, `test_rf24_adjuntos_mensajes.py`, `test_rf25_adjuntos_intervenciones.py`, `test_rf28_historial.py`. | Implementado y con pruebas automatizadas. Pendiente documentar la demostración de consulta cronológica del historial. |
| **CA-05. Consultar el resultado y la finalización del caso.** Se debe visualizar el resultado de la atención de un caso cerrado. | RF-07, RF-08, RF-14, RF-15, RF-17, RF-19, RF-20, RF-24, RF-25, RF-26, RF-28. | `app/api/solicitudes.py`, `app/api/cierres.py`, `app/api/mensajes.py`, `app/api/historial.py`; servicios `solicitudes.py`, `cierres.py`, `intervenciones.py`, `adjuntos_solicitudes.py`, `adjuntos_mensajes.py`, `adjuntos.py`, `historial.py`; modelos `solicitud.py`, `adjunto.py`, `historial_cambio.py`. | `test_rf07_consultar_solicitudes.py`, `test_rf14_actualizar_estado.py`, `test_rf15_20_cancelacion_cierre.py`, `test_rf19_registrar_solucion.py`, `test_rf24_adjuntos_mensajes.py`, `test_rf25_adjuntos_intervenciones.py`, `test_rf28_historial.py`. | Implementado y con pruebas automatizadas. Pendiente documentar la consulta del resultado por parte del solicitante después del cierre. |
| **CA-06. La coordinación puede consultar información consolidada sobre la atención.** Se deben mostrar varios casos, sus estados y responsables. | RF-02, RF-07, RF-11, RF-12, RF-27, RF-28, RF-29. | `app/api/solicitudes.py`, `app/api/asignaciones.py`, `app/api/notificaciones.py`, `app/api/historial.py`, `app/api/estadisticas.py`; servicios `solicitudes.py`, `asignaciones.py`, `notificaciones.py`, `historial.py`, `estadisticas.py`; modelos `solicitud.py`, `asignacion.py`, `notificacion.py`, `historial_cambio.py`. | `test_rf07_consultar_solicitudes.py`, `test_rf11_12_asignacion_tecnicos.py`, `test_rf27_notificaciones.py`, `test_rf28_historial.py`, `test_rf29_estadisticas.py`. | Implementado y con pruebas automatizadas. Pendiente documentar la demostración consolidada desde la perspectiva del coordinador. |

**Nota:** Las rutas anteriores son relativas a `apps/backend`. Los requisitos que comparten archivos de pruebas se validan mediante esos archivos; no se presupone que cada requisito tenga un archivo independiente.

## 3. Trazabilidad de los requisitos funcionales

| Requisito | Funcionalidad | Implementación principal | Prueba automatizada |
|---|---|---|---|
| RF-01 | Inicio de sesión | `api/auth.py`, `services/autenticacion.py` | `test_rf01_inicio_sesion.py` |
| RF-02 | Control de acceso por roles | `api/dependencies.py`, `api/permisos.py` y dependencias de los módulos | Pruebas de permisos de los módulos correspondientes |
| RF-03 | Administración de usuarios | `api/usuarios.py`, `services/usuarios.py` | `test_rf03_gestion_usuarios.py` |
| RF-04 | Cambio y restablecimiento de contraseña | `api/auth.py`, `services/autenticacion.py` | `test_rf04_cambio_restablecimiento_contrasena.py` |
| RF-05 | Gestión de datos de contacto | `api/usuarios.py`, `services/usuarios.py` | `test_rf03_gestion_usuarios.py` |
| RF-06 | Creación de solicitudes | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf06_crear_solicitud.py` |
| RF-07 | Consulta de solicitudes | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf07_consultar_solicitudes.py` |
| RF-08 | Adjuntos en solicitudes | `api/solicitudes.py`, `services/adjuntos_solicitudes.py` | `test_rf08_adjuntos_solicitudes.py` |
| RF-09 | Evaluación de solicitudes | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf09_evaluacion_clasificacion.py` |
| RF-10 | Clasificación y prioridad | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf09_evaluacion_clasificacion.py` |
| RF-11 | Asignación de técnicos | `api/asignaciones.py`, `services/asignaciones.py` | `test_rf11_12_asignacion_tecnicos.py` |
| RF-12 | Reasignación de solicitudes | `api/asignaciones.py`, `services/asignaciones.py` | `test_rf11_12_asignacion_tecnicos.py` |
| RF-13 | Consulta de solicitudes asignadas | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf13_solicitudes_asignadas.py` |
| RF-14 | Actualización del estado | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf14_actualizar_estado.py` |
| RF-15 | Cancelación de solicitudes | `api/cierres.py`, `services/cierres.py` | `test_rf15_20_cancelacion_cierre.py` |
| RF-16 | Registro de intervenciones | `api/solicitudes.py`, `services/intervenciones.py` | `test_rf16_registrar_intervenciones.py` |
| RF-17 | Visibilidad de intervenciones | `api/solicitudes.py`, `services/intervenciones.py` | `test_rf17_visibilidad_intervenciones.py` |
| RF-18 | Solicitud de información adicional | `api/solicitudes.py`, `api/peticiones_informacion.py`, `services/solicitudes_informacion.py` | `test_rf18_solicitar_informacion.py`, `test_rf18_responder_informacion.py` |
| RF-19 | Registro de solución | `api/solicitudes.py`, `services/solicitudes.py` | `test_rf19_registrar_solucion.py` |
| RF-20 | Revisión y cierre de solicitudes | `api/cierres.py`, `services/cierres.py` | `test_rf15_20_cancelacion_cierre.py` |
| RF-21 | Consulta de intervenciones | `api/solicitudes.py`, `services/intervenciones.py` | `test_rf17_visibilidad_intervenciones.py` |
| RF-22 | Conversación asociada a solicitudes | `api/mensajes.py`, `services/mensajes.py` | `test_rf22_23_26_mensajes.py` |
| RF-23 | Envío y consulta de mensajes | `api/mensajes.py`, `services/mensajes.py` | `test_rf22_23_26_mensajes.py` |
| RF-24 | Adjuntos en mensajes | `api/mensajes.py`, `services/adjuntos_mensajes.py` | `test_rf24_adjuntos_mensajes.py` |
| RF-25 | Adjuntos en intervenciones | `api/solicitudes.py`, `services/adjuntos.py` | `test_rf25_adjuntos_intervenciones.py` |
| RF-26 | Historial de conversación | `api/mensajes.py`, `services/mensajes.py` | `test_rf22_23_26_mensajes.py` |
| RF-27 | Notificaciones en la plataforma | `api/notificaciones.py`, `services/notificaciones.py` | `test_rf27_notificaciones.py` |
| RF-28 | Historial de cambios | `api/historial.py`, `services/historial.py` | `test_rf28_historial.py` |
| RF-29 | Consulta de estadísticas | `api/estadisticas.py`, `services/estadisticas.py` | `test_rf29_estadisticas.py` |

## 4. Integración y control de versiones

La integración del backend se encuentra en la rama:

`feature/backend-integrado`

El desarrollo se organiza mediante ramas por requisito funcional, de acuerdo con el flujo de trabajo establecido para el proyecto.

La integración de RF-24, adjuntos en mensajes, quedó incorporada en la rama integrada junto con:

- `apps/backend/app/api/mensajes.py`
- `apps/backend/app/services/adjuntos_mensajes.py`
- `apps/backend/tests/test_rf24_adjuntos_mensajes.py`

La integración se encuentra publicada en la rama `feature/backend-integrado`. El número o enlace del Pull Request debe registrarse cuando se confirme el PR correspondiente; no se asignan números sin evidencia.

Para verificar las integraciones y contribuciones individuales se debe consultar el historial de GitHub, los commits, las ramas y los Pull Requests.

## 5. Validación y evidencias pendientes

La suite automatizada del backend se ejecutó antes de la integración de RF-24 con 517 pruebas aprobadas y una advertencia de deprecación de Starlette relacionada con `httpx`. Después de integrar RF-24, sus pruebas específicas registraron 12 casos aprobados. También se informó una ejecución posterior de la suite general sin errores.

Estos resultados corresponden a pruebas automatizadas del backend y no sustituyen las pruebas funcionales exigidas para la entrega.

Queda pendiente consolidar en `docs/pruebas.md` las 12 pruebas funcionales reproducibles solicitadas en `proyecto2.md`, con:

1. Identificador y condición de aceptación relacionada.
2. Requisito funcional validado.
3. Objetivo de la prueba.
4. Precondiciones y datos de prueba.
5. Pasos de ejecución.
6. Resultado esperado.
7. Resultado obtenido.
8. Estado de aprobación o fallo.
9. Evidencia correspondiente.

También se deben adjuntar capturas o registros en la carpeta `evidencias/`.

## 6. Demostración para la sustentación

La demostración debe cubrir un proceso completo de atención:

1. Un solicitante inicia sesión y registra una solicitud.
2. El coordinador consulta, evalúa, clasifica y asigna el caso.
3. El técnico consulta la solicitud asignada y actualiza su estado.
4. El técnico registra intervenciones y, cuando corresponda, solicita información adicional.
5. Los participantes consultan los mensajes y adjuntos asociados al caso.
6. El técnico registra la solución.
7. El coordinador revisa y cierra la solicitud.
8. El solicitante consulta el resultado y la finalización.
9. El coordinador consulta el historial y las estadísticas de atención.

Durante la demostración se deben comprobar los permisos de cada rol y la persistencia de la información.

## 7. Mantenimiento de la matriz

Esta matriz debe actualizarse cuando se integre o modifique una funcionalidad.

Para registrar un requisito como completado se debe contar con:

- Implementación identificable en el repositorio.
- Pruebas automatizadas o funcionales correspondientes.
- Resultado de ejecución comprobable.
- Evidencia funcional cuando sea requerida.
- Referencia al commit o Pull Request de integración, cuando corresponda.

Las condiciones de aceptación solo se marcarán como demostradas cuando exista evidencia suficiente del flujo completo, no únicamente por la existencia de endpoints o pruebas unitarias.
