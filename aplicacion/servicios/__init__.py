"""
Servicios principales de la aplicacion.
"""

from aplicacion.servicios.servicio_estudiantes import (
    buscar_estudiante,
    consultar_estudiantes,
    modificar_estudiante,
    registrar_estudiante,
)

from aplicacion.servicios.servicio_salas import (
    buscar_sala,
    consultar_salas,
    modificar_sala,
    registrar_sala,
)


__all__ = [
    "registrar_estudiante",
    "buscar_estudiante",
    "consultar_estudiantes",
    "modificar_estudiante",
    "registrar_sala",
    "buscar_sala",
    "consultar_salas",
    "modificar_sala",
]