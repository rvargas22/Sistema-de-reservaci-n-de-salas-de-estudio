"""
Modelo de estudiante.
"""


class Estudiante:
    """Representa un estudiante del sistema."""

    def __init__(self, carne, nombre, correo, estado="activo"):
        self.carne = carne
        self.nombre = nombre
        self.correo = correo
        self.estado = estado