"""
Modelo que representa una reservacion de sala.
"""

from dataclasses import dataclass


ESTADO_ACTIVA = "activa"
ESTADO_CANCELADA = "cancelada"


@dataclass(slots=True)
class Reservacion:
    """
    Representa una reservacion registrada en el sistema.

    El identificador puede ser None antes de guardar
    la reservacion en SQLite.
    """

    carne_estudiante: str
    codigo_sala: str
    fecha: str
    hora_inicio: str
    duracion_horas: int
    cantidad_personas: int
    estado: str = ESTADO_ACTIVA
    id: int | None = None

    @property
    def esta_activa(self):
        """
        Indica si la reservacion se encuentra activa.
        """

        return self.estado == ESTADO_ACTIVA