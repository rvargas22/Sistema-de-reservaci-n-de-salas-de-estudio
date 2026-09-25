"""
Pruebas relacionadas con los identificadores
de las reservaciones.
"""

import pytest

from aplicacion.modelos import Reservacion
from aplicacion.persistencia import (
    guardar_reservacion,
    inicializar_base_datos,
    obtener_conexion,
    obtener_reservacion_por_id,
)


def crear_reservacion_prueba(
    codigo_sala="S01",
    fecha="2026-12-10",
    hora_inicio="10:00",
):
    """
    Crea una reservacion valida para las pruebas
    de persistencia.
    """

    return Reservacion(
        carne_estudiante="A001234567",
        codigo_sala=codigo_sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        duracion_horas=1,
        cantidad_personas=2,
    )


def test_sqlite_asigna_identificador(
    tmp_path,
):
    """
    Verifica que SQLite genere automaticamente
    el identificador.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    reservacion = crear_reservacion_prueba()

    assert reservacion.id is None

    reservacion_guardada = guardar_reservacion(
        reservacion,
        ruta_prueba,
    )

    assert reservacion_guardada.id == 1


def test_identificadores_incrementales(
    tmp_path,
):
    """
    Verifica que las nuevas reservaciones reciban
    identificadores incrementales.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    primera = guardar_reservacion(
        crear_reservacion_prueba(
            codigo_sala="S01",
            hora_inicio="10:00",
        ),
        ruta_prueba,
    )

    segunda = guardar_reservacion(
        crear_reservacion_prueba(
            codigo_sala="S02",
            hora_inicio="11:00",
        ),
        ruta_prueba,
    )

    assert primera.id == 1
    assert segunda.id == 2
    assert segunda.id > primera.id


def test_continuidad_identificador_despues_de_reabrir(
    tmp_path,
):
    """
    Verifica que la secuencia de identificadores
    se mantenga despues de cerrar y reabrir la base.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    primera = guardar_reservacion(
        crear_reservacion_prueba(
            codigo_sala="S01",
            hora_inicio="10:00",
        ),
        ruta_prueba,
    )

    # Simula una nueva ejecucion de la aplicacion.
    inicializar_base_datos(ruta_prueba)

    segunda = guardar_reservacion(
        crear_reservacion_prueba(
            codigo_sala="S02",
            fecha="2026-12-11",
            hora_inicio="11:00",
        ),
        ruta_prueba,
    )

    assert primera.id == 1
    assert segunda.id == 2


def test_cancelacion_conserva_identificador_y_no_lo_reutiliza(
    tmp_path,
):
    """
    Verifica que una reservacion cancelada conserve
    su identificador y que una nueva reservacion
    reciba uno diferente.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    primera = guardar_reservacion(
        crear_reservacion_prueba(),
        ruta_prueba,
    )

    conexion = obtener_conexion(ruta_prueba)

    conexion.execute(
        """
        UPDATE reservaciones
        SET estado = 'cancelada'
        WHERE id = ?
        """,
        (primera.id,),
    )

    conexion.commit()
    conexion.close()

    reservacion_cancelada = obtener_reservacion_por_id(
        primera.id,
        ruta_prueba,
    )

    segunda = guardar_reservacion(
        crear_reservacion_prueba(
            codigo_sala="S02",
            fecha="2026-12-11",
            hora_inicio="11:00",
        ),
        ruta_prueba,
    )

    assert reservacion_cancelada is not None
    assert reservacion_cancelada.id == primera.id
    assert reservacion_cancelada.estado == "cancelada"

    assert segunda.id != primera.id
    assert segunda.id > primera.id


def test_no_permitir_identificador_manual(
    tmp_path,
):
    """
    Verifica que una nueva reservacion no pueda
    guardarse con un identificador asignado manualmente.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-12-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        id=500,
    )

    with pytest.raises(
        ValueError,
        match="identificador",
    ):
        guardar_reservacion(
            reservacion,
            ruta_prueba,
        )


def test_obtener_reservacion_por_identificador(
    tmp_path,
):
    """
    Verifica que una reservacion almacenada pueda
    recuperarse utilizando su identificador.
    """

    ruta_prueba = tmp_path / "prueba.db"

    inicializar_base_datos(ruta_prueba)

    guardada = guardar_reservacion(
        crear_reservacion_prueba(),
        ruta_prueba,
    )

    recuperada = obtener_reservacion_por_id(
        guardada.id,
        ruta_prueba,
    )

    assert recuperada is not None

    assert recuperada.id == guardada.id
    assert recuperada.carne_estudiante == "A001234567"
    assert recuperada.codigo_sala == "S01"
    assert recuperada.estado == "activa"