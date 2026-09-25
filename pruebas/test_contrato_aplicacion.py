"""
Pruebas estructurales y de contrato tecnico
de la aplicacion.

Estas pruebas complementan la suite funcional.
"""

import importlib.util
import inspect
import sys

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    buscar_estudiante,
    consultar_estudiantes,
    consultar_panel,
    consultar_salas,
    registrar_estudiante,
)


pytestmark = pytest.mark.contrato


def preparar_base(
    tmp_path,
):
    """
    Inicializa una base temporal.
    """

    ruta = tmp_path / "contrato.db"

    inicializar_base_datos(
        ruta
    )

    return ruta


def test_python_310_o_superior():
    """
    Verifica RNF-01.
    """

    assert sys.version_info >= (
        3,
        10,
    )


def test_datos_iniciales_requeridos(
    tmp_path,
):
    """
    Verifica que la base nueva contenga exactamente
    los estudiantes y salas iniciales definidos.
    """

    ruta = preparar_base(
        tmp_path
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        estudiantes = conexion.execute(
            """
            SELECT
                carne,
                nombre,
                correo,
                estado

            FROM estudiantes

            ORDER BY carne
            """
        ).fetchall()

        salas = conexion.execute(
            """
            SELECT
                codigo,
                nombre,
                capacidad,
                estado

            FROM salas

            ORDER BY codigo
            """
        ).fetchall()

    finally:
        conexion.close()

    estudiantes = [
        tuple(fila)
        for fila in estudiantes
    ]

    salas = [
        tuple(fila)
        for fila in salas
    ]

    assert estudiantes == [
        (
            "A001234567",
            "Andrea Solano",
            "andrea@universidad.ac.cr",
            "activo",
        ),
        (
            "B009876543",
            "Carlos Méndez",
            "carlos@universidad.ac.cr",
            "activo",
        ),
        (
            "C004567890",
            "Daniela Rojas",
            "daniela@universidad.ac.cr",
            "inactivo",
        ),
    ]

    assert salas == [
        (
            "S01",
            "Sala Biblioteca 1",
            4,
            "disponible",
        ),
        (
            "S02",
            "Sala Biblioteca 2",
            6,
            "disponible",
        ),
        (
            "S03",
            "Laboratorio de estudio",
            10,
            "disponible",
        ),
        (
            "S04",
            "Sala multimedia",
            8,
            "fuera_de_servicio",
        ),
        (
            "S05",
            "Cubículo individual",
            1,
            "disponible",
        ),
    ]


def test_capas_principales_existen():
    """
    Comprueba la estructura modular principal.
    """

    modulos = [
        "aplicacion.modelos",
        "aplicacion.validaciones",
        "aplicacion.persistencia",
        "aplicacion.servicios",
        "aplicacion.interfaz",
    ]

    for modulo in modulos:
        assert (
            importlib.util.find_spec(
                modulo
            )
            is not None
        )


def test_logica_funciona_sin_qapplication(
    tmp_path,
):
    """
    Verifica RNF-10.

    Las operaciones de negocio pueden ejecutarse
    directamente sin crear QApplication ni
    automatizar clics.
    """

    ruta = preparar_base(
        tmp_path
    )

    estudiantes = consultar_estudiantes(
        ruta
    )

    salas = consultar_salas(
        ruta
    )

    panel = consultar_panel(
        ruta_base_datos=ruta
    )

    assert len(estudiantes) == 3
    assert len(salas) == 5
    assert panel == []


def test_modelos_no_dependen_de_pyside6():
    """
    Comprueba que los modelos del dominio no
    dependan de la interfaz Qt.
    """

    import aplicacion.modelos.estudiante as estudiante
    import aplicacion.modelos.reservacion as reservacion
    import aplicacion.modelos.sala as sala

    modulos = [
        estudiante,
        reservacion,
        sala,
    ]

    for modulo in modulos:
        fuente = inspect.getsource(
            modulo
        )

        assert "PySide6" not in fuente
        assert "aplicacion.interfaz" not in fuente


def test_servicios_no_dependen_de_interfaz():
    """
    Verifica la separacion entre servicios
    e interfaz grafica.
    """

    import aplicacion.servicios.servicio_auditoria as auditoria
    import aplicacion.servicios.servicio_disponibilidad as disponibilidad
    import aplicacion.servicios.servicio_estudiantes as estudiantes
    import aplicacion.servicios.servicio_panel as panel
    import aplicacion.servicios.servicio_recurrencia as recurrencia
    import aplicacion.servicios.servicio_reportes as reportes
    import aplicacion.servicios.servicio_reservaciones as reservaciones
    import aplicacion.servicios.servicio_salas as salas

    modulos = [
        auditoria,
        disponibilidad,
        estudiantes,
        panel,
        recurrencia,
        reportes,
        reservaciones,
        salas,
    ]

    for modulo in modulos:
        fuente = inspect.getsource(
            modulo
        )

        assert "PySide6" not in fuente
        assert "aplicacion.interfaz" not in fuente


def test_persistencia_no_depende_de_interfaz():
    """
    Verifica la separacion entre persistencia
    e interfaz grafica.
    """

    import aplicacion.persistencia.base_datos as base_datos
    import aplicacion.persistencia.inicializador as inicializador
    import aplicacion.persistencia.integridad as integridad
    import aplicacion.persistencia.repositorio_auditoria as auditoria
    import aplicacion.persistencia.repositorio_estudiantes as estudiantes
    import aplicacion.persistencia.repositorio_recurrencia as recurrencia
    import aplicacion.persistencia.repositorio_reservaciones as reservaciones
    import aplicacion.persistencia.repositorio_salas as salas
    import aplicacion.persistencia.transacciones as transacciones

    modulos = [
        base_datos,
        inicializador,
        integridad,
        auditoria,
        estudiantes,
        recurrencia,
        reservaciones,
        salas,
        transacciones,
    ]

    for modulo in modulos:
        fuente = inspect.getsource(
            modulo
        )

        assert "PySide6" not in fuente
        assert "aplicacion.interfaz" not in fuente


def test_utf8_se_conserva_en_persistencia(
    tmp_path,
):
    """
    Verifica la conservacion de caracteres UTF-8
    sin depender de exportacion CSV.
    """

    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        "D001234567",
        "María Peña Muñoz",
        "maria@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    estudiante = buscar_estudiante(
        "D001234567",
        ruta,
    )

    assert (
        estudiante.nombre
        == "María Peña Muñoz"
    )