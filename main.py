"""
Punto de entrada del Sistema de reservacion de salas de estudio.
"""

from aplicacion.persistencia.inicializador import inicializar_base_datos


def iniciar_aplicacion():
    """
    Inicializa los componentes principales de la aplicacion.
    """

    inicializar_base_datos()

    print("Sistema de reservacion de salas de estudio")
    print("Base de datos inicializada correctamente.")


if __name__ == "__main__":
    iniciar_aplicacion()