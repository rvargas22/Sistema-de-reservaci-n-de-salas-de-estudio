# Verificación final integral — Fase 2

## Sistema de reservación de salas de estudio

Este documento constituye la lista de control final de la versión
candidata antes del cierre técnico de la Fase 2.

La versión solamente puede declararse candidata aprobada cuando las
pruebas automatizadas, verificaciones manuales y requisitos aplicables
terminen sin defectos abiertos que contradigan la especificación.

---

## 1. Requisitos funcionales

### RF-01 — Cargar datos

Verificar:

- creación automática de SQLite.
- utilización de una base existente.
- ausencia de duplicación de datos iniciales.
- cinco salas iniciales.
- tres estudiantes iniciales.
- estado fuera_de_servicio de S04.
- primera ejecución sin cierre inesperado.

Estado: pendiente de ejecución final.

### RF-02 — Registrar estudiante

Verificar:

- carné.
- nombre.
- correo.
- validaciones.
- rechazo de duplicados.
- no guardar información parcial.
- estado inicial asignado automáticamente como activo.

Estado: pendiente de ejecución final.

### RF-03 — Consultar estudiantes

Verificar:

- carné.
- nombre.
- correo.
- estado.
- activos e inactivos.
- orden alfabético por nombre.
- estado vacío comprensible.

Estado: pendiente de ejecución final.

### RF-04 — Consultar salas

Verificar:

- código.
- nombre.
- capacidad.
- estado.
- orden por código.
- disponibles y fuera de servicio.

Estado: pendiente de ejecución final.

### RF-05 — Crear reservación

Verificar:

- existencia y estado de estudiante.
- existencia y estado de sala.
- fecha.
- hora.
- duración.
- capacidad.
- máximo por estudiante.
- conflictos.
- ID único.
- estado activa.
- confirmación visual con ID.
- ausencia de cambios ante rechazo.

Estado: pendiente de ejecución final.

### RF-06 — Consultar reservaciones

Verificar que el historial muestre:

- ID.
- estudiante.
- sala.
- fecha.
- hora de inicio.
- hora de fin.
- cantidad de personas.
- estado.

También:

- activas y canceladas.
- orden ascendente por fecha y hora.
- estado vacío comprensible.

Estado: pendiente de ejecución final.

### RF-07 — Buscar por estudiante

Verificar:

- búsqueda mediante carné.
- comparación sin distinguir mayúsculas y minúsculas.
- aviso cuando el estudiante no existe.
- aviso cuando no posee reservaciones.
- inclusión de activas y canceladas.

Estado: pendiente de ejecución final.

### RF-08 — Consultar disponibilidad

Verificar:

- sala.
- fecha.
- hora.
- duración.
- estado de sala.
- conflictos activos.
- operación exclusivamente de lectura.

Estado: pendiente de ejecución final.

### RF-09 — Cancelar reservación

Verificar:

- ID existente.
- rechazo si ya está cancelada.
- permanencia en historial.
- liberación del horario.
- persistencia inmediata.

Estado: pendiente de ejecución final.

### RF-10 — Salir

Verificar:

- opción visible para salir.
- cambios guardados antes del cierre.
- confirmación si existen cambios pendientes.
- cierre sin errores técnicos visibles.

Estado: pendiente de ejecución final.

### RF-11 — Modificar estudiante

Verificar:

- carné inmutable.
- nombre editable.
- correo editable.
- activar/inactivar.
- revalidación.
- historial conservado.
- estudiante inactivo sin nuevas reservaciones.
- confirmación visual.

Estado: pendiente de ejecución final.

### RF-12 — Gestionar salas

Verificar:

- registrar.
- modificar nombre.
- modificar capacidad.
- cambiar estado.
- código único.
- código inmutable.
- capacidad mayor que cero.
- no reducir capacidad por debajo de una reserva activa futura.
- fuera de servicio conserva historial.
- fuera de servicio rechaza nuevas reservas.

Estado: pendiente de ejecución final.

### RF-13 — Modificar reservación

Verificar:

- fecha.
- hora.
- duración.
- sala.
- cantidad.
- revalidación completa.
- conservación de ID.
- rollback lógico ante validación fallida.
- canceladas no modificables.

Estado: pendiente de ejecución final.

### RF-14 — Gestionar recurrencia

Verificar:

- series semanales.
- entre 2 y 8 ocurrencias.
- fechas válidas.
- disponibilidad.
- resumen de conflictos antes de guardar.
- cancelación individual.
- cancelación de ocurrencias futuras.

Estado: pendiente de ejecución final.

### RF-15 — Panel

Verificar que la pantalla principal presente:

- reservaciones del día.
- próximas reservaciones.
- ocupación por sala.
- actualización tras crear.
- actualización tras modificar.
- actualización tras cancelar.
- filtros combinados.
- estado vacío comprensible.

Estado: pendiente de ejecución final.

### RF-16 — Reportes

Verificar:

- fecha inicial obligatoria.
- fecha final obligatoria.
- rango válido.
- estudiante.
- sala.
- fecha.
- horario.
- cantidad.
- estado.
- CSV UTF-8.
- encabezados.
- cancelación del selector sin archivo incompleto.

Estado: pendiente de ejecución final.

### RF-17 — Auditoría

Verificar:

- creación.
- modificación.
- cancelación.
- fecha y hora.
- tipo de acción.
- entidad.
- identificador.
- consulta desde interfaz.
- solo lectura.
- errores de validación no registrados como acciones exitosas.

Estado: pendiente de ejecución final.

---

## 2. Reglas de negocio

Deben estar cubiertas las trece reglas:

- RN-01 estudiante registrado y activo.
- RN-02 fecha no pasada.
- RN-03 reservación de hoy posterior a la hora actual.
- RN-04 formato de 24 horas e inicio en hora completa.
- RN-05 horario 08:00–20:00.
- RN-06 duración 1 o 2 horas.
- RN-07 cantidad válida y capacidad.
- RN-08 sala fuera de servicio.
- RN-09 no superposición.
- RN-10 consecutivas permitidas.
- RN-11 máximo tres activas presentes/futuras.
- RN-12 canceladas permanecen y no bloquean.
- RN-13 ID cancelado nunca reutilizado.

El criterio de superposición debe permanecer:

`inicio_nuevo < fin_existente AND fin_nuevo > inicio_existente`

Estado: pendiente de ejecución final.

---

## 3. Requisitos no funcionales

Verificar:

- RNF-01 Python 3.10+.
- RNF-02 dependencias declaradas.
- RNF-03 portabilidad.
- RNF-04 usabilidad.
- RNF-05 robustez.
- RNF-06 integridad.
- RNF-07 mantenibilidad.
- RNF-08 UTF-8.
- RNF-09 rendimiento.
- RNF-10 testabilidad.

RNF-09 requiere:

- 1 000 estudiantes.
- 5 000 reservaciones.
- cada consulta menor de 2 segundos.

Estado: pendiente de ejecución final.

---

## 4. Persistencia e identificadores

Verificar:

- SQLite mediante sqlite3.
- creación automática de la base.
- integridad.
- ausencia de datos parciales.
- transacciones controladas.
- CSV UTF-8.
- ID de reservación con formato R0001, R0002, R0003....
- generación automática.
- continuidad después de reiniciar.
- no reutilización después de cancelar.

Estado: pendiente de ejecución final.

---

## 5. Vistas obligatorias

Deben existir:

1. Panel de control.
2. Gestión de estudiantes.
3. Gestión de salas.
4. Calendario / disponibilidad.
5. Gestión de reservaciones.
6. Reportes y exportación.
7. Historial de acciones.

Además:

- regresar al panel.
- cancelar una operación sin guardar.
- cierre controlado.
- errores visibles.
- no mostrar trazas técnicas a la persona usuaria.

Estado: pendiente de ejecución final.

---

## 6. Verificaciones manuales obligatorias

Aunque la mayor parte del sistema se encuentra automatizada, revisar
manualmente:

### Interfaz

- todos los textos son legibles.
- no existen textos blancos sobre fondos claros.
- botones identificables.
- tablas legibles.
- calendarios legibles.
- mensajes comprensibles.
- no aparecen trazas Python.

### Cancelación sin guardar

Iniciar una operación de:

- estudiante.
- sala.
- reservación.

y cancelarla antes de confirmar.

Confirmar que la base no cambió.

### Salida

Utilizar la opción Salir.

Confirmar:

- cierre controlado.
- confirmación cuando proceda.
- ninguna excepción visible.

### Recurrencia

Preparar una serie con conflicto.

Confirmar que el resumen sea visible antes de guardar.

### Panel

Confirmar visualmente:

- reservaciones de hoy.
- próximas reservaciones.
- ocupación por sala.

---

## 7. Comandos de verificación

Activar entorno:

`source .venv/bin/activate`

Verificación final específica:

`python -m pytest pruebas/test_verificacion_final_fase2.py -v`

Pruebas RNF:

`python -m pytest -m rnf -v`

Rendimiento:

`python -m pytest pruebas/test_rendimiento.py -v -s`

Suite completa:

`python -m pytest -v`

Integridad:

`python -c "from aplicacion.persistencia import obtener_estado_integridad. print(obtener_estado_integridad())"`

Aplicación:

`python main.py`

---

## 8. Política ante defectos finales

Si una prueba final falla:

1. no modificar el caso solamente para hacerlo pasar.
2. contrastar el resultado con la especificación.
3. corregir el producto cuando corresponda.
4. ejecutar la prueba específica.
5. ejecutar regresión completa.
6. actualizar la versión candidata.

Si `1.0.0-rc1` ya fue etiquetada y se requiere modificar código
productivo, no debe eliminarse ni reescribirse esa etiqueta.

La versión corregida debe identificarse, por ejemplo, como:

`1.0.0-rc2`

con una nueva etiqueta:

`v1.0.0-rc2`

---

## 9. Criterio final de aprobación

La Fase 2 puede considerarse técnicamente cerrada únicamente cuando:

- RF-01 a RF-17 están cubiertos.
- RN-01 a RN-13 están cubiertos.
- RNF-01 a RNF-10 están cubiertos.
- persistencia e identificadores cumplen la especificación.
- las siete vistas están disponibles.
- navegación y cierre son controlados.
- todas las pruebas automatizadas pasan.
- la prueba de rendimiento pasa.
- SQLite mantiene integridad.
- no existen defectos críticos abiertos.
- la versión candidata queda inequívocamente identificada.