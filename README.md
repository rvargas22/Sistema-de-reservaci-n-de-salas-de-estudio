# Sistema de reservación de salas de estudio

Aplicación de escritorio desarrollada en Python con PySide6 y SQLite para la administración de estudiantes, salas y reservaciones de espacios de estudio.

Proyecto desarrollado para el curso TI3603 — Calidad en Sistemas de Información del Tecnológico de Costa Rica.

## Versión

La versión actual se encuentra identificada en el archivo:

`VERSION`

Versión candidata actual:

`1.0.0-rc2`

Esta versión corresponde a la entrega de la Fase 2 del proyecto.

## Requisitos

Se requiere:

- Python 3.10 o superior.
- pip.
- un entorno gráfico compatible con Qt.
- Git, únicamente si se desea clonar el repositorio.

SQLite no requiere instalación adicional, ya que se utiliza mediante el módulo `sqlite3` incluido con Python.

## Dependencias

Las dependencias externas utilizadas durante el desarrollo se encuentran declaradas en:

`requirements.txt`

Actualmente se utilizan:

- PySide6 para la interfaz gráfica.
- pytest para comprobaciones internas realizadas durante el desarrollo.

Las pruebas con pytest se utilizaron como apoyo para verificar el comportamiento de distintos componentes durante la Fase 2. Los archivos de prueba no forman parte de esta entrega, ya que no corresponden todavía al entregable formal de pruebas cruzadas de las fases posteriores.

## Obtener el proyecto

Repositorio:

`https://github.com/rvargas22/Sistema-de-reservaci-n-de-salas-de-estudio`

Para clonar el repositorio:

```bash
git clone https://github.com/rvargas22/Sistema-de-reservaci-n-de-salas-de-estudio.git
```

Entrar al directorio:

```bash
cd Sistema-de-reservaci-n-de-salas-de-estudio
```

Si se utiliza el archivo ZIP de la entrega, basta con descomprimirlo y abrir una terminal en la carpeta principal del proyecto.

## Crear el entorno virtual

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```

En Windows CMD:

```cmd
py -m venv .venv
.venv\\Scripts\\activate.bat
```

## Instalar dependencias

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecutar la aplicación

Desde la carpeta principal del proyecto, ejecutar:

```bash
python main.py
```

La primera ejecución crea automáticamente la base de datos SQLite si todavía no existe.

La base de datos utilizada por defecto se crea en:

`datos/reservaciones.db`

La ruta se determina automáticamente a partir de la ubicación del proyecto, por lo que no es necesario modificar el código fuente.

## Datos iniciales

Al crear una base nueva se cargan los siguientes estudiantes:

| Carné | Nombre | Correo | Estado |
|---|---|---|---|
| A001234567 | Andrea Solano | andrea@universidad.ac.cr | activo |
| B009876543 | Carlos Méndez | carlos@universidad.ac.cr | activo |
| C004567890 | Daniela Rojas | daniela@universidad.ac.cr | inactivo |

También se cargan las siguientes salas:

| Código | Nombre | Capacidad | Estado |
|---|---|---:|---|
| S01 | Sala Biblioteca 1 | 4 | disponible |
| S02 | Sala Biblioteca 2 | 6 | disponible |
| S03 | Laboratorio de estudio | 10 | disponible |
| S04 | Sala multimedia | 8 | fuera_de_servicio |
| S05 | Cubículo individual | 1 | disponible |

La inicialización es idempotente: ejecutar nuevamente la aplicación no duplica estos registros.

## Módulos de la interfaz

La aplicación utiliza PySide6 y dispone de siete módulos principales:

1. Panel de control.
2. Gestión de estudiantes.
3. Gestión de salas.
4. Calendario y consulta de disponibilidad.
5. Gestión de reservaciones y recurrencia.
6. Reportes y exportación.
7. Historial de acciones.

La navegación se realiza desde el menú lateral de la ventana principal.

## Estudiantes

El módulo de estudiantes permite:

- registrar estudiantes;
- consultar estudiantes;
- modificar nombre y correo;
- activar o inactivar estudiantes;
- conservar el carné como identificador inmutable.

Las validaciones se ejecutan en la capa de servicios y reglas de negocio, no directamente en la interfaz.

## Salas

El módulo de salas permite:

- consultar salas;
- registrar nuevas salas;
- modificar nombre;
- modificar capacidad;
- cambiar el estado entre disponible y fuera de servicio.

El código de una sala existente no se modifica.

## Disponibilidad

La aplicación permite consultar horarios disponibles considerando:

- sala;
- fecha;
- duración;
- reservaciones activas existentes;
- horario permitido;
- superposición.

La consulta de disponibilidad no crea una reservación.

## Reservaciones

La aplicación permite:

- crear reservaciones;
- consultar el historial;
- modificar reservaciones activas;
- cancelar reservaciones;
- consultar por estudiante;
- validar disponibilidad;
- conservar reservaciones canceladas en el historial.

Las operaciones aplican las reglas de negocio antes de modificar la base de datos.

## Recurrencia

El sistema permite crear series de reservaciones semanales.

Antes de guardar una serie se analizan sus ocurrencias.

También pueden cancelarse ocurrencias individuales o las ocurrencias posteriores de una serie.

Las escrituras de una serie se realizan de forma transaccional para evitar datos parciales.

## Panel de control

El panel permite consultar reservaciones y utilizar filtros combinados por:

- fecha;
- sala;
- estado.

La información se obtiene nuevamente desde SQLite al refrescar la vista.

## Reportes

La aplicación permite generar reportes de reservaciones para un rango de fechas.

Los reportes pueden exportarse en formato CSV utilizando codificación UTF-8.

El archivo contiene encabezados y datos de estudiante, sala, fecha, horario, duración, cantidad de personas y estado.

La cancelación del selector de destino no crea un archivo parcial.

## Auditoría

Las operaciones relevantes se registran automáticamente en un historial de auditoría.

Los eventos contienen:

- fecha y hora;
- acción;
- entidad;
- identificador;
- detalle.

La auditoría se implementa mediante triggers de SQLite.

El historial es de solo lectura y las operaciones rechazadas no se registran como acciones exitosas.

## Arquitectura

La aplicación mantiene separación entre responsabilidades.

Estructura principal del código:

```text
aplicacion/
├── interfaz/
├── modelos/
├── persistencia/
├── servicios/
└── validaciones/

main.py
requirements.txt
VERSION
README.md
```

La carpeta `datos/` se crea automáticamente durante la ejecución cuando es necesaria para almacenar la base de datos local.

Flujo principal:

```text
Interfaz PySide6
       ↓
Servicios
       ↓
Validaciones y reglas
       ↓
Persistencia SQLite
```

La separación entre interfaz, lógica de negocio y persistencia permite mantener los componentes desacoplados y facilita su revisión.

## Persistencia

El sistema utiliza SQLite mediante el módulo estándar:

`sqlite3`

Cada conexión activa las claves foráneas.

Las operaciones críticas utilizan transacciones y rollback ante errores.

La integridad de la base puede comprobarse mediante:

- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`.

## Comprobaciones internas realizadas durante el desarrollo

Durante la Fase 2 se realizaron comprobaciones internas con pytest para apoyar la validación del desarrollo.

Estas comprobaciones se utilizaron durante la construcción y revisión de la solución, pero los archivos de prueba no se incluyen como parte del ZIP de esta fase.

La ejecución general utilizada durante el desarrollo fue:

```bash
pytest -v
```

La suite formal de pruebas, los casos de prueba trazables, las evidencias y los resultados de evaluación cruzada corresponden a fases posteriores del proyecto.

## Integridad de la base

Puede comprobarse manualmente desde la carpeta principal del proyecto con:

```bash
python -c "from aplicacion.persistencia import obtener_estado_integridad; print(obtener_estado_integridad())"
```

Un estado correcto debe mostrar un resultado equivalente a:

```text
{'integridad': 'ok', 'claves_foraneas': [], 'correcta': True}
```

## Codificación

El proyecto utiliza UTF-8.

SQLite y las exportaciones CSV conservan caracteres como:

`María Peña Muñoz`

`Cubículo individual`

## Manejo de errores

Las validaciones y reglas de negocio generan errores controlados.

En la interfaz gráfica, los errores se presentan mediante diálogos de Qt.

Una entrada inválida no debe cerrar la aplicación ni producir modificaciones parciales en la base de datos.

## Archivos generados localmente

La base SQLite de trabajo se genera localmente durante la ejecución y no necesita incluirse como parte del código fuente.

También deben excluirse del repositorio o de la entrega los archivos y directorios temporales generados por el entorno local, por ejemplo:

```text
.venv/
__pycache__/
*.pyc
.pytest_cache/
datos/*.db
.DS_Store
```

## Portabilidad

El código productivo no utiliza rutas personales absolutas.

Las rutas necesarias se construyen a partir de la ubicación del proyecto, por lo que puede ubicarse en directorios diferentes sin modificar el código fuente.

## Verificación básica de ejecución

Con el entorno virtual activado y las dependencias instaladas, se puede comprobar la ejecución mediante:

```bash
python main.py
```

La aplicación debe iniciar sin errores técnicos visibles y crear la base de datos local cuando esta no exista.

La integridad de la base también puede verificarse con:

```bash
python -c "from aplicacion.persistencia import obtener_estado_integridad; print(obtener_estado_integridad())"
```

## Estado

`1.0.0-rc2` corresponde a la versión candidata entregada al finalizar la Fase 2.

La solución incluye el código fuente, la configuración necesaria para instalar sus dependencias, los datos iniciales definidos por el proyecto y las instrucciones de ejecución reproducible.

Durante el desarrollo de esta fase también se realizaron comprobaciones internas con pytest como parte del proceso de validación del código.
"""

ruta = Path("/mnt/data/README_corregido_fase2_con_pytest.md")
ruta.write_text(contenido, encoding="utf-8")
print(ruta)