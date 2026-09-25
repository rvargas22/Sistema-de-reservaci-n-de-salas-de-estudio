"""
Capa de validaciones y reglas de negocio.
"""

from aplicacion.validaciones.excepciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)

from aplicacion.validaciones.validador_estudiantes import (
    validar_carne,
    validar_carne_disponible,
    validar_correo,
    validar_datos_estudiante,
    validar_nombre,
)

from aplicacion.validaciones.validador_reservaciones import (
    hay_superposicion,
    validar_cantidad_personas,
    validar_duracion,
    validar_fecha_reservacion,
    validar_horario,
    validar_limite_reservaciones,
    validar_reservacion,
    validar_sin_superposicion,
)

from aplicacion.validaciones.validador_salas import (
    validar_capacidad,
    validar_codigo_disponible,
    validar_datos_sala,
)


__all__ = [
    "ErrorValidacion",
    "ErrorReglaNegocio",
    "validar_carne",
    "validar_carne_disponible",
    "validar_correo",
    "validar_datos_estudiante",
    "validar_nombre",
    "validar_capacidad",
    "validar_codigo_disponible",
    "validar_datos_sala",
    "validar_fecha_reservacion",
    "validar_duracion",
    "validar_horario",
    "validar_cantidad_personas",
    "hay_superposicion",
    "validar_sin_superposicion",
    "validar_limite_reservaciones",
    "validar_reservacion",
]