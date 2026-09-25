"""
Herramientas para controlar transacciones SQLite.
"""

from contextlib import contextmanager

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)


@contextmanager
def transaccion(
    ruta_base_datos=None,
):
    """
    Ejecuta varias operaciones dentro de una unica
    transaccion SQLite.

    Si todo finaliza correctamente:
        COMMIT

    Si ocurre cualquier excepcion:
        ROLLBACK

    La conexion siempre se cierra.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        conexion.execute(
            "BEGIN"
        )

        yield conexion

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()