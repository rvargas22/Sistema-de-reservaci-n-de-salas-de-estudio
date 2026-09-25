"""
Logica de aplicacion relacionada con salas.
"""

import sqlite3
from datetime import date

from aplicacion.persistencia import (
    actualizar_sala,
    guardar_sala,
    listar_salas,
    obtener_maximo_personas_reservaciones_activas_desde,
    obtener_sala_por_codigo,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    validar_datos_sala,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)


def registrar_sala(
    codigo,
    nombre,
    capacidad,
    estado="disponible",
    ruta_base_datos=None,
):
    """
    Registra una nueva sala después de validar
    y normalizar sus datos.
    """

    sala = validar_datos_sala(
        codigo,
        nombre,
        capacidad,
        estado,
    )

    existente = obtener_sala_por_codigo(
        sala.codigo,
        ruta_base_datos,
    )

    if existente is not None:
        raise ErrorReglaNegocio(
            "Ya existe una sala con ese código."
        )

    try:
        guardar_sala(
            sala,
            ruta_base_datos,
        )

    except sqlite3.IntegrityError as error:
        raise ErrorReglaNegocio(
            "Ya existe una sala con ese código."
        ) from error

    return sala


def buscar_sala(
    codigo,
    ruta_base_datos=None,
):
    """
    Busca una sala utilizando su codigo.

    Devuelve None cuando no existe.
    """

    codigo = normalizar_codigo_sala(
        codigo
    )

    return obtener_sala_por_codigo(
        codigo,
        ruta_base_datos,
    )


def consultar_salas(
    ruta_base_datos=None,
):
    """
    Devuelve todas las salas registradas.
    """

    return listar_salas(
        ruta_base_datos,
    )


def modificar_sala(
    codigo,
    nombre=None,
    capacidad=None,
    estado=None,
    nuevo_codigo=None,
    ruta_base_datos=None,
    hoy=None,
):
    """
    Modifica los campos permitidos de una sala.

    El codigo de una sala es inmutable.

    Si se reduce la capacidad, se comprueba que
    ninguna reservacion activa presente o futura
    tenga una cantidad de personas superior
    a la nueva capacidad.
    """

    codigo = normalizar_codigo_sala(
        codigo
    )

    sala_actual = obtener_sala_por_codigo(
        codigo,
        ruta_base_datos,
    )

    if sala_actual is None:
        raise ErrorReglaNegocio(
            "La sala no existe."
        )

    if nuevo_codigo is not None:
        nuevo_codigo_normalizado = normalizar_codigo_sala(
            nuevo_codigo
        )

        if (
            nuevo_codigo_normalizado.casefold()
            != sala_actual.codigo.casefold()
        ):
            raise ErrorReglaNegocio(
                "El código de una sala no puede modificarse."
            )

    if nombre is None:
        nombre = sala_actual.nombre

    if capacidad is None:
        capacidad = sala_actual.capacidad

    if estado is None:
        estado = sala_actual.estado

    sala_modificada = validar_datos_sala(
        sala_actual.codigo,
        nombre,
        capacidad,
        estado,
    )

    if hoy is None:
        hoy = date.today()

    if (
        sala_modificada.capacidad
        < sala_actual.capacidad
    ):
        maximo_personas = (
            obtener_maximo_personas_reservaciones_activas_desde(
                sala_actual.codigo,
                hoy.isoformat(),
                ruta_base_datos,
            )
        )

        if (
            maximo_personas
            > sala_modificada.capacidad
        ):
            raise ErrorReglaNegocio(
                "No se puede reducir la capacidad "
                "porque existen reservaciones activas "
                "presentes o futuras con una cantidad "
                "de personas superior a la nueva capacidad."
            )

    actualizada = actualizar_sala(
        sala_modificada,
        ruta_base_datos,
    )

    if not actualizada:
        raise ErrorReglaNegocio(
            "No fue posible actualizar la sala."
        )

    return sala_modificada