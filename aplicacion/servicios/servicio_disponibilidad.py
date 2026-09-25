"""
Servicio para consultar la disponibilidad de salas.

Las consultas realizadas en este modulo no crean
ni modifican reservaciones.
"""

from datetime import datetime

from aplicacion.persistencia import (
    listar_reservaciones_activas_sala_fecha,
    obtener_sala_por_codigo,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    calcular_hora_fin,
    convertir_hora,
    hay_superposicion,
    validar_duracion,
    validar_fecha_reservacion,
    validar_hora_inicio,
    validar_horario,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)


def _intervalo_esta_libre(
    hora_inicio,
    duracion_horas,
    reservaciones_existentes,
):
    """
    Determina si un intervalo se encuentra libre
    respecto a las reservaciones recibidas.
    """

    inicio_nuevo = convertir_hora(
        hora_inicio
    )

    fin_nuevo = calcular_hora_fin(
        inicio_nuevo,
        duracion_horas,
    )

    for reservacion in reservaciones_existentes:

        inicio_existente = convertir_hora(
            reservacion.hora_inicio
        )

        fin_existente = calcular_hora_fin(
            inicio_existente,
            reservacion.duracion_horas,
        )

        if hay_superposicion(
            inicio_nuevo,
            fin_nuevo,
            inicio_existente,
            fin_existente,
        ):
            return False

    return True


def verificar_disponibilidad(
    codigo_sala,
    fecha,
    hora_inicio,
    duracion_horas,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Verifica si una sala se encuentra disponible
    para un intervalo concreto.

    Devuelve True cuando el intervalo esta libre
    y False cuando existe una reservacion activa
    que produce conflicto.

    Esta operacion no crea ninguna reservacion.
    """

    if ahora is None:
        ahora = datetime.now()

    codigo_sala = normalizar_codigo_sala(
        codigo_sala
    )

    sala = obtener_sala_por_codigo(
        codigo_sala,
        ruta_base_datos,
    )

    if sala is None:
        raise ErrorReglaNegocio(
            "La sala no existe."
        )

    fecha_validada = validar_fecha_reservacion(
        fecha,
        hoy=ahora.date(),
    )

    duracion_validada = validar_duracion(
        duracion_horas
    )

    if not sala.esta_disponible:
        return False

    hora_validada = validar_hora_inicio(
        hora_inicio,
        fecha_validada,
        ahora=ahora,
    )

    validar_horario(
        hora_validada,
        duracion_validada,
    )

    reservaciones = (
        listar_reservaciones_activas_sala_fecha(
            codigo_sala,
            fecha_validada.isoformat(),
            ruta_base_datos,
        )
    )

    return _intervalo_esta_libre(
        hora_validada,
        duracion_validada,
        reservaciones,
    )


def consultar_horarios_disponibles(
    codigo_sala,
    fecha,
    duracion_horas=1,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Devuelve los horarios de inicio disponibles para
    una sala, fecha y duracion determinadas.

    Los horarios se generan en horas completas dentro
    del periodo de funcionamiento de 08:00 a 20:00.

    La consulta no crea ni modifica reservaciones.
    """

    if ahora is None:
        ahora = datetime.now()

    codigo_sala = normalizar_codigo_sala(
        codigo_sala
    )

    sala = obtener_sala_por_codigo(
        codigo_sala,
        ruta_base_datos,
    )

    if sala is None:
        raise ErrorReglaNegocio(
            "La sala no existe."
        )

    fecha_validada = validar_fecha_reservacion(
        fecha,
        hoy=ahora.date(),
    )

    duracion_validada = validar_duracion(
        duracion_horas
    )

    if not sala.esta_disponible:
        return []

    reservaciones = (
        listar_reservaciones_activas_sala_fecha(
            codigo_sala,
            fecha_validada.isoformat(),
            ruta_base_datos,
        )
    )

    horarios_disponibles = []

    for hora in range(8, 20):

        hora_texto = f"{hora:02d}:00"

        try:
            hora_validada = validar_hora_inicio(
                hora_texto,
                fecha_validada,
                ahora=ahora,
            )

            validar_horario(
                hora_validada,
                duracion_validada,
            )

        except ErrorReglaNegocio:
            continue

        if _intervalo_esta_libre(
            hora_validada,
            duracion_validada,
            reservaciones,
        ):
            horarios_disponibles.append(
                hora_texto
            )

    return horarios_disponibles