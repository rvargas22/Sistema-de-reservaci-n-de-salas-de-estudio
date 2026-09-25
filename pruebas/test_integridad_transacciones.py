"""
Pruebas de integridad, transacciones y rollback.
"""

import sqlite3
from datetime import datetime

import pytest

from aplicacion.modelos import (
    Reservacion,
)

from aplicacion.persistencia import (
    guardar_serie_recurrente,
    inicializar_base_datos,
    obtener_conexion,
    obtener_errores_claves_foraneas,
    obtener_estado_integridad,
    obtener_resultado_integridad,
    transaccion,
    verificar_integridad_base_datos,
)

from aplicacion.servicios import (
    cancelar_reservacion,
    crear_reservacion,
    registrar_estudiante,
)


AHORA = datetime(
    2026,
    9,
    24,
    9,
    0,
)


def preparar_base(
    tmp_path,
):
    """
    Inicializa una base temporal.
    """

    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(
        ruta
    )

    return ruta


def test_claves_foraneas_activas(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        valor = conexion.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

    finally:
        conexion.close()

    assert valor == 1


def test_busy_timeout_configurado(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        valor = conexion.execute(
            "PRAGMA busy_timeout"
        ).fetchone()[0]

    finally:
        conexion.close()

    assert valor == 5000


def test_integrity_check_es_ok(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    resultado = obtener_resultado_integridad(
        ruta
    )

    assert resultado == "ok"


def test_foreign_key_check_sin_errores(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    errores = obtener_errores_claves_foraneas(
        ruta
    )

    assert errores == []


def test_estado_integridad_correcto(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    estado = obtener_estado_integridad(
        ruta
    )

    assert estado["integridad"] == "ok"
    assert estado["claves_foraneas"] == []
    assert estado["correcta"] is True

    assert (
        verificar_integridad_base_datos(
            ruta
        )
        is True
    )


def test_transaccion_exitosa_confirma_cambios(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with transaccion(
        ruta
    ) as conexion:

        conexion.execute(
            """
            INSERT INTO estudiantes (
                carne,
                nombre,
                correo,
                estado
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "D001234567",
                "David Ramírez",
                "david@universidad.ac.cr",
                "activo",
            ),
        )

    conexion = obtener_conexion(
        ruta
    )

    try:
        cantidad = conexion.execute(
            """
            SELECT COUNT(*)
            FROM estudiantes
            WHERE carne = ?
            """,
            (
                "D001234567",
            ),
        ).fetchone()[0]

    finally:
        conexion.close()

    assert cantidad == 1


def test_transaccion_fallida_revierte_todos_los_cambios(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        with transaccion(
            ruta
        ) as conexion:

            conexion.execute(
                """
                INSERT INTO estudiantes (
                    carne,
                    nombre,
                    correo,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "D001234567",
                    "David Ramírez",
                    "david@universidad.ac.cr",
                    "activo",
                ),
            )

            # A001234567 ya existe.
            conexion.execute(
                """
                INSERT INTO estudiantes (
                    carne,
                    nombre,
                    correo,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "A001234567",
                    "Duplicado",
                    "duplicado@universidad.ac.cr",
                    "activo",
                ),
            )

    conexion = obtener_conexion(
        ruta
    )

    try:
        cantidad = conexion.execute(
            """
            SELECT COUNT(*)
            FROM estudiantes
            WHERE carne = ?
            """,
            (
                "D001234567",
            ),
        ).fetchone()[0]

    finally:
        conexion.close()

    assert cantidad == 0


def test_rollback_tambien_revierte_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        with transaccion(
            ruta
        ) as conexion:

            conexion.execute(
                """
                INSERT INTO estudiantes (
                    carne,
                    nombre,
                    correo,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "D001234567",
                    "David Ramírez",
                    "david@universidad.ac.cr",
                    "activo",
                ),
            )

            conexion.execute(
                """
                INSERT INTO estudiantes (
                    carne,
                    nombre,
                    correo,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "A001234567",
                    "Duplicado",
                    "duplicado@universidad.ac.cr",
                    "activo",
                ),
            )

    conexion = obtener_conexion(
        ruta
    )

    try:
        eventos = conexion.execute(
            """
            SELECT COUNT(*)
            FROM auditoria
            """
        ).fetchone()[0]

    finally:
        conexion.close()

    assert eventos == 0


def test_clave_foranea_invalida_no_se_guarda(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        with transaccion(
            ruta
        ) as conexion:

            conexion.execute(
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
                    "Z999999999",
                    "S01",
                    "2026-10-10",
                    "10:00",
                    1,
                    2,
                    "activa",
                ),
            )

    conexion = obtener_conexion(
        ruta
    )

    try:
        cantidad = conexion.execute(
            """
            SELECT COUNT(*)
            FROM reservaciones
            """
        ).fetchone()[0]

    finally:
        conexion.close()

    assert cantidad == 0


def test_check_invalido_no_se_guarda(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        with transaccion(
            ruta
        ) as conexion:

            conexion.execute(
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
                    "A001234567",
                    "S01",
                    "2026-10-10",
                    "10:00",
                    3,
                    2,
                    "activa",
                ),
            )

    conexion = obtener_conexion(
        ruta
    )

    try:
        cantidad = conexion.execute(
            """
            SELECT COUNT(*)
            FROM reservaciones
            """
        ).fetchone()[0]

    finally:
        conexion.close()

    assert cantidad == 0


def test_serie_recurrente_es_atomica_ante_error_sqlite(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reservacion_valida = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-05",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
    )

    reservacion_invalida = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-12",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=0,
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        guardar_serie_recurrente(
            carne_estudiante="A001234567",
            codigo_sala="S01",
            fecha_inicio="2026-10-05",
            hora_inicio="10:00",
            duracion_horas=1,
            cantidad_personas=2,
            reservaciones=[
                reservacion_valida,
                reservacion_invalida,
            ],
            ruta_base_datos=ruta,
        )

    conexion = obtener_conexion(
        ruta
    )

    try:
        series = conexion.execute(
            """
            SELECT COUNT(*)
            FROM series_recurrentes
            """
        ).fetchone()[0]

        ocurrencias = conexion.execute(
            """
            SELECT COUNT(*)
            FROM ocurrencias_recurrentes
            """
        ).fetchone()[0]

        reservaciones = conexion.execute(
            """
            SELECT COUNT(*)
            FROM reservaciones
            """
        ).fetchone()[0]

        auditoria = conexion.execute(
            """
            SELECT COUNT(*)
            FROM auditoria
            """
        ).fetchone()[0]

    finally:
        conexion.close()

    assert series == 0
    assert ocurrencias == 0
    assert reservaciones == 0
    assert auditoria == 0


def test_conexion_transaccion_se_cierra(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with transaccion(
        ruta
    ) as conexion:

        conexion.execute(
            """
            SELECT 1
            """
        ).fetchone()

    with pytest.raises(
        sqlite3.ProgrammingError
    ):
        conexion.execute(
            "SELECT 1"
        )


def test_nueva_operacion_funciona_despues_de_rollback(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        with transaccion(
            ruta
        ) as conexion:

            conexion.execute(
                """
                INSERT INTO estudiantes (
                    carne,
                    nombre,
                    correo,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "A001234567",
                    "Duplicado",
                    "duplicado@universidad.ac.cr",
                    "activo",
                ),
            )

    estudiante = registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    assert (
        estudiante.carne
        == "D001234567"
    )


def test_integridad_despues_de_operaciones_normales(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    reservacion = crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    assert (
        verificar_integridad_base_datos(
            ruta
        )
        is True
    )

    assert (
        obtener_errores_claves_foraneas(
            ruta
        )
        == []
    )