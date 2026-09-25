"""
Servicios de gestion de reservaciones.
"""

from dataclasses import replace

from aplicacion.persistencia import (
    actualizar_reservacion,
    guardar_reservacion,
    listar_reservaciones,
    listar_reservaciones_por_carne,
    marcar_reservacion_cancelada,
    obtener_reservacion_por_id,
    obtener_estudiante_por_carne,
    obtener_sala_por_codigo,
)

from aplicacion.persistencia.identificadores import (
    formatear_identificador_reservacion,
    numero_identificador_reservacion,
)

from aplicacion.validaciones.excepciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)

from aplicacion.validaciones.validador_estudiantes import (
    normalizar_carne,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)

from aplicacion.validaciones.validador_reservaciones import (
    validar_reservacion,
)


def _validar_identificador(
    identificador,
):
    """
    Convierte un ID numerico o R0001 al numero
    interno utilizado por SQLite.
    """

    try:
        return numero_identificador_reservacion(
            identificador
        )

    except (
        TypeError,
        ValueError,
    ) as error:
        raise ErrorValidacion(
            (
                "El identificador de la reservación "
                "debe utilizar el formato R0001."
            )
        ) from error


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
    carne = normalizar_carne(
        carne_estudiante
    )

    codigo = normalizar_codigo_sala(
        codigo_sala
    )

    estudiante = obtener_estudiante_por_carne(
        carne,
        ruta_base_datos,
    )

    sala = obtener_sala_por_codigo(
        codigo,
        ruta_base_datos,
    )

    existentes = listar_reservaciones(
        ruta_base_datos
    )

    reservacion = validar_reservacion(
        estudiante=estudiante,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        duracion_horas=duracion_horas,
        cantidad_personas=cantidad_personas,
        reservaciones_existentes=existentes,
        ahora=ahora,
    )

    return guardar_reservacion(
        reservacion,
        ruta_base_datos,
    )


def consultar_historial_reservaciones(
    ruta_base_datos=None,
):
    return listar_reservaciones(
        ruta_base_datos
    )


def buscar_reservaciones_estudiante(
    carne,
    ruta_base_datos=None,
):
    carne_normalizado = normalizar_carne(
        carne
    )

    estudiante = obtener_estudiante_por_carne(
        carne_normalizado,
        ruta_base_datos,
    )

    if estudiante is None:
        raise ErrorReglaNegocio(
            (
                "no existe un estudiante "
                "registrado con ese carné."
            )
        )

    return listar_reservaciones_por_carne(
        carne_normalizado,
        ruta_base_datos,
    )


def cancelar_reservacion(
    identificador,
    ruta_base_datos=None,
):
    numero = _validar_identificador(
        identificador
    )

    actual = obtener_reservacion_por_id(
        numero,
        ruta_base_datos,
    )

    identificador_visible = (
        formatear_identificador_reservacion(
            numero
        )
    )

    if actual is None:
        raise ErrorReglaNegocio(
            (
                "no existe una reservación "
                f"con ID {identificador_visible}."
            )
        )

    if actual.estado == "cancelada":
        raise ErrorReglaNegocio(
            (
                "La reservación ya se encuentra "
                "cancelada."
            )
        )

    cambiado = marcar_reservacion_cancelada(
        numero,
        ruta_base_datos,
    )

    if not cambiado:
        raise ErrorReglaNegocio(
            "No fue posible cancelar la reservación."
        )

    return obtener_reservacion_por_id(
        numero,
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
    numero = _validar_identificador(
        identificador
    )

    actual = obtener_reservacion_por_id(
        numero,
        ruta_base_datos,
    )

    identificador_visible = (
        formatear_identificador_reservacion(
            numero
        )
    )

    if actual is None:
        raise ErrorReglaNegocio(
            (
                "no existe una reservación "
                f"con ID {identificador_visible}."
            )
        )

    if actual.estado != "activa":
        raise ErrorReglaNegocio(
            (
                "Una reservación cancelada "
                "no puede modificarse."
            )
        )

    nuevo_carne = (
        actual.carne_estudiante
        if carne_estudiante is None
        else normalizar_carne(
            carne_estudiante
        )
    )

    nuevo_codigo = (
        actual.codigo_sala
        if codigo_sala is None
        else normalizar_codigo_sala(
            codigo_sala
        )
    )

    estudiante = obtener_estudiante_por_carne(
        nuevo_carne,
        ruta_base_datos,
    )

    sala = obtener_sala_por_codigo(
        nuevo_codigo,
        ruta_base_datos,
    )

    existentes = [
        reservacion
        for reservacion
        in listar_reservaciones(
            ruta_base_datos
        )
        if reservacion.id != actual.id
    ]

    candidata = validar_reservacion(
        estudiante=estudiante,
        sala=sala,
        fecha=(
            actual.fecha
            if fecha is None
            else fecha
        ),
        hora_inicio=(
            actual.hora_inicio
            if hora_inicio is None
            else hora_inicio
        ),
        duracion_horas=(
            actual.duracion_horas
            if duracion_horas is None
            else duracion_horas
        ),
        cantidad_personas=(
            actual.cantidad_personas
            if cantidad_personas is None
            else cantidad_personas
        ),
        reservaciones_existentes=existentes,
        ahora=ahora,
    )

    modificada = replace(
        candidata,
        id=actual.id,
        estado=actual.estado,
    )

    resultado = actualizar_reservacion(
        modificada,
        ruta_base_datos,
    )

    if resultado is None:
        raise ErrorReglaNegocio(
            (
                "No fue posible modificar "
                "la reservación."
            )
        )

    return resultado