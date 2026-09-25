"""
Modelos principales del sistema.
"""

from aplicacion.modelos.estudiante import Estudiante
from aplicacion.modelos.reservacion import Reservacion
from aplicacion.modelos.sala import Sala


__all__ = [
    "Estudiante",
    "Sala",
    "Reservacion",
]