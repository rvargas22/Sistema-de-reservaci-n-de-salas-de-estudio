"""
Componentes de persistencia del sistema.
"""

from aplicacion.persistencia.base_datos import obtener_conexion
from aplicacion.persistencia.inicializador import inicializar_base_datos
from aplicacion.persistencia.repositorio_reservaciones import (
    guardar_reservacion,
    obtener_reservacion_por_id,
)


__all__ = [
    "obtener_conexion",
    "inicializar_base_datos",
    "guardar_reservacion",
    "obtener_reservacion_por_id",
]