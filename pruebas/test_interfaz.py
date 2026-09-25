"""
Pruebas estructurales de la interfaz PySide6.

No se automatizan clics para validar reglas
de negocio. Las reglas continúan probandose
directamente mediante los servicios.
"""

import os

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import pytest

from PySide6.QtWidgets import (
    QApplication,
)

from aplicacion.interfaz import (
    VentanaPrincipal,
)

from aplicacion.persistencia import (
    inicializar_base_datos,
)


@pytest.fixture(
    scope="session"
)
def aplicacion_qt():
    aplicacion = QApplication.instance()

    if aplicacion is None:
        aplicacion = QApplication(
            []
        )

    return aplicacion


@pytest.fixture
def ventana(
    aplicacion_qt,
    tmp_path,
):
    del aplicacion_qt

    ruta = tmp_path / "interfaz.db"

    inicializar_base_datos(
        ruta
    )

    ventana = VentanaPrincipal(
        ruta
    )

    yield ventana

    ventana.close()


def test_titulo_ventana(
    ventana,
):
    assert (
        ventana.windowTitle()
        == "Sistema de reservación de salas de estudio"
    )


def test_menu_tiene_siete_modulos(
    ventana,
):
    assert ventana.menu.count() == 7


def test_stack_tiene_siete_vistas(
    ventana,
):
    assert ventana.stack.count() == 7


def test_nombres_modulos_requeridos(
    ventana,
):
    nombres = [
        ventana.menu.item(
            indice
        ).text()
        for indice in range(
            ventana.menu.count()
        )
    ]

    assert nombres == [
        "Panel de control",
        "Estudiantes",
        "Salas",
        "Disponibilidad",
        "Reservaciones",
        "Reportes",
        "Historial de acciones",
    ]


def test_navegacion_cambia_vista(
    ventana,
):
    ventana.menu.setCurrentRow(
        3
    )

    assert (
        ventana.stack.currentIndex()
        == 3
    )

    assert (
        ventana.etiqueta_modulo.text()
        == "Disponibilidad"
    )


def test_estudiantes_iniciales_visibles(
    ventana,
):
    ventana.vista_estudiantes.refrescar()

    assert (
        ventana.vista_estudiantes
        .tabla.rowCount()
        == 3
    )


def test_salas_iniciales_visibles(
    ventana,
):
    ventana.vista_salas.refrescar()

    assert (
        ventana.vista_salas
        .tabla.rowCount()
        == 5
    )


def test_disponibilidad_carga_salas(
    ventana,
):
    ventana.vista_disponibilidad.refrescar()

    assert (
        ventana.vista_disponibilidad
        .combo_sala.count()
        == 5
    )


def test_reservaciones_carga_estudiantes_y_salas(
    ventana,
):
    ventana.vista_reservaciones.refrescar()

    assert (
        ventana.vista_reservaciones
        .combo_estudiante.count()
        == 3
    )

    assert (
        ventana.vista_reservaciones
        .combo_sala.count()
        == 5
    )


def test_reportes_y_auditoria_existen(
    ventana,
):
    assert (
        ventana.vista_reportes
        is not None
    )

    assert (
        ventana.vista_auditoria
        is not None
    )

    assert (
        ventana.vista_auditoria
        .tabla.rowCount()
        == 0
    )