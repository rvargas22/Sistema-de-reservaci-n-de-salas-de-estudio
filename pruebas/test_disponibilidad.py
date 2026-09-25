"""
Pruebas del servicio de disponibilidad.
"""

from datetime import datetime

import pytest

from aplicacion.modelos import Reservacion

from aplicacion.persistencia import (
    guardar_reservacion,
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    consultar_horarios_disponibles,
    verificar_disponibilidad,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
)


AHORA = datetime(
    2026,
    9,
    24,
    10,
    30,
)


def preparar_base(tmp_path):
    """
    Inicializa una base temporal.
    """

    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(ruta)

    return ruta


def guardar_reserva_directa(
    ruta,
    sala="S01",
    fecha="2026-09-25",
    hora="10:00",
    duracion=1,
    estado="activa",
):
    """
    Guarda una reservacion utilizada como
    preparacion de las pruebas.
    """

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala=sala,
        fecha=fecha,
        hora_inicio=hora,
        duracion_horas=duracion,
        cantidad_personas=2,
        estado=estado,
    )

    return guardar_reservacion(
        reservacion,
        ruta,
    )


def test_sala_libre_muestra_horarios_de_una_hora(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    horarios = consultar_horarios_disponibles(
        "S01",
        "2026-09-25",
        1,
        ruta,
        AHORA,
    )

    assert len(horarios) == 12
    assert horarios[0] == "08:00"
    assert horarios[-1] == "19:00"


def test_duracion_dos_horas_respeta_hora_cierre(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    horarios = consultar_horarios_disponibles(
        "S01",
        "2026-09-25",
        2,
        ruta,
        AHORA,
    )

    assert len(horarios) == 11
    assert horarios[0] == "08:00"
    assert horarios[-1] == "18:00"
    assert "19:00" not in horarios


def test_reservacion_activa_bloquea_superposiciones(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    guardar_reserva_directa(
        ruta,
        hora="10:00",
        duracion=2,
    )

    horarios = consultar_horarios_disponibles(
        "S01",
        "2026-09-25",
        1,
        ruta,
        AHORA,
    )

    assert "10:00" not in horarios
    assert "11:00" not in horarios

    assert "09:00" in horarios
    assert "12:00" in horarios


def test_reservaciones_consecutivas_estan_disponibles(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    guardar_reserva_directa(
        ruta,
        hora="10:00",
        duracion=2,
    )

    antes = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "09:00",
        1,
        ruta,
        AHORA,
    )

    despues = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "12:00",
        1,
        ruta,
        AHORA,
    )

    assert antes is True
    assert despues is True


def test_reservacion_cancelada_no_bloquea(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    guardar_reserva_directa(
        ruta,
        hora="10:00",
        duracion=2,
        estado="cancelada",
    )

    disponible = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "11:00",
        1,
        ruta,
        AHORA,
    )

    assert disponible is True


def test_reservacion_otra_sala_no_bloquea(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    guardar_reserva_directa(
        ruta,
        sala="S02",
        hora="10:00",
        duracion=2,
    )

    disponible = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "10:00",
        1,
        ruta,
        AHORA,
    )

    assert disponible is True


def test_reservacion_otra_fecha_no_bloquea(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    guardar_reserva_directa(
        ruta,
        fecha="2026-09-26",
        hora="10:00",
        duracion=2,
    )

    disponible = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "10:00",
        1,
        ruta,
        AHORA,
    )

    assert disponible is True


def test_verificar_intervalo_ocupado_devuelve_false(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    guardar_reserva_directa(
        ruta,
        hora="10:00",
        duracion=2,
    )

    disponible = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "11:00",
        1,
        ruta,
        AHORA,
    )

    assert disponible is False


def test_verificar_intervalo_libre_devuelve_true(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    disponible = verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "15:00",
        2,
        ruta,
        AHORA,
    )

    assert disponible is True


def test_sala_fuera_servicio_no_tiene_horarios(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    horarios = consultar_horarios_disponibles(
        "S04",
        "2026-09-25",
        1,
        ruta,
        AHORA,
    )

    assert horarios == []


def test_sala_inexistente_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="no existe",
    ):
        consultar_horarios_disponibles(
            "S99",
            "2026-09-25",
            1,
            ruta,
            AHORA,
        )


def test_fecha_pasada_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="fechas pasadas",
    ):
        consultar_horarios_disponibles(
            "S01",
            "2026-09-23",
            1,
            ruta,
            AHORA,
        )


def test_consulta_del_dia_excluye_horas_anteriores(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    horarios = consultar_horarios_disponibles(
        "S01",
        "2026-09-24",
        1,
        ruta,
        AHORA,
    )

    assert "08:00" not in horarios
    assert "09:00" not in horarios
    assert "10:00" not in horarios

    assert "11:00" in horarios


def test_duracion_invalida_es_rechazada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="1 o 2 horas",
    ):
        consultar_horarios_disponibles(
            "S01",
            "2026-09-25",
            3,
            ruta,
            AHORA,
        )


def test_consultar_disponibilidad_no_crea_reservaciones(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

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

    consultar_horarios_disponibles(
        "S01",
        "2026-09-25",
        1,
        ruta,
        AHORA,
    )

    verificar_disponibilidad(
        "S01",
        "2026-09-25",
        "10:00",
        1,
        ruta,
        AHORA,
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

    assert cantidad_antes == 0
    assert cantidad_despues == 0