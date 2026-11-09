
# Matriz de trazabilidad — SoporteTI

Esta matriz relaciona las condiciones de aceptación del proyecto con los requisitos funcionales aprobados, los componentes implementados, los Pull Requests y las pruebas realizadas.

La matriz se actualizará progresivamente durante el desarrollo y la integración de los módulos. Una funcionalidad solo se considerará completada cuando exista evidencia de su implementación y validación.

## 1. Matriz de trazabilidad

| Condición | Requisito aprobado | Implementación (ruta/componente) | Pull request | Prueba |
|---|---|---|---|---|
| CA-01 | RF-01: Inicio de sesión. RF-02: Control de acceso por roles. RF-03: Administración de usuarios. RF-04: Cambio y restablecimiento de contraseña. RF-05: Gestión de datos de contacto. | Pendiente de completar con la implementación integrada de autenticación y administración de usuarios. | Pendiente | Pendiente de consolidar las pruebas correspondientes. |
| CA-03 | RF-09: Evaluación. RF-10: Clasificación y prioridad. RF-11: Asignación de técnicos. RF-12: Reasignación. RF-13: Consulta de solicitudes asignadas. RF-14: Actualización del estado. | RF-13 y RF-14: `apps/backend/app/api/solicitudes.py` y `apps/backend/app/services/solicitudes.py`. Esquema de RF-14: `apps/backend/app/schemas/solicitud.py`. Modelo de historial: `apps/backend/app/models/historial_cambio.py`. | Pendiente | `apps/backend/tests/test_rf14_actualizar_estado.py`: 9 pruebas específicas aprobadas. |

| CA-04 | RF-16: Registro de intervenciones. RF-17: Visibilidad de intervenciones. RF-18: Solicitud de información adicional. RF-19: Registro de solución. RF-21: Consulta de intervenciones. RF-22: Conversación asociada a solicitudes. RF-23: Envío y consulta de mensajes. RF-26: Consulta de historial de mensajes. RF-28: Historial de cambios. | RF-16 y RF-17: `apps/backend/app/models/intervencion.py`, `apps/backend/app/schemas/intervencion.py`, `apps/backend/app/services/intervenciones.py` y `apps/backend/app/api/solicitudes.py`. RF-18: `apps/backend/app/models/solicitud_informacion.py`, `apps/backend/app/models/respuesta_informacion.py`, `apps/backend/app/schemas/solicitud_informacion.py`, `apps/backend/app/schemas/respuesta_informacion.py`, `apps/backend/app/services/solicitudes_informacion.py` y `apps/backend/app/api/solicitudes.py`. RF-19: `apps/backend/app/schemas/solucion.py`, `apps/backend/app/services/solicitudes.py` y `apps/backend/app/api/solicitudes.py`. RF-21: consulta mediante `GET /api/v1/requests/{id}/interventions`, implementada en `apps/backend/app/api/solicitudes.py` y `apps/backend/app/services/intervenciones.py`; reutiliza los controles de permisos y visibilidad de RF-17. | Pendiente de registrar los PR correspondientes. | RF-16: 9 pruebas aprobadas. RF-17: 7 pruebas aprobadas. RF-18: pruebas específicas aprobadas. RF-19: `apps/backend/tests/test_rf19_registrar_solucion.py`, pruebas específicas aprobadas. RF-21: `apps/backend/tests/test_rf17_visibilidad_intervenciones.py`, 8 pruebas aprobadas. Suite general del backend ejecutada sin errores. |

| CA-05 | RF-15: Cancelación de solicitudes. RF-20: Revisión y cierre de solicitudes. RF-24: Adjuntos en mensajes. RF-25: Adjuntos en intervenciones. | Pendiente de completar con los módulos correspondientes. | Pendiente | Pendiente |
| CA-06 | RF-27: Notificaciones en la plataforma. RF-29: Consulta de estadísticas. | Pendiente de completar con el módulo del coordinador. | Pendiente | Pendiente |

## 2. Sustentación del proyecto

Durante la sustentación, el equipo deberá:

1. Demostrar un caso completo del proceso de atención de una solicitud.
2. Explicar las principales decisiones de diseño y arquitectura.
3. Ejecutar nuevamente pruebas funcionales seleccionadas y mostrar sus resultados.
4. Mostrar el historial de commits, ramas y Pull Requests para evidenciar las contribuciones de cada integrante.
5. Explicar individualmente las funcionalidades desarrolladas por cada integrante.

## 3. Actualización de la matriz

La matriz deberá mantenerse actualizada a medida que se implementen, prueben e integren los requisitos.

Para registrar una implementación se deberá indicar la ruta concreta del código o componente. En la columna de Pull Request se incluirá el número o enlace correspondiente cuando exista. En la columna de pruebas se identificarán los archivos de pruebas y los resultados obtenidos.

Las funcionalidades pendientes de implementación, integración o validación deberán conservar ese estado hasta contar con evidencia suficiente.
