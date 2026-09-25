"""
Administracion de conexiones SQLite.
"""

import sqlite3
from pathlib import Path


RUTA_DATOS = (
    Path(__file__).resolve().parents[2]
    / "datos"
)

RUTA_BASE_DATOS = (
    RUTA_DATOS
    / "reservaciones.db"
)

TIEMPO_ESPERA_SEGUNDOS = 5

TIEMPO_ESPERA_BLOQUEO_MS = 5000


def obtener_conexion(
    ruta_base_datos=None,
):
    """
    Crea una conexion SQLite configurada para
    preservar la integridad de los datos.

    Cada conexion:

    - activa claves foraneas;
    - establece tiempo de espera ante bloqueos;
    - permite acceder a columnas por nombre.
    """

    if ruta_base_datos is None:
        ruta_base_datos = (
            RUTA_BASE_DATOS
        )

    ruta_base_datos = Path(
        ruta_base_datos
    )

    ruta_base_datos.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conexion = sqlite3.connect(
        ruta_base_datos,
        timeout=TIEMPO_ESPERA_SEGUNDOS,
    )

    conexion.row_factory = (
        sqlite3.Row
    )

    conexion.execute(
        "PRAGMA foreign_keys = ON"
    )

    conexion.execute(
        (
            "PRAGMA busy_timeout = "
            f"{TIEMPO_ESPERA_BLOQUEO_MS}"
        )
    )

    return conexion