"""
Vista del panel principal.
"""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
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
)

from aplicacion.servicios import (
    consultar_panel,
    consultar_salas,
)


class VistaPanel(QWidget):
    """
    Panel principal de reservaciones.
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

        self._crear_interfaz()

        self.refrescar()

    def _crear_interfaz(
        self,
    ):
        titulo = QLabel(
            "Panel de control"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        self.check_fecha = QCheckBox(
            "Filtrar por fecha"
        )

        self.fecha = QDateEdit(
            QDate.currentDate()
        )

        self.fecha.setCalendarPopup(
            True
        )

        self.fecha.setDisplayFormat(
            "yyyy-MM-dd"
        )

        self.combo_sala = QComboBox()

        self.combo_estado = QComboBox()

        self.combo_estado.addItem(
            "Todos los estados",
            None,
        )

        self.combo_estado.addItem(
            "Activa",
            "activa",
        )

        self.combo_estado.addItem(
            "Cancelada",
            "cancelada",
        )

        boton_aplicar = QPushButton(
            "Aplicar filtros"
        )

        boton_limpiar = QPushButton(
            "Limpiar"
        )

        boton_actualizar = QPushButton(
            "Actualizar"
        )

        boton_aplicar.clicked.connect(
            self.cargar_datos
        )

        boton_limpiar.clicked.connect(
            self.limpiar_filtros
        )

        boton_actualizar.clicked.connect(
            self.refrescar
        )

        filtros = QHBoxLayout()

        filtros.addWidget(
            self.check_fecha
        )

        filtros.addWidget(
            self.fecha
        )

        filtros.addWidget(
            QLabel("Sala:")
        )

        filtros.addWidget(
            self.combo_sala
        )

        filtros.addWidget(
            QLabel("Estado:")
        )

        filtros.addWidget(
            self.combo_estado
        )

        filtros.addWidget(
            boton_aplicar
        )

        filtros.addWidget(
            boton_limpiar
        )

        filtros.addWidget(
            boton_actualizar
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

        self.etiqueta_resultados = QLabel()

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            titulo
        )

        layout.addLayout(
            filtros
        )

        layout.addWidget(
            self.etiqueta_resultados
        )

        layout.addWidget(
            self.tabla
        )

    def refrescar_opciones_salas(
        self,
    ):
        codigo_actual = (
            self.combo_sala.currentData()
        )

        self.combo_sala.clear()

        self.combo_sala.addItem(
            "Todas las salas",
            None,
        )

        salas = consultar_salas(
            self.ruta_base_datos
        )

        for sala in salas:
            self.combo_sala.addItem(
                (
                    f"{sala.codigo} - "
                    f"{sala.nombre}"
                ),
                sala.codigo,
            )

        if codigo_actual is not None:
            indice = self.combo_sala.findData(
                codigo_actual
            )

            if indice >= 0:
                self.combo_sala.setCurrentIndex(
                    indice
                )

    def cargar_datos(
        self,
    ):
        try:
            fecha = None

            if self.check_fecha.isChecked():
                fecha = (
                    self.fecha.date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                )

            filas = consultar_panel(
                fecha=fecha,
                codigo_sala=(
                    self.combo_sala.currentData()
                ),
                estado=(
                    self.combo_estado.currentData()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            cargar_tabla(
                self.tabla,
                filas,
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
                    "Reservaciones mostradas: "
                    f"{len(filas)}"
                )
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def limpiar_filtros(
        self,
    ):
        self.check_fecha.setChecked(
            False
        )

        self.combo_sala.setCurrentIndex(
            0
        )

        self.combo_estado.setCurrentIndex(
            0
        )

        self.cargar_datos()

    def refrescar(
        self,
    ):
        try:
            self.refrescar_opciones_salas()
            self.cargar_datos()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )