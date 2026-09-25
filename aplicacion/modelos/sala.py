"""
Modelo que representa una sala de estudio.
"""

from dataclasses import dataclass


ESTADO_DISPONIBLE = "disponible"
ESTADO_FUERA_SERVICIO = "fuera_de_servicio"


@dataclass(slots=True)
class Sala:
    """
    Representa una sala disponible para el sistema
    de reservaciones.
    """

    codigo: str
    nombre: str
    capacidad: int
    estado: str = ESTADO_DISPONIBLE

    @property
    def esta_disponible(self):
        """
        Indica si la sala se encuentra disponible
        para nuevas reservaciones.
        """

        return self.estado == ESTADO_DISPONIBLE