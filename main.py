"""
Punto de entrada de la aplicacion.

Sistema de reservacion de salas de estudio.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from aplicacion.interfaz import (
    VentanaPrincipal,
)

from aplicacion.persistencia import (
    inicializar_base_datos,
)


RUTA_VERSION = (
    Path(__file__)
    .resolve()
    .with_name("VERSION")
)


def obtener_version_aplicacion():
    """
    Devuelve la version identificada en el
    archivo VERSION.

    Si el archivo no existe o esta vacio,
    devuelve 'desconocida'.
    """

    if not RUTA_VERSION.exists():
        return "desconocida"

    version = RUTA_VERSION.read_text(
        encoding="utf-8"
    ).strip()

    if not version:
        return "desconocida"

    return version


def crear_ventana_principal(
    ruta_base_datos=None,
):
    """
    Inicializa la base de datos y crea la
    ventana principal.

    La ruta puede sustituirse durante las
    pruebas para utilizar bases temporales.
    """

    inicializar_base_datos(
        ruta_base_datos
    )

    return VentanaPrincipal(
        ruta_base_datos
    )


def iniciar_aplicacion():
    """
    Inicia la aplicacion grafica.
    """

    aplicacion = QApplication(
        sys.argv
    )

    aplicacion.setApplicationName(
        (
            "Sistema de reservación "
            "de salas de estudio"
        )
    )

    aplicacion.setApplicationVersion(
        obtener_version_aplicacion()
    )

    ventana = crear_ventana_principal()

    ventana.show()

    return aplicacion.exec()


if __name__ == "__main__":
    sys.exit(
        iniciar_aplicacion()
    )