"""
Validaciones relacionadas con estudiantes.
"""

import re

from aplicacion.modelos import Estudiante
from aplicacion.validaciones.excepciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


PATRON_CARNE = re.compile(r"^[A-Za-z0-9]{10}$")

ESTADOS_ESTUDIANTE = {
    "activo",
    "inactivo",
}


def normalizar_carne(carne):
    """
    Elimina espacios iniciales y finales y convierte
    el carne a mayusculas.
    """

    if not isinstance(carne, str):
        raise ErrorValidacion(
            "El carné debe ser una cadena de texto."
        )

    return carne.strip().upper()


def validar_carne(carne):
    """
    Verifica que el carne contenga exactamente
    10 caracteres alfanumericos.
    """

    carne = normalizar_carne(carne)

    if not PATRON_CARNE.fullmatch(carne):
        raise ErrorValidacion(
            "El carné debe contener exactamente "
            "10 caracteres alfanuméricos y no puede "
            "contener espacios."
        )

    return carne


def validar_nombre(nombre):
    """
    Verifica que el nombre tenga al menos
    tres caracteres distintos de espacios.
    """

    if not isinstance(nombre, str):
        raise ErrorValidacion(
            "El nombre debe ser una cadena de texto."
        )

    nombre = nombre.strip()

    cantidad_caracteres = sum(
        1
        for caracter in nombre
        if not caracter.isspace()
    )

    if cantidad_caracteres < 3:
        raise ErrorValidacion(
            "El nombre debe contener al menos "
            "3 caracteres distintos de espacios."
        )

    return nombre


def validar_correo(correo):
    """
    Verifica las condiciones requeridas para el correo.

    Debe contener exactamente un signo @ y al menos
    un punto despues del signo @.
    """

    if not isinstance(correo, str):
        raise ErrorValidacion(
            "El correo debe ser una cadena de texto."
        )

    correo = correo.strip()

    if correo.count("@") != 1:
        raise ErrorValidacion(
            "El correo debe contener exactamente un signo @."
        )

    _, dominio = correo.split("@", 1)

    if "." not in dominio:
        raise ErrorValidacion(
            "El correo debe contener al menos un punto "
            "después del signo @."
        )

    return correo


def validar_estado_estudiante(estado):
    """
    Verifica que el estado del estudiante sea permitido.
    """

    if estado not in ESTADOS_ESTUDIANTE:
        raise ErrorValidacion(
            "El estado del estudiante debe ser "
            "'activo' o 'inactivo'."
        )

    return estado


def validar_carne_disponible(
    carne,
    estudiantes_existentes,
):
    """
    Verifica que el carne no pertenezca a otro estudiante.

    La comparacion no distingue mayusculas y minusculas.
    """

    carne_normalizado = validar_carne(carne)

    for estudiante in estudiantes_existentes:
        if (
            estudiante.carne.strip().casefold()
            == carne_normalizado.casefold()
        ):
            raise ErrorReglaNegocio(
                "Ya existe un estudiante con ese carné."
            )

    return carne_normalizado


def validar_datos_estudiante(
    carne,
    nombre,
    correo,
    estado="activo",
):
    """
    Valida y normaliza los datos de un estudiante.

    Devuelve una instancia de Estudiante lista para
    ser utilizada por la capa de servicios.
    """

    return Estudiante(
        carne=validar_carne(carne),
        nombre=validar_nombre(nombre),
        correo=validar_correo(correo),
        estado=validar_estado_estudiante(estado),
    )