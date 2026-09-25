"""
Operaciones de persistencia relacionadas
con series de reservaciones recurrentes.
"""

from dataclasses import replace

from aplicacion.modelos import (
    Reservacion,
)

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)

from aplicacion.persistencia.transacciones import (
    transaccion,
)


def _fila_a_reservacion(
    fila,
):
    """
    Convierte una fila SQLite en Reservacion.
    """

    if fila is None:
        return None

    return Reservacion(
        carne_estudiante=(
            fila["carne_estudiante"]
        ),
        codigo_sala=(
            fila["codigo_sala"]
        ),
        fecha=fila["fecha"],
        hora_inicio=(
            fila["hora_inicio"]
        ),
        duracion_horas=(
            fila["duracion_horas"]
        ),
        cantidad_personas=(
            fila["cantidad_personas"]
        ),
        estado=fila["estado"],
        id=fila["id"],
    )


def guardar_serie_recurrente(
    carne_estudiante,
    codigo_sala,
    fecha_inicio,
    hora_inicio,
    duracion_horas,
    cantidad_personas,
    reservaciones,
    ruta_base_datos=None,
):
    """
    Guarda una serie recurrente y todas sus
    ocurrencias dentro de una sola transaccion.
    """

    with transaccion(
        ruta_base_datos
    ) as conexion:

        cursor_serie = conexion.execute(
            """
            INSERT INTO series_recurrentes (
                carne_estudiante,
                codigo_sala,
                fecha_inicio,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                total_ocurrencias
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                carne_estudiante,
                codigo_sala,
                fecha_inicio,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                len(reservaciones),
            ),
        )

        serie_id = (
            cursor_serie.lastrowid
        )

        reservaciones_guardadas = []

        for numero, reservacion in enumerate(
            reservaciones,
            start=1,
        ):
            cursor = conexion.execute(
                """
                INSERT INTO reservaciones (
                    carne_estudiante,
                    codigo_sala,
                    fecha,
                    hora_inicio,
                    duracion_horas,
                    cantidad_personas,
                    estado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reservacion.carne_estudiante,
                    reservacion.codigo_sala,
                    reservacion.fecha,
                    reservacion.hora_inicio,
                    reservacion.duracion_horas,
                    reservacion.cantidad_personas,
                    reservacion.estado,
                ),
            )

            reservacion_id = (
                cursor.lastrowid
            )

            conexion.execute(
                """
                INSERT INTO ocurrencias_recurrentes (
                    serie_id,
                    numero_ocurrencia,
                    reservacion_id
                )
                VALUES (?, ?, ?)
                """,
                (
                    serie_id,
                    numero,
                    reservacion_id,
                ),
            )

            reservaciones_guardadas.append(
                replace(
                    reservacion,
                    id=reservacion_id,
                )
            )

    return {
        "serie_id":
            serie_id,

        "reservaciones":
            reservaciones_guardadas,
    }


def obtener_serie_recurrente_por_id(
    serie_id,
    ruta_base_datos=None,
):
    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        fila = conexion.execute(
            """
            SELECT
                id,
                carne_estudiante,
                codigo_sala,
                fecha_inicio,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                total_ocurrencias

            FROM series_recurrentes

            WHERE id = ?
            """,
            (
                serie_id,
            ),
        ).fetchone()

    finally:
        conexion.close()

    if fila is None:
        return None

    return dict(
        fila
    )


def listar_ocurrencias_serie(
    serie_id,
    ruta_base_datos=None,
):
    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            """
            SELECT
                o.numero_ocurrencia,

                r.id,
                r.carne_estudiante,
                r.codigo_sala,
                r.fecha,
                r.hora_inicio,
                r.duracion_horas,
                r.cantidad_personas,
                r.estado

            FROM ocurrencias_recurrentes o

            INNER JOIN reservaciones r
                ON r.id = o.reservacion_id

            WHERE o.serie_id = ?

            ORDER BY
                o.numero_ocurrencia
            """,
            (
                serie_id,
            ),
        ).fetchall()

    finally:
        conexion.close()

    return [
        {
            "numero_ocurrencia":
                fila["numero_ocurrencia"],

            "reservacion":
                _fila_a_reservacion(
                    fila
                ),
        }
        for fila in filas
    ]


def obtener_ocurrencia_serie(
    serie_id,
    numero_ocurrencia,
    ruta_base_datos=None,
):
    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        fila = conexion.execute(
            """
            SELECT
                o.numero_ocurrencia,

                r.id,
                r.carne_estudiante,
                r.codigo_sala,
                r.fecha,
                r.hora_inicio,
                r.duracion_horas,
                r.cantidad_personas,
                r.estado

            FROM ocurrencias_recurrentes o

            INNER JOIN reservaciones r
                ON r.id = o.reservacion_id

            WHERE o.serie_id = ?
              AND o.numero_ocurrencia = ?
            """,
            (
                serie_id,
                numero_ocurrencia,
            ),
        ).fetchone()

    finally:
        conexion.close()

    if fila is None:
        return None

    return {
        "numero_ocurrencia":
            fila["numero_ocurrencia"],

        "reservacion":
            _fila_a_reservacion(
                fila
            ),
    }


def cancelar_ocurrencias_posteriores(
    serie_id,
    numero_ocurrencia,
    incluir_seleccionada=False,
    ruta_base_datos=None,
):
    operador = (
        ">="
        if incluir_seleccionada
        else ">"
    )

    with transaccion(
        ruta_base_datos
    ) as conexion:

        consulta = f"""
            UPDATE reservaciones

            SET estado = 'cancelada'

            WHERE estado = 'activa'

              AND id IN (
                  SELECT reservacion_id

                  FROM ocurrencias_recurrentes

                  WHERE serie_id = ?

                    AND numero_ocurrencia
                        {operador} ?
              )
        """

        cursor = conexion.execute(
            consulta,
            (
                serie_id,
                numero_ocurrencia,
            ),
        )

        cantidad = (
            cursor.rowcount
        )

    return cantidad