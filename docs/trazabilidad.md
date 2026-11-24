# Matriz de trazabilidad — SoporteTI

## 1. Objetivo

Esta matriz relaciona las seis condiciones de aceptación establecidas en `proyecto2.md` con los requisitos funcionales aprobados, los componentes de implementación, los Pull Requests y las pruebas correspondientes.

Su propósito es permitir la identificación y verificación de cada funcionalidad, desde el requisito aprobado hasta su implementación y validación.

La matriz se debe mantener actualizada conforme se integren los requisitos funcionales y se ejecuten las pruebas del proyecto.

### 1.1. Estados utilizados

Los siguientes estados permiten identificar el nivel de avance de cada elemento:

- **Pendiente de verificar:** la implementación, integración o prueba requiere comprobación.
- **Implementado:** existe una implementación identificable en el repositorio.
- **Pendiente de integración:** el desarrollo todavía no se ha incorporado a la rama correspondiente.
- **Pendiente de prueba funcional:** falta ejecutar y documentar la prueba funcional.
- **Pendiente de evidencia:** falta adjuntar la evidencia que demuestra el resultado.
- **Verificado:** existe evidencia suficiente de implementación y validación.

La existencia de código o de una prueba automatizada no demuestra por sí sola el cumplimiento completo de una condición de aceptación.

## 2. Matriz de trazabilidad de las condiciones de aceptación

Las condiciones de aceptación corresponden a las seis condiciones obligatorias definidas en `proyecto2.md`.

| Condición de aceptación | Requisitos funcionales relacionados | Implementación (rutas principales) | Pull Request | Prueba funcional relacionada | Estado |
|---|---|---|---|---|---|
| **CA-01. Registro de casos de soporte.** Un usuario solicitante puede reportar un incidente o solicitar soporte tecnológico mediante la plataforma. El sistema registra el caso de forma persistente y permite recuperarlo posteriormente. | RF-06 | `apps/backend/app/api/solicitudes.py`, `apps/backend/app/services/solicitudes.py`. Modelos relacionados con solicitudes y usuarios. | Pendiente de identificar. | PF-01, PF-02, PF-03, PF-11 y PF-12. | Pendiente de consolidar evidencia funcional. |
| **CA-02. Evaluación y gestión de casos.** El personal autorizado puede evaluar y gestionar un caso mediante las actuaciones permitidas para su rol. Las acciones deben quedar asociadas al caso y al responsable correspondiente. | RF-09, RF-10, RF-11, RF-12, RF-14 | `apps/backend/app/api/solicitudes.py`, `apps/backend/app/api/asignaciones.py`, `apps/backend/app/services/solicitudes.py`, `apps/backend/app/services/asignaciones.py`. | Pendiente de identificar. | PF-05, PF-06, PF-11 y PF-12. | Pendiente de consolidar evidencia funcional. |
| **CA-03. Consulta del estado y responsable.** El sistema permite identificar quién es responsable de un caso y consultar su estado durante el proceso de atención. | RF-07, RF-11, RF-12, RF-13, RF-14 | `apps/backend/app/api/solicitudes.py`, `apps/backend/app/api/asignaciones.py`, `apps/backend/app/services/solicitudes.py`, `apps/backend/app/services/asignaciones.py`. | Pendiente de identificar. | PF-03, PF-04, PF-07 y PF-12. | Pendiente de consolidar evidencia funcional. |
| **CA-04. Historial de intervenciones.** El sistema conserva las intervenciones realizadas durante la atención de un caso y permite consultarlas en la secuencia correspondiente, respetando los permisos y las reglas de visibilidad. | RF-16, RF-17, RF-21 | `apps/backend/app/api/solicitudes.py`, `apps/backend/app/services/intervenciones.py`. | Pendiente de identificar. | PF-08, PF-11 y PF-12. | Pendiente de consolidar evidencia funcional. |
| **CA-05. Consulta del resultado y finalización.** El solicitante puede consultar el resultado de la atención y la finalización de su caso. El resultado debe permanecer disponible para consulta autorizada. | RF-07, RF-19, RF-20 | `apps/backend/app/api/solicitudes.py`, `apps/backend/app/api/cierres.py`, `apps/backend/app/services/solicitudes.py`, `apps/backend/app/services/cierres.py`. | Pendiente de identificar. | PF-03, PF-09 y PF-12. | Pendiente de consolidar evidencia funcional. |
| **CA-06. Consulta consolidada de coordinación.** El coordinador puede consultar información consolidada de varios casos, incluyendo sus estados y responsables. | RF-29 | `apps/backend/app/api/estadisticas.py`, `apps/backend/app/services/estadisticas.py`. | Pendiente de identificar. | PF-10 y PF-12. | Pendiente de consolidar evidencia funcional. |

**Nota sobre las rutas:** las rutas de implementación se presentan como referencias registradas para los componentes del backend y deben cotejarse con los archivos existentes en la rama evaluada. No se consideran una confirmación de que todos los componentes estén integrados.

**Nota sobre los Pull Requests:** se debe registrar el número o enlace real del Pull Request correspondiente a cada requisito o integración. No se asignan números sin haberlos comprobado en GitHub.

## 3. Trazabilidad de los requisitos funcionales

La siguiente tabla relaciona cada requisito funcional con su implementación principal y su prueba automatizada de referencia.

Las rutas y nombres de pruebas corresponden al registro de desarrollo del proyecto. Su existencia y estado actual deben verificarse en el repositorio antes de considerar un requisito completamente validado.

| Requisito | Funcionalidad | Implementación principal | Prueba automatizada de referencia |
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

**Consideraciones:**

- Las rutas anteriores son relativas a `apps/backend`.
- Los nombres de las pruebas son referencias para localizar las validaciones correspondientes.
- Algunos requisitos comparten archivos de pruebas.
- Las pruebas automatizadas no reemplazan las doce pruebas funcionales exigidas para la entrega.
- La implementación debe comprobarse contra la rama que se está evaluando.

## 4. Integración y control de versiones

El desarrollo de SoporteTI se organiza mediante ramas por requisito funcional, de acuerdo con el flujo de trabajo establecido para el proyecto.

La rama que se documenta en esta versión es:

`feature/entorno-local-postgresql`

En esta rama se está trabajando en la configuración del entorno local con PostgreSQL y en la actualización de la documentación correspondiente.

Cada requisito funcional debe relacionarse con su rama de desarrollo, su integración y el Pull Request correspondiente, cuando aplique.

Para mantener el registro de integración se debe documentar:

| Elemento | Información que debe registrarse |
|---|---|
| Requisito funcional | Identificador RF correspondiente. |
| Rama de desarrollo | Nombre exacto de la rama utilizada. |
| Commit | Identificador del commit que contiene la implementación. |
| Pull Request | Número y enlace del PR, cuando exista. |
| Rama de destino | Rama en la que se integró el cambio. |
| Estado | Pendiente, abierto, integrado o cerrado, según corresponda. |

No se considera integrada una funcionalidad únicamente porque exista una rama o un commit. Se debe comprobar su incorporación en la rama de destino.

Los números y enlaces de Pull Requests deben obtenerse del historial real del repositorio. No se deben completar con referencias supuestas.

## 5. Validación y evidencias

La validación del proyecto contempla dos niveles complementarios:

### 5.1. Pruebas automatizadas

Las pruebas automatizadas permiten verificar el comportamiento de los componentes del backend, las reglas de negocio y las operaciones de la API.

Los resultados deben registrarse después de ejecutar la suite correspondiente en el entorno local.

Se debe documentar:

- Comando utilizado para ejecutar las pruebas.
- Cantidad de pruebas ejecutadas.
- Cantidad de pruebas aprobadas.
- Cantidad de pruebas fallidas.
- Advertencias presentadas durante la ejecución.
- Resultado general.
- Rama y commit sobre los que se ejecutaron.

Los resultados históricos no deben utilizarse como evidencia de una ejecución posterior si no se ha repetido la validación sobre la versión correspondiente.

### 5.2. Pruebas funcionales

De acuerdo con la Actividad 6 de `proyecto2.md`, el proyecto debe contar con doce pruebas funcionales que permitan verificar los servicios web, las reglas de negocio y la integración entre la interfaz, la API REST y la base de datos.

Las doce pruebas requeridas son:

| ID | Prueba funcional | Criterio relacionado |
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

Estas pruebas funcionales no deben confundirse con los archivos de pruebas automatizadas de pytest.

Cada prueba funcional debe registrar:

1. Identificador de la prueba.
2. Condición de aceptación relacionada.
3. Requisito funcional validado.
4. Objetivo de la prueba.
5. Precondiciones y datos de prueba.
6. Pasos de ejecución.
7. Resultado esperado.
8. Resultado obtenido.
9. Estado de aprobación o fallo.
10. Evidencia correspondiente.

Las evidencias pueden incluir capturas de la interfaz, solicitudes y respuestas HTTP, registros de ejecución y consultas que permitan demostrar la persistencia de los datos.

Los resultados y evidencias deben documentarse en `docs/pruebas.md` y conservarse en la carpeta `evidencias/`.

La existencia de esta matriz no significa que las doce pruebas ya estén ejecutadas o aprobadas.

## 6. Demostración para la sustentación

La demostración debe cubrir un proceso completo de atención de una solicitud de soporte.

1. Un solicitante inicia sesión y registra una solicitud.
2. El coordinador consulta, evalúa y clasifica el caso.
3. El coordinador asigna el caso a un técnico.
4. El técnico consulta las solicitudes que tiene asignadas.
5. El técnico actualiza el estado de la solicitud.
6. El técnico registra intervenciones y, cuando corresponda, solicita información adicional.
7. Los participantes autorizados consultan los mensajes y adjuntos asociados al caso.
8. El técnico registra la solución.
9. El coordinador revisa y cierra la solicitud.
10. El solicitante consulta el resultado y la finalización.
11. El coordinador consulta el historial y las estadísticas de atención.

Durante la demostración se deben comprobar:

- Los permisos correspondientes a cada rol.
- La persistencia de la información.
- La relación entre las solicitudes y sus responsables.
- El registro de las intervenciones.
- La conservación del resultado después del cierre.
- La consulta consolidada de varios casos.

## 7. Mantenimiento de la matriz

Esta matriz debe actualizarse cuando se implemente, modifique o integre un requisito funcional.

Para registrar un requisito como completado se debe contar con:

- Implementación identificable en el repositorio.
- Relación con el requisito funcional aprobado.
- Referencia a la rama y al commit correspondiente.
- Pull Request real, cuando corresponda.
- Prueba automatizada o funcional relacionada.
- Resultado de ejecución comprobable.
- Evidencia funcional cuando sea requerida.

Las condiciones de aceptación solo se marcarán como demostradas cuando exista evidencia suficiente del flujo completo.

No se debe considerar cumplida una condición únicamente por la existencia de endpoints, archivos de código, ramas o pruebas automatizadas aisladas.