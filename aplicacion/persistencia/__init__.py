"""
Componentes de persistencia del sistema.
"""

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)

from aplicacion.persistencia.inicializador import (
    inicializar_base_datos,
)

from aplicacion.persistencia.repositorio_auditoria import (
    listar_eventos_auditoria,
    obtener_evento_auditoria,
)

from aplicacion.persistencia.repositorio_estudiantes import (
    actualizar_estudiante,
    guardar_estudiante,
    listar_estudiantes,
    obtener_estudiante_por_carne,
)

from aplicacion.persistencia.repositorio_recurrencia import (
    cancelar_ocurrencias_posteriores,
    guardar_serie_recurrente,
    listar_ocurrencias_serie,
    obtener_ocurrencia_serie,
    obtener_serie_recurrente_por_id,
)

from aplicacion.persistencia.repositorio_reservaciones import (
    actualizar_reservacion,
    consultar_reservaciones_panel,
    consultar_reservaciones_por_rango,
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
    "listar_reservaciones_por_carne",
    "listar_reservaciones_activas_sala_fecha",
    "actualizar_reservacion",
    "marcar_reservacion_cancelada",
    "consultar_reservaciones_panel",
    "consultar_reservaciones_por_rango",

    "guardar_serie_recurrente",
    "obtener_serie_recurrente_por_id",
    "listar_ocurrencias_serie",
    "obtener_ocurrencia_serie",
    "cancelar_ocurrencias_posteriores",

    "listar_eventos_auditoria",
    "obtener_evento_auditoria",
]