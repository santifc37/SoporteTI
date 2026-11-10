# Matriz de trazabilidad — SoporteTI

Esta matriz relaciona las seis condiciones de aceptación obligatorias definidas en `proyecto2.md` con los requisitos funcionales, las implementaciones del sistema, los Pull Requests y las pruebas correspondientes.

La matriz se actualizará progresivamente durante el desarrollo. Una condición solo se considerará completamente validada cuando exista evidencia de su implementación, integración y prueba funcional.

## 1. Matriz de trazabilidad

| Condición | Requisito aprobado | Implementación (ruta/componente) | Pull request | Prueba |
|---|---|---|---|---|
| CA-01 | RF-06: Creación de solicitudes. | Pendiente de completar con las rutas y componentes definitivos de registro de solicitudes. | Pendiente de identificar. | PF-01: Registro válido. PF-02: Registro con datos inválidos. Pendientes de ejecución y documentación. |
| CA-02 | RF-09: Evaluación de solicitudes. RF-10: Clasificación y prioridad. RF-11: Asignación de técnicos. RF-12: Reasignación de solicitudes. RF-14: Actualización del estado. | RF-13 y RF-14: `apps/backend/app/api/solicitudes.py` y `apps/backend/app/services/solicitudes.py`. Esquema de RF-14: `apps/backend/app/schemas/solicitud.py`. Modelo de historial: `apps/backend/app/models/historial_cambio.py`. Las demás rutas y componentes deben verificarse según su implementación integrada. | Pendiente de identificar los PR correspondientes. | PF-05: Gestión por personal autorizado. PF-06: Gestión por actor no autorizado. Pendientes de ejecución y documentación. Las pruebas automatizadas existentes son evidencia complementaria. |
| CA-03 | RF-07: Consulta de solicitudes. RF-11: Asignación de técnicos. RF-12: Reasignación de solicitudes. RF-13: Consulta de solicitudes asignadas. RF-14: Actualización del estado. | RF-13 y RF-14: `apps/backend/app/api/solicitudes.py` y `apps/backend/app/services/solicitudes.py`. Las rutas de consulta y los componentes de interfaz deben verificarse con la integración completa. | Pendiente de identificar los PR correspondientes. | PF-03: Consulta de caso existente. PF-04: Consulta de caso inexistente. PF-07: Consulta del estado y responsable. Pendientes de ejecución y documentación. |
| CA-04 | RF-16: Registro de intervenciones. RF-17: Visibilidad de intervenciones. RF-21: Consulta de intervenciones. RF-28: Historial de cambios. | RF-16 y RF-17: `apps/backend/app/models/intervencion.py`, `apps/backend/app/schemas/intervencion.py`, `apps/backend/app/services/intervenciones.py` y `apps/backend/app/api/solicitudes.py`. RF-21: consulta mediante `GET /api/v1/requests/{id}/interventions`, implementada en `apps/backend/app/api/solicitudes.py` y `apps/backend/app/services/intervenciones.py`. RF-28: modelo `apps/backend/app/models/historial_cambio.py`. | Pendiente de identificar los PR correspondientes. | PF-08: Consulta del historial de intervenciones. Pendiente de ejecución y documentación. Existen pruebas automatizadas para RF-16, RF-17 y RF-21, que son complementarias. |
| CA-05 | RF-07: Consulta de solicitudes. RF-19: Registro de solución. RF-20: Revisión y cierre de solicitudes. | RF-19: `apps/backend/app/schemas/solucion.py`, `apps/backend/app/services/solicitudes.py` y `apps/backend/app/api/solicitudes.py`. La implementación de cierre y la consulta del resultado deben verificarse en el código integrado. | Pendiente de identificar los PR correspondientes. | PF-09: Cierre de caso y consulta del resultado. Pendiente de ejecución y documentación. Existen pruebas automatizadas para RF-19, como evidencia complementaria. |
| CA-06 | RF-29: Consulta de estadísticas. | Pendiente de verificar la implementación del módulo de coordinación y sus consultas consolidadas. | Pendiente de identificar. | PF-10: Consulta consolidada de coordinación. Pendiente de ejecución y documentación. |

## 2. Pruebas de persistencia e integración

Además de las pruebas asociadas directamente a cada condición, se deben ejecutar y documentar los siguientes escenarios exigidos por la Actividad 6:

| Prueba | Alcance | Estado |
|---|---|---|
| PF-11 | Verificación de persistencia e integridad de las relaciones entre casos, actores e intervenciones. | Pendiente de ejecución y documentación. |
| PF-12 | Verificación de la integración completa entre interfaz, API REST y base de datos. | Pendiente de ejecución y documentación. |

Los resultados de las doce pruebas funcionales se registrarán en `docs/pruebas.md`. Las evidencias correspondientes se conservarán en la carpeta `evidencias/`.

Las pruebas automatizadas existentes en el backend pueden utilizarse como evidencia técnica complementaria, pero no sustituyen las doce pruebas funcionales documentadas que exige la Actividad 6.

## 3. Sustentación del proyecto

Durante la sustentación, el equipo deberá:

1. Demostrar un caso completo del proceso de atención de una solicitud.
2. Explicar las principales decisiones de diseño y arquitectura.
3. Ejecutar nuevamente pruebas funcionales seleccionadas y mostrar sus resultados.
4. Mostrar el historial de commits, ramas y Pull Requests para evidenciar las contribuciones de cada integrante.
5. Explicar individualmente las funcionalidades desarrolladas por cada integrante.

## 4. Actualización de la matriz

La matriz deberá mantenerse actualizada a medida que se implementen, prueben e integren los requisitos.

Para registrar una implementación se deberá indicar la ruta concreta del código o componente. En la columna de Pull Request se incluirá el número o enlace correspondiente cuando exista.

En la columna de pruebas se identificarán los escenarios funcionales, sus resultados y las evidencias correspondientes. Las pruebas automatizadas podrán registrarse como complemento, diferenciándolas de las pruebas funcionales manuales.

Las funcionalidades pendientes de implementación, integración o validación deberán conservar ese estado hasta contar con evidencia suficiente.