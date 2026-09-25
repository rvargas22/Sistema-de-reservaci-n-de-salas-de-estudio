# Matriz de cobertura de pruebas

## Sistema de reservación de salas de estudio

Este documento relaciona los requisitos funcionales, reglas de negocio y
requisitos no funcionales con las pruebas internas desarrolladas durante
la Fase 2.

La ejecución formal de los casos de TestRail corresponde a la etapa de
pruebas definida por el proyecto. Las pruebas incluidas en el repositorio
son pruebas internas de desarrollo realizadas con pytest.

---

## 1. Tipos de prueba utilizados

La suite contiene:

- pruebas de persistencia.
- pruebas de modelos.
- pruebas de identificadores.
- pruebas de validaciones.
- pruebas de servicios.
- pruebas de reglas de negocio.
- pruebas de disponibilidad.
- pruebas de recurrencia.
- pruebas de panel.
- pruebas de reportes.
- pruebas de auditoría.
- pruebas estructurales de interfaz.
- pruebas de transacciones e integridad.
- pruebas de integración.
- pruebas de contrato.
- pruebas de requisitos no funcionales.
- pruebas de rendimiento.

La lógica de negocio se prueba directamente mediante servicios y no
depende de automatización de clics en la interfaz gráfica.

---

## 2. Requisitos funcionales

| Requisito | Cobertura principal |
|---|---|
| RF-01 | `test_persistencia.py`, `test_contrato_aplicacion.py` |
| RF-02 | `test_servicio_estudiantes.py`, `test_integracion_flujos.py` |
| RF-03 | `test_servicio_estudiantes.py` |
| RF-04 | `test_servicio_salas.py` |
| RF-05 | `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |
| RF-06 | `test_servicio_reservaciones.py` |
| RF-07 | `test_servicio_reservaciones.py` |
| RF-08 | `test_disponibilidad.py`, `test_integracion_flujos.py` |
| RF-09 | `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |
| RF-10 | Interfaz, `main.py` y revisión final de cierre controlado |
| RF-11 | `test_servicio_estudiantes.py`, `test_integracion_flujos.py` |
| RF-12 | `test_servicio_salas.py` |
| RF-13 | `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |
| RF-14 | `test_recurrencia.py`, `test_integracion_flujos.py` |
| RF-15 | `test_panel.py`, `test_integracion_flujos.py` |
| RF-16 | `test_reportes.py`, `test_integracion_flujos.py` |
| RF-17 | `test_auditoria.py`, `test_integracion_flujos.py` |

---

## 3. Reglas de negocio

| Regla | Cobertura principal |
|---|---|
| RN-01 | `test_validaciones.py`, `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |
| RN-02 | `test_validaciones.py`, `test_servicio_reservaciones.py` |
| RN-03 | `test_validaciones.py`, `test_disponibilidad.py` |
| RN-04 | `test_validaciones.py` |
| RN-05 | `test_validaciones.py`, `test_disponibilidad.py` |
| RN-06 | `test_validaciones.py`, `test_disponibilidad.py` |
| RN-07 | `test_validaciones.py`, `test_servicio_reservaciones.py` |
| RN-08 | `test_validaciones.py`, `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |
| RN-09 | `test_validaciones.py`, `test_servicio_reservaciones.py`, `test_disponibilidad.py` |
| RN-10 | `test_validaciones.py`, `test_servicio_reservaciones.py`, `test_disponibilidad.py` |
| RN-11 | `test_validaciones.py`, `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |
| RN-12 | `test_servicio_reservaciones.py`, `test_disponibilidad.py`, `test_integracion_flujos.py` |
| RN-13 | `test_identificadores.py`, `test_servicio_reservaciones.py`, `test_integracion_flujos.py` |

---

## 4. Requisitos no funcionales

| Requisito | Categoría | Cobertura |
|---|---|---|
| RNF-01 | Compatibilidad | `test_contrato_aplicacion.py`, `test_requisitos_no_funcionales.py` |
| RNF-02 | Dependencias | `test_requisitos_no_funcionales.py`, `requirements.txt` |
| RNF-03 | Portabilidad | `test_requisitos_no_funcionales.py` |
| RNF-04 | Usabilidad | `test_interfaz.py`, `test_requisitos_no_funcionales.py`, revisión visual |
| RNF-05 | Robustez | `test_integridad_transacciones.py`, `test_requisitos_no_funcionales.py` |
| RNF-06 | Integridad | `test_integridad_transacciones.py`, `test_requisitos_no_funcionales.py` |
| RNF-07 | Mantenibilidad | `test_contrato_aplicacion.py`, `test_requisitos_no_funcionales.py` |
| RNF-08 | Codificación | `test_reportes.py`, `test_integracion_flujos.py`, `test_requisitos_no_funcionales.py` |
| RNF-09 | Rendimiento | `test_rendimiento.py`, `evidencias/rnf09_rendimiento.txt` |
| RNF-10 | Testabilidad | Suite de servicios, `test_contrato_aplicacion.py`, `test_requisitos_no_funcionales.py` |

---

## 5. Integridad de datos

La suite verifica:

- claves foráneas activas.
- restricciones CHECK.
- rollback ante errores.
- commit de operaciones exitosas.
- cierre de conexiones.
- atomicidad de series recurrentes.
- rollback de auditoría.
- `PRAGMA integrity_check`.
- `PRAGMA foreign_key_check`.

Pruebas principales:

- `test_persistencia.py`.
- `test_integridad_transacciones.py`.
- `test_integracion_flujos.py`.
- `test_requisitos_no_funcionales.py`.

---

## 6. Interfaz

La interfaz PySide6 se comprueba estructuralmente mediante:

- `test_interfaz.py`.
- `test_requisitos_no_funcionales.py`.

Se verifica:

- creación de la ventana principal.
- existencia de siete módulos.
- navegación.
- carga de estudiantes.
- carga de salas.
- disponibilidad.
- reservaciones.
- reportes.
- auditoría.
- aplicación de un estilo común.

Las reglas de negocio no se prueban mediante clics.

---

## 7. Flujos de integración

`test_integracion_flujos.py` comprueba:

1. estudiante → reservación → panel → reporte → auditoría.
2. disponibilidad → reservación → cancelación → disponibilidad.
3. modificación → persistencia → panel.
4. estudiante inactivo → rechazo.
5. sala fuera de servicio → rechazo.
6. máximo de tres reservaciones activas.
7. cancelación → liberación del límite.
8. continuidad de identificadores.
9. recurrencia → ocurrencias → panel.
10. cancelación individual en serie.
11. conflicto recurrente sin guardado parcial.
12. reporte CSV UTF-8.
13. filtros combinados.
14. modificación inválida sin alterar datos.
15. persistencia al reabrir la conexión.
16. integridad después de un flujo mixto.

---

## 8. Verificación de rendimiento

RNF-09 se prueba con:

- exactamente 1 000 estudiantes.
- exactamente 5 000 reservaciones.
- tres mediciones por consulta.
- límite máximo de 2 segundos.

Se miden:

- estudiantes.
- salas.
- panel completo.
- panel filtrado.
- búsqueda por estudiante.
- disponibilidad.
- reportes.
- auditoría.

La preparación de los datos no forma parte del tiempo medido.

La evidencia puede conservarse en:

`evidencias/rnf09_rendimiento.txt`

---

## 9. Testabilidad

RNF-10 queda cubierto porque la lógica se puede ejecutar directamente
desde pytest sin automatizar clics.

La arquitectura utilizada es:

Interfaz PySide6  
→ Servicios  
→ Validaciones / reglas  
→ Persistencia SQLite

Los servicios y la persistencia no dependen de la capa de interfaz.

---

## 10. Criterio de cierre de Fase 2 hasta Bloque 17

El estado se considera satisfactorio cuando:

- todas las pruebas funcionales pasan.
- todas las pruebas de integración pasan.
- las pruebas de contrato pasan.
- las pruebas RNF pasan.
- RNF-09 permanece por debajo de 2 segundos.
- no existen regresiones.
- SQLite conserva su integridad.
- la aplicación gráfica continúa iniciando correctamente.