"""
Modelo de reservacion.
"""


class Reservacion:
    """Representa una reservacion de una sala."""

    def __init__(
        self,
        identificador,
        carne,
        codigo_sala,
        fecha,
        hora_inicio,
        duracion,
        cantidad_personas,
        estado="activa",
    ):
        self.identificador = identificador
        self.carne = carne
        self.codigo_sala = codigo_sala
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.duracion = duracion
        self.cantidad_personas = cantidad_personas
        self.estado = estado