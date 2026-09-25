"""
Pruebas del servicio de reservaciones.
"""

from datetime import datetime

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_reservacion_por_id,
)

from aplicacion.servicios import (
    buscar_reservaciones_estudiante,
    cancelar_reservacion,
    consultar_historial_reservaciones,
    crear_reservacion,
    modificar_reservacion,
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


def crear_reserva(
    ruta,
    carne="A001234567",
    sala="S01",
    fecha="2026-09-25",
    hora="10:00",
    duracion=1,
    personas=2,
):
    """
    Crea una reservacion valida para las pruebas.
    """

    return crear_reservacion(
        carne_estudiante=carne,
        codigo_sala=sala,
        fecha=fecha,
        hora_inicio=hora,
        duracion_horas=duracion,
        cantidad_personas=personas,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )


def test_crear_reservacion_valida(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    reservacion = crear_reserva(
        ruta
    )

    assert reservacion.id == 1
    assert reservacion.carne_estudiante == "A001234567"
    assert reservacion.codigo_sala == "S01"
    assert reservacion.estado == "activa"


def test_reservacion_creada_persiste(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    creada = crear_reserva(
        ruta
    )

    recuperada = obtener_reservacion_por_id(
        creada.id,
        ruta,
    )

    assert recuperada is not None
    assert recuperada.id == creada.id
    assert recuperada.hora_inicio == "10:00"


def test_rechazar_estudiante_inexistente(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="estudiante no existe",
    ):
        crear_reserva(
            ruta,
            carne="Z999999999",
        )


def test_rechazar_estudiante_inactivo(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="inactivo",
    ):
        crear_reserva(
            ruta,
            carne="C004567890",
        )


def test_rechazar_sala_inexistente(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="sala no existe",
    ):
        crear_reserva(
            ruta,
            sala="S99",
        )


def test_rechazar_sala_fuera_servicio(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="fuera de servicio",
    ):
        crear_reserva(
            ruta,
            sala="S04",
        )


def test_rechazar_fecha_pasada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorReglaNegocio):
        crear_reserva(
            ruta,
            fecha="2026-09-23",
        )


def test_rechazar_superposicion(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    crear_reserva(
        ruta,
        hora="10:00",
        duracion=2,
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="superpone",
    ):
        crear_reserva(
            ruta,
            hora="11:00",
        )


def test_permitir_reservaciones_consecutivas(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    primera = crear_reserva(
        ruta,
        hora="10:00",
        duracion=1,
    )

    segunda = crear_reserva(
        ruta,
        hora="11:00",
        duracion=1,
    )

    assert primera.id == 1
    assert segunda.id == 2


def test_rechazar_cuarta_reservacion_activa(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    crear_reserva(
        ruta,
        fecha="2026-09-25",
        sala="S01",
    )

    crear_reserva(
        ruta,
        fecha="2026-09-26",
        sala="S02",
    )

    crear_reserva(
        ruta,
        fecha="2026-09-27",
        sala="S03",
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="máximo",
    ):
        crear_reserva(
            ruta,
            fecha="2026-09-28",
            sala="S01",
        )


def test_consultar_historial_completo(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    primera = crear_reserva(
        ruta,
        fecha="2026-09-25",
    )

    crear_reserva(
        ruta,
        sala="S02",
        fecha="2026-09-26",
    )

    cancelar_reservacion(
        primera.id,
        ruta,
    )

    historial = consultar_historial_reservaciones(
        ruta
    )

    assert len(historial) == 2

    estados = {
        reservacion.estado
        for reservacion in historial
    }

    assert "activa" in estados
    assert "cancelada" in estados


def test_buscar_reservaciones_por_carne(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    crear_reserva(
        ruta,
        fecha="2026-09-25",
    )

    crear_reserva(
        ruta,
        fecha="2026-09-26",
        sala="S02",
    )

    resultado = buscar_reservaciones_estudiante(
        "A001234567",
        ruta,
    )

    assert len(resultado) == 2

    assert all(
        reservacion.carne_estudiante == "A001234567"
        for reservacion in resultado
    )


def test_busqueda_carne_no_distingue_mayusculas(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    crear_reserva(
        ruta
    )

    resultado = buscar_reservaciones_estudiante(
        "a001234567",
        ruta,
    )

    assert len(resultado) == 1


def test_busqueda_sin_reservaciones_devuelve_lista_vacia(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    resultado = buscar_reservaciones_estudiante(
        "B009876543",
        ruta,
    )

    assert resultado == []


def test_cancelar_reservacion_activa(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    reservacion = crear_reserva(
        ruta
    )

    cancelada = cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    assert cancelada.estado == "cancelada"


def test_cancelacion_conserva_identificador(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    reservacion = crear_reserva(
        ruta
    )

    cancelada = cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    assert cancelada.id == reservacion.id


def test_rechazar_cancelacion_inexistente(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="no existe",
    ):
        cancelar_reservacion(
            999,
            ruta,
        )


def test_rechazar_reservacion_ya_cancelada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    reservacion = crear_reserva(
        ruta
    )

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="ya se encuentra cancelada",
    ):
        cancelar_reservacion(
            reservacion.id,
            ruta,
        )


def test_cancelacion_libera_horario(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    primera = crear_reserva(
        ruta,
        hora="10:00",
    )

    cancelar_reservacion(
        primera.id,
        ruta,
    )

    segunda = crear_reserva(
        ruta,
        hora="10:00",
    )

    assert segunda.id > primera.id
    assert segunda.estado == "activa"


def test_modificar_reservacion_conserva_identificador(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    reservacion = crear_reserva(
        ruta
    )

    modificada = modificar_reservacion(
        reservacion.id,
        hora_inicio="11:00",
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert modificada.id == reservacion.id
    assert modificada.hora_inicio == "11:00"


def test_modificacion_parcial_conserva_datos(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    original = crear_reserva(
        ruta,
        sala="S02",
        fecha="2026-09-25",
        hora="10:00",
        personas=2,
    )

    modificada = modificar_reservacion(
        original.id,
        cantidad_personas=4,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert modificada.id == original.id
    assert modificada.codigo_sala == "S02"
    assert modificada.fecha == "2026-09-25"
    assert modificada.hora_inicio == "10:00"
    assert modificada.cantidad_personas == 4


def test_modificar_sala_de_reservacion(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    original = crear_reserva(
        ruta,
        sala="S01",
    )

    modificada = modificar_reservacion(
        original.id,
        codigo_sala="S02",
        cantidad_personas=5,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert modificada.id == original.id
    assert modificada.codigo_sala == "S02"
    assert modificada.cantidad_personas == 5


def test_modificacion_invalida_conserva_datos_originales(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    original = crear_reserva(
        ruta,
        sala="S01",
        personas=2,
    )

    with pytest.raises(ErrorReglaNegocio):
        modificar_reservacion(
            original.id,
            cantidad_personas=10,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )

    despues = obtener_reservacion_por_id(
        original.id,
        ruta,
    )

    assert despues.id == original.id
    assert despues.codigo_sala == original.codigo_sala
    assert despues.fecha == original.fecha
    assert despues.hora_inicio == original.hora_inicio
    assert despues.cantidad_personas == 2


def test_rechazar_modificacion_cancelada(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    reservacion = crear_reserva(
        ruta
    )

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="cancelada no puede modificarse",
    ):
        modificar_reservacion(
            reservacion.id,
            hora_inicio="11:00",
            ruta_base_datos=ruta,
            ahora=AHORA,
        )


def test_rechazar_modificacion_inexistente(
    tmp_path,
):
    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="no existe",
    ):
        modificar_reservacion(
            999,
            hora_inicio="11:00",
            ruta_base_datos=ruta,
            ahora=AHORA,
        )