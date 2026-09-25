"""
Operaciones de persistencia relacionadas con reservaciones.
"""

import sqlite3
from dataclasses import replace

from aplicacion.modelos import Reservacion
from aplicacion.persistencia.base_datos import obtener_conexion


def _fila_a_reservacion(fila):
    """
    Convierte una fila de SQLite en una Reservacion.
    """

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


def guardar_reservacion(
    reservacion,
    ruta_base_datos=None,
):
    """
    Guarda una nueva reservacion.

    El identificador es generado exclusivamente
    por SQLite.
    """

    if reservacion.id is not None:
        raise ValueError(
            "Una reservación nueva no puede tener "
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

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return replace(
        reservacion,
        id=identificador,
    )


def obtener_reservacion_por_id(
    identificador,
    ruta_base_datos=None,
):
    """
    Busca una reservacion por su identificador.

    Devuelve None si no existe.
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

    return _fila_a_reservacion(fila)


def listar_reservaciones(
    ruta_base_datos=None,
):
    """
    Devuelve el historial completo de reservaciones.

    Incluye reservaciones activas y canceladas.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        filas = conexion.execute(
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
            ORDER BY
                fecha,
                hora_inicio,
                id
            """
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_reservacion(fila)
        for fila in filas
    ]


def listar_reservaciones_por_carne(
    carne,
    ruta_base_datos=None,
):
    """
    Devuelve todas las reservaciones asociadas
    con un estudiante.

    Incluye reservaciones activas y canceladas.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        filas = conexion.execute(
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
            WHERE carne_estudiante = ?
            ORDER BY
                fecha,
                hora_inicio,
                id
            """,
            (carne,),
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_reservacion(fila)
        for fila in filas
    ]


def actualizar_reservacion(
    reservacion,
    ruta_base_datos=None,
):
    """
    Actualiza una reservacion existente.

    El identificador no se modifica.
    """

    if reservacion.id is None:
        raise ValueError(
            "La reservación debe tener un identificador."
        )

    conexion = obtener_conexion(ruta_base_datos)

    try:
        cursor = conexion.execute(
            """
            UPDATE reservaciones
            SET
                carne_estudiante = ?,
                codigo_sala = ?,
                fecha = ?,
                hora_inicio = ?,
                duracion_horas = ?,
                cantidad_personas = ?,
                estado = ?
            WHERE id = ?
            """,
            (
                reservacion.carne_estudiante,
                reservacion.codigo_sala,
                reservacion.fecha,
                reservacion.hora_inicio,
                reservacion.duracion_horas,
                reservacion.cantidad_personas,
                reservacion.estado,
                reservacion.id,
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


def marcar_reservacion_cancelada(
    identificador,
    ruta_base_datos=None,
):
    """
    Cambia una reservacion activa al estado cancelada.

    La reservacion no se elimina del historial.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        cursor = conexion.execute(
            """
            UPDATE reservaciones
            SET estado = 'cancelada'
            WHERE id = ?
              AND estado = 'activa'
            """,
            (identificador,),
        )

        conexion.commit()

        actualizada = cursor.rowcount > 0

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return actualizada