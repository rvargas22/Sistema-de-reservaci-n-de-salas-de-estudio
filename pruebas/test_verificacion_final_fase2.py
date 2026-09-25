"""
Verificacion final integral de la Fase 2.

Estas pruebas complementan la suite existente y
comprueban aspectos de la especificacion aprobada
que requieren una validacion final explicita.
"""

import os
import re
from datetime import datetime

import pytest

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
)

from aplicacion.interfaz import (
    VentanaPrincipal,
)

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    cancelar_reservacion,
    consultar_estudiantes,
    crear_reservacion,
    registrar_estudiante,
    verificar_disponibilidad,
)


pytestmark = pytest.mark.final


AHORA = datetime(
    2026,
    9,
    25,
    9,
    0,
)


def preparar_base(
    tmp_path,
):
    ruta = (
        tmp_path
        / "verificacion_final.db"
    )

    inicializar_base_datos(
        ruta
    )

    return ruta


def contar(
    ruta,
    tabla,
):
    permitidas = {
        "estudiantes",
        "salas",
        "reservaciones",
        "auditoria",
    }

    if tabla not in permitidas:
        raise ValueError(
            "Tabla no permitida."
        )

    conexion = obtener_conexion(
        ruta
    )

    try:
        return conexion.execute(
            f"""
            SELECT COUNT(*)
            FROM {tabla}
            """
        ).fetchone()[0]

    finally:
        conexion.close()


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


def test_rf01_inicializacion_es_idempotente(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    inicializar_base_datos(
        ruta
    )

    assert contar(
        ruta,
        "estudiantes",
    ) == 3

    assert contar(
        ruta,
        "salas",
    ) == 5

    conexion = obtener_conexion(
        ruta
    )

    try:
        sala = conexion.execute(
            """
            SELECT
                codigo,
                estado

            FROM salas

            WHERE codigo = 'S04'
            """
        ).fetchone()

    finally:
        conexion.close()

    assert sala is not None

    assert (
        sala["estado"]
        == "fuera_de_servicio"
    )


def test_rf02_estudiante_nuevo_inicia_activo(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    estudiante = registrar_estudiante(
        carne="Z000000001",
        nombre="Aaron Álvarez",
        correo="aaron@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    assert (
        estudiante.estado
        == "activo"
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        vista = ventana.vista_estudiantes

        vista.nuevo()

        assert (
            vista.combo_estado.currentData()
            == "activo"
        )

        assert (
            vista.combo_estado.isEnabled()
            is False
        )

    finally:
        ventana.close()


def test_rf03_estudiantes_ordenados_por_nombre(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        carne="Z000000001",
        nombre="Aaron Álvarez",
        correo="aaron@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    registrar_estudiante(
        carne="D000000001",
        nombre="Zoé Vargas",
        correo="zoe@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    estudiantes = consultar_estudiantes(
        ruta
    )

    nombres = [
        estudiante.nombre
        for estudiante
        in estudiantes
    ]

    assert nombres == sorted(
        nombres,
        key=str.casefold,
    )


def test_rf05_identificador_formato_r0001(
    tmp_path,
):
    """
    El ID interno permanece numerico y el
    identificador visible cumple R0001.
    """

    ruta = preparar_base(
        tmp_path
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

    assert isinstance(
        reservacion.id,
        int,
    )

    assert (
        reservacion.id
        == 1
    )

    assert isinstance(
        reservacion.identificador,
        str,
    )

    assert re.fullmatch(
        r"R\d{4,}",
        reservacion.identificador,
    )

    assert (
        reservacion.identificador
        == "R0001"
    )


def test_identificador_continua_y_no_se_reutiliza(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    primera = crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert (
        primera.id
        == 1
    )

    assert (
        primera.identificador
        == "R0001"
    )

    cancelar_reservacion(
        primera.identificador,
        ruta,
    )

    inicializar_base_datos(
        ruta
    )

    segunda = crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S02",
        fecha="2026-10-11",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert (
        segunda.id
        == 2
    )

    assert (
        segunda.identificador
        == "R0002"
    )

    assert (
        segunda.identificador
        != primera.identificador
    )


def test_rf06_interfaz_muestra_inicio_y_fin(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        tabla = (
            ventana
            .vista_reservaciones
            .tabla_reservaciones
        )

        encabezados = [
            (
                tabla.horizontalHeaderItem(
                    indice
                )
                .text()
                .strip()
                .lower()
            )
            for indice in range(
                tabla.columnCount()
            )
        ]

        assert any(
            "inicio" in texto
            for texto
            in encabezados
        )

        assert any(
            "fin" in texto
            for texto
            in encabezados
        )

    finally:
        ventana.close()


def test_rf07_interfaz_incluye_busqueda_por_estudiante(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        vista = (
            ventana.vista_reservaciones
        )

        textos = []

        for boton in vista.findChildren(
            QPushButton
        ):
            textos.append(
                boton.text().lower()
            )

        for etiqueta in vista.findChildren(
            QLabel
        ):
            textos.append(
                etiqueta.text().lower()
            )

        for campo in vista.findChildren(
            QLineEdit
        ):
            textos.append(
                campo.placeholderText().lower()
            )

        contenido = " ".join(
            textos
        )

        assert (
            "buscar" in contenido
        )

        assert (
            "estudiante" in contenido
            or "carné" in contenido
            or "carne" in contenido
        )

    finally:
        ventana.close()


def test_rf08_disponibilidad_no_modifica_datos(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reservaciones_antes = contar(
        ruta,
        "reservaciones",
    )

    auditoria_antes = contar(
        ruta,
        "auditoria",
    )

    disponible = verificar_disponibilidad(
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert disponible is True

    assert contar(
        ruta,
        "reservaciones",
    ) == reservaciones_antes

    assert contar(
        ruta,
        "auditoria",
    ) == auditoria_antes


def test_rf10_existe_salida_controlada(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        textos = []

        for boton in ventana.findChildren(
            QPushButton
        ):
            textos.append(
                boton.text().strip().lower()
            )

        for indice in range(
            ventana.menu.count()
        ):
            textos.append(
                ventana.menu.item(
                    indice
                ).text().strip().lower()
            )

        for accion in (
            ventana.menuBar().actions()
        ):
            textos.append(
                accion.text().strip().lower()
            )

        assert any(
            "salir" in texto
            for texto
            in textos
        )

        assert (
            "closeEvent"
            in type(
                ventana
            ).__dict__
        )

    finally:
        ventana.close()


def test_rf14_interfaz_muestra_analisis_previo(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        vista = (
            ventana.vista_reservaciones
        )

        textos = []

        for boton in vista.findChildren(
            QPushButton
        ):
            textos.append(
                boton.text().lower()
            )

        for etiqueta in vista.findChildren(
            QLabel
        ):
            textos.append(
                etiqueta.text().lower()
            )

        contenido = " ".join(
            textos
        )

        assert (
            "analizar serie"
            in contenido
        )

        assert (
            "análisis previo"
            in contenido
            or "analisis previo"
            in contenido
        )

    finally:
        ventana.close()


def test_rf15_panel_presenta_resumen_obligatorio(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        vista = ventana.vista_panel

        textos = [
            etiqueta.text().lower()
            for etiqueta
            in vista.findChildren(
                QLabel
            )
        ]

        contenido = " ".join(
            textos
        )

        assert "hoy" in contenido

        assert (
            "próxim" in contenido
            or "proxim" in contenido
        )

        assert (
            "ocupación" in contenido
            or "ocupacion" in contenido
        )

    finally:
        ventana.close()


def test_vistas_obligatorias_y_regreso_al_panel(
    tmp_path,
    aplicacion_qt,
):
    del aplicacion_qt

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        esperados = [
            "Panel de control",
            "Estudiantes",
            "Salas",
            "Disponibilidad",
            "Reservaciones",
            "Reportes",
            "Historial de acciones",
        ]

        reales = [
            ventana.menu.item(
                indice
            ).text()
            for indice
            in range(
                ventana.menu.count()
            )
        ]

        assert reales == esperados

        ventana.menu.setCurrentRow(
            4
        )

        assert (
            ventana.stack.currentIndex()
            == 4
        )

        ventana.menu.setCurrentRow(
            0
        )

        assert (
            ventana.stack.currentIndex()
            == 0
        )

        assert (
            ventana.etiqueta_modulo.text()
            == "Panel de control"
        )

    finally:
        ventana.close()