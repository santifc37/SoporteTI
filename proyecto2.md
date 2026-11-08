# Guía de Trabajo Práctico Experimental — Proyecto Final 02

**Mesa de servicios de soporte tecnológico — Desarrollo e integración de aplicaciones y servicios web**

---

| Campo | Valor |
|---|---|
| **Código de guía** | PF-02 |
| **Laboratorio** | Laboratorio de Aplicaciones y Servicios Web |
| **Tiempo de trabajo práctico estimado** | Según cronograma del curso |
| **Asignatura** | Aplicaciones y Servicios Web |
| **Programa académico** | Tecnología en Desarrollo de Software |
| **Elaborado por** | Juan Carlos Morales Guerra |
| **Revisado por** | Juan Carlos Morales Guerra |
| **Versión** | 002 |
| **Fecha** | 04-11-2026 |

---

## 1. Competencias, Contenido Temático e Indicador de Logro

| Competencias | Contenido Temático | Indicador de Logro |
|---|---|---|
| Diseñar, desarrollar e integrar aplicaciones y servicios web mediante tecnologías frontend y backend, implementando APIs REST, persistencia de datos, validaciones y pruebas de funcionamiento, a partir de los requisitos de un problema organizacional. | Arquitectura cliente-servidor. Desarrollo frontend y backend. API REST. Métodos HTTP y códigos de respuesta. Operaciones CRUD. Validación de datos. Persistencia y bases de datos relacionales. Integración y consumo de servicios web. Manejo de errores. Pruebas de APIs y funcionalidades. Git y GitHub. Documentación técnica. | El equipo implementa una aplicación web funcional que integra una interfaz de usuario, una API REST y una base de datos; ejecuta operaciones de consulta y modificación de información, aplica reglas de negocio y validaciones, verifica su funcionamiento mediante pruebas y documenta su desarrollo en GitHub. |

---

## 2. Fundamento Teórico

Una **aplicación web** permite que los usuarios interactúen con un sistema mediante un navegador. En una arquitectura **cliente-servidor**, el frontend presenta información y recibe acciones de los usuarios, mientras el backend procesa solicitudes, aplica reglas de negocio y accede a los datos.

Una **API REST** permite exponer recursos mediante HTTP para que el frontend y otros clientes intercambien información con el backend. Los métodos `GET`, `POST`, `PUT`, `PATCH` y `DELETE` representan operaciones sobre recursos cuando corresponda; los códigos de estado HTTP comunican el resultado de cada solicitud. **CRUD** describe las operaciones de creación, consulta, actualización y eliminación, pero no todas deben estar habilitadas para cualquier recurso: dependen de las reglas del proceso.

La **persistencia de datos** permite conservar la información más allá de la ejecución de la aplicación. El diseño de una base de datos relacional requiere identificar entidades, claves y relaciones, así como aplicar restricciones para mantener la consistencia de los registros.

La **integración frontend–API–base de datos** requiere intercambiar datos reales entre los componentes, gestionar estados de la interfaz, validar entradas y tratar errores. Las validaciones del servidor deben proteger la integridad de los datos incluso si una solicitud se envía sin utilizar la interfaz web.

Las **pruebas de servicios web** verifican las respuestas de los endpoints ante solicitudes válidas, entradas incorrectas, recursos inexistentes y acciones no autorizadas. En este proyecto, las verificaciones se realizarán mediante **pruebas funcionales documentadas**, utilizando las herramientas de consulta HTTP y de ejecución de la aplicación trabajadas durante el curso. No se exige automatizar su ejecución.

**Git** registra los cambios del proyecto. **GitHub** facilita el trabajo colaborativo mediante ramas, commits y *pull requests*. Cada cambio debe ser comprensible y tener relación con el trabajo implementado o corregido.

El **levantamiento de requisitos** y los criterios de aceptación se utilizarán para delimitar qué comportamiento debe implementar la aplicación. En este proyecto son insumos para el desarrollo y las pruebas, no el producto principal de la asignatura.

---

## 3. Objetivos

### Objetivo General

Desarrollar e integrar una aplicación web para la atención de incidentes y solicitudes de soporte tecnológico de una institución, mediante una interfaz frontend, una API REST y una base de datos, verificando su funcionamiento con pruebas funcionales documentadas y registrando el desarrollo en GitHub.

### Objetivos Específicos

- Delimitar el problema mediante requisitos funcionales, reglas de negocio y criterios de aceptación verificables.
- Diseñar la arquitectura cliente-servidor, las interfaces, el modelo de datos y los servicios web necesarios.
- Implementar una API REST con recursos, métodos HTTP, validaciones, respuestas y manejo de errores coherentes con el proceso.
- Implementar una interfaz web que consuma la API y permita ejecutar el proceso de reporte, atención y cierre de casos de soporte tecnológico.
- Almacenar y consultar información mediante una base de datos con relaciones e integridad de datos.
- Integrar frontend, backend y persistencia en flujos completos y reproducibles.
- Diseñar, ejecutar y documentar pruebas funcionales de endpoints y reglas de negocio, además de comprobar el funcionamiento de la aplicación integrada.
- Utilizar Git y GitHub para organizar el trabajo en ramas, registrar commits descriptivos y documentar la integración de cambios mediante *pull requests*.
- Documentar la instalación, los servicios implementados y la evidencia de cumplimiento de las condiciones de aceptación.

---

## 4. Recursos Requeridos

### Equipos

- Computador personal o estación de trabajo con acceso a Internet.

### Herramientas de Software

- Editor de código o IDE.
- Git y cuenta en GitHub.
- Lenguaje, framework frontend y framework backend seleccionados y justificados por el equipo.
- Sistema de gestión de bases de datos seleccionado por el equipo.
- Herramientas de consulta HTTP y verificación de endpoints utilizadas durante el curso (por ejemplo, la interfaz de documentación interactiva de la API o un cliente HTTP conocido por el equipo).

### Recursos suministrados

- Enunciado del problema y condiciones de aceptación obligatorias de esta guía.
- Sesión de levantamiento de requisitos con el docente en el papel de representante de la organización.
- Revisión y aprobación del alcance por parte del docente.

### Restricciones técnicas comunes

- La aplicación debe incluir una **interfaz web**, un **backend con API REST** y **persistencia en una base de datos**.
- Debe existir comunicación real entre interfaz, API y base de datos; no se aceptan pantallas con datos simulados como sustituto de las funciones obligatorias.
- El diseño, las rutas HTTP, la estructura de tablas y la tecnología concreta deberán ser definidos y documentados por el equipo.
- Deben ejecutarse y documentarse las pruebas funcionales de la Actividad 6. No se exigen frameworks de pruebas automatizadas ni herramientas de CI.
- No se exige despliegue en la nube ni uso de Docker.

---

## 5. Aspectos de Seguridad

La actividad corresponde a desarrollo de software y no implica riesgos físicos o químicos propios de prácticas experimentales.

- No incorporar contraseñas, tokens, claves o cadenas de conexión reales en el repositorio.
- Mantener los archivos locales `.env` fuera del control de versiones y proporcionar un `.env.example` sin secretos, cuando corresponda.
- Utilizar datos ficticios para demostrar los casos de uso; no publicar información personal real de usuarios de la organización.
- Validar las entradas tanto en el servidor como en los puntos de interacción que resulten necesarios.
- Definir y aplicar permisos acordes con los actores identificados, evitando que un usuario acceda o modifique información no autorizada.
- Evitar que los registros y mensajes de error revelen información sensible.

---

## 6. Procedimiento o Metodología para el Desarrollo

El proyecto se desarrolla de forma colaborativa. Los equipos, fechas, hitos de entrega y condiciones de sustentación serán los comunicados por el docente. El trabajo debe conservar evidencias de las decisiones y de la participación individual.

### Actividad 1: Comprensión del Problema y Delimitación del Alcance

#### A. Contexto

Una institución educativa cuenta con un equipo de soporte tecnológico que atiende necesidades de docentes y personal administrativo relacionadas con computadores, conectividad, software y acceso a plataformas institucionales. La atención puede incluir la resolución de incidentes y la ejecución de solicitudes de soporte, según las condiciones del servicio.

#### B. Situación actual

Los reportes llegan por correo electrónico, llamadas y comunicaciones directas con el personal técnico. No existe un registro unificado de los casos ni una forma consistente de conocer quién está a cargo de cada atención. Los usuarios desconocen el avance de sus reportes; el personal técnico tiene dificultades para recuperar las intervenciones anteriores y la coordinación no dispone de una visión consolidada del trabajo pendiente y atendido.

#### C. Actores involucrados

- **Usuario solicitante:** docente o funcionario que reporta una dificultad o solicita soporte y necesita conocer su atención.
- **Personal técnico:** responsable de analizar y atender los casos de soporte que le correspondan.
- **Coordinación de soporte:** responsable de organizar la atención y consultar el estado general de los casos.

Estos actores describen responsabilidades, no un diseño de cuentas ni una lista cerrada de permisos. Las reglas de acceso, distribución de casos y operación deberán definirse durante el levantamiento de requisitos.

#### D. Problema a resolver

La institución necesita una solución web que permita registrar y dar seguimiento a los casos de soporte tecnológico desde su reporte hasta su resolución o cierre, manteniendo información verificable sobre las intervenciones realizadas y el resultado de la atención.

#### E. Límites obligatorios del alcance

La aplicación debe cubrir, como mínimo, **el reporte, la evaluación, la atención, el seguimiento y el cierre de casos de soporte tecnológico**. Debe conservar la relación entre el caso, sus intervenciones y el resultado comunicado al usuario. La coordinación debe poder consultar la situación general de los casos gestionados.

El alcance obligatorio se limita a la **gestión del proceso de soporte**. No exige solucionar técnicamente fallas reales, conectarse a herramientas de acceso remoto, monitorear redes, integrar directorios institucionales ni enviar mensajes mediante correo o WhatsApp. Cualquier integración adicional debe justificarse y no sustituye las funciones del proceso obligatorio.

#### F. Condiciones de aceptación obligatorias

| ID | Condición | Demostración esperada |
|---|---|---|
| CA-01 | Un usuario puede reportar un incidente o solicitar soporte tecnológico. | Se registra un caso de forma persistente y puede recuperarse. |
| CA-02 | El personal autorizado puede evaluar y gestionar el caso. | Una actuación de gestión válida queda asociada al caso y al responsable correspondiente. |
| CA-03 | Es posible identificar el responsable y consultar el estado del caso durante su atención. | Se recuperan datos coherentes de responsable y estado conforme a las reglas aprobadas. |
| CA-04 | El sistema conserva el historial de intervenciones de soporte. | Pueden consultarse las actuaciones realizadas sobre un caso en su secuencia correspondiente. |
| CA-05 | El usuario puede consultar el resultado y la finalización de su caso. | Se visualiza el resultado de la atención de un caso cerrado. |
| CA-06 | La coordinación puede consultar información consolidada sobre la atención. | Se demuestra una consulta o resumen de varios casos, sus estados y responsables, según el alcance aprobado. |

**Estas condiciones delimitan el producto, pero no son una especificación completa.** El equipo deberá definir y justificar los datos de cada reporte, clasificación de casos, estados, reglas de asignación, validaciones, permisos, historial, cierre, excepciones y criterios verificables. No se podrá reemplazar el proceso de soporte por un CRUD aislado.

### Actividad 2: Definición de Requisitos para el Desarrollo

1. Preparar preguntas para una entrevista con el docente en el rol de representante de la organización.
2. Realizar la entrevista y registrar preguntas, respuestas, acuerdos y cuestiones pendientes.
3. Identificar actores, procesos, necesidades, reglas de negocio y restricciones.
4. Formular requisitos funcionales identificados como `RF-XX` y no funcionales como `RNF-XX`.
5. Elaborar historias de usuario o casos de uso con criterios de aceptación verificables.
6. Priorizar requisitos y proponer un alcance realizable, sin excluir las condiciones CA-01 a CA-06.
7. Presentar la especificación al docente para su revisión y aprobación.

**Entrega:** `docs/requisitos.md`, registro breve de entrevista, alcance y criterios de aceptación aprobados. Este documento delimita qué se implementará; no se evaluará por su extensión, sino por su claridad y utilidad para desarrollar y probar la aplicación. Los supuestos no confirmados deben identificarse.

### Actividad 3: Diseño de la Aplicación y de los Servicios Web

1. Proponer una arquitectura que identifique frontend, backend, API REST y persistencia.
2. Diseñar el modelo de datos, con entidades, atributos, claves y relaciones.
3. Diseñar los recorridos principales de los actores y los prototipos de interfaz.
4. Especificar los recursos de la API, métodos HTTP, formatos de solicitud y respuesta, validaciones y errores esperados.
5. Definir cómo se aplicarán las reglas de negocio y las restricciones de acceso.
6. Documentar las decisiones técnicas y su correspondencia con los requisitos.

**Entrega:** `docs/diseno.md`, diagramas, prototipos, modelo de datos y especificación de API. No se proporciona una estructura de carpetas obligatoria; el equipo deberá justificar cómo organiza las responsabilidades de su aplicación.

### Actividad 4: Desarrollo de Frontend, API REST y Persistencia

1. Configurar el repositorio y los entornos de desarrollo.
2. Implementar persistencia y relaciones entre los datos definidos.
3. Desarrollar la API REST con respuestas y códigos HTTP apropiados.
4. Implementar las interfaces web necesarias para cumplir los casos aprobados.
5. Integrar interfaz, API y base de datos.
6. Incorporar validación de datos, manejo de errores y controles de acceso definidos.
7. Verificar que un caso de soporte pueda reportarse, atenderse y cerrarse de principio a fin.

**Entrega:** código funcional de frontend y backend, base de datos configurada, documentación de endpoints, instrucciones reproducibles de ejecución y evidencia de al menos un flujo completo de reporte, atención y cierre desde la interfaz hasta la persistencia. Las operaciones CRUD solo deben implementarse cuando estén justificadas por el proceso.

### Actividad 5: Control de Versiones y Trabajo Colaborativo

Cada equipo deberá:

- Utilizar un repositorio de GitHub accesible para evaluación.
- Utilizar ramas para desarrollar cambios y *pull requests* para integrarlos.
- Redactar commits descriptivos que permitan comprender la evolución del sistema.
- Documentar en los pull requests el propósito, cambios realizados, pruebas efectuadas y requisitos asociados.
- Conservar evidencia de revisiones del código entre integrantes, cuando el equipo tenga más de una persona.
- Identificar los aportes verificables de cada integrante.

No se considerará evidencia suficiente una única carga final del proyecto, un historial compuesto exclusivamente por commits genéricos o una lista de contribuciones sin respaldo en GitHub.

### Actividad 6: Pruebas Funcionales de API, Reglas de Negocio e Integración

Diseñar y ejecutar **pruebas funcionales documentadas** para los endpoints y las reglas de negocio implementadas, con especial atención a las seis condiciones obligatorias. Se evaluarán las respuestas HTTP, los casos exitosos, las entradas inválidas, los recursos inexistentes, las restricciones de acceso y el flujo de integración entre interfaz, API y base de datos. Las pruebas se podrán realizar con las herramientas HTTP y de ejecución utilizadas durante el curso; no se exige escribir scripts de automatización.

| # | Prueba mínima | Evidencia esperada |
|---|---|---|
| 1 | Registro válido de caso de soporte | Caso persistido y recuperable |
| 2 | Registro con datos inválidos | Caso rechazado sin guardar información inválida |
| 3 | Consulta de caso existente | Información correcta del caso solicitado |
| 4 | Consulta de caso inexistente | Respuesta de error controlada |
| 5 | Gestión por personal autorizado | Acción de gestión válida registrada |
| 6 | Gestión por actor no autorizado | Operación impedida |
| 7 | Consulta de estado y responsable | Datos coherentes con las actuaciones registradas |
| 8 | Consulta de historial de intervenciones | Actuaciones vinculadas al caso correspondiente |
| 9 | Cierre de caso y consulta de resultado | Resultado final recuperable por el solicitante |
| 10 | Consulta consolidada de coordinación | Información de varios casos y sus responsables/estados |
| 11 | Persistencia e integridad de relaciones | Relaciones entre casos, actores e intervenciones consistentes |
| 12 | Integración interfaz–API–base de datos | Flujo completo de soporte demostrado desde la interfaz |

Para cada prueba se deberá documentar: identificador, requisito asociado, condiciones iniciales, pasos de ejecución, datos de entrada, resultado esperado, resultado obtenido, estado (aprobada/fallida), evidencia y, cuando aplique, método y código HTTP. Las evidencias pueden incluir capturas de solicitudes y respuestas, registros relevantes o capturas del funcionamiento de la interfaz. Deben permitir que el docente reproduzca la verificación. **No se exigen pruebas automatizadas, Postman CLI, Newman, pytest, Jest, Vitest ni GitHub Actions.**

### Actividad 7: Matriz de Trazabilidad y Sustentación

Crear `docs/trazabilidad.md` con la correspondencia entre condiciones obligatorias, requisitos, componentes implementados, pull requests y pruebas.

| Condición | Requisito aprobado | Implementación (ruta/componente) | Pull request | Prueba |
|---|---|---|---|---|
| CA-01 | Por completar | Por completar | Por completar | Por completar |
| CA-02 | Por completar | Por completar | Por completar | Por completar |
| CA-03 | Por completar | Por completar | Por completar | Por completar |
| CA-04 | Por completar | Por completar | Por completar | Por completar |
| CA-05 | Por completar | Por completar | Por completar | Por completar |
| CA-06 | Por completar | Por completar | Por completar | Por completar |

Durante la sustentación, el equipo deberá demostrar un caso completo, explicar las principales decisiones de diseño, repetir pruebas funcionales seleccionadas y mostrar el historial de contribuciones. El docente podrá preguntar individualmente a los integrantes sobre su participación.

---

## 7. Resultado Esperado del Proyecto

Al finalizar, cada equipo deberá disponer de:

- Una aplicación web funcional con frontend, API REST y base de datos.
- Una definición breve de requisitos y un diseño que permitan comprobar por qué se implementaron los componentes y servicios seleccionados.
- Un flujo de atención de casos de soporte tecnológico de principio a fin que cumpla CA-01 a CA-06.
- Validaciones, permisos y tratamiento de errores apropiados a las reglas definidas.
- Pruebas funcionales ejecutadas y resultados documentados.
- Un historial Git verificable de ramas, commits y pull requests.
- Una matriz de trazabilidad de requisitos, implementación y pruebas.
- Un README que permita instalar, ejecutar, revisar y evaluar la solución.

**Criterio de cumplimiento:** una pantalla aislada, una API sin interfaz, datos únicamente simulados o un CRUD genérico que no represente el proceso de soporte tecnológico no constituyen una solución completa.

### Criterios de evaluación

| Criterio | Peso |
|---|---:|
| Delimitación de requisitos y criterios de aceptación | 10 % |
| Diseño de arquitectura, API y modelo de datos | 10 % |
| Implementación frontend, backend, API REST y persistencia; integración funcional | 45 % |
| Pruebas funcionales de servicios web, reglas de negocio y documentación técnica | 20 % |
| Git y GitHub: commits, ramas, pull requests y aportes verificables | 15 % |
| **Total** | **100 %** |

La evaluación priorizará el funcionamiento real y la integración de la aplicación y los servicios web. La documentación de requisitos y diseño debe sustentar el desarrollo, no sustituirlo. La cantidad de pantallas o endpoints, por sí sola, no determina la calidad de la solución.

---

## 8. Parámetros para Elaboración del Informe

El informe final se presentará en formato **`README.md`** dentro del repositorio. No se aceptará como sustituto un informe externo en Word o PDF. Los documentos técnicos complementarios deben conservarse en el repositorio y enlazarse desde el README.

### Contenido del README.md

#### 1. Información General

- Nombre del proyecto y problema seleccionado.
- Integrantes y contribución de cada uno.
- Asignatura, fecha y enlace al repositorio.

#### 2. Descripción del Sistema

- Problema abordado, actores y alcance aprobado.
- Resumen de la solución y de sus restricciones.
- Enlace a `docs/requisitos.md`.

#### 3. Requisitos y Alcance

- Método utilizado para obtener la información.
- Evidencia de entrevista y decisiones confirmadas por el docente.
- Requisitos priorizados, historias de usuario/casos de uso y criterios de aceptación.

#### 4. Arquitectura, Diseño de API y Modelo de Datos

- Diagrama de componentes y responsabilidades.
- Modelo de datos y relaciones.
- Prototipos o capturas de interfaces.
- Justificación de tecnologías y enlaces a `docs/diseno.md`.

#### 5. Configuración del Entorno

- Requisitos de software, dependencias y comandos de instalación.
- Configuración de variables de entorno sin exponer secretos.
- Pasos para preparar la base de datos y ejecutar frontend y backend.
- Datos de prueba ficticios o instrucciones para generarlos.

#### 6. Servicios Web Implementados

Tabla de endpoints reales:

| Método | Ruta | Descripción | Requisito relacionado |
|---|---|---|---|
| Por completar | Por completar | Por completar | Por completar |

Incluir ejemplos de solicitudes y respuestas, validaciones y errores, y enlace a la documentación de API.

#### 7. Pruebas de API e Integración y Evidencias de Funcionamiento

- Tabla de pruebas de endpoints, reglas de negocio e integración con resultados y requisitos asociados.
- Pasos para reproducir las pruebas funcionales con las herramientas utilizadas en el curso.
- Evidencias del proceso completo y de casos inválidos.
- Enlace a la matriz de trazabilidad.

Guardar las evidencias en una carpeta `evidencias/` o enlazar los resultados generados de manera reproducible.

#### 8. Control de Versiones

- Enlace al repositorio y pull requests relevantes.
- Resumen verificable de aportes de cada integrante.
- Referencias a commits, ramas y pull requests que evidencien el desarrollo y la revisión de cambios.

#### 9. Conclusiones y Limitaciones

- Cumplimiento de las condiciones del problema.
- Dificultades técnicas verificadas y soluciones aplicadas.
- Restricciones o comportamientos pendientes dentro del alcance aprobado, si existen.

### Requisitos del Repositorio

El repositorio debe contener, al menos, estos recursos o equivalentes justificados:

```text
README.md
.gitignore
.env.example                  # Si se emplean variables de entorno
docs/
  requisitos.md
  diseno.md
  trazabilidad.md
evidencias/                   # Evidencias de pruebas funcionales y operación
```

También debe contener el código fuente, la definición reproducible de dependencias, los archivos necesarios para preparar la base de datos y las instrucciones para ejecutar la solución. Las pruebas funcionales deben registrarse en el README o en un documento enlazado, indicando pasos y evidencias para reproducirlas. No se deben incluir credenciales reales.

---

## 9. Disposición de Residuos

La actividad descrita en esta guía no genera residuos físicos o químicos. No se requiere un procedimiento específico de disposición de residuos.

---

## 10. Bibliografía

- Git. *Git Documentation*. https://git-scm.com/doc
- GitHub. *GitHub Docs*. https://docs.github.com/
- OpenAPI Initiative. *OpenAPI Specification*. https://spec.openapis.org/oas/latest.html
- MDN Web Docs. *HTTP*. https://developer.mozilla.org/en-US/docs/Web/HTTP
- MDN Web Docs. *Client-server overview*. https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview
- Chacon, S., & Straub, B. (2014). *Pro Git*. Apress. https://git-scm.com/book/en/v2
