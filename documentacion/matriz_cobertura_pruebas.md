# Matriz de cobertura de pruebas

## Sistema de reservación de salas de estudio

Este documento relaciona los requisitos funcionales, reglas de negocio y
requisitos no funcionales con las pruebas internas desarrolladas durante
la Fase 2.

La ejecución formal de los casos de TestRail corresponde a una etapa
posterior. Las pruebas incluidas en el repositorio son pruebas internas de
desarrollo realizadas con pytest.

---

## 1. Tipos de prueba utilizados

La suite contiene los siguientes niveles:

- pruebas de persistencia;
- pruebas de modelos;
- pruebas de validaciones;
- pruebas de servicios;
- pruebas de reglas de negocio;
- pruebas de interfaz estructural;
- pruebas de transacciones e integridad;
- pruebas de integración entre módulos;
- pruebas de contrato y arquitectura.

La lógica de negocio se prueba directamente mediante servicios y no
depende de automatización de clics en la interfaz gráfica.

---

## 2. Requisitos funcionales

| Requisito | Área cubierta | Pruebas principales |
|---|---|---|
| RF-01 | Inicialización y comportamiento base del sistema. La asociación textual exacta debe mantenerse conforme al enunciado original del proyecto. | test_persistencia.py, test_contrato_aplicacion.py |
| RF-02 | Gestión de estudiantes | test_servicio_estudiantes.py, test_integracion_flujos.py |
| RF-03 | Consulta/gestión de estudiantes | test_servicio_estudiantes.py |
| RF-04 | Gestión de salas | test_servicio_salas.py |
| RF-05 | Reservaciones | test_servicio_reservaciones.py, test_integracion_flujos.py |
| RF-06 | Reservaciones | test_servicio_reservaciones.py |
| RF-07 | Reservaciones | test_servicio_reservaciones.py |
| RF-08 | Consulta de disponibilidad | test_disponibilidad.py, test_integracion_flujos.py |
| RF-09 | Reservaciones | test_servicio_reservaciones.py |
| RF-10 | La descripción textual debe verificarse contra el enunciado original antes de cerrar la trazabilidad definitiva. | Suite general |
| RF-11 | Modificación y estado de estudiantes | test_servicio_estudiantes.py, test_integracion_flujos.py |
| RF-12 | Modificación de salas y código inmutable | test_servicio_salas.py |
| RF-13 | Gestión/modificación de reservaciones | test_servicio_reservaciones.py, test_integracion_flujos.py |
| RF-14 | Reservaciones recurrentes | test_recurrencia.py, test_integracion_flujos.py |
| RF-15 | Panel principal y filtros | test_panel.py, test_integracion_flujos.py |
| RF-16 | Reportes y exportación CSV | test_reportes.py, test_integracion_flujos.py |
| RF-17 | Auditoría | test_auditoria.py, test_integracion_flujos.py |

RF-01 y RF-10 deben contrastarse contra el texto literal del documento de
requisitos antes de emitir la matriz final de entrega. La cobertura técnica
existente no debe utilizarse para inventar o sustituir la descripción formal
de esos requisitos.

---

## 3. Reglas de negocio

| Regla | Cobertura |
|---|---|
| RN-01: estudiante registrado y activo para reservar | test_validaciones.py, test_servicio_reservaciones.py, test_integracion_flujos.py |
| RN-02: no reservar en fecha pasada | test_validaciones.py, test_servicio_reservaciones.py |
| RN-03: para el día actual la reservación debe iniciar después de la hora actual | test_validaciones.py, test_disponibilidad.py |
| RN-04: formato de 24 horas e inicio en hora completa | test_validaciones.py |
| RN-05: horario de 08:00 a 20:00 | test_validaciones.py, test_disponibilidad.py |
| RN-06: duración de 1 o 2 horas | test_validaciones.py, test_disponibilidad.py |
| RN-07: cantidad de personas mayor que cero y no superior a la capacidad | test_validaciones.py, test_servicio_reservaciones.py |
| RN-08: sala fuera de servicio no puede reservarse | test_validaciones.py, test_servicio_reservaciones.py, test_integracion_flujos.py |
| RN-09: no permitir superposición de reservaciones activas en la misma sala y fecha | test_validaciones.py, test_servicio_reservaciones.py, test_disponibilidad.py |
| RN-10: reservaciones consecutivas permitidas | test_validaciones.py, test_servicio_reservaciones.py, test_disponibilidad.py |
| RN-11: máximo tres reservaciones activas presentes/futuras por estudiante | test_validaciones.py, test_servicio_reservaciones.py, test_integracion_flujos.py |
| RN-12: cancelada permanece en historial y no bloquea | test_servicio_reservaciones.py, test_disponibilidad.py, test_integracion_flujos.py |
| RN-13: identificadores cancelados no se reutilizan | test_identificadores.py, test_servicio_reservaciones.py, test_integracion_flujos.py |

---

## 4. Requisitos no funcionales

| Requisito | Cobertura actual |
|---|---|
| RNF-01: Python 3.10 o superior | test_contrato_aplicacion.py |
| RNF-02 | Verificación formal pendiente de contrastar con el texto literal del requisito en el Bloque 17 |
| RNF-03 | Verificación formal pendiente de contrastar con el texto literal del requisito en el Bloque 17 |
| RNF-04 | Verificación formal pendiente de contrastar con el texto literal del requisito en el Bloque 17 |
| RNF-05 | Verificación formal pendiente de contrastar con el texto literal del requisito en el Bloque 17 |
| RNF-06 | Verificación formal pendiente de contrastar con el texto literal del requisito en el Bloque 17 |
| RNF-07: separación entre interfaz, negocio y persistencia | test_contrato_aplicacion.py |
| RNF-08: UTF-8 y conservación de tildes/ñ | test_reportes.py, test_contrato_aplicacion.py, test_integracion_flujos.py |
| RNF-09: 1000 estudiantes, 5000 reservaciones y consultas menores de 2 segundos | Se medirá formalmente en el Bloque 17 |
| RNF-10: lógica de negocio comprobable sin automatización de clics | suite de servicios, test_contrato_aplicacion.py |

---

## 5. Integridad de datos

La suite verifica:

- claves foráneas activas;
- restricciones CHECK;
- rollback ante errores;
- commit de operaciones exitosas;
- cierre de conexiones;
- atomicidad de series recurrentes;
- rollback de auditoría;
- PRAGMA integrity_check;
- PRAGMA foreign_key_check.

Pruebas principales:

- test_persistencia.py;
- test_integridad_transacciones.py;
- test_integracion_flujos.py.

---

## 6. Interfaz

La interfaz PySide6 se comprueba estructuralmente mediante
`test_interfaz.py`.

Se verifica:

- creación de la ventana principal;
- existencia de siete módulos;
- navegación;
- carga de estudiantes;
- carga de salas;
- carga de opciones de disponibilidad;
- carga de opciones de reservaciones;
- existencia de reportes;
- existencia de auditoría.

Las reglas de negocio no se prueban mediante clics.

---

## 7. Flujos de integración

`test_integracion_flujos.py` comprueba, entre otros, los siguientes
escenarios:

1. estudiante → reservación → panel → reporte → auditoría;
2. disponibilidad → reservación → cancelación → disponibilidad;
3. modificación → persistencia → panel;
4. estudiante inactivo → rechazo de reservación;
5. sala fuera de servicio → rechazo de reservación;
6. máximo de tres reservaciones activas;
7. cancelación → liberación del límite de tres;
8. continuidad de identificadores;
9. recurrencia → ocurrencias → panel;
10. cancelación individual dentro de una serie;
11. conflicto recurrente sin guardado parcial;
12. reporte CSV en UTF-8;
13. filtros combinados del panel;
14. modificación inválida sin alterar datos;
15. persistencia después de reabrir conexión;
16. integridad después de un flujo mixto.

---

## 8. Criterio de cierre del Bloque 16

El Bloque 16 se considera aprobado cuando:

- todas las pruebas de integración pasan;
- todas las pruebas de contrato pasan;
- no aparece ninguna regresión en las pruebas anteriores;
- la suite completa finaliza sin fallos;
- la matriz de cobertura queda disponible en `documentacion/`.

RNF-09 y la revisión detallada de los requisitos no funcionales se
realizarán en el Bloque 17.