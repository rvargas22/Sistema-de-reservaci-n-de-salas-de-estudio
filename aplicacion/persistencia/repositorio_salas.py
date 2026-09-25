"""
Operaciones de persistencia relacionadas con salas.
"""

import sqlite3

from aplicacion.modelos import Sala
from aplicacion.persistencia.base_datos import obtener_conexion


def _fila_a_sala(fila):
    """
    Convierte una fila de SQLite en una instancia de Sala.
    """

    if fila is None:
        return None

    return Sala(
        codigo=fila["codigo"],
        nombre=fila["nombre"],
        capacidad=fila["capacidad"],
        estado=fila["estado"],
    )


def guardar_sala(
    sala,
    ruta_base_datos=None,
):
    """
    Guarda una nueva sala en la base de datos.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        conexion.execute(
            """
            INSERT INTO salas (
                codigo,
                nombre,
                capacidad,
                estado
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                sala.codigo,
                sala.nombre,
                sala.capacidad,
                sala.estado,
            ),
        )

        conexion.commit()

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return sala


def obtener_sala_por_codigo(
    codigo,
    ruta_base_datos=None,
):
    """
    Busca una sala por su codigo.

    La busqueda no distingue entre mayusculas
    y minusculas.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        fila = conexion.execute(
            """
            SELECT
                codigo,
                nombre,
                capacidad,
                estado
            FROM salas
            WHERE codigo = ?
            """,
            (codigo,),
        ).fetchone()

    finally:
        conexion.close()

    return _fila_a_sala(fila)


def listar_salas(
    ruta_base_datos=None,
):
    """
    Devuelve todas las salas registradas,
    ordenadas por codigo.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        filas = conexion.execute(
            """
            SELECT
                codigo,
                nombre,
                capacidad,
                estado
            FROM salas
            ORDER BY codigo
            """
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_sala(fila)
        for fila in filas
    ]


def actualizar_sala(
    sala,
    ruta_base_datos=None,
):
    """
    Actualiza nombre, capacidad y estado de una sala.

    El codigo no se modifica.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        cursor = conexion.execute(
            """
            UPDATE salas
            SET
                nombre = ?,
                capacidad = ?,
                estado = ?
            WHERE codigo = ?
            """,
            (
                sala.nombre,
                sala.capacidad,
                sala.estado,
                sala.codigo,
            ),
        )

        conexion.commit()

        actualizada = cursor.rowcount > 0

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return actualizada


def obtener_maximo_personas_reservaciones_activas_desde(
    codigo_sala,
    fecha_desde,
    ruta_base_datos=None,
):
    """
    Obtiene la mayor cantidad de personas de las
    reservaciones activas de una sala a partir
    de una fecha determinada.

    Devuelve cero cuando no existen reservaciones.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        fila = conexion.execute(
            """
            SELECT
                COALESCE(MAX(cantidad_personas), 0)
                AS maximo_personas
            FROM reservaciones
            WHERE codigo_sala = ?
              AND estado = 'activa'
              AND fecha >= ?
            """,
            (
                codigo_sala,
                fecha_desde,
            ),
        ).fetchone()

    finally:
        conexion.close()

    return fila["maximo_personas"]