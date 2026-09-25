"""
Pruebas de validaciones y reglas de negocio.
"""

from datetime import datetime

import pytest

from aplicacion.modelos import (
    Estudiante,
    Reservacion,
    Sala,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
    validar_carne,
    validar_carne_disponible,
    validar_codigo_disponible,
    validar_datos_estudiante,
    validar_datos_sala,
    validar_reservacion,
)


AHORA = datetime(
    2026,
    9,
    24,
    10,
    30,
)


def estudiante_activo():
    return Estudiante(
        carne="A001234567",
        nombre="Andrea Solano",
        correo="andrea@universidad.ac.cr",
        estado="activo",
    )


def sala_disponible():
    return Sala(
        codigo="S01",
        nombre="Sala Biblioteca 1",
        capacidad=4,
        estado="disponible",
    )


def crear_reservacion_existente(
    hora="10:00",
    duracion=1,
    estado="activa",
    fecha="2026-09-25",
):
    return Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha=fecha,
        hora_inicio=hora,
        duracion_horas=duracion,
        cantidad_personas=2,
        estado=estado,
        id=1,
    )


def test_normalizar_datos_estudiante():

    estudiante = validar_datos_estudiante(
        " a001234567 ",
        "  Andrea Solano  ",
        "  andrea@universidad.ac.cr  ",
    )

    assert estudiante.carne == "A001234567"
    assert estudiante.nombre == "Andrea Solano"
    assert estudiante.correo == "andrea@universidad.ac.cr"


def test_rechazar_carne_con_longitud_incorrecta():

    with pytest.raises(ErrorValidacion):
        validar_carne("A123")


def test_rechazar_carne_con_espacios():

    with pytest.raises(ErrorValidacion):
        validar_carne("A001 34567")


def test_rechazar_nombre_menor_a_tres_caracteres():

    with pytest.raises(ErrorValidacion):
        validar_datos_estudiante(
            "D001234567",
            " A ",
            "a@universidad.ac.cr",
        )


def test_rechazar_correo_con_multiples_arrobas():

    with pytest.raises(ErrorValidacion):
        validar_datos_estudiante(
            "D001234567",
            "Nombre válido",
            "persona@@universidad.ac.cr",
        )


def test_rechazar_correo_sin_punto_despues_arroba():

    with pytest.raises(ErrorValidacion):
        validar_datos_estudiante(
            "D001234567",
            "Nombre válido",
            "persona@universidad",
        )


def test_detectar_carne_duplicado_sin_distinguir_mayusculas():

    existentes = [
        estudiante_activo()
    ]

    with pytest.raises(ErrorReglaNegocio):
        validar_carne_disponible(
            "a001234567",
            existentes,
        )


def test_normalizar_datos_sala():

    sala = validar_datos_sala(
        " s06 ",
        " Sala nueva ",
        5,
    )

    assert sala.codigo == "S06"
    assert sala.nombre == "Sala nueva"
    assert sala.capacidad == 5


def test_rechazar_capacidad_cero():

    with pytest.raises(ErrorValidacion):
        validar_datos_sala(
            "S06",
            "Sala nueva",
            0,
        )


def test_detectar_codigo_sala_duplicado():

    existentes = [
        sala_disponible()
    ]

    with pytest.raises(ErrorReglaNegocio):
        validar_codigo_disponible(
            "s01",
            existentes,
        )


def test_rechazar_estado_invalido_sala():

    with pytest.raises(ErrorValidacion):
        validar_datos_sala(
            "S06",
            "Sala nueva",
            5,
            "cerrada",
        )


def test_rechazar_fecha_pasada():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-23",
            "10:00",
            1,
            2,
            ahora=AHORA,
        )


def test_rechazar_hora_actual_del_mismo_dia():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-24",
            "10:00",
            1,
            2,
            ahora=AHORA,
        )


def test_permitir_hora_posterior_del_mismo_dia():

    reservacion = validar_reservacion(
        estudiante_activo(),
        sala_disponible(),
        "2026-09-24",
        "11:00",
        1,
        2,
        ahora=AHORA,
    )

    assert reservacion.hora_inicio == "11:00"


def test_rechazar_hora_no_completa():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "10:30",
            1,
            2,
            ahora=AHORA,
        )


def test_rechazar_hora_antes_de_las_ocho():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "07:00",
            1,
            2,
            ahora=AHORA,
        )


def test_rechazar_reservacion_que_finaliza_despues_de_20():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "19:00",
            2,
            2,
            ahora=AHORA,
        )


def test_rechazar_duracion_invalida():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "10:00",
            3,
            2,
            ahora=AHORA,
        )


def test_rechazar_cero_personas():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "10:00",
            1,
            0,
            ahora=AHORA,
        )


def test_rechazar_personas_superiores_a_capacidad():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "10:00",
            1,
            5,
            ahora=AHORA,
        )


def test_rechazar_estudiante_inactivo():

    estudiante = Estudiante(
        carne="C004567890",
        nombre="Daniela Rojas",
        correo="daniela@universidad.ac.cr",
        estado="inactivo",
    )

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante,
            sala_disponible(),
            "2026-09-25",
            "10:00",
            1,
            1,
            ahora=AHORA,
        )


def test_rechazar_sala_fuera_de_servicio():

    sala = Sala(
        codigo="S04",
        nombre="Sala multimedia",
        capacidad=8,
        estado="fuera_de_servicio",
    )

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala,
            "2026-09-25",
            "10:00",
            1,
            2,
            ahora=AHORA,
        )


def test_rechazar_estudiante_inexistente():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            None,
            sala_disponible(),
            "2026-09-25",
            "10:00",
            1,
            2,
            ahora=AHORA,
        )


def test_rechazar_sala_inexistente():

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            None,
            "2026-09-25",
            "10:00",
            1,
            2,
            ahora=AHORA,
        )


def test_detectar_superposicion():

    existentes = [
        crear_reservacion_existente(
            hora="10:00",
            duracion=2,
        )
    ]

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-25",
            "11:00",
            1,
            2,
            existentes,
            AHORA,
        )


def test_permitir_reservaciones_consecutivas():

    existentes = [
        crear_reservacion_existente(
            hora="10:00",
            duracion=1,
        )
    ]

    nueva = validar_reservacion(
        estudiante_activo(),
        sala_disponible(),
        "2026-09-25",
        "11:00",
        1,
        2,
        existentes,
        AHORA,
    )

    assert nueva.hora_inicio == "11:00"


def test_cancelada_no_bloquea_horario():

    existentes = [
        crear_reservacion_existente(
            hora="10:00",
            duracion=2,
            estado="cancelada",
        )
    ]

    nueva = validar_reservacion(
        estudiante_activo(),
        sala_disponible(),
        "2026-09-25",
        "11:00",
        1,
        2,
        existentes,
        AHORA,
    )

    assert nueva.hora_inicio == "11:00"


def test_rechazar_cuarta_reservacion_activa():

    existentes = [
        crear_reservacion_existente(
            fecha="2026-09-25",
            hora="08:00",
        ),
        crear_reservacion_existente(
            fecha="2026-09-26",
            hora="09:00",
        ),
        crear_reservacion_existente(
            fecha="2026-09-27",
            hora="10:00",
        ),
    ]

    with pytest.raises(ErrorReglaNegocio):
        validar_reservacion(
            estudiante_activo(),
            sala_disponible(),
            "2026-09-28",
            "11:00",
            1,
            2,
            existentes,
            AHORA,
        )


def test_reservacion_pasada_no_cuenta_para_limite():

    existentes = [
        crear_reservacion_existente(
            fecha="2026-09-20",
            hora="08:00",
        ),
        crear_reservacion_existente(
            fecha="2026-09-25",
            hora="09:00",
        ),
        crear_reservacion_existente(
            fecha="2026-09-26",
            hora="10:00",
        ),
    ]

    nueva = validar_reservacion(
        estudiante_activo(),
        sala_disponible(),
        "2026-09-27",
        "11:00",
        1,
        2,
        existentes,
        AHORA,
    )

    assert nueva.fecha == "2026-09-27"


def test_crear_reservacion_completamente_valida():

    reservacion = validar_reservacion(
        estudiante_activo(),
        sala_disponible(),
        "2026-09-25",
        "18:00",
        2,
        4,
        [],
        AHORA,
    )

    assert reservacion.id is None
    assert reservacion.carne_estudiante == "A001234567"
    assert reservacion.codigo_sala == "S01"
    assert reservacion.fecha == "2026-09-25"
    assert reservacion.hora_inicio == "18:00"
    assert reservacion.duracion_horas == 2
    assert reservacion.cantidad_personas == 4
    assert reservacion.estado == "activa"