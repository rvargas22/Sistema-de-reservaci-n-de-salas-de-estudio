"""
Pruebas del servicio del panel principal.
"""

from datetime import datetime

import pytest

from aplicacion.modelos import (
    Reservacion,
)

from aplicacion.persistencia import (
    guardar_reservacion,
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    cancelar_reservacion,
    consultar_panel,
    crear_reservacion,
    modificar_reservacion,
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


def guardar_reserva_directa(
    ruta,
    carne="A001234567",
    sala="S01",
    fecha="2026-10-10",
    hora="10:00",
    estado="activa",
):
    """
    Guarda una reservacion para preparar
    escenarios de prueba del panel.
    """

    reservacion = Reservacion(
        carne_estudiante=carne,
        codigo_sala=sala,
        fecha=fecha,
        hora_inicio=hora,
        duracion_horas=1,
        cantidad_personas=2,
        estado=estado,
    )

    return guardar_reservacion(
        reservacion,
        ruta,
    )


def preparar_varias_reservaciones(
    ruta,
):
    """
    Prepara diferentes combinaciones
    de fecha, sala y estado.
    """

    guardar_reserva_directa(
        ruta,
        carne="A001234567",
        sala="S01",
        fecha="2026-10-10",
        hora="10:00",
        estado="activa",
    )

    guardar_reserva_directa(
        ruta,
        carne="B009876543",
        sala="S01",
        fecha="2026-10-10",
        hora="12:00",
        estado="cancelada",
    )

    guardar_reserva_directa(
        ruta,
        carne="A001234567",
        sala="S02",
        fecha="2026-10-10",
        hora="14:00",
        estado="activa",
    )

    guardar_reserva_directa(
        ruta,
        carne="A001234567",
        sala="S01",
        fecha="2026-10-11",
        hora="10:00",
        estado="activa",
    )


def test_panel_vacio(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    resultado = consultar_panel(
        ruta_base_datos=ruta
    )

    assert resultado == []


def test_panel_muestra_todas_las_reservaciones(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
        ruta
    )

    resultado = consultar_panel(
        ruta_base_datos=ruta
    )

    assert len(resultado) == 4

    assert (
        resultado[0]["nombre_estudiante"]
        == "Andrea Solano"
    )

    assert (
        resultado[0]["nombre_sala"]
        == "Sala Biblioteca 1"
    )


def test_filtrar_panel_por_fecha(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
        ruta
    )

    resultado = consultar_panel(
        fecha="2026-10-10",
        ruta_base_datos=ruta,
    )

    assert len(resultado) == 3

    assert all(
        fila["fecha"] == "2026-10-10"
        for fila in resultado
    )


def test_filtrar_panel_por_sala(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
        ruta
    )

    resultado = consultar_panel(
        codigo_sala="S02",
        ruta_base_datos=ruta,
    )

    assert len(resultado) == 1

    assert (
        resultado[0]["codigo_sala"]
        == "S02"
    )


def test_filtrar_panel_por_estado(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
        ruta
    )

    resultado = consultar_panel(
        estado="cancelada",
        ruta_base_datos=ruta,
    )

    assert len(resultado) == 1

    assert (
        resultado[0]["estado"]
        == "cancelada"
    )


def test_combinar_fecha_sala_y_estado(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
        ruta
    )

    resultado = consultar_panel(
        fecha="2026-10-10",
        codigo_sala="S01",
        estado="cancelada",
        ruta_base_datos=ruta,
    )

    assert len(resultado) == 1

    assert (
        resultado[0]["fecha"]
        == "2026-10-10"
    )

    assert (
        resultado[0]["codigo_sala"]
        == "S01"
    )

    assert (
        resultado[0]["estado"]
        == "cancelada"
    )


def test_estado_se_normaliza(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
        ruta
    )

    resultado = consultar_panel(
        estado=" ACTIVA ",
        ruta_base_datos=ruta,
    )

    assert len(resultado) == 3


def test_panel_se_actualiza_despues_de_crear(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    antes = consultar_panel(
        ruta_base_datos=ruta
    )

    assert len(antes) == 0

    crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    despues = consultar_panel(
        ruta_base_datos=ruta
    )

    assert len(despues) == 1


def test_panel_se_actualiza_despues_de_modificar(
    tmp_path,
):
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

    modificar_reservacion(
        reservacion.id,
        hora_inicio="11:00",
        cantidad_personas=3,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    resultado = consultar_panel(
        ruta_base_datos=ruta
    )

    assert len(resultado) == 1

    assert (
        resultado[0]["hora_inicio"]
        == "11:00"
    )

    assert (
        resultado[0]["cantidad_personas"]
        == 3
    )


def test_panel_se_actualiza_despues_de_cancelar(
    tmp_path,
):
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

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    resultado = consultar_panel(
        ruta_base_datos=ruta
    )

    assert len(resultado) == 1

    assert (
        resultado[0]["estado"]
        == "cancelada"
    )


def test_estado_invalido_es_rechazado(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion,
        match="estado",
    ):
        consultar_panel(
            estado="eliminada",
            ruta_base_datos=ruta,
        )


def test_fecha_invalida_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion,
    ):
        consultar_panel(
            fecha="10-10-2026",
            ruta_base_datos=ruta,
        )


def test_sala_inexistente_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="no existe",
    ):
        consultar_panel(
            codigo_sala="S99",
            ruta_base_datos=ruta,
        )


def test_consultar_panel_no_modifica_base(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    preparar_varias_reservaciones(
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

    consultar_panel(
        fecha="2026-10-10",
        codigo_sala="S01",
        estado="activa",
        ruta_base_datos=ruta,
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

    assert cantidad_antes == 4
    assert cantidad_despues == 4