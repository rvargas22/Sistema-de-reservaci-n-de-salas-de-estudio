"""
Consultas de persistencia relacionadas
con el historial de auditoria.

Este repositorio es exclusivamente de lectura.
"""

from aplicacion.modelos import (
    EventoAuditoria,
)

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)


def _fila_a_evento(
    fila,
):
    """
    Convierte una fila SQLite en EventoAuditoria.
    """

    if fila is None:
        return None

    return EventoAuditoria(
        id=fila["id"],
        fecha_hora=fila["fecha_hora"],
        accion=fila["accion"],
        entidad=fila["entidad"],
        identificador=str(
            fila["identificador"]
        ),
        detalle=fila["detalle"],
    )


def listar_eventos_auditoria(
    ruta_base_datos=None,
):
    """
    Devuelve todos los eventos del historial
    de auditoria.

    La consulta es exclusivamente de lectura.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            """
            SELECT
                id,
                fecha_hora,
                accion,
                entidad,
                identificador,
                detalle

            FROM auditoria

            ORDER BY id
            """
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_evento(
            fila
        )
        for fila in filas
    ]


def obtener_evento_auditoria(
    identificador_evento,
    ruta_base_datos=None,
):
    """
    Obtiene un evento concreto del historial.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        fila = conexion.execute(
            """
            SELECT
                id,
                fecha_hora,
                accion,
                entidad,
                identificador,
                detalle

            FROM auditoria

            WHERE id = ?
            """,
            (
                identificador_evento,
            ),
        ).fetchone()

    finally:
        conexion.close()

    return _fila_a_evento(
        fila
    )