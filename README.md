# Sistema de reservación de salas de estudio

Aplicación de escritorio desarrollada en Python con PySide6 y SQLite para
la administración de estudiantes, salas y reservaciones de espacios de
estudio.

Proyecto desarrollado para el curso TI3603 — Calidad en Sistemas de
Información del Tecnológico de Costa Rica.

## Versión

La versión actual se encuentra identificada en el archivo:

`VERSION`

Versión candidata actual:

`1.0.0-rc2`

Esta versión corresponde a una versión candidata de la Fase 2 y debe
superar la verificación final antes de considerarse versión definitiva.

## Requisitos

Se requiere:

- Python 3.10 o superior.
- pip.
- un entorno gráfico compatible con Qt.
- Git, únicamente si se desea clonar el repositorio.

SQLite no requiere instalación adicional, ya que se utiliza mediante el
módulo `sqlite3` incluido con Python.

## Dependencias

Las dependencias externas se encuentran declaradas en:

`requirements.txt`

Actualmente se utilizan:

- PySide6 para la interfaz gráfica.
- pytest para las pruebas automatizadas.

## Obtener el proyecto

Repositorio:

`https://github.com/rvargas22/Sistema-de-reservaci-n-de-salas-de-estudio`

Clonar:

```bash
git clone https://github.com/rvargas22/Sistema-de-reservaci-n-de-salas-de-estudio.git
```

Entrar al directorio:

```bash
cd Sistema-de-reservaci-n-de-salas-de-estudio
```

## Crear el entorno virtual

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

En Windows CMD:

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

## Instalar dependencias

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecutar la aplicación

Ejecutar:

```bash
python main.py
```

La primera ejecución crea automáticamente la base SQLite si todavía no
existe.

La base de datos utilizada por defecto se encuentra en:

`datos/reservaciones.db`

La aplicación no necesita modificar el código fuente para determinar esta
ruta.

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

La inicialización es idempotente: ejecutar nuevamente la aplicación no
debe duplicar estos registros.

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

- registrar estudiantes.
- consultar estudiantes.
- modificar nombre y correo.
- activar o inactivar estudiantes.
- conservar el carné como identificador inmutable.

Las validaciones se ejecutan en la capa de servicios y reglas de negocio,
no directamente en la interfaz.

## Salas

El módulo de salas permite:

- consultar salas.
- registrar nuevas salas.
- modificar nombre.
- modificar capacidad.
- cambiar el estado entre disponible y fuera de servicio.

El código de una sala existente no se modifica.

## Disponibilidad

La aplicación permite consultar horarios disponibles considerando:

- sala.
- fecha.
- duración.
- reservaciones activas existentes.
- horario permitido.
- superposición.

La consulta de disponibilidad no crea una reservación.

## Reservaciones

La aplicación permite:

- crear reservaciones.
- consultar historial.
- modificar reservaciones activas.
- cancelar reservaciones.
- consultar por estudiante.
- validar disponibilidad.
- conservar reservaciones canceladas en el historial.

Las operaciones aplican las reglas de negocio antes de modificar la base
de datos.

## Recurrencia

El sistema permite crear series de reservaciones semanales.

Antes de guardar una serie se analizan sus ocurrencias.

También pueden cancelarse ocurrencias individuales o posteriores de una
serie.

Las escrituras de una serie se realizan de forma transaccional para evitar
datos parciales.

## Panel de control

El panel permite consultar reservaciones y utilizar filtros combinados por:

- fecha.
- sala.
- estado.

La información se obtiene nuevamente desde SQLite al refrescar la vista.

## Reportes

La aplicación permite generar reportes de reservaciones para un rango de
fechas.

Los reportes pueden exportarse en formato CSV utilizando codificación
UTF-8.

El archivo contiene encabezados y datos de estudiante, sala, fecha,
horario, duración, cantidad de personas y estado.

La cancelación del selector de destino no crea un archivo parcial.

## Auditoría

Las operaciones relevantes se registran automáticamente en un historial de
auditoría.

Los eventos contienen:

- fecha y hora.
- acción.
- entidad.
- identificador.
- detalle.

La auditoría se implementa mediante triggers de SQLite.

El historial es de solo lectura y las operaciones rechazadas no se
registran como acciones exitosas.

## Arquitectura

La aplicación mantiene separación entre responsabilidades.

Estructura principal:

```text
aplicacion/
├── interfaz/
├── modelos/
├── persistencia/
├── servicios/
└── validaciones/

datos/
documentacion/
evidencias/
pruebas/

main.py
requirements.txt
VERSION
pytest.ini
README.md
```

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

La lógica de negocio puede probarse directamente sin automatizar clics
sobre la interfaz gráfica.

## Persistencia

El sistema utiliza SQLite mediante el módulo estándar:

`sqlite3`

Cada conexión activa claves foráneas.

Las operaciones críticas utilizan transacciones y rollback ante errores.

La integridad puede comprobarse mediante:

- `PRAGMA integrity_check`.
- `PRAGMA foreign_key_check`.

## Ejecutar las pruebas

Con el entorno virtual activado:

```bash
pytest -v
```

Ejecución resumida:

```bash
pytest -q
```

## Pruebas de integración

```bash
pytest -m integracion -v
```

## Pruebas de contrato

```bash
pytest -m contrato -v
```

## Requisitos no funcionales

```bash
pytest -m rnf -v
```

## Rendimiento

El requisito RNF-09 utiliza una base temporal preparada con:

- 1 000 estudiantes.
- 5 000 reservaciones.

Para ejecutar la prueba:

```bash
pytest pruebas/test_rendimiento.py -v -s
```

Para conservar la evidencia:

```bash
GENERAR_EVIDENCIA_RNF09=1 pytest pruebas/test_rendimiento.py -q -s
```

La evidencia queda en:

`evidencias/rnf09_rendimiento.txt`

La preparación de los datos no forma parte del tiempo medido.

## Integridad de la base

Puede comprobarse manualmente con:

```bash
python -c "from aplicacion.persistencia import obtener_estado_integridad. print(obtener_estado_integridad())"
```

Un estado correcto debe indicar:

```text
integridad: ok
claves_foraneas: []
correcta: True
```

## Codificación

El proyecto utiliza UTF-8.

SQLite y las exportaciones CSV deben conservar correctamente caracteres
como:

`María Peña Muñoz`

`Cubículo individual`

## Manejo de errores

Las validaciones y reglas de negocio generan errores controlados.

En la interfaz gráfica, los errores se presentan mediante diálogos de Qt.

Una entrada inválida no debe cerrar la aplicación ni producir
modificaciones parciales en la base de datos.

## Archivos generados localmente

La base SQLite de trabajo no forma parte del código fuente versionado.

También se excluyen del repositorio elementos locales como:

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

Las rutas necesarias se construyen a partir de la ubicación del proyecto,
por lo que el repositorio puede ubicarse en directorios diferentes sin
modificar el código fuente.

## Versión candidata

La versión se identifica mediante tres elementos:

1. archivo `VERSION`.
2. commit de Git.
3. etiqueta Git correspondiente a la versión candidata.

Para consultar la versión:

```bash
cat VERSION
```

Resultado esperado para esta candidata:

```text
1.0.0-rc2
```

## Verificación antes de entregar

Antes de identificar una nueva versión candidata se debe ejecutar:

```bash
pytest -v
```

Luego:

```bash
python -c "from aplicacion.persistencia import obtener_estado_integridad. print(obtener_estado_integridad())"
```

Y finalmente:

```bash
python main.py
```

La versión candidata solamente debe etiquetarse después de confirmar que
la suite no presenta fallos.

## Identificación mediante Git

Crear el commit de la candidata:

```bash
git add README.md requirements.txt VERSION main.py pruebas/test_version_candidata.py
git commit -m "Preparar version candidata reproducible"
```

Crear la etiqueta:

```bash
git tag -a v1.0.0-rc2 -m "Version candidata 1.0.0-rc2"
```

Publicar el commit:

```bash
git push
```

Publicar la etiqueta:

```bash
git push origin v1.0.0-rc2
```

## Estado

`1.0.0-rc2` es una versión candidata.

La verificación global definitiva de la Fase 2 se realiza después de esta
preparación.