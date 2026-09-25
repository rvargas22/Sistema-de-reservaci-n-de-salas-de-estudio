"""
Modelo de reservacion.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(
    slots=True,
)
class Reservacion:
    """
    Representa una reservacion del sistema.

    El campo id conserva el identificador numerico
    utilizado internamente por SQLite.

    La propiedad identificador presenta el formato
    publico R0001, R0002, R0003...
    """

    carne_estudiante: str
    codigo_sala: str
    fecha: str
    hora_inicio: str
    duracion_horas: int
    cantidad_personas: int
    estado: str = "activa"
    id: int | None = None

    @property
    def esta_activa(
        self,
    ):
        """
        Indica si la reservacion se encuentra activa.
        """

        return (
            self.estado
            == "activa"
        )

    @property
    def identificador(
        self,
    ):
        """
        Devuelve el identificador visible.

        Ejemplos:

        1  -> R0001
        25 -> R0025
        """

        if self.id is None:
            return None

        return f"R{self.id:04d}"

    @property
    def hora_fin(
        self,
    ):
        """
        Calcula la hora final de la reservacion.
        """

        inicio = datetime.strptime(
            self.hora_inicio,
            "%H:%M",
        )

        fin = (
            inicio
            + timedelta(
                hours=self.duracion_horas
            )
        )

        return fin.strftime(
            "%H:%M"
        )