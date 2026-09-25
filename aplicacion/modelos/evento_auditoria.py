"""
Modelo que representa un evento del historial
de auditoria.
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class EventoAuditoria:
    """
    Representa una accion exitosa registrada
    automáticamente por el sistema.

    El modelo es inmutable.
    """

    id: int
    fecha_hora: str
    accion: str
    entidad: str
    identificador: str
    detalle: str