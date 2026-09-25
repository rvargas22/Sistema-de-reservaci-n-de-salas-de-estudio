"""
Pruebas del historial de auditoria.
"""

import sqlite3
from dataclasses import FrozenInstanceError
from datetime import date, datetime

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    cancelar_reservacion,
    consultar_historial_auditoria,
    crear_reservacion,
    crear_serie_recurrente,
    modificar_estudiante,
    modificar_reservacion,
    modificar_sala,
    registrar_estudiante,
    registrar_sala,
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


HOY = date(
    2026,
    9,
    24,
)


def preparar_base(
    tmp_path,
):
    """
    Inicializa una base temporal.
    """

    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(
        ruta
    )

    return ruta


def test_datos_iniciales_no_generan_auditoria(
    tmp_path,
):
    """
    Verifica que la carga inicial del sistema
    no sea registrada como accion del usuario.
    """

    ruta = preparar_base(
        tmp_path
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert eventos == []


def test_registrar_estudiante_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 1

    evento = eventos[0]

    assert evento.accion == "crear"
    assert evento.entidad == "estudiante"
    assert evento.identificador == "D001234567"


def test_modificar_estudiante_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    modificar_estudiante(
        "A001234567",
        nombre="Andrea Modificada",
        ruta_base_datos=ruta,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 1

    assert eventos[0].accion == "modificar"
    assert eventos[0].entidad == "estudiante"


def test_registrar_sala_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_sala(
        "S06",
        "Sala nueva",
        5,
        ruta_base_datos=ruta,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 1

    assert eventos[0].accion == "crear"
    assert eventos[0].entidad == "sala"
    assert eventos[0].identificador == "S06"


def test_modificar_sala_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    modificar_sala(
        "S01",
        nombre="Sala modificada",
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 1

    assert eventos[0].accion == "modificar"
    assert eventos[0].entidad == "sala"


def test_crear_reservacion_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reservacion = crear_reservacion(
        "A001234567",
        "S01",
        "2026-10-10",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 1

    assert eventos[0].accion == "crear"
    assert eventos[0].entidad == "reservacion"

    assert (
        eventos[0].identificador
        == str(reservacion.id)
    )


def test_modificar_reservacion_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reservacion = crear_reservacion(
        "A001234567",
        "S01",
        "2026-10-10",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    modificar_reservacion(
        reservacion.id,
        hora_inicio="11:00",
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 2

    assert eventos[-1].accion == "modificar"
    assert eventos[-1].entidad == "reservacion"


def test_cancelar_reservacion_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    reservacion = crear_reservacion(
        "A001234567",
        "S01",
        "2026-10-10",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert len(eventos) == 2

    assert eventos[-1].accion == "cancelar"
    assert eventos[-1].entidad == "reservacion"

    assert (
        eventos[-1].identificador
        == str(reservacion.id)
    )


def test_validacion_fallida_no_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorValidacion
    ):
        registrar_estudiante(
            "A12",
            "Nombre válido",
            "correo@universidad.ac.cr",
            ruta_base_datos=ruta,
        )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert eventos == []


def test_operacion_rechazada_no_genera_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    with pytest.raises(
        ErrorReglaNegocio
    ):
        registrar_estudiante(
            "A001234567",
            "Estudiante duplicado",
            "otro@universidad.ac.cr",
            ruta_base_datos=ruta,
        )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert eventos == []


def test_consultar_auditoria_no_modifica_historial(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_sala(
        "S06",
        "Sala nueva",
        5,
        ruta_base_datos=ruta,
    )

    primera_consulta = (
        consultar_historial_auditoria(
            ruta
        )
    )

    segunda_consulta = (
        consultar_historial_auditoria(
            ruta
        )
    )

    assert len(
        primera_consulta
    ) == 1

    assert len(
        segunda_consulta
    ) == 1

    assert (
        primera_consulta[0]
        == segunda_consulta[0]
    )


def test_modelo_auditoria_es_inmutable(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_sala(
        "S06",
        "Sala nueva",
        5,
        ruta_base_datos=ruta,
    )

    evento = consultar_historial_auditoria(
        ruta
    )[0]

    with pytest.raises(
        FrozenInstanceError
    ):
        evento.accion = "modificar"


def test_sqlite_impide_modificar_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_sala(
        "S06",
        "Sala nueva",
        5,
        ruta_base_datos=ruta,
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="solo lectura",
        ):
            conexion.execute(
                """
                UPDATE auditoria
                SET accion = 'modificar'
                WHERE id = 1
                """
            )

            conexion.commit()

    finally:
        conexion.close()


def test_sqlite_impide_eliminar_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    registrar_sala(
        "S06",
        "Sala nueva",
        5,
        ruta_base_datos=ruta,
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="solo lectura",
        ):
            conexion.execute(
                """
                DELETE FROM auditoria
                WHERE id = 1
                """
            )

            conexion.commit()

    finally:
        conexion.close()


def test_crear_serie_recurrente_registra_auditoria(
    tmp_path,
):
    ruta = preparar_base(
        tmp_path
    )

    crear_serie_recurrente(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha_inicio="2026-10-05",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        cantidad_ocurrencias=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    eventos_serie = [
        evento
        for evento in eventos
        if evento.entidad
        == "serie_recurrente"
    ]

    assert len(
        eventos_serie
    ) == 1

    assert (
        eventos_serie[0].accion
        == "crear"
    )