"""
Pruebas del servicio de estudiantes.
"""

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    buscar_estudiante,
    consultar_estudiantes,
    modificar_estudiante,
    registrar_estudiante,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


def preparar_base(tmp_path):
    """
    Crea una base temporal inicializada.
    """

    ruta = tmp_path / "prueba.db"

    inicializar_base_datos(ruta)

    return ruta


def test_registrar_estudiante_valido(
    tmp_path,
):
    """
    Verifica el registro exitoso de un estudiante.
    """

    ruta = preparar_base(tmp_path)

    estudiante = registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    assert estudiante.carne == "D001234567"
    assert estudiante.nombre == "David Ramírez"
    assert estudiante.correo == "david@universidad.ac.cr"
    assert estudiante.estado == "activo"


def test_registro_normaliza_datos(
    tmp_path,
):
    """
    Verifica la normalizacion de espacios y carne.
    """

    ruta = preparar_base(tmp_path)

    estudiante = registrar_estudiante(
        " d001234567 ",
        "  David Ramírez  ",
        "  david@universidad.ac.cr  ",
        ruta_base_datos=ruta,
    )

    assert estudiante.carne == "D001234567"
    assert estudiante.nombre == "David Ramírez"
    assert estudiante.correo == "david@universidad.ac.cr"


def test_estudiante_registrado_persiste(
    tmp_path,
):
    """
    Verifica que el estudiante quede almacenado
    realmente en SQLite.
    """

    ruta = preparar_base(tmp_path)

    registrar_estudiante(
        "D001234567",
        "David Ramírez",
        "david@universidad.ac.cr",
        ruta_base_datos=ruta,
    )

    conexion = obtener_conexion(ruta)

    cantidad = conexion.execute(
        """
        SELECT COUNT(*)
        FROM estudiantes
        WHERE carne = ?
        """,
        ("D001234567",),
    ).fetchone()[0]

    conexion.close()

    assert cantidad == 1


def test_rechazar_carne_duplicado(
    tmp_path,
):
    """
    Verifica que no se pueda registrar
    un carne existente.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="Ya existe",
    ):
        registrar_estudiante(
            "A001234567",
            "Otra Andrea",
            "otra@universidad.ac.cr",
            ruta_base_datos=ruta,
        )


def test_rechazar_duplicado_sin_distinguir_mayusculas(
    tmp_path,
):
    """
    Verifica la unicidad sin distinguir
    mayusculas y minusculas.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorReglaNegocio):
        registrar_estudiante(
            "a001234567",
            "Otra Andrea",
            "otra@universidad.ac.cr",
            ruta_base_datos=ruta,
        )


def test_rechazar_datos_invalidos_en_registro(
    tmp_path,
):
    """
    Verifica que las validaciones se apliquen
    antes de guardar.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorValidacion):
        registrar_estudiante(
            "A12",
            "Nombre",
            "correo@universidad.ac.cr",
            ruta_base_datos=ruta,
        )


def test_rechazar_correo_invalido_en_registro(
    tmp_path,
):
    """
    Verifica que un correo invalido no sea almacenado.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(ErrorValidacion):
        registrar_estudiante(
            "D001234567",
            "David Ramírez",
            "correo-invalido",
            ruta_base_datos=ruta,
        )


def test_consultar_estudiantes_iniciales(
    tmp_path,
):
    """
    Verifica que la consulta incluya todos
    los estudiantes iniciales.
    """

    ruta = preparar_base(tmp_path)

    estudiantes = consultar_estudiantes(
        ruta,
    )

    assert len(estudiantes) == 3

    assert estudiantes[0].carne == "A001234567"
    assert estudiantes[1].carne == "B009876543"
    assert estudiantes[2].carne == "C004567890"


def test_consulta_incluye_activos_e_inactivos(
    tmp_path,
):
    """
    Verifica que el listado no excluya
    estudiantes inactivos.
    """

    ruta = preparar_base(tmp_path)

    estudiantes = consultar_estudiantes(
        ruta,
    )

    estados = {
        estudiante.estado
        for estudiante in estudiantes
    }

    assert "activo" in estados
    assert "inactivo" in estados


def test_buscar_estudiante_por_carne(
    tmp_path,
):
    """
    Verifica la busqueda de un estudiante.
    """

    ruta = preparar_base(tmp_path)

    estudiante = buscar_estudiante(
        "A001234567",
        ruta,
    )

    assert estudiante is not None
    assert estudiante.nombre == "Andrea Solano"


def test_busqueda_no_distingue_mayusculas(
    tmp_path,
):
    """
    Verifica que la busqueda del carne sea
    independiente de mayusculas y minusculas.
    """

    ruta = preparar_base(tmp_path)

    estudiante = buscar_estudiante(
        "a001234567",
        ruta,
    )

    assert estudiante is not None
    assert estudiante.carne == "A001234567"


def test_buscar_estudiante_inexistente(
    tmp_path,
):
    """
    Verifica que una busqueda sin resultado
    devuelva None.
    """

    ruta = preparar_base(tmp_path)

    estudiante = buscar_estudiante(
        "Z999999999",
        ruta,
    )

    assert estudiante is None


def test_modificar_nombre_correo_y_estado(
    tmp_path,
):
    """
    Verifica la modificacion de los campos
    permitidos.
    """

    ruta = preparar_base(tmp_path)

    estudiante = modificar_estudiante(
        "A001234567",
        nombre="Andrea María Solano",
        correo="andrea.nueva@universidad.ac.cr",
        estado="inactivo",
        ruta_base_datos=ruta,
    )

    assert estudiante.carne == "A001234567"
    assert estudiante.nombre == "Andrea María Solano"
    assert (
        estudiante.correo
        == "andrea.nueva@universidad.ac.cr"
    )
    assert estudiante.estado == "inactivo"


def test_modificacion_parcial_conserva_otros_datos(
    tmp_path,
):
    """
    Verifica que puedan modificarse solamente
    los campos enviados.
    """

    ruta = preparar_base(tmp_path)

    antes = buscar_estudiante(
        "A001234567",
        ruta,
    )

    despues = modificar_estudiante(
        "A001234567",
        estado="inactivo",
        ruta_base_datos=ruta,
    )

    assert despues.nombre == antes.nombre
    assert despues.correo == antes.correo
    assert despues.estado == "inactivo"


def test_modificacion_no_cambia_carne(
    tmp_path,
):
    """
    Verifica que el carne permanezca como
    identificador inmutable.
    """

    ruta = preparar_base(tmp_path)

    modificar_estudiante(
        "A001234567",
        nombre="Andrea Modificada",
        ruta_base_datos=ruta,
    )

    estudiante = buscar_estudiante(
        "A001234567",
        ruta,
    )

    assert estudiante is not None
    assert estudiante.carne == "A001234567"
    assert estudiante.nombre == "Andrea Modificada"


def test_rechazar_modificacion_estudiante_inexistente(
    tmp_path,
):
    """
    Verifica que no se pueda modificar
    un estudiante inexistente.
    """

    ruta = preparar_base(tmp_path)

    with pytest.raises(
        ErrorReglaNegocio,
        match="no existe",
    ):
        modificar_estudiante(
            "Z999999999",
            nombre="Estudiante inexistente",
            ruta_base_datos=ruta,
        )