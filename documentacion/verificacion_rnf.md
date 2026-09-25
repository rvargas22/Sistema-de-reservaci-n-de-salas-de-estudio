# Verificación de requisitos no funcionales

## Sistema de reservación de salas de estudio

Este documento registra el método utilizado durante la Fase 2 para
verificar internamente los requisitos no funcionales RNF-01 a RNF-10.

La verificación combina pruebas automatizadas, revisión estructural y una
prueba específica de rendimiento.

---

## RNF-01 — Compatibilidad

**Requisito:** La aplicación debe ejecutarse con Python 3.10 o superior.

**Verificación:**

`pruebas/test_requisitos_no_funcionales.py`

La prueba comprueba que `sys.version_info` sea igual o superior a Python
3.10.

**Criterio de aprobación:** la prueba debe finalizar correctamente.

---

## RNF-02 — Dependencias

**Requisito:** La aplicación debe declarar todas sus dependencias y
ejecutarse mediante las instrucciones entregadas.

**Verificación:**

Se comprueba la existencia de `requirements.txt` y la declaración de las
dependencias externas utilizadas por el proyecto.

Las dependencias actuales son:

- PySide6.
- pytest.

La instalación se realiza con:

`pip install -r requirements.txt`

La aplicación se inicia con:

`python main.py`

**Criterio de aprobación:** el archivo de dependencias existe y contiene
las dependencias necesarias.

---

## RNF-03 — Portabilidad

**Requisito:** La aplicación debe ejecutarse en otra computadora sin
modificar rutas absolutas ni código fuente.

**Verificación:**

La prueba revisa el código productivo y rechaza rutas personales
hardcodeadas de macOS, Linux o Windows.

La ubicación de la base de datos se obtiene a partir de la estructura del
proyecto y no de una ruta personal fija.

**Criterio de aprobación:** no existen rutas personales absolutas en el
código productivo.

---

## RNF-04 — Usabilidad

**Requisito:** La interfaz debe mantener navegación, mensajes, etiquetas y
controles consistentes.

**Verificación:**

Se comprueba estructuralmente la existencia y navegación de los siguientes
módulos:

1. Panel de control.
2. Estudiantes.
3. Salas.
4. Disponibilidad.
5. Reservaciones.
6. Reportes.
7. Historial de acciones.

Las vistas utilizan componentes PySide6 y las utilidades compartidas de
interfaz para tablas, mensajes de error y confirmaciones.

**Criterio de aprobación:** las siete vistas están disponibles, la
navegación mantiene el orden definido y la aplicación utiliza el estilo
general configurado.

La revisión visual final debe confirmar además la legibilidad y
consistencia de mensajes, etiquetas y controles.

---

## RNF-05 — Robustez

**Requisito:** Una entrada inválida no debe cerrar el programa ni producir
datos parciales.

**Verificación:**

Se ejecutan entradas inválidas contra la capa de servicios y se compara el
estado de la base antes y después del rechazo.

La interfaz captura errores de validación, reglas de negocio y errores de
SQLite mediante mensajes de Qt.

**Criterio de aprobación:** la operación es rechazada, no se guardan datos
parciales y la integridad permanece correcta.

---

## RNF-06 — Integridad

**Requisito:** Las operaciones de escritura deben conservar la integridad
de la base de datos incluso cuando sean rechazadas.

**Verificación:**

La suite comprueba:

- claves foráneas.
- restricciones CHECK.
- transacciones.
- rollback.
- atomicidad de recurrencia.
- rollback de auditoría.
- `PRAGMA integrity_check`.
- `PRAGMA foreign_key_check`.

**Criterio de aprobación:** las operaciones rechazadas no modifican
parcialmente la base y la comprobación de integridad devuelve un estado
correcto.

---

## RNF-07 — Mantenibilidad

**Requisito:** La lógica de negocio, persistencia e interacción deben
separarse en funciones o módulos identificables.

**Verificación:**

La estructura principal mantiene:

`aplicacion/modelos/`

`aplicacion/validaciones/`

`aplicacion/persistencia/`

`aplicacion/servicios/`

`aplicacion/interfaz/`

Las capas de servicios y persistencia no importan PySide6 ni dependen de
la capa de interfaz.

**Criterio de aprobación:** las capas permanecen identificables y la
dependencia entre ellas conserva la dirección prevista.

---

## RNF-08 — Codificación

**Requisito:** La base de datos y las exportaciones deben conservar
correctamente tildes y la letra ñ.

**Verificación:**

Se almacenan y recuperan datos como:

`María Peña Muñoz`

y:

`Cubículo individual`

El reporte CSV se lee nuevamente utilizando codificación UTF-8.

**Criterio de aprobación:** los caracteres se conservan exactamente en
SQLite y en el archivo CSV.

---

## RNF-09 — Rendimiento

**Requisito:** Con 1 000 estudiantes y 5 000 reservaciones, cada consulta
debe responder en menos de 2 segundos en el equipo de prueba.

**Carga utilizada:**

- 1 000 estudiantes.
- 5 000 reservaciones.

La preparación de la base no se incluye dentro de los tiempos de consulta.

Se miden las siguientes operaciones:

- consulta de estudiantes.
- consulta de salas.
- panel completo.
- panel con filtros.
- búsqueda por estudiante.
- consulta de disponibilidad.
- reporte de reservaciones.
- historial de auditoría.

Cada consulta se ejecuta tres veces y se registran:

- tiempo mínimo.
- tiempo promedio.
- tiempo máximo.

Para cumplir el requisito, incluso el tiempo máximo registrado para cada
consulta debe permanecer por debajo de 2 segundos.

La evidencia se genera con:

`GENERAR_EVIDENCIA_RNF09=1 pytest pruebas/test_rendimiento.py -q -s`

El resultado se conserva en:

`evidencias/rnf09_rendimiento.txt`

El archivo de evidencia registra información básica del ambiente sin
guardar rutas personales.

---

## RNF-10 — Testabilidad

**Requisito:** La lógica de negocio debe poder probarse sin automatizar
clics sobre la interfaz gráfica.

**Verificación:**

Las pruebas unitarias y de integración invocan directamente validadores,
repositorios y servicios.

Las reglas de negocio no requieren simulación de ratón, teclado ni clics
sobre componentes PySide6.

**Criterio de aprobación:** la lógica se ejecuta satisfactoriamente desde
pytest utilizando directamente la capa de servicios.

---

# Ejecución

Pruebas generales de RNF:

`pytest pruebas/test_requisitos_no_funcionales.py -v`

Prueba de rendimiento:

`pytest pruebas/test_rendimiento.py -v -s`

Todas las pruebas RNF:

`pytest -m rnf -v`

Suite completa:

`pytest -v`

---

# Criterio de cierre

La revisión de requisitos no funcionales se considera aprobada cuando:

- las nueve pruebas generales de RNF pasan.
- la prueba RNF-09 pasa.
- ninguna consulta medida supera 2 segundos.
- la evidencia de rendimiento queda preservada.
- la suite completa no presenta regresiones.
- la aplicación gráfica continúa iniciando correctamente.