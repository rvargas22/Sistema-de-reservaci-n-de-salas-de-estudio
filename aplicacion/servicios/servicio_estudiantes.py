"""
Logica de aplicacion relacionada con estudiantes.
"""

import sqlite3

from aplicacion.persistencia import (
    actualizar_estudiante,
    guardar_estudiante,
    listar_estudiantes,
    obtener_estudiante_por_carne,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    validar_carne,
    validar_datos_estudiante,
)


def registrar_estudiante(
    carne,
    nombre,
    correo,
    estado="activo",
    ruta_base_datos=None,
):
    """
    Registra un estudiante nuevo.

    Todo estudiante nuevo debe iniciar activo.
    """

    if (
        not isinstance(
            estado,
            str,
        )
        or estado.strip().lower()
        != "activo"
    ):
        raise ErrorReglaNegocio(
            "Todo estudiante nuevo debe "
            "registrarse con estado activo."
        )

    estudiante = validar_datos_estudiante(
        carne,
        nombre,
        correo,
        "activo",
    )

    existente = obtener_estudiante_por_carne(
        estudiante.carne,
        ruta_base_datos,
    )

    if existente is not None:
        raise ErrorReglaNegocio(
            "Ya existe un estudiante "
            "con ese carné."
        )

    try:
        guardar_estudiante(
            estudiante,
            ruta_base_datos,
        )

    except sqlite3.IntegrityError as error:
        raise ErrorReglaNegocio(
            "Ya existe un estudiante "
            "con ese carné."
        ) from error

    return estudiante


def buscar_estudiante(
    carne,
    ruta_base_datos=None,
):
    carne = validar_carne(
        carne
    )

    return obtener_estudiante_por_carne(
        carne,
        ruta_base_datos,
    )


def consultar_estudiantes(
    ruta_base_datos=None,
):
    return listar_estudiantes(
        ruta_base_datos
    )


def modificar_estudiante(
    carne,
    nombre=None,
    correo=None,
    estado=None,
    ruta_base_datos=None,
):
    carne = validar_carne(
        carne
    )

    estudiante_actual = (
        obtener_estudiante_por_carne(
            carne,
            ruta_base_datos,
        )
    )

    if estudiante_actual is None:
        raise ErrorReglaNegocio(
            "El estudiante no existe."
        )

    if nombre is None:
        nombre = (
            estudiante_actual.nombre
        )

    if correo is None:
        correo = (
            estudiante_actual.correo
        )

    if estado is None:
        estado = (
            estudiante_actual.estado
        )

    estudiante_modificado = (
        validar_datos_estudiante(
            estudiante_actual.carne,
            nombre,
            correo,
            estado,
        )
    )

    actualizado = actualizar_estudiante(
        estudiante_modificado,
        ruta_base_datos,
    )

    if not actualizado:
        raise ErrorReglaNegocio(
            "No fue posible actualizar "
            "el estudiante."
        )

    return estudiante_modificado