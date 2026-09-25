"""
Logica de aplicacion relacionada con reservaciones.
"""

from dataclasses import replace

from aplicacion.persistencia import (
    actualizar_reservacion,
    guardar_reservacion,
    listar_reservaciones,
    listar_reservaciones_por_carne,
    marcar_reservacion_cancelada,
    obtener_estudiante_por_carne,
    obtener_reservacion_por_id,
    obtener_sala_por_codigo,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
    validar_carne,
    validar_reservacion,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)


def _validar_identificador(
    identificador,
):
    """
    Verifica que un identificador sea un entero
    positivo.
    """

    if (
        isinstance(identificador, bool)
        or not isinstance(identificador, int)
    ):
        raise ErrorValidacion(
            "El identificador de la reservación "
            "debe ser un número entero."
        )

    if identificador <= 0:
        raise ErrorValidacion(
            "El identificador de la reservación "
            "debe ser mayor que cero."
        )

    return identificador


def crear_reservacion(
    carne_estudiante,
    codigo_sala,
    fecha,
    hora_inicio,
    duracion_horas,
    cantidad_personas,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Crea una nueva reservacion después de aplicar
    todas las reglas de negocio.
    """

    carne_estudiante = validar_carne(
        carne_estudiante
    )

    codigo_sala = normalizar_codigo_sala(
        codigo_sala
    )

    estudiante = obtener_estudiante_por_carne(
        carne_estudiante,
        ruta_base_datos,
    )

    sala = obtener_sala_por_codigo(
        codigo_sala,
        ruta_base_datos,
    )

    reservaciones_existentes = listar_reservaciones(
        ruta_base_datos
    )

    reservacion = validar_reservacion(
        estudiante=estudiante,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        duracion_horas=duracion_horas,
        cantidad_personas=cantidad_personas,
        reservaciones_existentes=reservaciones_existentes,
        ahora=ahora,
    )

    return guardar_reservacion(
        reservacion,
        ruta_base_datos,
    )


def consultar_historial_reservaciones(
    ruta_base_datos=None,
):
    """
    Devuelve el historial completo.

    Incluye reservaciones activas y canceladas.
    """

    return listar_reservaciones(
        ruta_base_datos
    )


def buscar_reservaciones_estudiante(
    carne,
    ruta_base_datos=None,
):
    """
    Busca todas las reservaciones de un estudiante.
    """

    carne = validar_carne(
        carne
    )

    return listar_reservaciones_por_carne(
        carne,
        ruta_base_datos,
    )


def cancelar_reservacion(
    identificador,
    ruta_base_datos=None,
):
    """
    Cancela una reservacion activa.

    La reservacion permanece en el historial
    conservando su identificador.
    """

    identificador = _validar_identificador(
        identificador
    )

    reservacion = obtener_reservacion_por_id(
        identificador,
        ruta_base_datos,
    )

    if reservacion is None:
        raise ErrorReglaNegocio(
            "La reservación no existe."
        )

    if reservacion.estado == "cancelada":
        raise ErrorReglaNegocio(
            "La reservación ya se encuentra cancelada."
        )

    actualizada = marcar_reservacion_cancelada(
        identificador,
        ruta_base_datos,
    )

    if not actualizada:
        raise ErrorReglaNegocio(
            "No fue posible cancelar la reservación."
        )

    return obtener_reservacion_por_id(
        identificador,
        ruta_base_datos,
    )


def modificar_reservacion(
    identificador,
    carne_estudiante=None,
    codigo_sala=None,
    fecha=None,
    hora_inicio=None,
    duracion_horas=None,
    cantidad_personas=None,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Modifica una reservacion activa.

    El identificador original se conserva.

    Primero se valida completamente la nueva version.
    Solo si todas las validaciones son exitosas se
    actualiza SQLite.
    """

    identificador = _validar_identificador(
        identificador
    )

    actual = obtener_reservacion_por_id(
        identificador,
        ruta_base_datos,
    )

    if actual is None:
        raise ErrorReglaNegocio(
            "La reservación no existe."
        )

    if actual.estado == "cancelada":
        raise ErrorReglaNegocio(
            "Una reservación cancelada no puede modificarse."
        )

    if carne_estudiante is None:
        carne_estudiante = actual.carne_estudiante
    else:
        carne_estudiante = validar_carne(
            carne_estudiante
        )

    if codigo_sala is None:
        codigo_sala = actual.codigo_sala
    else:
        codigo_sala = normalizar_codigo_sala(
            codigo_sala
        )

    if fecha is None:
        fecha = actual.fecha

    if hora_inicio is None:
        hora_inicio = actual.hora_inicio

    if duracion_horas is None:
        duracion_horas = actual.duracion_horas

    if cantidad_personas is None:
        cantidad_personas = actual.cantidad_personas

    estudiante = obtener_estudiante_por_carne(
        carne_estudiante,
        ruta_base_datos,
    )

    sala = obtener_sala_por_codigo(
        codigo_sala,
        ruta_base_datos,
    )

    reservaciones_existentes = [
        reservacion
        for reservacion in listar_reservaciones(
            ruta_base_datos
        )
        if reservacion.id != identificador
    ]

    validada = validar_reservacion(
        estudiante=estudiante,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        duracion_horas=duracion_horas,
        cantidad_personas=cantidad_personas,
        reservaciones_existentes=reservaciones_existentes,
        ahora=ahora,
    )

    modificada = replace(
        validada,
        id=actual.id,
        estado=actual.estado,
    )

    actualizada = actualizar_reservacion(
        modificada,
        ruta_base_datos,
    )

    if not actualizada:
        raise ErrorReglaNegocio(
            "No fue posible modificar la reservación."
        )

    return obtener_reservacion_por_id(
        identificador,
        ruta_base_datos,
    )