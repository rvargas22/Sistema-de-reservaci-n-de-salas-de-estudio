"""
Pruebas del servicio de salas.
"""

from datetime import date

import pytest

from aplicacion.modelos import Reservacion

from aplicacion.persistencia import (
    guardar_reservacion,
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    buscar_sala,
    consultar_salas,
    modificar_sala,
    registrar_sala,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


HOY = date(
    2026,
    9,
    24,
)


def preparar_base(tmp_path):
    """
    Crea una base temporal inicializada.
    """

    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(ruta)

    return ruta


def test_registrar_sala_valida(
    tmp_path,
):
    """
    Verifica el registro exitoso de una sala.
    """

    ruta = preparar_base(tmp_path)

    sala = registrar_sala(
        "S06",
        "Sala de estudio 6",
        5,
        ruta_base_datos=ruta,
    )

    assert sala.codigo == "S06"
    assert sala.nombre == "Sala de estudio 6"
    assert sala.capacidad == 5
    assert sala.estado == "disponible"


def test_registro_normaliza_datos_sala(
    tmp_path,
):
    """
    Verifica la normalizacion de codigo y nombre.
    """

    ruta = preparar_base(tmp_path)

    sala = registrar_sala(
        " s06 ",
        "  Sala de estudio 6  ",
        5,
        ruta_base_datos=ruta,
    )

    assert sala.codigo == "S06"
    assert sala.nombre == "Sala de estudio 6"


def test_sala_registrada_persiste(
    tmp_path,
):
    """
    Verifica que una sala registrada quede
    almacenada en SQLite.
    """

    ruta = preparar_base(tmp_path)

    registrar_sala(
        "S06",
        "Sala de estudio 6",
        5,
        ruta_base_datos=ruta,
    )

    conexion = obtener_conexion(ruta)

    cantidad = conexion.execute(
        """
        SELECT COUNT(*)
        FROM salas
        WHERE codigo = ?
        """,
        ("S06",),
    ).fetchone()[0]

    conexion.close()

    assert cantidad == 1


def test_rechazar_codigo_duplicado(
    tmp_path,
):
    """
    Verifica que no se pueda registrar
    un codigo existente.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="Ya existe",
    ):
        registrar_sala(
            "S01",
            "Sala duplicada",
            4,
            ruta_base_datos=ruta,
        )


def test_rechazar_codigo_duplicado_sin_distinguir_mayusculas(
    tmp_path,
):
    """
    Verifica la unicidad del codigo sin distinguir
    mayusculas y minusculas.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorReglaNegocio):
        registrar_sala(
            "s01",
            "Sala duplicada",
            4,
            ruta_base_datos=ruta,
        )


def test_rechazar_capacidad_cero(
    tmp_path,
):
    """
    Verifica que una sala no pueda tener
    capacidad cero.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorValidacion):
        registrar_sala(
            "S06",
            "Sala inválida",
            0,
            ruta_base_datos=ruta,
        )


def test_rechazar_capacidad_negativa(
    tmp_path,
):
    """
    Verifica que una sala no pueda tener
    capacidad negativa.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorValidacion):
        registrar_sala(
            "S06",
            "Sala inválida",
            -1,
            ruta_base_datos=ruta,
        )


def test_consultar_salas_iniciales(
    tmp_path,
):
    """
    Verifica las cinco salas iniciales.
    """

    ruta = preparar_base(tmp_path)

    salas = consultar_salas(
        ruta,
    )

    assert len(salas) == 5

    assert salas[0].codigo == "S01"
    assert salas[1].codigo == "S02"
    assert salas[2].codigo == "S03"
    assert salas[3].codigo == "S04"
    assert salas[4].codigo == "S05"


def test_consulta_incluye_salas_disponibles_y_fuera_servicio(
    tmp_path,
):
    """
    Verifica que el listado incluya salas
    con ambos estados.
    """

    ruta = preparar_base(tmp_path)

    salas = consultar_salas(
        ruta,
    )

    estados = {
        sala.estado
        for sala in salas
    }

    assert "disponible" in estados
    assert "fuera_de_servicio" in estados


def test_buscar_sala_por_codigo(
    tmp_path,
):
    """
    Verifica la busqueda de una sala.
    """

    ruta = preparar_base(tmp_path)

    sala = buscar_sala(
        "S01",
        ruta,
    )

    assert sala is not None
    assert sala.codigo == "S01"
    assert sala.nombre == "Sala Biblioteca 1"


def test_busqueda_sala_no_distingue_mayusculas(
    tmp_path,
):
    """
    Verifica la busqueda independientemente
    de mayusculas y minusculas.
    """

    ruta = preparar_base(tmp_path)

    sala = buscar_sala(
        "s01",
        ruta,
    )

    assert sala is not None
    assert sala.codigo == "S01"


def test_buscar_sala_inexistente(
    tmp_path,
):
    """
    Verifica que una sala inexistente
    devuelva None.
    """

    ruta = preparar_base(tmp_path)

    sala = buscar_sala(
        "S99",
        ruta,
    )

    assert sala is None


def test_modificar_nombre_capacidad_y_estado(
    tmp_path,
):
    """
    Verifica la modificacion de los campos permitidos.
    """

    ruta = preparar_base(tmp_path)

    sala = modificar_sala(
        "S01",
        nombre="Sala Biblioteca Principal",
        capacidad=6,
        estado="fuera_de_servicio",
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    assert sala.codigo == "S01"
    assert sala.nombre == "Sala Biblioteca Principal"
    assert sala.capacidad == 6
    assert sala.estado == "fuera_de_servicio"


def test_modificacion_parcial_conserva_otros_datos(
    tmp_path,
):
    """
    Verifica que una modificacion parcial
    conserve los datos no enviados.
    """

    ruta = preparar_base(tmp_path)

    antes = buscar_sala(
        "S01",
        ruta,
    )

    despues = modificar_sala(
        "S01",
        estado="fuera_de_servicio",
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    assert despues.nombre == antes.nombre
    assert despues.capacidad == antes.capacidad
    assert despues.estado == "fuera_de_servicio"


def test_impedir_modificar_codigo_sala(
    tmp_path,
):
    """
    Verifica que el codigo de una sala
    sea inmutable.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="no puede modificarse",
    ):
        modificar_sala(
            "S01",
            nuevo_codigo="S99",
            ruta_base_datos=ruta,
            hoy=HOY,
        )


def test_permitir_mismo_codigo_en_modificacion(
    tmp_path,
):
    """
    Verifica que reenviar el mismo codigo
    no sea interpretado como un cambio.
    """

    ruta = preparar_base(tmp_path)

    sala = modificar_sala(
        "S01",
        nuevo_codigo="s01",
        nombre="Sala Biblioteca Modificada",
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    assert sala.codigo == "S01"
    assert sala.nombre == "Sala Biblioteca Modificada"


def test_permitir_reduccion_capacidad_compatible(
    tmp_path,
):
    """
    Verifica que una reduccion sea permitida
    cuando no contradice reservaciones activas.
    """

    ruta = preparar_base(tmp_path)

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S03",
        fecha="2026-09-25",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=6,
    )

    guardar_reservacion(
        reservacion,
        ruta,
    )

    sala = modificar_sala(
        "S03",
        capacidad=6,
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    assert sala.capacidad == 6


def test_rechazar_reduccion_capacidad_incompatible(
    tmp_path,
):
    """
    Verifica que no pueda reducirse la capacidad
    por debajo de una reservacion activa futura.
    """

    ruta = preparar_base(tmp_path)

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S03",
        fecha="2026-09-25",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=8,
    )

    guardar_reservacion(
        reservacion,
        ruta,
    )

    with pytest.raises(
        ErrorReglaNegocio,
        match="reducir la capacidad",
    ):
        modificar_sala(
            "S03",
            capacidad=6,
            ruta_base_datos=ruta,
            hoy=HOY,
        )

    sala = buscar_sala(
        "S03",
        ruta,
    )

    assert sala.capacidad == 10


def test_reservacion_cancelada_no_impide_reducir_capacidad(
    tmp_path,
):
    """
    Verifica que una reservacion cancelada
    no bloquee una reduccion de capacidad.
    """

    ruta = preparar_base(tmp_path)

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S03",
        fecha="2026-09-25",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=8,
        estado="cancelada",
    )

    guardar_reservacion(
        reservacion,
        ruta,
    )

    sala = modificar_sala(
        "S03",
        capacidad=6,
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    assert sala.capacidad == 6


def test_reservacion_pasada_no_impide_reducir_capacidad(
    tmp_path,
):
    """
    Verifica que una reservacion de una fecha pasada
    no bloquee una reduccion actual.
    """

    ruta = preparar_base(tmp_path)

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S03",
        fecha="2026-09-20",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=8,
    )

    guardar_reservacion(
        reservacion,
        ruta,
    )

    sala = modificar_sala(
        "S03",
        capacidad=6,
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    assert sala.capacidad == 6


def test_rechazar_modificacion_sala_inexistente(
    tmp_path,
):
    """
    Verifica que no pueda modificarse
    una sala inexistente.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="no existe",
    ):
        modificar_sala(
            "S99",
            nombre="Sala inexistente",
            ruta_base_datos=ruta,
            hoy=HOY,
        )