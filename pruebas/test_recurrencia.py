"""
Pruebas del modulo de recurrencia.
"""

from datetime import datetime

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    analizar_serie_recurrente,
    cancelar_ocurrencia_recurrente,
    cancelar_ocurrencias_futuras,
    consultar_ocurrencias_serie,
    crear_reservacion,
    crear_serie_recurrente,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
)


AHORA = datetime(
    2026,
    9,
    24,
    9,
    0,
)


def preparar_base(tmp_path):
    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(
        ruta
    )

    return ruta


def crear_serie(
    ruta,
    cantidad=3,
):
    return crear_serie_recurrente(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha_inicio="2026-10-05",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        cantidad_ocurrencias=cantidad,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )


def test_rechazar_una_ocurrencia(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="entre 2 y 8",
    ):
        crear_serie(
            ruta,
            1,
        )


def test_aceptar_dos_ocurrencias(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        2,
    )

    assert serie["serie_id"] == 1
    assert len(
        serie["reservaciones"]
    ) == 2


def test_aceptar_ocho_ocurrencias(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        8,
    )

    assert len(
        serie["reservaciones"]
    ) == 8


def test_rechazar_nueve_ocurrencias(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="entre 2 y 8",
    ):
        crear_serie(
            ruta,
            9,
        )


def test_fechas_son_semanales(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        3,
    )

    fechas = [
        reservacion.fecha
        for reservacion
        in serie["reservaciones"]
    ]

    assert fechas == [
        "2026-10-05",
        "2026-10-12",
        "2026-10-19",
    ]


def test_analisis_muestra_conflicto_antes_de_guardar(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    crear_reservacion(
        carne_estudiante="B009876543",
        codigo_sala="S01",
        fecha="2026-10-12",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    resumen = analizar_serie_recurrente(
        "A001234567",
        "S01",
        "2026-10-05",
        "10:00",
        1,
        2,
        3,
        ruta,
        AHORA,
    )

    assert resumen["hay_conflictos"] is True

    assert (
        resumen["ocurrencias"][0]["disponible"]
        is True
    )

    assert (
        resumen["ocurrencias"][1]["disponible"]
        is False
    )

    assert (
        resumen["ocurrencias"][2]["disponible"]
        is True
    )


def test_conflicto_impide_guardado_parcial(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    crear_reservacion(
        "B009876543",
        "S01",
        "2026-10-12",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="conflictos",
    ):
        crear_serie(
            ruta,
            3,
        )

    conexion = obtener_conexion(
        ruta
    )

    cantidad_series = conexion.execute(
        """
        SELECT COUNT(*)
        FROM series_recurrentes
        """
    ).fetchone()[0]

    cantidad_reservaciones = conexion.execute(
        """
        SELECT COUNT(*)
        FROM reservaciones
        """
    ).fetchone()[0]

    conexion.close()

    assert cantidad_series == 0

    # Solamente permanece la reservacion
    # preparada para producir el conflicto.
    assert cantidad_reservaciones == 1


def test_estudiante_inactivo_no_crea_serie(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="inactivo",
    ):
        crear_serie_recurrente(
            "C004567890",
            "S01",
            "2026-10-05",
            "10:00",
            1,
            1,
            2,
            ruta,
            AHORA,
        )


def test_sala_fuera_servicio_no_crea_serie(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="fuera de servicio",
    ):
        crear_serie_recurrente(
            "A001234567",
            "S04",
            "2026-10-05",
            "10:00",
            1,
            2,
            2,
            ruta,
            AHORA,
        )


def test_capacidad_aplica_a_serie(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    resumen = analizar_serie_recurrente(
        "A001234567",
        "S01",
        "2026-10-05",
        "10:00",
        1,
        5,
        2,
        ruta,
        AHORA,
    )

    assert resumen["hay_conflictos"] is True

    assert all(
        ocurrencia["disponible"] is False
        for ocurrencia
        in resumen["ocurrencias"]
    )


def test_cancelar_una_ocurrencia(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        3,
    )

    cancelar_ocurrencia_recurrente(
        serie["serie_id"],
        2,
        ruta,
    )

    ocurrencias = (
        consultar_ocurrencias_serie(
            serie["serie_id"],
            ruta,
        )
    )

    assert (
        ocurrencias[0]["reservacion"].estado
        == "activa"
    )

    assert (
        ocurrencias[1]["reservacion"].estado
        == "cancelada"
    )

    assert (
        ocurrencias[2]["reservacion"].estado
        == "activa"
    )


def test_cancelar_futuras_conserva_anteriores(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        4,
    )

    ocurrencias = cancelar_ocurrencias_futuras(
        serie["serie_id"],
        2,
        ruta,
    )

    # Con el comportamiento por defecto,
    # la seleccionada se conserva y se cancelan
    # solamente las posteriores.
    assert (
        ocurrencias[0]["reservacion"].estado
        == "activa"
    )

    assert (
        ocurrencias[1]["reservacion"].estado
        == "activa"
    )

    assert (
        ocurrencias[2]["reservacion"].estado
        == "cancelada"
    )

    assert (
        ocurrencias[3]["reservacion"].estado
        == "cancelada"
    )


def test_cancelar_futuras_puede_incluir_seleccionada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        4,
    )

    ocurrencias = cancelar_ocurrencias_futuras(
        serie_id=serie["serie_id"],
        numero_ocurrencia_desde=2,
        ruta_base_datos=ruta,
        incluir_seleccionada=True,
    )

    assert (
        ocurrencias[0]["reservacion"].estado
        == "activa"
    )

    assert (
        ocurrencias[1]["reservacion"].estado
        == "cancelada"
    )

    assert (
        ocurrencias[2]["reservacion"].estado
        == "cancelada"
    )

    assert (
        ocurrencias[3]["reservacion"].estado
        == "cancelada"
    )


def test_canceladas_permanecen_en_historial_serie(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    serie = crear_serie(
        ruta,
        3,
    )

    cancelar_ocurrencia_recurrente(
        serie["serie_id"],
        2,
        ruta,
    )

    ocurrencias = consultar_ocurrencias_serie(
        serie["serie_id"],
        ruta,
    )

    assert len(ocurrencias) == 3

    assert (
        ocurrencias[1]["reservacion"].estado
        == "cancelada"
    )

    assert (
        ocurrencias[1]["reservacion"].id
        is not None
    )