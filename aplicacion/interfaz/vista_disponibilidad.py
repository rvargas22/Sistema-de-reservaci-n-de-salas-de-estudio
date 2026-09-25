"""
Vista de consulta de disponibilidad.
"""

from PySide6.QtWidgets import (
    QCalendarWidget,
    QComboBox,
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
    consultar_horarios_disponibles,
    consultar_salas,
)


class VistaDisponibilidad(QWidget):
    """
    Calendario y consulta de disponibilidad.
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
            "Calendario y disponibilidad"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        self.calendario = QCalendarWidget()

        self.combo_sala = QComboBox()

        self.combo_duracion = QComboBox()

        self.combo_duracion.addItem(
            "1 hora",
            1,
        )

        self.combo_duracion.addItem(
            "2 horas",
            2,
        )

        boton_consultar = QPushButton(
            "Consultar disponibilidad"
        )

        boton_consultar.clicked.connect(
            self.consultar
        )

        controles = QHBoxLayout()

        controles.addWidget(
            QLabel("Sala:")
        )

        controles.addWidget(
            self.combo_sala
        )

        controles.addWidget(
            QLabel("Duración:")
        )

        controles.addWidget(
            self.combo_duracion
        )

        controles.addWidget(
            boton_consultar
        )

        self.etiqueta_resultado = QLabel()

        self.tabla = QTableWidget()

        configurar_tabla(
            self.tabla,
            [
                "Horario disponible",
            ],
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            self.calendario
        )

        layout.addLayout(
            controles
        )

        layout.addWidget(
            self.etiqueta_resultado
        )

        layout.addWidget(
            self.tabla
        )

    def refrescar(
        self,
    ):
        try:
            codigo_actual = (
                self.combo_sala.currentData()
            )

            self.combo_sala.clear()

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
                indice = (
                    self.combo_sala.findData(
                        codigo_actual
                    )
                )

                if indice >= 0:
                    self.combo_sala.setCurrentIndex(
                        indice
                    )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def consultar(
        self,
    ):
        try:
            codigo = (
                self.combo_sala.currentData()
            )

            fecha = (
                self.calendario.selectedDate()
                .toString(
                    "yyyy-MM-dd"
                )
            )

            duracion = (
                self.combo_duracion.currentData()
            )

            horarios = (
                consultar_horarios_disponibles(
                    codigo_sala=codigo,
                    fecha=fecha,
                    duracion_horas=duracion,
                    ruta_base_datos=(
                        self.ruta_base_datos
                    ),
                )
            )

            filas = [
                {
                    "hora": hora,
                }
                for hora in horarios
            ]

            cargar_tabla(
                self.tabla,
                filas,
                [
                    "hora",
                ],
            )

            self.etiqueta_resultado.setText(
                (
                    f"{fecha} · "
                    f"{len(horarios)} horarios "
                    "disponibles"
                )
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )