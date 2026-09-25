"""
Modelo de sala.
"""


class Sala:
    """Representa una sala de estudio."""

    def __init__(self, codigo, nombre, capacidad, estado="disponible"):
        self.codigo = codigo
        self.nombre = nombre
        self.capacidad = capacidad
        self.estado = estado