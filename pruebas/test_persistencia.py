"""
Pruebas de persistencia e inicializacion del sistema.
"""

import sqlite3

import pytest

from aplicacion.persistencia.base_datos import obtener_conexion
from aplicacion.persistencia.inicializador import inicializar_base_datos


def test_creacion_base_datos_y_tablas(tmp_path):
    """
    Verifica que la base de datos y sus tablas principales
    se creen correctamente.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    assert ruta_prueba.exists()

    conexion = obtener_conexion(ruta_prueba)

    tablas = {
        fila["name"]
        for fila in conexion.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()
    }

    conexion.close()

    assert "estudiantes" in tablas
    assert "salas" in tablas
    assert "reservaciones" in tablas


def test_datos_iniciales_correctos(tmp_path):
    """
    Verifica que se carguen exactamente los estudiantes
    y salas definidos para el sistema.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    estudiantes = conexion.execute(
        """
        SELECT carne, nombre, correo, estado
        FROM estudiantes
        ORDER BY carne
        """
    ).fetchall()

    salas = conexion.execute(
        """
        SELECT codigo, nombre, capacidad, estado
        FROM salas
        ORDER BY codigo
        """
    ).fetchall()

    conexion.close()

    assert len(estudiantes) == 3
    assert len(salas) == 5

    assert estudiantes[0]["carne"] == "A001234567"
    assert estudiantes[0]["nombre"] == "Andrea Solano"

    assert estudiantes[1]["carne"] == "B009876543"
    assert estudiantes[1]["nombre"] == "Carlos Méndez"

    assert estudiantes[2]["carne"] == "C004567890"
    assert estudiantes[2]["estado"] == "inactivo"

    assert salas[0]["codigo"] == "S01"
    assert salas[0]["capacidad"] == 4

    assert salas[3]["codigo"] == "S04"
    assert salas[3]["estado"] == "fuera_de_servicio"

    assert salas[4]["codigo"] == "S05"
    assert salas[4]["capacidad"] == 1


def test_inicializacion_no_duplica_datos(tmp_path):
    """
    Verifica que ejecutar varias veces la inicializacion
    no duplique estudiantes ni salas.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)
    inicializar_base_datos(ruta_prueba)
    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    cantidad_estudiantes = conexion.execute(
        """
        SELECT COUNT(*)
        FROM estudiantes
        """
    ).fetchone()[0]

    cantidad_salas = conexion.execute(
        """
        SELECT COUNT(*)
        FROM salas
        """
    ).fetchone()[0]

    conexion.close()

    assert cantidad_estudiantes == 3
    assert cantidad_salas == 5


def test_no_permitir_carne_duplicado_sin_distinguir_mayusculas(
    tmp_path,
):
    """
    Verifica que el carne sea unico sin distinguir
    mayusculas y minusculas.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

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
                    "a001234567",
                    "Estudiante duplicado",
                    "duplicado@universidad.ac.cr",
                    "activo",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_no_permitir_codigo_sala_duplicado(
    tmp_path,
):
    """
    Verifica que el codigo de sala sea unico
    sin distinguir mayusculas y minusculas.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

            conexion.execute(
                """
                INSERT INTO salas (
                    codigo,
                    nombre,
                    capacidad,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "s01",
                    "Sala duplicada",
                    4,
                    "disponible",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_no_permitir_capacidad_invalida(
    tmp_path,
):
    """
    Verifica que la capacidad de una sala sea mayor que cero.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

            conexion.execute(
                """
                INSERT INTO salas (
                    codigo,
                    nombre,
                    capacidad,
                    estado
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    "S99",
                    "Sala invalida",
                    0,
                    "disponible",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_reservacion_requiere_estudiante_existente(
    tmp_path,
):
    """
    Verifica la integridad referencial entre
    reservaciones y estudiantes.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

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
                    "2026-12-10",
                    "10:00",
                    1,
                    2,
                    "activa",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_reservacion_requiere_sala_existente(
    tmp_path,
):
    """
    Verifica la integridad referencial entre
    reservaciones y salas.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

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
                    "S99",
                    "2026-12-10",
                    "10:00",
                    1,
                    2,
                    "activa",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_no_permitir_duracion_invalida(
    tmp_path,
):
    """
    Verifica que la duracion almacenada sea
    solamente de una o dos horas.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

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
                    "2026-12-10",
                    "10:00",
                    3,
                    2,
                    "activa",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_no_permitir_cantidad_personas_invalida(
    tmp_path,
):
    """
    Verifica que la cantidad de personas almacenada
    sea mayor que cero.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

    try:
        with pytest.raises(sqlite3.IntegrityError):

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
                    "2026-12-10",
                    "10:00",
                    1,
                    0,
                    "activa",
                ),
            )

            conexion.commit()

    finally:
        conexion.close()


def test_persistencia_despues_de_reabrir_base(
    tmp_path,
):
    """
    Verifica que los datos permanezcan almacenados despues
    de cerrar y volver a abrir la base.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

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
            "Estudiante Persistencia",
            "persistencia@universidad.ac.cr",
            "activo",
        ),
    )

    conexion.commit()
    conexion.close()

    nueva_conexion = obtener_conexion(ruta_prueba)

    estudiante = nueva_conexion.execute(
        """
        SELECT carne, nombre
        FROM estudiantes
        WHERE carne = ?
        """,
        ("D001234567",),
    ).fetchone()

    nueva_conexion.close()

    assert estudiante is not None
    assert estudiante["carne"] == "D001234567"
    assert estudiante["nombre"] == "Estudiante Persistencia"


def test_identificador_autoincremental_no_se_reutiliza(
    tmp_path,
):
    """
    Verifica que SQLite mantenga la continuidad de los
    identificadores de reservacion.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    conexion = obtener_conexion(ruta_prueba)

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
            "A001234567",
            "S01",
            "2026-12-10",
            "10:00",
            1,
            2,
            "activa",
        ),
    )

    primer_id = cursor.lastrowid

    conexion.commit()

    conexion.execute(
        """
        DELETE FROM reservaciones
        WHERE id = ?
        """,
        (primer_id,),
    )

    conexion.commit()

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
            "A001234567",
            "S02",
            "2026-12-11",
            "11:00",
            1,
            2,
            "activa",
        ),
    )

    segundo_id = cursor.lastrowid

    conexion.commit()
    conexion.close()

    assert segundo_id > primer_id