"""
Servicio relacionado con el panel principal.
"""

from datetime import date

from aplicacion.persistencia import (
    consultar_reservaciones_panel,
    listar_salas,
    obtener_sala_por_codigo,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
    convertir_fecha,
)

from aplicacion.validaciones.validador_salas import (
    normalizar_codigo_sala,
)


ESTADOS_RESERVACION = {
    "activa",
    "cancelada",
}


def _normalizar_estado_panel(
    estado,
):
    if estado is None:
        return None

    if not isinstance(
        estado,
        str,
    ):
        raise ErrorValidacion(
            "El estado debe ser texto."
        )

    estado = (
        estado.strip().lower()
    )

    if estado not in ESTADOS_RESERVACION:
        raise ErrorValidacion(
            "El estado debe ser 'activa' "
            "o 'cancelada'."
        )

    return estado


def _calcular_hora_fin(
    hora_inicio,
    duracion_horas,
):
    hora, minuto = map(
        int,
        hora_inicio.split(":"),
    )

    total = (
        hora * 60
        + minuto
        + duracion_horas * 60
    )

    return (
        f"{total // 60:02d}:"
        f"{total % 60:02d}"
    )


def _enriquecer_fila(
    fila,
):
    fila = dict(
        fila
    )

    fila["identificador"] = (
        f"R{fila['id']:04d}"
    )

    fila["hora_fin"] = (
        _calcular_hora_fin(
            fila["hora_inicio"],
            fila["duracion_horas"],
        )
    )

    return fila


def consultar_panel(
    fecha=None,
    codigo_sala=None,
    estado=None,
    ruta_base_datos=None,
):
    fecha_normalizada = None
    codigo_normalizado = None

    if fecha is not None:
        fecha_normalizada = (
            convertir_fecha(
                fecha
            ).isoformat()
        )

    if codigo_sala is not None:
        codigo_normalizado = (
            normalizar_codigo_sala(
                codigo_sala
            )
        )

        sala = obtener_sala_por_codigo(
            codigo_normalizado,
            ruta_base_datos,
        )

        if sala is None:
            raise ErrorReglaNegocio(
                "La sala no existe."
            )

    estado_normalizado = (
        _normalizar_estado_panel(
            estado
        )
    )

    filas = consultar_reservaciones_panel(
        fecha=fecha_normalizada,
        codigo_sala=codigo_normalizado,
        estado=estado_normalizado,
        ruta_base_datos=ruta_base_datos,
    )

    return [
        _enriquecer_fila(
            fila
        )
        for fila in filas
    ]


def obtener_resumen_panel(
    fecha_referencia=None,
    ruta_base_datos=None,
):
    """
    Devuelve las reservaciones del dia,
    las proximas reservaciones y la ocupacion
    por sala.
    """

    if fecha_referencia is None:
        fecha_referencia = (
            date.today()
        )

    else:
        fecha_referencia = (
            convertir_fecha(
                fecha_referencia
            )
        )

    fecha_texto = (
        fecha_referencia.isoformat()
    )

    reservaciones = consultar_panel(
        ruta_base_datos=(
            ruta_base_datos
        )
    )

    reservaciones_dia = [
        fila
        for fila in reservaciones
        if fila["fecha"]
        == fecha_texto
    ]

    proximas_reservaciones = [
        fila
        for fila in reservaciones
        if (
            fila["estado"] == "activa"
            and fila["fecha"]
            > fecha_texto
        )
    ]

    reservaciones_activas_dia = [
        fila
        for fila in reservaciones_dia
        if fila["estado"]
        == "activa"
    ]

    ocupacion = []

    for sala in listar_salas(
        ruta_base_datos
    ):
        reservas_sala = [
            fila
            for fila
            in reservaciones_activas_dia
            if (
                fila["codigo_sala"]
                == sala.codigo
            )
        ]

        ocupacion.append(
            {
                "codigo_sala":
                    sala.codigo,

                "nombre_sala":
                    sala.nombre,

                "reservaciones_activas":
                    len(
                        reservas_sala
                    ),

                "personas_reservadas":
                    sum(
                        fila[
                            "cantidad_personas"
                        ]
                        for fila
                        in reservas_sala
                    ),
            }
        )

    return {
        "fecha":
            fecha_texto,

        "reservaciones_dia":
            reservaciones_dia,

        "proximas_reservaciones":
            proximas_reservaciones,

        "ocupacion_salas":
            ocupacion,

        "salas_ocupadas":
            sum(
                1
                for fila in ocupacion
                if (
                    fila[
                        "reservaciones_activas"
                    ]
                    > 0
                )
            ),
    }