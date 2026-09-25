"""
Vista de reportes y exportacion CSV.
"""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.interfaz.utilidades import (
    cargar_tabla,
    configurar_tabla,
    mostrar_error,
    mostrar_exito,
)

from aplicacion.servicios import (
    exportar_reporte_csv,
    generar_reporte_reservaciones,
)


class VistaReportes(QWidget):
    """
    Generacion y exportacion de reportes.
    """

    def __init__(
        self,
        ruta_base_datos=None,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.ruta_base_datos = (
            ruta_base_datos
        )

        self.reporte_actual = []
        self.reporte_generado = False

        self._crear_interfaz()

    def _crear_interfaz(
        self,
    ):
        titulo = QLabel(
            "Reportes y exportación"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        self.fecha_inicial = QDateEdit(
            QDate.currentDate()
        )

        self.fecha_final = QDateEdit(
            QDate.currentDate().addMonths(
                1
            )
        )

        for control in (
            self.fecha_inicial,
            self.fecha_final,
        ):
            control.setCalendarPopup(
                True
            )

            control.setDisplayFormat(
                "yyyy-MM-dd"
            )

        boton_generar = QPushButton(
            "Generar reporte"
        )

        boton_exportar = QPushButton(
            "Exportar CSV"
        )

        boton_generar.clicked.connect(
            self.generar
        )

        boton_exportar.clicked.connect(
            self.exportar
        )

        controles = QHBoxLayout()

        controles.addWidget(
            QLabel("Fecha inicial:")
        )

        controles.addWidget(
            self.fecha_inicial
        )

        controles.addWidget(
            QLabel("Fecha final:")
        )

        controles.addWidget(
            self.fecha_final
        )

        controles.addWidget(
            boton_generar
        )

        controles.addWidget(
            boton_exportar
        )

        self.etiqueta_resultados = QLabel(
            "Reporte no generado."
        )

        self.tabla = QTableWidget()

        configurar_tabla(
            self.tabla,
            [
                "ID",
                "Carné",
                "Estudiante",
                "Sala",
                "Nombre sala",
                "Fecha",
                "Hora",
                "Duración",
                "Personas",
                "Estado",
            ],
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            titulo
        )

        layout.addLayout(
            controles
        )

        layout.addWidget(
            self.etiqueta_resultados
        )

        layout.addWidget(
            self.tabla
        )

    def generar(
        self,
    ):
        try:
            self.reporte_actual = (
                generar_reporte_reservaciones(
                    fecha_inicial=(
                        self.fecha_inicial.date()
                        .toString(
                            "yyyy-MM-dd"
                        )
                    ),
                    fecha_final=(
                        self.fecha_final.date()
                        .toString(
                            "yyyy-MM-dd"
                        )
                    ),
                    ruta_base_datos=(
                        self.ruta_base_datos
                    ),
                )
            )

            self.reporte_generado = True

            cargar_tabla(
                self.tabla,
                self.reporte_actual,
                [
                    "id",
                    "carne_estudiante",
                    "nombre_estudiante",
                    "codigo_sala",
                    "nombre_sala",
                    "fecha",
                    "hora_inicio",
                    "duracion_horas",
                    "cantidad_personas",
                    "estado",
                ],
            )

            self.etiqueta_resultados.setText(
                (
                    "Registros encontrados: "
                    f"{len(self.reporte_actual)}"
                )
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def exportar(
        self,
    ):
        if not self.reporte_generado:
            mostrar_error(
                self,
                ValueError(
                    "Primero debe generar "
                    "un reporte."
                ),
            )
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar reporte",
            "reporte_reservaciones.csv",
            "Archivos CSV (*.csv)",
        )

        if not ruta:
            return

        try:
            resultado = exportar_reporte_csv(
                self.reporte_actual,
                ruta,
            )

            if resultado is not None:
                mostrar_exito(
                    self,
                    (
                        "Reporte exportado "
                        f"correctamente:\n{resultado}"
                    ),
                )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def refrescar(
        self,
    ):
        """
        No genera automaticamente un reporte porque
        las fechas deben permanecer bajo control
        del usuario.
        """
        return None