"""
Servicio de consulta del historial de auditoria.

La auditoria es exclusivamente de lectura.
"""

from aplicacion.persistencia import (
    listar_eventos_auditoria,
    obtener_evento_auditoria,
)

from aplicacion.validaciones import (
    ErrorValidacion,
)


def consultar_historial_auditoria(
    ruta_base_datos=None,
):
    """
    Devuelve todos los eventos registrados
    en el historial de auditoria.
    """

    return listar_eventos_auditoria(
        ruta_base_datos
    )


def consultar_evento_auditoria(
    identificador_evento,
    ruta_base_datos=None,
):
    """
    Consulta un evento concreto.
    """

    if (
        isinstance(
            identificador_evento,
            bool,
        )
        or not isinstance(
            identificador_evento,
            int,
        )
    ):
        raise ErrorValidacion(
            "El identificador del evento "
            "debe ser un número entero."
        )

    if identificador_evento <= 0:
        raise ErrorValidacion(
            "El identificador del evento "
            "debe ser mayor que cero."
        )

    return obtener_evento_auditoria(
        identificador_evento,
        ruta_base_datos,
    )