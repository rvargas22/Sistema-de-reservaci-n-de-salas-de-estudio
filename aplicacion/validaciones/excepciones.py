"""
Excepciones utilizadas por la capa de validaciones.
"""


class ErrorValidacion(ValueError):
    """
    Se produce cuando un dato no cumple con el formato
    o las condiciones requeridas.
    """


class ErrorReglaNegocio(ValueError):
    """
    Se produce cuando una operacion incumple una regla
    de negocio del sistema.
    """