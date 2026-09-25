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

- estudiantes;
- salas;
- reservaciones.

Entre las principales reglas implementadas se encuentran:

- carné de estudiante de exactamente 10 caracteres alfanuméricos;
- normalización de espacios iniciales y finales;
- validación de nombre y correo;
- capacidad positiva de salas;
- estudiante activo para reservar;
- sala disponible para reservar;
- fechas no pasadas;
- inicio en horas completas;
- horario de funcionamiento entre 08:00 y 20:00;
- duración de una o dos horas;
- cantidad de personas dentro de la capacidad;
- detección de superposición de reservaciones;
- reservaciones consecutivas permitidas;
- máximo de tres reservaciones activas presentes o futuras;
- las reservaciones canceladas no bloquean disponibilidad.

La lógica de negocio puede probarse directamente sin automatizar clics
sobre la interfaz gráfica.