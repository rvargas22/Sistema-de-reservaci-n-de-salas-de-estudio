"""
Punto de entrada de la aplicacion.
"""

import sys

from PySide6.QtWidgets import QApplication

from aplicacion.interfaz import (
    VentanaPrincipal,
)

from aplicacion.persistencia import (
    inicializar_base_datos,
)


def crear_ventana_principal(
    ruta_base_datos=None,
):
    """
    Inicializa la base y crea la ventana principal.

    Esta funcion facilita las pruebas de la interfaz
    utilizando una base temporal.
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
        "Sistema de reservación de salas de estudio"
    )

    ventana = crear_ventana_principal()

    ventana.show()

    return aplicacion.exec()


if __name__ == "__main__":
    sys.exit(
        iniciar_aplicacion()
    )