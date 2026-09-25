"""
Operaciones de persistencia relacionadas con estudiantes.
"""

import sqlite3

from aplicacion.modelos import Estudiante
from aplicacion.persistencia.base_datos import obtener_conexion


def _fila_a_estudiante(fila):
    """
    Convierte una fila de SQLite en una instancia
    del modelo Estudiante.
    """

    if fila is None:
        return None

    return Estudiante(
        carne=fila["carne"],
        nombre=fila["nombre"],
        correo=fila["correo"],
        estado=fila["estado"],
    )


def guardar_estudiante(
    estudiante,
    ruta_base_datos=None,
):
    """
    Guarda un nuevo estudiante en la base de datos.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        conexion.execute(
            """
            INSERT INTO estudiantes (
                carne,
                nombre,
                correo,
                estado
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                estudiante.carne,
                estudiante.nombre,
                estudiante.correo,
                estudiante.estado,
            ),
        )

        conexion.commit()

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return estudiante


def obtener_estudiante_por_carne(
    carne,
    ruta_base_datos=None,
):
    """
    Busca un estudiante por su carne.

    La busqueda no distingue mayusculas
    y minusculas debido a COLLATE NOCASE.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        fila = conexion.execute(
            """
            SELECT
                carne,
                nombre,
                correo,
                estado
            FROM estudiantes
            WHERE carne = ?
            """,
            (carne,),
        ).fetchone()

    finally:
        conexion.close()

    return _fila_a_estudiante(fila)


def listar_estudiantes(
    ruta_base_datos=None,
):
    """
    Devuelve todos los estudiantes registrados,
    ordenados por carne.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        filas = conexion.execute(
            """
            SELECT
                carne,
                nombre,
                correo,
                estado
            FROM estudiantes
            ORDER BY carne
            """
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_estudiante(fila)
        for fila in filas
    ]


def actualizar_estudiante(
    estudiante,
    ruta_base_datos=None,
):
    """
    Actualiza nombre, correo y estado.

    El carne no se modifica.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        cursor = conexion.execute(
            """
            UPDATE estudiantes
            SET
                nombre = ?,
                correo = ?,
                estado = ?
            WHERE carne = ?
            """,
            (
                estudiante.nombre,
                estudiante.correo,
                estudiante.estado,
                estudiante.carne,
            ),
        )

        conexion.commit()

        actualizado = cursor.rowcount > 0

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return actualizado