"""
Servicio relacionado con el panel principal.

El panel utiliza siempre informacion actualizada
directamente desde SQLite.
"""

from aplicacion.persistencia import (
    consultar_reservaciones_panel,
    obtener_sala_por_codigo,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
    convertir_fecha,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)


ESTADOS_RESERVACION = {
    "activa",
    "cancelada",
}


def _normalizar_estado_panel(
    estado,
):
    """
    Valida y normaliza un estado utilizado
    como filtro del panel.
    """

    if estado is None:
        return None

    if not isinstance(
        estado,
        str,
    ):
        raise ErrorValidacion(
            "El estado debe ser texto."
        )

    estado = estado.strip().lower()

    if estado not in ESTADOS_RESERVACION:
        raise ErrorValidacion(
            "El estado debe ser 'activa' "
            "o 'cancelada'."
        )

    return estado


def consultar_panel(
    fecha=None,
    codigo_sala=None,
    estado=None,
    ruta_base_datos=None,
):
    """
    Consulta las reservaciones del panel principal.

    Los filtros son opcionales y pueden combinarse
    entre si.

    Si no se especifica ningun filtro, devuelve todo
    el historial de reservaciones.

    Esta funcion es exclusivamente de lectura.
    """

    fecha_normalizada = None
    codigo_normalizado = None

    if fecha is not None:
        fecha_normalizada = convertir_fecha(
            fecha
        ).isoformat()

    if codigo_sala is not None:
        codigo_normalizado = (
            normalizar_codigo_sala(
                codigo_sala
            )
        )

        sala = obtener_sala_por_codigo(
            codigo_normalizado,
            ruta_base_datos,
        )

        if sala is None:
            raise ErrorReglaNegocio(
                "La sala no existe."
            )

    estado_normalizado = (
        _normalizar_estado_panel(
            estado
        )
    )

    return consultar_reservaciones_panel(
        fecha=fecha_normalizada,
        codigo_sala=codigo_normalizado,
        estado=estado_normalizado,
        ruta_base_datos=ruta_base_datos,
    )