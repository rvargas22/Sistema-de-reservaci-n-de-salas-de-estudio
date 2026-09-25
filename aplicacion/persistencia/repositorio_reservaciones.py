"""
Operaciones de persistencia para reservaciones.
"""

import sqlite3
from dataclasses import replace

from aplicacion.modelos import Reservacion
from aplicacion.persistencia.base_datos import obtener_conexion


def guardar_reservacion(
    reservacion,
    ruta_base_datos=None,
):
    """
    Guarda una nueva reservacion en SQLite.

    El identificador es generado exclusivamente por la
    base de datos.

    Devuelve una nueva instancia de Reservacion con el
    identificador asignado.
    """

    if reservacion.id is not None:
        raise ValueError(
            "Una reservacion nueva no puede tener "
            "un identificador asignado manualmente."
        )

    conexion = obtener_conexion(ruta_base_datos)

    try:
        cursor = conexion.execute(
            """
            INSERT INTO reservaciones (
                carne_estudiante,
                codigo_sala,
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reservacion.carne_estudiante,
                reservacion.codigo_sala,
                reservacion.fecha,
                reservacion.hora_inicio,
                reservacion.duracion_horas,
                reservacion.cantidad_personas,
                reservacion.estado,
            ),
        )

        conexion.commit()

        identificador = cursor.lastrowid

        return replace(
            reservacion,
            id=identificador,
        )

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def obtener_reservacion_por_id(
    identificador,
    ruta_base_datos=None,
):
    """
    Busca una reservacion utilizando su identificador.

    Devuelve None cuando el identificador no existe.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        fila = conexion.execute(
            """
            SELECT
                id,
                carne_estudiante,
                codigo_sala,
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado
            FROM reservaciones
            WHERE id = ?
            """,
            (identificador,),
        ).fetchone()

    finally:
        conexion.close()

    if fila is None:
        return None

    return Reservacion(
        carne_estudiante=fila["carne_estudiante"],
        codigo_sala=fila["codigo_sala"],
        fecha=fila["fecha"],
        hora_inicio=fila["hora_inicio"],
        duracion_horas=fila["duracion_horas"],
        cantidad_personas=fila["cantidad_personas"],
        estado=fila["estado"],
        id=fila["id"],
    )