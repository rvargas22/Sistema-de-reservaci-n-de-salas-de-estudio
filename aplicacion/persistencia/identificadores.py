"""
Conversión de identificadores visibles de reservación.

SQLite conserva internamente un identificador entero
autoincremental, mientras que la aplicación utiliza
el formato público R0001, R0002, R0003...
"""

import re


PATRON_IDENTIFICADOR = re.compile(
    r"^R(\d+)$",
    re.IGNORECASE,
)


def numero_identificador_reservacion(
    identificador,
):
    """
    Convierte un identificador visible o numérico
    al entero utilizado internamente por SQLite.

    Se aceptan enteros para conservar compatibilidad
    con operaciones internas existentes.
    """

    if isinstance(
        identificador,
        bool,
    ):
        raise ValueError(
            "Identificador de reservación inválido."
        )

    if isinstance(
        identificador,
        int,
    ):
        numero = identificador

    elif isinstance(
        identificador,
        str,
    ):
        texto = identificador.strip()

        if not texto:
            raise ValueError(
                "Identificador de reservación vacío."
            )

        if texto.isdigit():
            numero = int(
                texto
            )

        else:
            coincidencia = (
                PATRON_IDENTIFICADOR.fullmatch(
                    texto
                )
            )

            if coincidencia is None:
                raise ValueError(
                    "El identificador debe usar "
                    "el formato R0001."
                )

            numero = int(
                coincidencia.group(
                    1
                )
            )

    else:
        raise ValueError(
            "Identificador de reservación inválido."
        )

    if numero <= 0:
        raise ValueError(
            "El identificador debe ser mayor que cero."
        )

    return numero


def formatear_identificador_reservacion(
    identificador,
):
    """
    Devuelve el identificador público de una
    reservación.

    Ejemplos:

    1 -> R0001
    25 -> R0025
    10000 -> R10000
    """

    numero = numero_identificador_reservacion(
        identificador
    )

    return f"R{numero:04d}"