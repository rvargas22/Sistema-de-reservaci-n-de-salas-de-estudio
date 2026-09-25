"""
Modelo de reservacion.
"""

from dataclasses import dataclass


ESTADO_ACTIVA = "activa"
ESTADO_CANCELADA = "cancelada"


@dataclass(slots=True)
class Reservacion:
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
        return self.estado == ESTADO_ACTIVA

    @property
    def identificador(self):
        """
        Identificador publico de la reservacion.

        SQLite conserva internamente un entero
        AUTOINCREMENT, pero el identificador visible
        cumple el formato R0001, R0002, etc.
        """

        if self.id is None:
            return None

        return f"R{self.id:04d}"

    @property
    def hora_fin(self):
        """
        Calcula la hora de finalizacion a partir de
        la hora de inicio y la duracion.
        """

        hora, minuto = map(
            int,
            self.hora_inicio.split(":"),
        )

        minutos_totales = (
            hora * 60
            + minuto
            + self.duracion_horas * 60
        )

        hora_fin = (
            minutos_totales // 60
        )

        minuto_fin = (
            minutos_totales % 60
        )

        return (
            f"{hora_fin:02d}:"
            f"{minuto_fin:02d}"
        )