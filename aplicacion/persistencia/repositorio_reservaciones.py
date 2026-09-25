"""
Operaciones de persistencia para reservaciones.
"""

from dataclasses import replace

from aplicacion.modelos import (
    Reservacion,
)

from aplicacion.persistencia.base_datos import (
    obtener_conexion,
)

from aplicacion.persistencia.identificadores import (
    numero_identificador_reservacion,
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


def guardar_reservacion(
    reservacion,
    ruta_base_datos=None,
):
    """
    Guarda una reservacion nueva.

    SQLite genera automaticamente el ID numerico.
    """

    if reservacion.id is not None:
        raise ValueError(
            (
                "Una reservación nueva no debe "
                "tener identificador."
            )
        )

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
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

        conexion.commit()

        identificador = (
            cursor.lastrowid
        )

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return replace(
        reservacion,
        id=identificador,
    )


def obtener_reservacion_por_id(
    identificador,
    ruta_base_datos=None,
):
    """
    Obtiene una reservacion.

    Acepta tanto 1 como R0001.
    """

    numero = numero_identificador_reservacion(
        identificador
    )

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
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado

            FROM reservaciones

            WHERE id = ?
            """,
            (
                numero,
            ),
        ).fetchone()

    finally:
        conexion.close()

    return _fila_a_reservacion(
        fila
    )


def listar_reservaciones(
    ruta_base_datos=None,
):
    """
    Devuelve todas las reservaciones.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            """
            SELECT
                id,
                carne_estudiante,
                codigo_sala,
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado

            FROM reservaciones

            ORDER BY
                fecha,
                hora_inicio,
                id
            """
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_reservacion(
            fila
        )
        for fila in filas
    ]


def listar_reservaciones_por_carne(
    carne,
    ruta_base_datos=None,
):
    """
    Devuelve reservaciones de un estudiante.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            """
            SELECT
                id,
                carne_estudiante,
                codigo_sala,
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado

            FROM reservaciones

            WHERE carne_estudiante = ?
                  COLLATE NOCASE

            ORDER BY
                fecha,
                hora_inicio,
                id
            """,
            (
                carne,
            ),
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_reservacion(
            fila
        )
        for fila in filas
    ]


def listar_reservaciones_activas_sala_fecha(
    codigo_sala,
    fecha,
    ruta_base_datos=None,
):
    """
    Devuelve reservaciones activas de una sala
    en una fecha determinada.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            """
            SELECT
                id,
                carne_estudiante,
                codigo_sala,
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado

            FROM reservaciones

            WHERE codigo_sala = ?
                  COLLATE NOCASE
              AND fecha = ?
              AND estado = 'activa'

            ORDER BY
                hora_inicio,
                id
            """,
            (
                codigo_sala,
                fecha,
            ),
        ).fetchall()

    finally:
        conexion.close()

    return [
        _fila_a_reservacion(
            fila
        )
        for fila in filas
    ]


def actualizar_reservacion(
    reservacion,
    ruta_base_datos=None,
):
    """
    Actualiza una reservacion existente.
    """

    if reservacion.id is None:
        raise ValueError(
            (
                "La reservación debe tener "
                "identificador."
            )
        )

    numero = numero_identificador_reservacion(
        reservacion.id
    )

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        cursor = conexion.execute(
            """
            UPDATE reservaciones

            SET carne_estudiante = ?,
                codigo_sala = ?,
                fecha = ?,
                hora_inicio = ?,
                duracion_horas = ?,
                cantidad_personas = ?,
                estado = ?

            WHERE id = ?
            """,
            (
                reservacion.carne_estudiante,
                reservacion.codigo_sala,
                reservacion.fecha,
                reservacion.hora_inicio,
                reservacion.duracion_horas,
                reservacion.cantidad_personas,
                reservacion.estado,
                numero,
            ),
        )

        conexion.commit()

        actualizado = (
            cursor.rowcount
            > 0
        )

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    if not actualizado:
        return None

    return obtener_reservacion_por_id(
        numero,
        ruta_base_datos,
    )


def marcar_reservacion_cancelada(
    identificador,
    ruta_base_datos=None,
):
    """
    Marca como cancelada una reservacion activa.
    """

    numero = numero_identificador_reservacion(
        identificador
    )

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        cursor = conexion.execute(
            """
            UPDATE reservaciones

            SET estado = 'cancelada'

            WHERE id = ?
              AND estado = 'activa'
            """,
            (
                numero,
            ),
        )

        conexion.commit()

        resultado = (
            cursor.rowcount
            > 0
        )

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    return resultado


def consultar_reservaciones_panel(
    fecha=None,
    codigo_sala=None,
    estado=None,
    ruta_base_datos=None,
):
    """
    Consulta reservaciones para el panel.
    """

    condiciones = []
    parametros = []

    if fecha is not None:
        condiciones.append(
            "r.fecha = ?"
        )

        parametros.append(
            fecha
        )

    if codigo_sala is not None:
        condiciones.append(
            """
            r.codigo_sala = ?
            COLLATE NOCASE
            """
        )

        parametros.append(
            codigo_sala
        )

    if estado is not None:
        condiciones.append(
            "r.estado = ?"
        )

        parametros.append(
            estado
        )

    where = ""

    if condiciones:
        where = (
            "WHERE "
            + " AND ".join(
                condiciones
            )
        )

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            f"""
            SELECT
                r.id,
                r.carne_estudiante,
                e.nombre
                    AS nombre_estudiante,
                r.codigo_sala,
                s.nombre
                    AS nombre_sala,
                r.fecha,
                r.hora_inicio,
                r.duracion_horas,
                r.cantidad_personas,
                r.estado

            FROM reservaciones r

            INNER JOIN estudiantes e
                ON e.carne =
                   r.carne_estudiante

            INNER JOIN salas s
                ON s.codigo =
                   r.codigo_sala

            {where}

            ORDER BY
                r.fecha,
                r.hora_inicio,
                r.id
            """,
            parametros,
        ).fetchall()

    finally:
        conexion.close()

    return [
        dict(
            fila
        )
        for fila in filas
    ]


def consultar_reservaciones_por_rango(
    fecha_inicial,
    fecha_final,
    ruta_base_datos=None,
):
    """
    Consulta reservaciones dentro de un rango
    inclusivo de fechas.
    """

    conexion = obtener_conexion(
        ruta_base_datos
    )

    try:
        filas = conexion.execute(
            """
            SELECT
                r.id,
                r.carne_estudiante,
                e.nombre
                    AS nombre_estudiante,
                r.codigo_sala,
                s.nombre
                    AS nombre_sala,
                r.fecha,
                r.hora_inicio,
                r.duracion_horas,
                r.cantidad_personas,
                r.estado

            FROM reservaciones r

            INNER JOIN estudiantes e
                ON e.carne =
                   r.carne_estudiante

            INNER JOIN salas s
                ON s.codigo =
                   r.codigo_sala

            WHERE r.fecha >= ?
              AND r.fecha <= ?

            ORDER BY
                r.fecha,
                r.hora_inicio,
                r.id
            """,
            (
                fecha_inicial,
                fecha_final,
            ),
        ).fetchall()

    finally:
        conexion.close()

    return [
        dict(
            fila
        )
        for fila in filas
    ]