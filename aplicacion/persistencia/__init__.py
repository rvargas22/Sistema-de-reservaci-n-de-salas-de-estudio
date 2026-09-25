"""
Componentes de persistencia del sistema.
"""

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)

from aplicacion.persistencia.inicializador import (
    inicializar_base_datos,
)

from aplicacion.persistencia.repositorio_estudiantes import (
    actualizar_estudiante,
    guardar_estudiante,
    listar_estudiantes,
    obtener_estudiante_por_carne,
)

from aplicacion.persistencia.repositorio_reservaciones import (
    actualizar_reservacion,
    guardar_reservacion,
    listar_reservaciones,
    listar_reservaciones_activas_sala_fecha,
    listar_reservaciones_por_carne,
    marcar_reservacion_cancelada,
    obtener_reservacion_por_id,
)

from aplicacion.persistencia.repositorio_salas import (
    actualizar_sala,
    guardar_sala,
    listar_salas,
    obtener_maximo_personas_reservaciones_activas_desde,
    obtener_sala_por_codigo,
)


__all__ = [
    "obtener_conexion",
    "inicializar_base_datos",

    "guardar_estudiante",
    "obtener_estudiante_por_carne",
    "listar_estudiantes",
    "actualizar_estudiante",

    "guardar_sala",
    "obtener_sala_por_codigo",
    "listar_salas",
    "actualizar_sala",
    "obtener_maximo_personas_reservaciones_activas_desde",

    "guardar_reservacion",
    "obtener_reservacion_por_id",
    "listar_reservaciones",
    "listar_reservaciones_activas_sala_fecha",
    "listar_reservaciones_por_carne",
    "actualizar_reservacion",
    "marcar_reservacion_cancelada",
]