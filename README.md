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