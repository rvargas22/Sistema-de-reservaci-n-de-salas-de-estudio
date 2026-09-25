"""
Utilidades compartidas por las vistas de la interfaz.
"""

import sqlite3

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

    tabla.setAlternatingRowColors(
        True
    )


def cargar_tabla(
    tabla,
    filas,
    campos,
):
    """
    Carga diccionarios u objetos en una tabla.
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
    Selecciona un elemento usando su userData.
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
    Presenta los errores de forma comprensible
    sin cerrar la aplicacion.
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

        return

    if isinstance(
        error,
        sqlite3.IntegrityError,
    ):
        QMessageBox.critical(
            padre,
            "Error de integridad",
            (
                "La base de datos rechazó la "
                "operación porque produciría "
                "información inconsistente.\n\n"
                f"Detalle: {error}"
            ),
        )

        return

    if isinstance(
        error,
        sqlite3.OperationalError,
    ):
        QMessageBox.critical(
            padre,
            "Error de base de datos",
            (
                "No fue posible completar la "
                "operación en SQLite.\n\n"
                f"Detalle: {error}"
            ),
        )

        return

    if isinstance(
        error,
        sqlite3.DatabaseError,
    ):
        QMessageBox.critical(
            padre,
            "Problema con la base de datos",
            (
                "SQLite detectó un problema "
                "durante la operación.\n\n"
                f"Detalle: {error}"
            ),
        )

        return

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
    Muestra una confirmacion.
    """

    QMessageBox.information(
        padre,
        "Operación completada",
        mensaje,
    )