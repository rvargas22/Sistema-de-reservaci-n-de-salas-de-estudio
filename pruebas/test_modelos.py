"""
Pruebas de los modelos principales del sistema.
"""

from aplicacion.modelos import Estudiante, Reservacion, Sala


def test_crear_estudiante():
    """
    Verifica la creacion de un estudiante.
    """

    estudiante = Estudiante(
        carne="A001234567",
        nombre="Andrea Solano",
        correo="andrea@universidad.ac.cr",
    )

    assert estudiante.carne == "A001234567"
    assert estudiante.nombre == "Andrea Solano"
    assert estudiante.correo == "andrea@universidad.ac.cr"
    assert estudiante.estado == "activo"


def test_identificar_estudiante_activo():
    """
    Verifica la propiedad esta_activo.
    """

    estudiante = Estudiante(
        carne="A001234567",
        nombre="Andrea Solano",
        correo="andrea@universidad.ac.cr",
        estado="activo",
    )

    assert estudiante.esta_activo is True


def test_identificar_estudiante_inactivo():
    """
    Verifica que un estudiante inactivo sea reconocido.
    """

    estudiante = Estudiante(
        carne="C004567890",
        nombre="Daniela Rojas",
        correo="daniela@universidad.ac.cr",
        estado="inactivo",
    )

    assert estudiante.esta_activo is False


def test_crear_sala():
    """
    Verifica la creacion de una sala.
    """

    sala = Sala(
        codigo="S01",
        nombre="Sala Biblioteca 1",
        capacidad=4,
    )

    assert sala.codigo == "S01"
    assert sala.nombre == "Sala Biblioteca 1"
    assert sala.capacidad == 4
    assert sala.estado == "disponible"


def test_identificar_sala_disponible():
    """
    Verifica que una sala disponible sea reconocida.
    """

    sala = Sala(
        codigo="S01",
        nombre="Sala Biblioteca 1",
        capacidad=4,
        estado="disponible",
    )

    assert sala.esta_disponible is True


def test_identificar_sala_fuera_de_servicio():
    """
    Verifica que una sala fuera de servicio
    no sea considerada disponible.
    """

    sala = Sala(
        codigo="S04",
        nombre="Sala multimedia",
        capacidad=8,
        estado="fuera_de_servicio",
    )

    assert sala.esta_disponible is False


def test_crear_reservacion_sin_identificador():
    """
    Verifica la creacion de una reservacion antes
    de almacenarla en SQLite.
    """

    reservacion = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-12-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
    )

    assert reservacion.id is None
    assert reservacion.carne_estudiante == "A001234567"
    assert reservacion.codigo_sala == "S01"
    assert reservacion.fecha == "2026-12-10"
    assert reservacion.hora_inicio == "10:00"
    assert reservacion.duracion_horas == 1
    assert reservacion.cantidad_personas == 2
    assert reservacion.estado == "activa"


def test_estado_de_reservacion():
    """
    Verifica la identificacion de reservaciones
    activas y canceladas.
    """

    reservacion_activa = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-12-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        estado="activa",
    )

    reservacion_cancelada = Reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-12-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        estado="cancelada",
    )

    assert reservacion_activa.esta_activa is True
    assert reservacion_cancelada.esta_activa is False