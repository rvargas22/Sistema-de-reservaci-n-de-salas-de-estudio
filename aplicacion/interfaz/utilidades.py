"""
Utilidades compartidas por las vistas de la interfaz.
"""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
)


def configurar_tabla(
    tabla,
    encabezados,
):
    """
    Aplica una configuracion comun a las tablas.
    """

    tabla.setColumnCount(
        len(encabezados)
    )

    tabla.setHorizontalHeaderLabels(
        encabezados
    )

    tabla.setSelectionBehavior(
        QAbstractItemView.SelectionBehavior.SelectRows
    )

    tabla.setSelectionMode(
        QAbstractItemView.SelectionMode.SingleSelection
    )

    tabla.setEditTriggers(
        QAbstractItemView.EditTrigger.NoEditTriggers
    )

    tabla.verticalHeader().setVisible(
        False
    )

    tabla.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )


def cargar_tabla(
    tabla,
    filas,
    campos,
):
    """
    Carga una coleccion de diccionarios u objetos
    dentro de un QTableWidget.
    """

    tabla.setRowCount(
        len(filas)
    )

    for numero_fila, fila in enumerate(
        filas
    ):
        for numero_columna, campo in enumerate(
            campos
        ):
            if isinstance(
                fila,
                dict,
            ):
                valor = fila.get(
                    campo,
                    "",
                )
            else:
                valor = getattr(
                    fila,
                    campo,
                    "",
                )

            if valor is None:
                valor = ""

            tabla.setItem(
                numero_fila,
                numero_columna,
                QTableWidgetItem(
                    str(valor)
                ),
            )


def seleccionar_combo_por_dato(
    combo,
    dato,
):
    """
    Selecciona en un QComboBox el elemento cuyo
    userData coincide con el dato indicado.
    """

    indice = combo.findData(
        dato
    )

    if indice >= 0:
        combo.setCurrentIndex(
            indice
        )


def mostrar_error(
    padre,
    error,
):
    """
    Muestra un error de negocio, validacion
    o un error inesperado.
    """

    if isinstance(
        error,
        (
            ErrorValidacion,
            ErrorReglaNegocio,
        ),
    ):
        QMessageBox.warning(
            padre,
            "Operación no permitida",
            str(error),
        )

    else:
        QMessageBox.critical(
            padre,
            "Error inesperado",
            (
                "Ocurrió un error inesperado.\n\n"
                f"{error}"
            ),
        )


def mostrar_exito(
    padre,
    mensaje,
):
    """
    Muestra un mensaje de confirmacion.
    """

    QMessageBox.information(
        padre,
        "Operación completada",
        mensaje,
    )