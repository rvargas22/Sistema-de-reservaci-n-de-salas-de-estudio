"""
Pruebas del servicio de reportes y exportacion CSV.
"""

import csv
from datetime import datetime

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    cancelar_reservacion,
    crear_reservacion,
    exportar_reporte_csv,
    generar_reporte_reservaciones,
    registrar_estudiante,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


AHORA = datetime(
    2026,
    9,
    24,
    9,
    0,
)


def preparar_base(tmp_path):
    """
    Inicializa una base temporal.
    """

    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(
        ruta
    )

    return ruta


def preparar_reservaciones(
    ruta,
):
    """
    Crea reservaciones en distintas fechas
    para las pruebas de reportes.
    """

    primera = crear_reservacion(
        "A001234567",
        "S01",
        "2026-10-01",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    segunda = crear_reservacion(
        "B009876543",
        "S02",
        "2026-10-05",
        "11:00",
        1,
        3,
        ruta,
        AHORA,
    )

    tercera = crear_reservacion(
        "A001234567",
        "S03",
        "2026-10-10",
        "12:00",
        1,
        4,
        ruta,
        AHORA,
    )

    return (
        primera,
        segunda,
        tercera,
    )


def test_generar_reporte_por_rango(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-05",
        ruta,
    )

    assert len(reporte) == 2


def test_rango_incluye_ambos_extremos(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    fechas = [
        fila["fecha"]
        for fila in reporte
    ]

    assert "2026-10-01" in fechas
    assert "2026-10-10" in fechas


def test_reporte_excluye_fechas_fuera_del_rango(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-05",
        "2026-10-05",
        ruta,
    )

    assert len(reporte) == 1
    assert reporte[0]["fecha"] == "2026-10-05"


def test_fecha_inicial_es_obligatoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion,
        match="fecha inicial",
    ):
        generar_reporte_reservaciones(
            None,
            "2026-10-10",
            ruta,
        )


def test_fecha_final_es_obligatoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion,
        match="fecha final",
    ):
        generar_reporte_reservaciones(
            "2026-10-01",
            None,
            ruta,
        )


def test_fecha_vacia_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion,
    ):
        generar_reporte_reservaciones(
            "",
            "2026-10-10",
            ruta,
        )


def test_fecha_final_anterior_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="anterior",
    ):
        generar_reporte_reservaciones(
            "2026-10-10",
            "2026-10-01",
            ruta,
        )


def test_formato_fecha_invalido_es_rechazado(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion,
    ):
        generar_reporte_reservaciones(
            "01-10-2026",
            "2026-10-10",
            ruta,
        )


def test_reporte_vacio_devuelve_lista_vacia(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reporte = generar_reporte_reservaciones(
        "2027-01-01",
        "2027-01-31",
        ruta,
    )

    assert reporte == []


def test_reporte_incluye_activas_y_canceladas(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    primera, _, _ = preparar_reservaciones(
        ruta
    )

    cancelar_reservacion(
        primera.id,
        ruta,
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    estados = {
        fila["estado"]
        for fila in reporte
    }

    assert "activa" in estados
    assert "cancelada" in estados


def test_exportar_csv_crea_archivo(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    destino = tmp_path / "reporte.csv"

    resultado = exportar_reporte_csv(
        reporte,
        destino,
    )

    assert resultado == destino
    assert destino.exists()


def test_exportacion_agrega_extension_csv(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    destino = tmp_path / "reporte"

    resultado = exportar_reporte_csv(
        reporte,
        destino,
    )

    assert resultado.suffix == ".csv"
    assert resultado.exists()


def test_csv_contiene_encabezados_correctos(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    destino = tmp_path / "reporte.csv"

    exportar_reporte_csv(
        reporte,
        destino,
    )

    with open(
        destino,
        encoding="utf-8",
        newline="",
    ) as archivo:

        lector = csv.reader(
            archivo
        )

        encabezados = next(
            lector
        )

    assert encabezados == [
        "id",
        "carne_estudiante",
        "nombre_estudiante",
        "codigo_sala",
        "nombre_sala",
        "fecha",
        "hora_inicio",
        "duracion_horas",
        "cantidad_personas",
        "estado",
    ]


def test_csv_conserva_tildes_y_enie(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        "D001234567",
        "María Peña",
        "maria@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    crear_reservacion(
        "D001234567",
        "S05",
        "2026-10-15",
        "10:00",
        1,
        1,
        ruta,
        AHORA,
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-15",
        "2026-10-15",
        ruta,
    )

    destino = tmp_path / "reporte_utf8.csv"

    exportar_reporte_csv(
        reporte,
        destino,
    )

    contenido = destino.read_text(
        encoding="utf-8"
    )

    assert "María Peña" in contenido
    assert "Cubículo individual" in contenido


def test_cancelar_destino_no_crea_archivo(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    archivos_antes = set(
        tmp_path.iterdir()
    )

    resultado = exportar_reporte_csv(
        reporte,
        None,
    )

    archivos_despues = set(
        tmp_path.iterdir()
    )

    assert resultado is None

    assert (
        archivos_antes
        == archivos_despues
    )


def test_cancelar_con_cadena_vacia_no_crea_csv(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    resultado = exportar_reporte_csv(
        reporte,
        "",
    )

    assert resultado is None

    assert not list(
        tmp_path.glob("*.csv")
    )


def test_generar_y_exportar_reporte_no_modifica_base(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_reservaciones(
        ruta
    )

    conexion = obtener_conexion(
        ruta
    )

    cantidad_antes = conexion.execute(
        """
        SELECT COUNT(*)
        FROM reservaciones
        """
    ).fetchone()[0]

    conexion.close()

    reporte = generar_reporte_reservaciones(
        "2026-10-01",
        "2026-10-10",
        ruta,
    )

    exportar_reporte_csv(
        reporte,
        tmp_path / "reporte.csv",
    )

    conexion = obtener_conexion(
        ruta
    )

    cantidad_despues = conexion.execute(
        """
        SELECT COUNT(*)
        FROM reservaciones
        """
    ).fetchone()[0]

    conexion.close()

    assert cantidad_antes == 3
    assert cantidad_despues == 3