"""
Validaciones relacionadas con las salas.
"""

from aplicacion.modelos import Sala
from aplicacion.validaciones.excepciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


ESTADOS_SALA = {
    "disponible",
    "fuera_de_servicio",
}


def normalizar_codigo_sala(codigo):
    """
    Elimina espacios iniciales y finales y convierte
    el codigo de sala a mayusculas.
    """

    if not isinstance(codigo, str):
        raise ErrorValidacion(
            "El código de sala debe ser texto."
        )

    codigo = codigo.strip().upper()

    if not codigo:
        raise ErrorValidacion(
            "El código de sala no puede estar vacío."
        )

    return codigo


def validar_nombre_sala(nombre):
    """
    Normaliza el nombre de una sala.
    """

    if not isinstance(nombre, str):
        raise ErrorValidacion(
            "El nombre de la sala debe ser texto."
        )

    nombre = nombre.strip()

    if not nombre:
        raise ErrorValidacion(
            "El nombre de la sala no puede estar vacío."
        )

    return nombre


def validar_capacidad(capacidad):
    """
    Verifica que la capacidad sea un entero mayor que cero.
    """

    if (
        isinstance(capacidad, bool)
        or not isinstance(capacidad, int)
    ):
        raise ErrorValidacion(
            "La capacidad debe ser un número entero."
        )

    if capacidad <= 0:
        raise ErrorValidacion(
            "La capacidad debe ser mayor que cero."
        )

    return capacidad


def validar_estado_sala(estado):
    """
    Verifica el estado permitido de una sala.
    """

    if estado not in ESTADOS_SALA:
        raise ErrorValidacion(
            "El estado debe ser 'disponible' "
            "o 'fuera_de_servicio'."
        )

    return estado


def validar_codigo_disponible(
    codigo,
    salas_existentes,
):
    """
    Verifica que no exista otra sala con el mismo codigo.
    """

    codigo_normalizado = normalizar_codigo_sala(codigo)

    for sala in salas_existentes:
        if (
            sala.codigo.strip().casefold()
            == codigo_normalizado.casefold()
        ):
            raise ErrorReglaNegocio(
                "Ya existe una sala con ese código."
            )

    return codigo_normalizado


def validar_datos_sala(
    codigo,
    nombre,
    capacidad,
    estado="disponible",
):
    """
    Valida y normaliza los datos de una sala.
    """

    return Sala(
        codigo=normalizar_codigo_sala(codigo),
        nombre=validar_nombre_sala(nombre),
        capacidad=validar_capacidad(capacidad),
        estado=validar_estado_sala(estado),
    )