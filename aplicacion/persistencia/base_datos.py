"""
Administracion de la conexion con la base de datos SQLite.
"""

import sqlite3
from pathlib import Path


RUTA_DATOS = Path(__file__).resolve().parents[2] / "datos"
RUTA_BASE_DATOS = RUTA_DATOS / "reservaciones.db"


def obtener_conexion(ruta_base_datos=None):
    """
    Crea y devuelve una conexion con la base de datos SQLite.

    Si no se especifica una ruta, se utiliza la base de datos
    principal ubicada en la carpeta datos.
    """

    if ruta_base_datos is None:
        ruta_base_datos = RUTA_BASE_DATOS

    ruta_base_datos = Path(ruta_base_datos)

    ruta_base_datos.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conexion = sqlite3.connect(ruta_base_datos)

    # Activa las claves foraneas en SQLite.
    conexion.execute("PRAGMA foreign_keys = ON")

    # Permite acceder a los campos utilizando su nombre.
    conexion.row_factory = sqlite3.Row

    return conexion