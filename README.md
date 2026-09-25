# Sistema de reservacion de salas de estudio

Proyecto final del curso TI3603 - Calidad en Sistemas de Informacion.

## Descripcion

Aplicacion de escritorio para la gestion de estudiantes, salas y reservaciones
de salas de estudio.

## Requisitos

- Python 3.10 o superior.

## Estructura general

- `aplicacion/modelos`: entidades principales del sistema.
- `aplicacion/persistencia`: acceso y administracion de SQLite.
- `aplicacion/servicios`: logica funcional del sistema.
- `aplicacion/validaciones`: validaciones y reglas de negocio.
- `aplicacion/interfaz`: interfaz grafica y navegacion.
- `datos`: archivos de persistencia local.
- `pruebas`: pruebas automatizadas.
- `documentacion`: documentacion complementaria.

## Ejecucion

Desde la raiz del proyecto:

```bash
python main.py

## Persistencia

La aplicación utiliza SQLite como mecanismo de persistencia local.

La base de datos se crea automáticamente en:

`datos/reservaciones.db`

Las tablas principales iniciales son:

- estudiantes
- salas
- reservaciones

La aplicación carga automáticamente los estudiantes y salas iniciales
cuando la base de datos se crea por primera vez.

La inicialización puede ejecutarse varias veces sin duplicar los datos.

Las claves foráneas de SQLite se encuentran habilitadas para mantener
la integridad referencial.

## Pruebas

Las pruebas automatizadas se ejecutan con:

```bash
pytest -v

## Modelos del dominio

La aplicación utiliza tres modelos principales:

### Estudiante

Representa a los estudiantes registrados en el sistema.

Atributos principales:

- carné
- nombre
- correo
- estado

Los estados utilizados son:

- activo
- inactivo

### Sala

Representa las salas que pueden ser utilizadas para reservaciones.

Atributos principales:

- código
- nombre
- capacidad
- estado

Los estados utilizados son:

- disponible
- fuera_de_servicio

### Reservación

Representa una reservación de una sala por parte de un estudiante.

Atributos principales:

- identificador
- carné del estudiante
- código de sala
- fecha
- hora de inicio
- duración
- cantidad de personas
- estado

Los estados utilizados son:

- activa
- cancelada

El identificador de una reservación puede ser `None` antes de que el
registro sea almacenado en SQLite.

## Identificadores de reservaciones

Los identificadores de las reservaciones son generados
automáticamente por SQLite.

La columna utilizada es:

`INTEGER PRIMARY KEY AUTOINCREMENT`

La aplicación no calcula ni asigna manualmente los identificadores.

Después de insertar una reservación se utiliza `lastrowid` para obtener
el identificador generado por SQLite.

La secuencia se mantiene aunque la aplicación se cierre y se vuelva
a ejecutar.

Una reservación cancelada conserva permanentemente su identificador.
Las nuevas reservaciones reciben identificadores diferentes y los
identificadores anteriores no se reutilizan.

## Validaciones y reglas de negocio

Las validaciones se encuentran separadas de la interfaz gráfica y de la
persistencia.

La carpeta `aplicacion/validaciones` contiene las reglas relacionadas con:

- estudiantes.
- salas.
- reservaciones.

Entre las principales reglas implementadas se encuentran:

- carné de estudiante de exactamente 10 caracteres alfanuméricos.
- normalización de espacios iniciales y finales.
- validación de nombre y correo.
- capacidad positiva de salas.
- estudiante activo para reservar.
- sala disponible para reservar.
- fechas no pasadas.
- inicio en horas completas.
- horario de funcionamiento entre 08:00 y 20:00.
- duración de una o dos horas.
- cantidad de personas dentro de la capacidad.
- detección de superposición de reservaciones.
- reservaciones consecutivas permitidas.
- máximo de tres reservaciones activas presentes o futuras.
- las reservaciones canceladas no bloquean disponibilidad.

La lógica de negocio puede probarse directamente sin automatizar clics
sobre la interfaz gráfica.

## Gestión de estudiantes

El módulo de estudiantes permite:

- registrar nuevos estudiantes.
- consultar todos los estudiantes registrados.
- buscar un estudiante por carné.
- modificar nombre.
- modificar correo.
- cambiar el estado entre activo e inactivo.

El carné funciona como identificador del estudiante y no se modifica
después del registro.

Antes de almacenar un estudiante se aplican las validaciones definidas
para carné, nombre, correo y estado.

Los carnés se normalizan a mayúsculas y su unicidad no distingue entre
mayúsculas y minúsculas.

Los estudiantes inactivos permanecen registrados en el sistema y
continúan apareciendo en las consultas e historial, pero posteriormente
no podrán generar nuevas reservaciones.

## Gestión de salas

El módulo de salas permite:

- registrar nuevas salas.
- consultar todas las salas.
- buscar una sala por código.
- modificar el nombre.
- modificar la capacidad.
- cambiar el estado entre disponible y fuera de servicio.

El código de una sala funciona como identificador y es inmutable después
de su registro.

Los códigos se normalizan a mayúsculas y su unicidad no distingue entre
mayúsculas y minúsculas.

La capacidad debe ser un número entero mayor que cero.

Cuando se intenta reducir la capacidad de una sala, la aplicación
verifica las reservaciones activas presentes o futuras. La operación se
rechaza si existe alguna reservación cuya cantidad de personas supere la
nueva capacidad.

Las reservaciones canceladas y las correspondientes a fechas pasadas no
bloquean una reducción de capacidad.

## Gestión de reservaciones

El módulo de reservaciones permite:

- crear nuevas reservaciones.
- consultar el historial completo.
- buscar reservaciones por carné de estudiante.
- cancelar reservaciones.
- modificar reservaciones activas.

Antes de guardar o modificar una reservación se aplican las reglas de
negocio definidas para estudiantes, salas, fechas, horarios, duración,
capacidad y disponibilidad.

Las reservaciones canceladas permanecen almacenadas en el historial y
dejan de bloquear la disponibilidad de la sala.

Una reservación cancelada no puede modificarse.

Las modificaciones conservan el identificador original. La aplicación
valida completamente los nuevos datos antes de actualizar SQLite; si
alguna validación falla, la reservación almacenada permanece sin cambios.

Los identificadores son generados automáticamente por SQLite y no se
reutilizan.

## Consulta de disponibilidad

La aplicación permite consultar los horarios disponibles de una sala sin
crear una reservación.

La consulta considera:

- código de sala.
- fecha.
- duración de una o dos horas.
- horario de funcionamiento entre 08:00 y 20:00.
- reservaciones activas existentes.
- estado de la sala.

Una reservación produce conflicto cuando se cumple:

`inicio_nuevo < fin_existente`
y
`fin_nuevo > inicio_existente`

Las reservaciones consecutivas están permitidas. Por ejemplo, una
reservación que termina a las 10:00 no impide otra que inicia exactamente
a las 10:00.

Las reservaciones canceladas no bloquean disponibilidad.

Las consultas de disponibilidad son operaciones de solo lectura y no
crean ni modifican registros en SQLite.

## Reservaciones recurrentes

La aplicación permite crear series semanales de reservaciones.

Una serie debe contener entre 2 y 8 ocurrencias.

Antes de guardar una serie se calculan y validan todas las fechas. La
aplicación genera un resumen que permite identificar las ocurrencias
disponibles y aquellas que presentan conflictos.

Si existe cualquier conflicto, la serie completa se rechaza y no se
guardan ocurrencias parciales.

Cuando todas las ocurrencias son válidas, la serie y sus reservaciones
se almacenan dentro de una única transacción SQLite.

Cada ocurrencia es una reservación independiente y posee su propio
identificador.

La aplicación permite cancelar:

- una ocurrencia individual.
- las ocurrencias posteriores a una ocurrencia seleccionada.
- opcionalmente, la seleccionada y todas las posteriores.

Las ocurrencias canceladas permanecen almacenadas en el historial.

### Relación entre recurrencia y límite general de reservaciones

RF-14 permite expresamente series de entre 2 y 8 ocurrencias. La
especificación no define cómo interactúa esta funcionalidad con el límite
general de tres reservaciones activas por estudiante.

Para mantener operativo el rango definido por RF-14, la creación de una
serie recurrente utiliza su propio límite de 2 a 8 ocurrencias y no aplica
el límite RN-11 durante la creación de la serie.

## Panel principal

El panel principal consulta directamente la información almacenada en
SQLite y no mantiene una copia independiente de las reservaciones.

Cada registro del panel puede incluir:

- identificador.
- carné del estudiante.
- nombre del estudiante.
- código de sala.
- nombre de sala.
- fecha.
- hora de inicio.
- duración.
- cantidad de personas.
- estado.

El panel permite aplicar opcionalmente filtros por fecha, sala y estado.

Los filtros pueden combinarse entre sí.

Los estados permitidos son:

- activa
- cancelada

Después de crear, modificar o cancelar una reservación, una nueva consulta
del panel refleja inmediatamente los datos almacenados en SQLite.

Las consultas del panel son operaciones de solo lectura y no modifican la
base de datos.

## Reportes y exportación CSV

La aplicación permite generar reportes de reservaciones utilizando un
rango obligatorio de fechas.

La fecha inicial y la fecha final son obligatorias.

La fecha final debe ser igual o posterior a la fecha inicial.

El rango es inclusivo, por lo que las reservaciones correspondientes a
ambas fechas límite forman parte del reporte.

Los reportes incluyen reservaciones activas y canceladas.

Cada fila contiene:

- identificador.
- carné del estudiante.
- nombre del estudiante.
- código de sala.
- nombre de sala.
- fecha.
- hora de inicio.
- duración.
- cantidad de personas.
- estado.

Los reportes pueden exportarse en formato CSV con codificación UTF-8.

La codificación conserva correctamente caracteres como tildes y la letra
ñ.

La exportación utiliza un archivo temporal y solamente crea o reemplaza el
archivo final después de completar correctamente la escritura.

Si el usuario cancela la selección del destino, no se crea ningún archivo.

La generación y exportación de reportes son operaciones de lectura y no
modifican las reservaciones almacenadas.

## Auditoría

La aplicación mantiene un historial automático de acciones exitosas.

La auditoría registra operaciones de creación, modificación y cancelación
sobre las principales entidades del sistema.

Cada evento contiene:

- identificador del evento.
- fecha y hora.
- acción.
- tipo de entidad.
- identificador de la entidad.
- detalle de la operación.

La auditoría se implementa mediante triggers de SQLite. Esto permite que
el evento se registre dentro de la misma transacción que modifica los
datos.

Si una operación falla o es rechazada por una validación, no se registra
como acción exitosa.

Las consultas y reportes no generan eventos de auditoría.

Los datos iniciales cargados automáticamente al crear la base tampoco se
registran como acciones del usuario.

El historial de auditoría es de solo lectura.

La aplicación no expone operaciones para modificar o eliminar eventos y
SQLite contiene triggers que bloquean cualquier UPDATE o DELETE sobre la
tabla de auditoría.