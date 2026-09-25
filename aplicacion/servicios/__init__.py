"""
Servicios principales de la aplicacion.
"""

from aplicacion.servicios.servicio_auditoria import (
    consultar_evento_auditoria,
    consultar_historial_auditoria,
)

from aplicacion.servicios.servicio_disponibilidad import (
    consultar_horarios_disponibles,
    verificar_disponibilidad,
)

from aplicacion.servicios.servicio_estudiantes import (
    buscar_estudiante,
    consultar_estudiantes,
    modificar_estudiante,
    registrar_estudiante,
)

from aplicacion.servicios.servicio_panel import (
    consultar_panel,
)

from aplicacion.servicios.servicio_recurrencia import (
    analizar_serie_recurrente,
    cancelar_ocurrencia_recurrente,
    cancelar_ocurrencias_futuras,
    consultar_ocurrencias_serie,
    crear_serie_recurrente,
)

from aplicacion.servicios.servicio_reportes import (
    exportar_reporte_csv,
    generar_reporte_reservaciones,
)

from aplicacion.servicios.servicio_reservaciones import (
    buscar_reservaciones_estudiante,
    cancelar_reservacion,
    consultar_historial_reservaciones,
    crear_reservacion,
    modificar_reservacion,
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

    "crear_reservacion",
    "consultar_historial_reservaciones",
    "buscar_reservaciones_estudiante",
    "cancelar_reservacion",
    "modificar_reservacion",

    "verificar_disponibilidad",
    "consultar_horarios_disponibles",

    "analizar_serie_recurrente",
    "crear_serie_recurrente",
    "consultar_ocurrencias_serie",
    "cancelar_ocurrencia_recurrente",
    "cancelar_ocurrencias_futuras",

    "consultar_panel",

    "generar_reporte_reservaciones",
    "exportar_reporte_csv",

    "consultar_historial_auditoria",
    "consultar_evento_auditoria",
]