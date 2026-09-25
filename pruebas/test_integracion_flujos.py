"""
Pruebas de integracion del sistema.

Estas pruebas verifican flujos completos utilizando
varios modulos de la aplicacion al mismo tiempo.

No automatizan clics de la interfaz grafica.
"""

from datetime import date, datetime

import pytest

from aplicacion.persistencia import (
    obtener_conexion,
    obtener_estado_integridad,
    obtener_reservacion_por_id,
    inicializar_base_datos,
)

from aplicacion.servicios import (
    buscar_reservaciones_estudiante,
    cancelar_ocurrencia_recurrente,
    cancelar_reservacion,
    consultar_historial_auditoria,
    consultar_horarios_disponibles,
    consultar_ocurrencias_serie,
    consultar_panel,
    crear_reservacion,
    crear_serie_recurrente,
    exportar_reporte_csv,
    generar_reporte_reservaciones,
    modificar_estudiante,
    modificar_reservacion,
    modificar_sala,
    registrar_estudiante,
    registrar_sala,
    verificar_disponibilidad,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
)


pytestmark = pytest.mark.integracion


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
    Crea una base SQLite temporal con los
    datos iniciales del sistema.
    """

    ruta = tmp_path / "integracion.db"

    inicializar_base_datos(
        ruta
    )

    return ruta


def test_flujo_estudiante_reservacion_panel_reporte_auditoria(
    tmp_path,
):
    """
    Verifica un flujo completo desde el registro
    del estudiante hasta auditoria y reportes.
    """

    ruta = preparar_base(
        tmp_path
    )

    estudiante = registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    assert (
        estudiante.carne
        == "D001234567"
    )

    reservacion = crear_reservacion(
        carne_estudiante="D001234567",
        codigo_sala="S05",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert (
        reservacion.id
        is not None
    )

    panel = consultar_panel(
        fecha="2026-10-10",
        codigo_sala="S05",
        estado="activa",
        ruta_base_datos=ruta,
    )

    assert len(panel) == 1

    assert (
        panel[0]["nombre_estudiante"]
        == "David Ramírez"
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-10",
        "2026-10-10",
        ruta,
    )

    assert len(reporte) == 1

    assert (
        reporte[0]["carne_estudiante"]
        == "D001234567"
    )

    eventos = consultar_historial_auditoria(
        ruta
    )

    assert any(
        evento.entidad == "estudiante"
        and evento.accion == "crear"
        and evento.identificador
        == "D001234567"
        for evento in eventos
    )

    assert any(
        evento.entidad == "reservacion"
        and evento.accion == "crear"
        and evento.identificador
        == str(reservacion.id)
        for evento in eventos
    )


def test_disponibilidad_cambia_al_crear_y_cancelar(
    tmp_path,
):
    """
    Verifica que disponibilidad, reservaciones y
    cancelaciones trabajen sobre los mismos datos.
    """

    ruta = preparar_base(
        tmp_path
    )

    antes = verificar_disponibilidad(
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert antes is True

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

    durante = verificar_disponibilidad(
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert durante is False

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    despues = verificar_disponibilidad(
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert despues is True


def test_modificacion_reservacion_se_refleja_en_panel_y_persistencia(
    tmp_path,
):
    """
    Verifica que una modificacion exitosa sea visible
    tanto en SQLite como en el panel.
    """

    ruta = preparar_base(
        tmp_path
    )

    original = crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S02",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    modificada = modificar_reservacion(
        identificador=original.id,
        hora_inicio="11:00",
        cantidad_personas=4,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert (
        modificada.id
        == original.id
    )

    persistida = obtener_reservacion_por_id(
        original.id,
        ruta,
    )

    assert (
        persistida.hora_inicio
        == "11:00"
    )

    assert (
        persistida.cantidad_personas
        == 4
    )

    panel = consultar_panel(
        fecha="2026-10-10",
        codigo_sala="S02",
        estado="activa",
        ruta_base_datos=ruta,
    )

    assert len(panel) == 1

    assert (
        panel[0]["hora_inicio"]
        == "11:00"
    )

    assert (
        panel[0]["cantidad_personas"]
        == 4
    )


def test_estudiante_inactivo_impide_nueva_reservacion(
    tmp_path,
):
    """
    Verifica la integracion entre gestion de
    estudiantes y reservaciones.
    """

    ruta = preparar_base(
        tmp_path
    )

    modificar_estudiante(
        "A001234567",
        estado="inactivo",
        ruta_base_datos=ruta,
    )

    with pytest.raises(
        ErrorReglaNegocio
    ):
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


def test_sala_fuera_servicio_impide_reserva_y_disponibilidad(
    tmp_path,
):
    """
    Verifica la relacion entre estado de sala,
    disponibilidad y reservaciones.
    """

    ruta = preparar_base(
        tmp_path
    )

    horarios = (
        consultar_horarios_disponibles(
            codigo_sala="S04",
            fecha="2026-10-10",
            duracion_horas=1,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )
    )

    assert horarios == []

    with pytest.raises(
        ErrorReglaNegocio
    ):
        crear_reservacion(
            carne_estudiante="A001234567",
            codigo_sala="S04",
            fecha="2026-10-10",
            hora_inicio="10:00",
            duracion_horas=1,
            cantidad_personas=2,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )


def test_limite_tres_reservaciones_activas(
    tmp_path,
):
    """
    Verifica RN-11 a traves del servicio real
    y SQLite.
    """

    ruta = preparar_base(
        tmp_path
    )

    for fecha in (
        "2026-10-10",
        "2026-10-11",
        "2026-10-12",
    ):
        crear_reservacion(
            carne_estudiante="A001234567",
            codigo_sala="S01",
            fecha=fecha,
            hora_inicio="10:00",
            duracion_horas=1,
            cantidad_personas=2,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )

    with pytest.raises(
        ErrorReglaNegocio
    ):
        crear_reservacion(
            carne_estudiante="A001234567",
            codigo_sala="S01",
            fecha="2026-10-13",
            hora_inicio="10:00",
            duracion_horas=1,
            cantidad_personas=2,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )


def test_cancelacion_libera_limite_de_tres_reservaciones(
    tmp_path,
):
    """
    Verifica que una reservacion cancelada deje de
    contar dentro del limite de activas.
    """

    ruta = preparar_base(
        tmp_path
    )

    reservaciones = []

    for fecha in (
        "2026-10-10",
        "2026-10-11",
        "2026-10-12",
    ):
        reservaciones.append(
            crear_reservacion(
                carne_estudiante="A001234567",
                codigo_sala="S01",
                fecha=fecha,
                hora_inicio="10:00",
                duracion_horas=1,
                cantidad_personas=2,
                ruta_base_datos=ruta,
                ahora=AHORA,
            )
        )

    cancelar_reservacion(
        reservaciones[1].id,
        ruta,
    )

    nueva = crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-13",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    assert nueva.estado == "activa"

    activas = [
        reservacion
        for reservacion
        in buscar_reservaciones_estudiante(
            "A001234567",
            ruta,
        )
        if reservacion.estado
        == "activa"
    ]

    assert len(activas) == 3


def test_identificador_cancelado_no_se_reutiliza(
    tmp_path,
):
    """
    Verifica continuidad de identificadores
    despues de una cancelacion.
    """

    ruta = preparar_base(
        tmp_path
    )

    primera = crear_reservacion(
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
        primera.id,
        ruta,
    )

    segunda = crear_reservacion(
        "A001234567",
        "S02",
        "2026-10-11",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    assert (
        segunda.id
        > primera.id
    )

    assert (
        segunda.id
        != primera.id
    )


def test_recurrencia_crea_ocurrencias_semanales_y_panel(
    tmp_path,
):
    """
    Verifica integracion entre recurrencia,
    reservaciones y panel.
    """

    ruta = preparar_base(
        tmp_path
    )

    resultado = crear_serie_recurrente(
        carne_estudiante="A001234567",
        codigo_sala="S03",
        fecha_inicio="2026-10-05",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        cantidad_ocurrencias=3,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    ocurrencias = consultar_ocurrencias_serie(
        resultado["serie_id"],
        ruta,
    )

    assert len(ocurrencias) == 3

    fechas = [
        ocurrencia["reservacion"].fecha
        for ocurrencia in ocurrencias
    ]

    assert fechas == [
        "2026-10-05",
        "2026-10-12",
        "2026-10-19",
    ]

    panel = consultar_panel(
        codigo_sala="S03",
        estado="activa",
        ruta_base_datos=ruta,
    )

    assert len(panel) == 3


def test_cancelar_ocurrencia_recurrente_no_afecta_otras(
    tmp_path,
):
    """
    Verifica que una cancelacion individual de
    recurrencia conserve las demas ocurrencias.
    """

    ruta = preparar_base(
        tmp_path
    )

    resultado = crear_serie_recurrente(
        carne_estudiante="A001234567",
        codigo_sala="S03",
        fecha_inicio="2026-10-05",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        cantidad_ocurrencias=3,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    cancelar_ocurrencia_recurrente(
        resultado["serie_id"],
        2,
        ruta,
    )

    ocurrencias = consultar_ocurrencias_serie(
        resultado["serie_id"],
        ruta,
    )

    estados = [
        ocurrencia["reservacion"].estado
        for ocurrencia in ocurrencias
    ]

    assert estados == [
        "activa",
        "cancelada",
        "activa",
    ]


def test_conflicto_recurrencia_no_guarda_serie_parcial(
    tmp_path,
):
    """
    Verifica que un conflicto previo impida
    almacenar parcialmente una serie.
    """

    ruta = preparar_base(
        tmp_path
    )

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

    with pytest.raises(
        ErrorReglaNegocio
    ):
        crear_serie_recurrente(
            carne_estudiante="A001234567",
            codigo_sala="S01",
            fecha_inicio="2026-10-05",
            hora_inicio="10:00",
            duracion_horas=1,
            cantidad_personas=2,
            cantidad_ocurrencias=3,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )

    conexion = obtener_conexion(
        ruta
    )

    try:
        cantidad_series = conexion.execute(
            """
            SELECT COUNT(*)
            FROM series_recurrentes
            """
        ).fetchone()[0]

        cantidad_reservaciones = (
            conexion.execute(
                """
                SELECT COUNT(*)
                FROM reservaciones
                """
            ).fetchone()[0]
        )

    finally:
        conexion.close()

    assert cantidad_series == 0

    # Solamente permanece la reservacion utilizada
    # para provocar el conflicto.
    assert cantidad_reservaciones == 1


def test_reporte_csv_utf8_flujo_completo(
    tmp_path,
):
    """
    Verifica persistencia, reporte y exportacion
    de caracteres UTF-8.
    """

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
        carne_estudiante="D001234567",
        codigo_sala="S05",
        fecha="2026-10-15",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    reporte = generar_reporte_reservaciones(
        "2026-10-15",
        "2026-10-15",
        ruta,
    )

    destino = (
        tmp_path
        / "reporte_integracion.csv"
    )

    resultado = exportar_reporte_csv(
        reporte,
        destino,
    )

    assert resultado == destino
    assert destino.exists()

    contenido = destino.read_text(
        encoding="utf-8"
    )

    assert "María Peña" in contenido
    assert "Cubículo individual" in contenido


def test_filtros_panel_combinados(
    tmp_path,
):
    """
    Verifica filtros de fecha, sala y estado
    trabajando simultaneamente.
    """

    ruta = preparar_base(
        tmp_path
    )

    crear_reservacion(
        "A001234567",
        "S01",
        "2026-10-10",
        "10:00",
        1,
        2,
        ruta,
        AHORA,
    )

    cancelada = crear_reservacion(
        "B009876543",
        "S01",
        "2026-10-10",
        "12:00",
        1,
        2,
        ruta,
        AHORA,
    )

    crear_reservacion(
        "A001234567",
        "S02",
        "2026-10-10",
        "14:00",
        1,
        2,
        ruta,
        AHORA,
    )

    cancelar_reservacion(
        cancelada.id,
        ruta,
    )

    resultado = consultar_panel(
        fecha="2026-10-10",
        codigo_sala="S01",
        estado="cancelada",
        ruta_base_datos=ruta,
    )

    assert len(resultado) == 1

    assert (
        resultado[0]["id"]
        == cancelada.id
    )


def test_modificacion_invalida_conserva_original(
    tmp_path,
):
    """
    Verifica que una modificacion rechazada
    no altere la reservacion persistida.
    """

    ruta = preparar_base(
        tmp_path
    )

    original = crear_reservacion(
        carne_estudiante="A001234567",
        codigo_sala="S01",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=2,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    with pytest.raises(
        ErrorReglaNegocio
    ):
        modificar_reservacion(
            identificador=original.id,
            cantidad_personas=10,
            ruta_base_datos=ruta,
            ahora=AHORA,
        )

    persistida = obtener_reservacion_por_id(
        original.id,
        ruta,
    )

    assert (
        persistida.cantidad_personas
        == 2
    )

    assert (
        persistida.hora_inicio
        == "10:00"
    )


def test_persistencia_despues_de_reabrir_conexion(
    tmp_path,
):
    """
    Verifica que los datos permanezcan despues
    de cerrar y abrir una nueva conexion.
    """

    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    reservacion = crear_reservacion(
        carne_estudiante="D001234567",
        codigo_sala="S05",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=1,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        estudiante = conexion.execute(
            """
            SELECT nombre
            FROM estudiantes
            WHERE carne = ?
            """,
            (
                "D001234567",
            ),
        ).fetchone()

        fila_reservacion = conexion.execute(
            """
            SELECT id, estado
            FROM reservaciones
            WHERE id = ?
            """,
            (
                reservacion.id,
            ),
        ).fetchone()

    finally:
        conexion.close()

    assert (
        estudiante["nombre"]
        == "David Ramírez"
    )

    assert (
        fila_reservacion["id"]
        == reservacion.id
    )

    assert (
        fila_reservacion["estado"]
        == "activa"
    )


def test_integridad_despues_de_flujo_mixto(
    tmp_path,
):
    """
    Ejecuta diversas operaciones y comprueba
    la integridad final de SQLite.
    """

    ruta = preparar_base(
        tmp_path
    )

    registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    registrar_sala(
        "S06",
        "Sala de integración",
        5,
        ruta_base_datos=ruta,
    )

    reservacion = crear_reservacion(
        carne_estudiante="D001234567",
        codigo_sala="S06",
        fecha="2026-10-10",
        hora_inicio="10:00",
        duracion_horas=1,
        cantidad_personas=3,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    modificar_reservacion(
        identificador=reservacion.id,
        cantidad_personas=4,
        ruta_base_datos=ruta,
        ahora=AHORA,
    )

    cancelar_reservacion(
        reservacion.id,
        ruta,
    )

    modificar_sala(
        "S06",
        capacidad=4,
        ruta_base_datos=ruta,
        hoy=HOY,
    )

    estado = obtener_estado_integridad(
        ruta
    )

    assert (
        estado["integridad"]
        == "ok"
    )

    assert (
        estado["claves_foraneas"]
        == []
    )

    assert (
        estado["correcta"]
        is True
    )