"""
Validaciones y reglas de negocio relacionadas
con las reservaciones.
"""

import re
from datetime import date, datetime, time, timedelta

from aplicacion.modelos import Reservacion
from aplicacion.validaciones.excepciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


PATRON_HORA = re.compile(
    r"^\d{2}:\d{2}$"
)


def convertir_fecha(fecha):
    """
    Convierte una fecha a un objeto date.

    Se acepta un objeto date o una cadena AAAA-MM-DD.
    """

    if isinstance(fecha, datetime):
        return fecha.date()

    if isinstance(fecha, date):
        return fecha

    if isinstance(fecha, str):
        try:
            return datetime.strptime(
                fecha.strip(),
                "%Y-%m-%d",
            ).date()

        except ValueError as error:
            raise ErrorValidacion(
                "La fecha debe utilizar el formato AAAA-MM-DD."
            ) from error

    raise ErrorValidacion(
        "La fecha proporcionada no es válida."
    )


def convertir_hora(hora):
    """
    Convierte una hora a un objeto time.

    El formato esperado es HH:MM en horario de 24 horas.
    """

    if isinstance(hora, time):
        return hora

    if not isinstance(hora, str):
        raise ErrorValidacion(
            "La hora proporcionada no es válida."
        )

    hora = hora.strip()

    if not PATRON_HORA.fullmatch(hora):
        raise ErrorValidacion(
            "La hora debe utilizar el formato HH:MM."
        )

    try:
        return datetime.strptime(
            hora,
            "%H:%M",
        ).time()

    except ValueError as error:
        raise ErrorValidacion(
            "La hora proporcionada no es válida."
        ) from error


def validar_fecha_reservacion(
    fecha,
    hoy=None,
):
    """
    Verifica que la fecha de reservacion no sea pasada.
    """

    fecha = convertir_fecha(fecha)

    if hoy is None:
        hoy = date.today()

    if fecha < hoy:
        raise ErrorReglaNegocio(
            "No se pueden crear reservaciones "
            "para fechas pasadas."
        )

    return fecha


def validar_hora_inicio(
    hora_inicio,
    fecha,
    ahora=None,
):
    """
    Verifica el formato, hora completa y condiciones
    correspondientes al inicio de una reservacion.
    """

    hora_inicio = convertir_hora(hora_inicio)
    fecha = convertir_fecha(fecha)

    if hora_inicio.minute != 0:
        raise ErrorReglaNegocio(
            "La reservación debe iniciar exactamente "
            "a una hora completa."
        )

    if hora_inicio < time(8, 0):
        raise ErrorReglaNegocio(
            "Las reservaciones no pueden iniciar "
            "antes de las 08:00."
        )

    if hora_inicio > time(20, 0):
        raise ErrorReglaNegocio(
            "Las reservaciones no pueden iniciar "
            "después de las 20:00."
        )

    if ahora is None:
        ahora = datetime.now()

    if fecha == ahora.date():
        if hora_inicio.hour <= ahora.hour:
            raise ErrorReglaNegocio(
                "Una reservación para el día actual "
                "debe iniciar después de la hora actual."
            )

    return hora_inicio


def validar_duracion(duracion_horas):
    """
    Verifica que una reservacion dure una o dos horas.
    """

    if (
        isinstance(duracion_horas, bool)
        or not isinstance(duracion_horas, int)
    ):
        raise ErrorValidacion(
            "La duración debe ser un número entero."
        )

    if duracion_horas not in (1, 2):
        raise ErrorReglaNegocio(
            "La duración debe ser de 1 o 2 horas."
        )

    return duracion_horas


def calcular_hora_fin(
    hora_inicio,
    duracion_horas,
):
    """
    Calcula la hora de finalizacion de una reservacion.
    """

    hora_inicio = convertir_hora(hora_inicio)
    validar_duracion(duracion_horas)

    referencia = datetime.combine(
        date.today(),
        hora_inicio,
    )

    fin = referencia + timedelta(
        hours=duracion_horas
    )

    return fin.time()


def validar_horario(
    hora_inicio,
    duracion_horas,
):
    """
    Verifica que la reservacion se encuentre dentro
    del horario permitido de 08:00 a 20:00.
    """

    hora_inicio = convertir_hora(hora_inicio)

    validar_duracion(duracion_horas)

    if hora_inicio.minute != 0:
        raise ErrorReglaNegocio(
            "La reservación debe comenzar "
            "a una hora completa."
        )

    if hora_inicio < time(8, 0):
        raise ErrorReglaNegocio(
            "La reservación debe iniciar a partir "
            "de las 08:00."
        )

    hora_fin = calcular_hora_fin(
        hora_inicio,
        duracion_horas,
    )

    if hora_fin > time(20, 0):
        raise ErrorReglaNegocio(
            "La reservación no puede finalizar "
            "después de las 20:00."
        )

    return hora_fin


def validar_cantidad_personas(
    cantidad_personas,
    capacidad_sala,
):
    """
    Verifica la cantidad de personas de una reservacion.
    """

    if (
        isinstance(cantidad_personas, bool)
        or not isinstance(cantidad_personas, int)
    ):
        raise ErrorValidacion(
            "La cantidad de personas debe ser "
            "un número entero."
        )

    if cantidad_personas <= 0:
        raise ErrorReglaNegocio(
            "La cantidad de personas debe ser "
            "mayor que cero."
        )

    if cantidad_personas > capacidad_sala:
        raise ErrorReglaNegocio(
            "La cantidad de personas supera "
            "la capacidad de la sala."
        )

    return cantidad_personas


def validar_estudiante_para_reservar(
    estudiante,
):
    """
    Verifica que el estudiante exista y se encuentre activo.
    """

    if estudiante is None:
        raise ErrorReglaNegocio(
            "El estudiante no existe."
        )

    if not estudiante.esta_activo:
        raise ErrorReglaNegocio(
            "El estudiante se encuentra inactivo "
            "y no puede realizar reservaciones."
        )

    return estudiante


def validar_sala_para_reservar(
    sala,
):
    """
    Verifica que la sala exista y se encuentre disponible.
    """

    if sala is None:
        raise ErrorReglaNegocio(
            "La sala no existe."
        )

    if not sala.esta_disponible:
        raise ErrorReglaNegocio(
            "La sala se encuentra fuera de servicio "
            "y no puede ser reservada."
        )

    return sala


def hay_superposicion(
    inicio_nuevo,
    fin_nuevo,
    inicio_existente,
    fin_existente,
):
    """
    Determina si dos intervalos de reservacion
    se superponen.

    Se utiliza la regla:

    inicio_nuevo < fin_existente
    y
    fin_nuevo > inicio_existente
    """

    inicio_nuevo = convertir_hora(inicio_nuevo)
    fin_nuevo = convertir_hora(fin_nuevo)

    inicio_existente = convertir_hora(
        inicio_existente
    )

    fin_existente = convertir_hora(
        fin_existente
    )

    return (
        inicio_nuevo < fin_existente
        and fin_nuevo > inicio_existente
    )


def validar_sin_superposicion(
    reservacion_nueva,
    reservaciones_existentes,
):
    """
    Verifica que no exista una reservacion activa
    superpuesta para la misma sala y fecha.
    """

    inicio_nuevo = convertir_hora(
        reservacion_nueva.hora_inicio
    )

    fin_nuevo = calcular_hora_fin(
        inicio_nuevo,
        reservacion_nueva.duracion_horas,
    )

    for reservacion in reservaciones_existentes:

        if reservacion.estado != "activa":
            continue

        misma_sala = (
            reservacion.codigo_sala.casefold()
            == reservacion_nueva.codigo_sala.casefold()
        )

        misma_fecha = (
            reservacion.fecha
            == reservacion_nueva.fecha
        )

        if not (
            misma_sala
            and misma_fecha
        ):
            continue

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
            raise ErrorReglaNegocio(
                "La reservación se superpone con "
                "otra reservación activa."
            )

    return True


def validar_limite_reservaciones(
    estudiante,
    reservaciones_existentes,
    hoy=None,
):
    """
    Verifica el limite maximo de tres reservaciones
    activas presentes o futuras por estudiante.
    """

    if hoy is None:
        hoy = date.today()

    cantidad = 0

    for reservacion in reservaciones_existentes:

        if reservacion.estado != "activa":
            continue

        if (
            reservacion.carne_estudiante.casefold()
            != estudiante.carne.casefold()
        ):
            continue

        fecha_reservacion = convertir_fecha(
            reservacion.fecha
        )

        if fecha_reservacion >= hoy:
            cantidad += 1

    if cantidad >= 3:
        raise ErrorReglaNegocio(
            "El estudiante ya posee el máximo "
            "de tres reservaciones activas "
            "presentes o futuras."
        )

    return True


def validar_reservacion(
    estudiante,
    sala,
    fecha,
    hora_inicio,
    duracion_horas,
    cantidad_personas,
    reservaciones_existentes=None,
    ahora=None,
):
    """
    Ejecuta todas las validaciones necesarias para
    una nueva reservacion.

    Devuelve una Reservacion normalizada y lista
    para ser enviada a la capa de persistencia.
    """

    if reservaciones_existentes is None:
        reservaciones_existentes = []

    if ahora is None:
        ahora = datetime.now()

    estudiante = validar_estudiante_para_reservar(
        estudiante
    )

    sala = validar_sala_para_reservar(
        sala
    )

    fecha_validada = validar_fecha_reservacion(
        fecha,
        hoy=ahora.date(),
    )

    hora_validada = validar_hora_inicio(
        hora_inicio,
        fecha_validada,
        ahora=ahora,
    )

    duracion_validada = validar_duracion(
        duracion_horas
    )

    validar_horario(
        hora_validada,
        duracion_validada,
    )

    cantidad_validada = validar_cantidad_personas(
        cantidad_personas,
        sala.capacidad,
    )

    validar_limite_reservaciones(
        estudiante,
        reservaciones_existentes,
        hoy=ahora.date(),
    )

    reservacion = Reservacion(
        carne_estudiante=estudiante.carne,
        codigo_sala=sala.codigo,
        fecha=fecha_validada.isoformat(),
        hora_inicio=hora_validada.strftime(
            "%H:%M"
        ),
        duracion_horas=duracion_validada,
        cantidad_personas=cantidad_validada,
    )

    validar_sin_superposicion(
        reservacion,
        reservaciones_existentes,
    )

    return reservacion