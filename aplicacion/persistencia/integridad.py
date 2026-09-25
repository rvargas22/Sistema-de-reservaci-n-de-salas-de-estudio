"""
Comprobaciones de integridad de la base de datos.
"""

import sqlite3

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)


def obtener_resultado_integridad(
    ruta_base_datos=None,
):
    """
    Ejecuta PRAGMA integrity_check.

    Devuelve el resultado textual producido
    por SQLite.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        fila = conexion.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        return fila[0]

    finally:
        conexion.close()


def obtener_errores_claves_foraneas(
    ruta_base_datos=None,
):
    """
    Ejecuta PRAGMA foreign_key_check.

    Devuelve una lista con las inconsistencias
    encontradas.

    Una lista vacia significa que no existen
    violaciones de claves foraneas.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        return [
            dict(fila)
            for fila in filas
        ]

    finally:
        conexion.close()


def obtener_estado_integridad(
    ruta_base_datos=None,
):
    """
    Devuelve un resumen de integridad de la
    base de datos.
    """

    resultado_integridad = (
        obtener_resultado_integridad(
            ruta_base_datos
        )
    )

    errores_foraneos = (
        obtener_errores_claves_foraneas(
            ruta_base_datos
        )
    )

    return {
        "integridad":
            resultado_integridad,

        "claves_foraneas":
            errores_foraneos,

        "correcta":
            (
                resultado_integridad
                == "ok"
                and not errores_foraneos
            ),
    }


def verificar_integridad_base_datos(
    ruta_base_datos=None,
):
    """
    Verifica que SQLite no reporte corrupcion
    ni inconsistencias de claves foraneas.

    Devuelve True cuando la base es consistente.
    """

    estado = obtener_estado_integridad(
        ruta_base_datos
    )

    if estado["integridad"] != "ok":
        raise sqlite3.DatabaseError(
            (
                "SQLite detectó un problema de "
                "integridad en la base de datos: "
                f"{estado['integridad']}"
            )
        )

    if estado["claves_foraneas"]:
        raise sqlite3.IntegrityError(
            (
                "Se detectaron inconsistencias "
                "de claves foráneas."
            )
        )

    return True