"""
Servicio para gestionar reservaciones recurrentes.
"""

from datetime import datetime, timedelta

from aplicacion.persistencia import (
    cancelar_ocurrencias_posteriores,
    guardar_serie_recurrente,
    listar_ocurrencias_serie,
    listar_reservaciones_activas_sala_fecha,
    obtener_estudiante_por_carne,
    obtener_ocurrencia_serie,
    obtener_sala_por_codigo,
    obtener_serie_recurrente_por_id,
)

from aplicacion.servicios.servicio_reservaciones import (
    cancelar_reservacion,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
    convertir_fecha,
    validar_carne,
    validar_reservacion,
    validar_sin_superposicion,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)


def validar_cantidad_ocurrencias(
    cantidad_ocurrencias,
):
    """
    Verifica que una serie tenga entre
    2 y 8 ocurrencias.
    """

    if (
        isinstance(cantidad_ocurrencias, bool)
        or not isinstance(cantidad_ocurrencias, int)
    ):
        raise ErrorValidacion(
            "La cantidad de ocurrencias debe ser "
            "un número entero."
        )

    if not 2 <= cantidad_ocurrencias <= 8:
        raise ErrorReglaNegocio(
            "Una serie recurrente debe contener "
            "entre 2 y 8 ocurrencias."
        )

    return cantidad_ocurrencias


def _validar_numero_ocurrencia(
    numero_ocurrencia,
):
    """
    Valida un numero de ocurrencia.
    """

    if (
        isinstance(numero_ocurrencia, bool)
        or not isinstance(numero_ocurrencia, int)
    ):
        raise ErrorValidacion(
            "El número de ocurrencia debe ser entero."
        )

    if numero_ocurrencia <= 0:
        raise ErrorValidacion(
            "El número de ocurrencia debe ser "
            "mayor que cero."
        )

    return numero_ocurrencia


def _analizar_serie(
    carne_estudiante,
    codigo_sala,
    fecha_inicio,
    hora_inicio,
    duracion_horas,
    cantidad_personas,
    cantidad_ocurrencias,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Construye y valida todas las ocurrencias
    sin realizar escrituras en SQLite.
    """

    if ahora is None:
        ahora = datetime.now()

    cantidad_ocurrencias = (
        validar_cantidad_ocurrencias(
            cantidad_ocurrencias
        )
    )

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

    if estudiante is None:
        raise ErrorReglaNegocio(
            "El estudiante no existe."
        )

    if not estudiante.esta_activo:
        raise ErrorReglaNegocio(
            "El estudiante se encuentra inactivo "
            "y no puede crear una serie recurrente."
        )

    sala = obtener_sala_por_codigo(
        codigo_sala,
        ruta_base_datos,
    )

    if sala is None:
        raise ErrorReglaNegocio(
            "La sala no existe."
        )

    if not sala.esta_disponible:
        raise ErrorReglaNegocio(
            "La sala se encuentra fuera de servicio."
        )

    fecha_base = convertir_fecha(
        fecha_inicio
    )

    resumen_ocurrencias = []
    reservaciones_candidatas = []

    for indice in range(
        cantidad_ocurrencias
    ):
        numero = indice + 1

        fecha_ocurrencia = (
            fecha_base
            + timedelta(
                weeks=indice
            )
        )

        try:
            # Se valida cada ocurrencia individualmente.
            #
            # La lista se entrega vacia deliberadamente:
            # RF-14 permite entre 2 y 8 ocurrencias y la
            # especificacion no define como interactua
            # esta regla con el limite RN-11.
            candidata = validar_reservacion(
                estudiante=estudiante,
                sala=sala,
                fecha=fecha_ocurrencia,
                hora_inicio=hora_inicio,
                duracion_horas=duracion_horas,
                cantidad_personas=cantidad_personas,
                reservaciones_existentes=[],
                ahora=ahora,
            )

            existentes = (
                listar_reservaciones_activas_sala_fecha(
                    codigo_sala,
                    candidata.fecha,
                    ruta_base_datos,
                )
            )

            validar_sin_superposicion(
                candidata,
                existentes,
            )

            reservaciones_candidatas.append(
                candidata
            )

            resumen_ocurrencias.append(
                {
                    "numero": numero,
                    "fecha": candidata.fecha,
                    "hora_inicio":
                        candidata.hora_inicio,
                    "disponible": True,
                    "motivo": None,
                }
            )

        except ErrorReglaNegocio as error:
            resumen_ocurrencias.append(
                {
                    "numero": numero,
                    "fecha":
                        fecha_ocurrencia.isoformat(),
                    "hora_inicio":
                        str(hora_inicio),
                    "disponible": False,
                    "motivo": str(error),
                }
            )

    hay_conflictos = any(
        not ocurrencia["disponible"]
        for ocurrencia
        in resumen_ocurrencias
    )

    resumen = {
        "cantidad_ocurrencias":
            cantidad_ocurrencias,

        "hay_conflictos":
            hay_conflictos,

        "ocurrencias":
            resumen_ocurrencias,
    }

    return (
        resumen,
        reservaciones_candidatas,
    )


def analizar_serie_recurrente(
    carne_estudiante,
    codigo_sala,
    fecha_inicio,
    hora_inicio,
    duracion_horas,
    cantidad_personas,
    cantidad_ocurrencias,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Analiza la serie completa antes de guardarla.

    Devuelve un resumen de todas las ocurrencias
    y de los posibles conflictos.

    No modifica SQLite.
    """

    resumen, _ = _analizar_serie(
        carne_estudiante,
        codigo_sala,
        fecha_inicio,
        hora_inicio,
        duracion_horas,
        cantidad_personas,
        cantidad_ocurrencias,
        ruta_base_datos,
        ahora,
    )

    return resumen


def crear_serie_recurrente(
    carne_estudiante,
    codigo_sala,
    fecha_inicio,
    hora_inicio,
    duracion_horas,
    cantidad_personas,
    cantidad_ocurrencias,
    ruta_base_datos=None,
    ahora=None,
):
    """
    Crea una serie semanal completa.

    Primero vuelve a validar todas las ocurrencias.

    Si existe cualquier conflicto, no guarda ninguna.
    """

    resumen, reservaciones = _analizar_serie(
        carne_estudiante,
        codigo_sala,
        fecha_inicio,
        hora_inicio,
        duracion_horas,
        cantidad_personas,
        cantidad_ocurrencias,
        ruta_base_datos,
        ahora,
    )

    if resumen["hay_conflictos"]:
        raise ErrorReglaNegocio(
            "La serie recurrente presenta uno o más "
            "conflictos y no puede guardarse."
        )

    fecha_base = convertir_fecha(
        fecha_inicio
    )

    return guardar_serie_recurrente(
        carne_estudiante=validar_carne(
            carne_estudiante
        ),
        codigo_sala=normalizar_codigo_sala(
            codigo_sala
        ),
        fecha_inicio=fecha_base.isoformat(),
        hora_inicio=reservaciones[0].hora_inicio,
        duracion_horas=duracion_horas,
        cantidad_personas=cantidad_personas,
        reservaciones=reservaciones,
        ruta_base_datos=ruta_base_datos,
    )


def consultar_ocurrencias_serie(
    serie_id,
    ruta_base_datos=None,
):
    """
    Devuelve las ocurrencias de una serie recurrente.
    """

    serie = obtener_serie_recurrente_por_id(
        serie_id,
        ruta_base_datos,
    )

    if serie is None:
        raise ErrorReglaNegocio(
            "La serie recurrente no existe."
        )

    return listar_ocurrencias_serie(
        serie_id,
        ruta_base_datos,
    )


def cancelar_ocurrencia_recurrente(
    serie_id,
    numero_ocurrencia,
    ruta_base_datos=None,
):
    """
    Cancela una unica ocurrencia de una serie.

    Las demas ocurrencias permanecen sin cambios.
    """

    numero_ocurrencia = (
        _validar_numero_ocurrencia(
            numero_ocurrencia
        )
    )

    ocurrencia = obtener_ocurrencia_serie(
        serie_id,
        numero_ocurrencia,
        ruta_base_datos,
    )

    if ocurrencia is None:
        raise ErrorReglaNegocio(
            "La ocurrencia indicada no existe "
            "dentro de la serie."
        )

    return cancelar_reservacion(
        ocurrencia["reservacion"].id,
        ruta_base_datos,
    )


def cancelar_ocurrencias_futuras(
    serie_id,
    numero_ocurrencia_desde,
    ruta_base_datos=None,
    incluir_seleccionada=False,
):
    """
    Cancela ocurrencias posteriores a la seleccionada.

    La especificacion no define expresamente si la
    ocurrencia seleccionada forma parte de las
    'ocurrencias futuras'.

    Por ello el comportamiento queda explicito mediante
    incluir_seleccionada.
    """

    numero_ocurrencia_desde = (
        _validar_numero_ocurrencia(
            numero_ocurrencia_desde
        )
    )

    serie = obtener_serie_recurrente_por_id(
        serie_id,
        ruta_base_datos,
    )

    if serie is None:
        raise ErrorReglaNegocio(
            "La serie recurrente no existe."
        )

    ocurrencia = obtener_ocurrencia_serie(
        serie_id,
        numero_ocurrencia_desde,
        ruta_base_datos,
    )

    if ocurrencia is None:
        raise ErrorReglaNegocio(
            "La ocurrencia seleccionada no existe."
        )

    cancelar_ocurrencias_posteriores(
        serie_id=serie_id,
        numero_ocurrencia=
            numero_ocurrencia_desde,
        incluir_seleccionada=
            incluir_seleccionada,
        ruta_base_datos=
            ruta_base_datos,
    )

    return listar_ocurrencias_serie(
        serie_id,
        ruta_base_datos,
    )