"""
Vista de gestion de salas.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
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
    buscar_sala,
    consultar_salas,
    modificar_sala,
    registrar_sala,
)


class VistaSalas(QWidget):
    """
    Gestion de salas.
    """

    datos_cambiados = Signal()

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

        self.codigo_seleccionado = None

        self._crear_interfaz()

        self.refrescar()

    def _crear_interfaz(
        self,
    ):
        titulo = QLabel(
            "Gestión de salas"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        self.campo_codigo = QLineEdit()

        self.campo_nombre = QLineEdit()

        self.campo_capacidad = QSpinBox()

        self.campo_capacidad.setRange(
            1,
            10000,
        )

        self.combo_estado = QComboBox()

        self.combo_estado.addItem(
            "Disponible",
            "disponible",
        )

        self.combo_estado.addItem(
            "Fuera de servicio",
            "fuera_de_servicio",
        )

        formulario = QFormLayout()

        formulario.addRow(
            "Código:",
            self.campo_codigo,
        )

        formulario.addRow(
            "Nombre:",
            self.campo_nombre,
        )

        formulario.addRow(
            "Capacidad:",
            self.campo_capacidad,
        )

        formulario.addRow(
            "Estado:",
            self.combo_estado,
        )

        boton_nueva = QPushButton(
            "Nueva"
        )

        boton_registrar = QPushButton(
            "Registrar"
        )

        boton_modificar = QPushButton(
            "Modificar"
        )

        boton_actualizar = QPushButton(
            "Actualizar"
        )

        boton_nueva.clicked.connect(
            self.nueva
        )

        boton_registrar.clicked.connect(
            self.registrar
        )

        boton_modificar.clicked.connect(
            self.modificar
        )

        boton_actualizar.clicked.connect(
            self.refrescar
        )

        botones = QHBoxLayout()

        botones.addWidget(
            boton_nueva
        )

        botones.addWidget(
            boton_registrar
        )

        botones.addWidget(
            boton_modificar
        )

        botones.addWidget(
            boton_actualizar
        )

        self.tabla = QTableWidget()

        configurar_tabla(
            self.tabla,
            [
                "Código",
                "Nombre",
                "Capacidad",
                "Estado",
            ],
        )

        self.tabla.cellClicked.connect(
            self.cargar_seleccion
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            titulo
        )

        layout.addLayout(
            formulario
        )

        layout.addLayout(
            botones
        )

        layout.addWidget(
            self.tabla
        )

    def nueva(
        self,
    ):
        self.codigo_seleccionado = None

        self.campo_codigo.setEnabled(
            True
        )

        self.campo_codigo.clear()
        self.campo_nombre.clear()

        self.campo_capacidad.setValue(
            1
        )

        self.combo_estado.setCurrentIndex(
            0
        )

        self.tabla.clearSelection()

    def registrar(
        self,
    ):
        try:
            sala = registrar_sala(
                codigo=(
                    self.campo_codigo.text()
                ),
                nombre=(
                    self.campo_nombre.text()
                ),
                capacidad=(
                    self.campo_capacidad.value()
                ),
                estado=(
                    self.combo_estado.currentData()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            mostrar_exito(
                self,
                (
                    "Sala registrada correctamente: "
                    f"{sala.codigo}"
                ),
            )

            self.nueva()
            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def modificar(
        self,
    ):
        if self.codigo_seleccionado is None:
            mostrar_error(
                self,
                ValueError(
                    "Seleccione una sala "
                    "antes de modificar."
                ),
            )
            return

        try:
            sala = modificar_sala(
                codigo=(
                    self.codigo_seleccionado
                ),
                nombre=(
                    self.campo_nombre.text()
                ),
                capacidad=(
                    self.campo_capacidad.value()
                ),
                estado=(
                    self.combo_estado.currentData()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            mostrar_exito(
                self,
                (
                    "Sala modificada correctamente: "
                    f"{sala.codigo}"
                ),
            )

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def cargar_seleccion(
        self,
        fila,
        columna,
    ):
        del columna

        item = self.tabla.item(
            fila,
            0,
        )

        if item is None:
            return

        try:
            sala = buscar_sala(
                item.text(),
                self.ruta_base_datos,
            )

            if sala is None:
                return

            self.codigo_seleccionado = (
                sala.codigo
            )

            self.campo_codigo.setText(
                sala.codigo
            )

            self.campo_codigo.setEnabled(
                False
            )

            self.campo_nombre.setText(
                sala.nombre
            )

            self.campo_capacidad.setValue(
                sala.capacidad
            )

            indice = self.combo_estado.findData(
                sala.estado
            )

            if indice >= 0:
                self.combo_estado.setCurrentIndex(
                    indice
                )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def refrescar(
        self,
    ):
        try:
            salas = consultar_salas(
                self.ruta_base_datos
            )

            cargar_tabla(
                self.tabla,
                salas,
                [
                    "codigo",
                    "nombre",
                    "capacidad",
                    "estado",
                ],
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )