"""
Servicios principales de la aplicacion.
"""

from aplicacion.servicios.servicio_estudiantes import (
    buscar_estudiante,
    consultar_estudiantes,
    modificar_estudiante,
    registrar_estudiante,
)


__all__ = [
    "registrar_estudiante",
    "buscar_estudiante",
    "consultar_estudiantes",
    "modificar_estudiante",
]