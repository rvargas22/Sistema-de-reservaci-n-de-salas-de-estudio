"""
Verificacion automatizada de los requisitos
no funcionales RNF-01 a RNF-08 y RNF-10.

RNF-09 se verifica separadamente mediante
test_rendimiento.py porque requiere una carga
especifica de 1 000 estudiantes y
5 000 reservaciones.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import pytest

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

from PySide6.QtWidgets import QApplication

from aplicacion.interfaz import (
    VentanaPrincipal,
)

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
    verificar_integridad_base_datos,
)

from aplicacion.servicios import (
    buscar_estudiante,
    consultar_estudiantes,
    consultar_panel,
    consultar_salas,
    crear_reservacion,
    exportar_reporte_csv,
    generar_reporte_reservaciones,
    registrar_estudiante,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


pytestmark = pytest.mark.rnf


RAIZ_PROYECTO = (
    Path(__file__).resolve().parents[1]
)


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
    """
    Inicializa una base temporal independiente.
    """

    ruta = (
        tmp_path
        / "requisitos_no_funcionales.db"
    )

    inicializar_base_datos(
        ruta
    )

    return ruta


def contar_registros(
    ruta,
    tabla,
):
    """
    Cuenta registros de una tabla conocida.

    La funcion se utiliza solamente dentro
    de estas pruebas.
    """

    tablas_permitidas = {
        "estudiantes",
        "salas",
        "reservaciones",
        "auditoria",
    }

    if tabla not in tablas_permitidas:
        raise ValueError(
            "Tabla no permitida."
        )

    conexion = obtener_conexion(
        ruta
    )

    try:
        cantidad = conexion.execute(
            f"""
            SELECT COUNT(*)
            FROM {tabla}
            """
        ).fetchone()[0]

    finally:
        conexion.close()

    return cantidad


def test_rnf01_python_310_o_superior():
    """
    RNF-01 Compatibilidad.

    La aplicacion debe ejecutarse con
    Python 3.10 o superior.
    """

    assert sys.version_info >= (
        3,
        10,
    )


def test_rnf02_dependencias_declaradas():
    """
    RNF-02 Dependencias.

    Comprueba que exista requirements.txt y que
    las dependencias externas utilizadas por el
    proyecto esten declaradas.
    """

    ruta_requirements = (
        RAIZ_PROYECTO
        / "requirements.txt"
    )

    assert ruta_requirements.exists()

    contenido = (
        ruta_requirements.read_text(
            encoding="utf-8"
        )
        .lower()
    )

    assert "pyside6" in contenido

    assert "pytest" in contenido


def test_rnf03_codigo_productivo_sin_rutas_personales_absolutas():
    """
    RNF-03 Portabilidad.

    Comprueba que el codigo productivo no contenga
    rutas personales absolutas tipicas de macOS,
    Linux o Windows.
    """

    archivos = list(
        (
            RAIZ_PROYECTO
            / "aplicacion"
        ).rglob(
            "*.py"
        )
    )

    archivos.append(
        RAIZ_PROYECTO
        / "main.py"
    )

    patrones_prohibidos = [
        "/Users/",
        "/home/",
        "C:\\Users\\",
        "C:/Users/",
    ]

    hallazgos = []

    for archivo in archivos:
        contenido = archivo.read_text(
            encoding="utf-8"
        )

        for patron in patrones_prohibidos:
            if patron in contenido:
                hallazgos.append(
                    (
                        str(
                            archivo.relative_to(
                                RAIZ_PROYECTO
                            )
                        ),
                        patron,
                    )
                )

    assert hallazgos == []


def test_rnf04_interfaz_mantiene_navegacion_consistente(
    tmp_path,
):
    """
    RNF-04 Usabilidad.

    Verifica estructuralmente que la ventana
    principal mantenga los siete modulos
    obligatorios y una navegacion consistente.
    """

    aplicacion = QApplication.instance()

    if aplicacion is None:
        aplicacion = QApplication(
            []
        )

    ruta = preparar_base(
        tmp_path
    )

    ventana = VentanaPrincipal(
        ruta
    )

    try:
        nombres_esperados = [
            "Panel de control",
            "Estudiantes",
            "Salas",
            "Disponibilidad",
            "Reservaciones",
            "Reportes",
            "Historial de acciones",
        ]

        assert (
            ventana.menu.count()
            == len(
                nombres_esperados
            )
        )

        assert (
            ventana.stack.count()
            == len(
                nombres_esperados
            )
        )

        nombres_reales = [
            ventana.menu.item(
                indice
            ).text()
            for indice
            in range(
                ventana.menu.count()
            )
        ]

        assert (
            nombres_reales
            == nombres_esperados
        )

        for indice, nombre in enumerate(
            nombres_esperados
        ):
            ventana.menu.setCurrentRow(
                indice
            )

            assert (
                ventana.stack.currentIndex()
                == indice
            )

            assert (
                ventana.etiqueta_modulo.text()
                == nombre
            )

        assert (
            ventana.styleSheet().strip()
            != ""
        )

    finally:
        ventana.close()


def test_rnf05_entrada_invalida_no_genera_datos_parciales(
    tmp_path,
):
    """
    RNF-05 Robustez.

    Una entrada invalida debe ser rechazada sin
    producir datos parciales.
    """

    ruta = preparar_base(
        tmp_path
    )

    cantidad_antes = contar_registros(
        ruta,
        "estudiantes",
    )

    with pytest.raises(
        ErrorValidacion
    ):
        registrar_estudiante(
            carne="A12",
            nombre="Estudiante inválido",
            correo="estudiante@universidad.ac.cr",
            ruta_base_datos=ruta,
        )

    cantidad_despues = contar_registros(
        ruta,
        "estudiantes",
    )

    assert (
        cantidad_despues
        == cantidad_antes
    )

    assert (
        verificar_integridad_base_datos(
            ruta
        )
        is True
    )


def test_rnf06_operacion_rechazada_conserva_integridad(
    tmp_path,
):
    """
    RNF-06 Integridad.

    Una escritura rechazada no debe modificar
    reservaciones ni deteriorar la integridad
    de SQLite.
    """

    ruta = preparar_base(
        tmp_path
    )

    reservaciones_antes = (
        contar_registros(
            ruta,
            "reservaciones",
        )
    )

    auditoria_antes = (
        contar_registros(
            ruta,
            "auditoria",
        )
    )

    with pytest.raises(
        ErrorReglaNegocio
    ):
        crear_reservacion(
            carne_estudiante="Z999999999",
            codigo_sala="S01",
            fecha="2026-10-10",
            hora_inicio="10:00",
            duracion_horas=1,
            cantidad_personas=2,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )

    reservaciones_despues = (
        contar_registros(
            ruta,
            "reservaciones",
        )
    )

    auditoria_despues = (
        contar_registros(
            ruta,
            "auditoria",
        )
    )

    assert (
        reservaciones_despues
        == reservaciones_antes
    )

    assert (
        auditoria_despues
        == auditoria_antes
    )

    assert (
        verificar_integridad_base_datos(
            ruta
        )
        is True
    )


def test_rnf07_capas_identificables_y_sin_dependencia_hacia_interfaz():
    """
    RNF-07 Mantenibilidad.

    Verifica la existencia de las capas principales
    y que servicios/persistencia no dependan de
    PySide6 ni de la capa de interfaz.
    """

    carpetas = [
        "modelos",
        "persistencia",
        "servicios",
        "validaciones",
        "interfaz",
    ]

    for carpeta in carpetas:
        assert (
            (
                RAIZ_PROYECTO
                / "aplicacion"
                / carpeta
            ).is_dir()
        )

    archivos_sin_interfaz = []

    archivos_sin_interfaz.extend(
        (
            RAIZ_PROYECTO
            / "aplicacion"
            / "servicios"
        ).rglob(
            "*.py"
        )
    )

    archivos_sin_interfaz.extend(
        (
            RAIZ_PROYECTO
            / "aplicacion"
            / "persistencia"
        ).rglob(
            "*.py"
        )
    )

    for archivo in archivos_sin_interfaz:
        contenido = archivo.read_text(
            encoding="utf-8"
        )

        assert (
            "PySide6"
            not in contenido
        )

        assert (
            "aplicacion.interfaz"
            not in contenido
        )


def test_rnf08_utf8_base_y_exportacion(
    tmp_path,
):
    """
    RNF-08 Codificacion.

    Comprueba caracteres con tilde y ñ tanto
    en SQLite como en el CSV exportado.
    """

    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        carne="D001234567",
        nombre="María Peña Muñoz",
        correo="maria@universidad.ac.cr",
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

    crear_reservacion(
        carne_estudiante="D001234567",
        codigo_sala="S05",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-10",
        "2026-10-10",
        ruta,
    )

    destino = (
        tmp_path
        / "reporte_utf8.csv"
    )

    exportar_reporte_csv(
        reporte,
        destino,
    )

    contenido = destino.read_text(
        encoding="utf-8"
    )

    assert (
        "María Peña Muñoz"
        in contenido
    )

    assert (
        "Cubículo individual"
        in contenido
    )


def test_rnf10_logica_negocio_sin_automatizacion_gui(
    tmp_path,
):
    """
    RNF-10 Testabilidad.

    Comprueba que los servicios puedan utilizarse
    directamente sin automatizar interacciones
    de la interfaz grafica.
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

    assert len(estudiantes) == 3
    assert len(salas) == 5
    assert panel == []

    assert (
        reservacion.id
        is not None
    )