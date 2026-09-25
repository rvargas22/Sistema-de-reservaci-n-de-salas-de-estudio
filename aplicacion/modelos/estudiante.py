"""
Modelo que representa a un estudiante del sistema.
"""

from dataclasses import dataclass


ESTADO_ACTIVO = "activo"
ESTADO_INACTIVO = "inactivo"


@dataclass(slots=True)
class Estudiante:
    """
    Representa un estudiante registrado en el sistema.
    """

    carne: str
    nombre: str
    correo: str
    estado: str = ESTADO_ACTIVO

    @property
    def esta_activo(self):
        """
        Indica si el estudiante se encuentra activo.
        """

        return self.estado == ESTADO_ACTIVO