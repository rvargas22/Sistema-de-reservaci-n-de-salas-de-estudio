"""
Vista de gestion de estudiantes.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
    buscar_estudiante,
    consultar_estudiantes,
    modificar_estudiante,
    registrar_estudiante,
)

from aplicacion.validaciones import (
    ErrorValidacion,
)


class VistaEstudiantes(QWidget):
    """
    Gestion de estudiantes.
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

        self.carne_seleccionado = None

        self._crear_interfaz()

        self.nuevo()

        self.refrescar()

    def _crear_interfaz(
        self,
    ):
        titulo = QLabel(
            "Gestión de estudiantes"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        self.campo_carne = QLineEdit()

        self.campo_carne.setPlaceholderText(
            "Ej. A001234567"
        )

        self.campo_nombre = QLineEdit()

        self.campo_nombre.setPlaceholderText(
            "Nombre completo"
        )

        self.campo_correo = QLineEdit()

        self.campo_correo.setPlaceholderText(
            "correo@universidad.ac.cr"
        )

        self.combo_estado = QComboBox()

        self.combo_estado.addItem(
            "Activo",
            "activo",
        )

        self.combo_estado.addItem(
            "Inactivo",
            "inactivo",
        )

        formulario = QFormLayout()

        formulario.addRow(
            "Carné:",
            self.campo_carne,
        )

        formulario.addRow(
            "Nombre:",
            self.campo_nombre,
        )

        formulario.addRow(
            "Correo:",
            self.campo_correo,
        )

        formulario.addRow(
            "Estado:",
            self.combo_estado,
        )

        boton_nuevo = QPushButton(
            "Nuevo"
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

        boton_nuevo.clicked.connect(
            self.nuevo
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
            boton_nuevo
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
                "Carné",
                "Nombre",
                "Correo",
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

    def nuevo(
        self,
    ):
        """
        Prepara el formulario para registrar
        un estudiante nuevo.

        El estado inicial es siempre activo.
        """

        self.carne_seleccionado = None

        self.campo_carne.setEnabled(
            True
        )

        self.campo_carne.clear()
        self.campo_nombre.clear()
        self.campo_correo.clear()

        indice = self.combo_estado.findData(
            "activo"
        )

        if indice >= 0:
            self.combo_estado.setCurrentIndex(
                indice
            )

        self.combo_estado.setEnabled(
            False
        )

        self.tabla.clearSelection()

        self.campo_carne.setFocus()

    def registrar(
        self,
    ):
        try:
            estudiante = registrar_estudiante(
                carne=(
                    self.campo_carne.text()
                ),
                nombre=(
                    self.campo_nombre.text()
                ),
                correo=(
                    self.campo_correo.text()
                ),
                estado="activo",
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            mostrar_exito(
                self,
                (
                    "Estudiante registrado "
                    "correctamente.\n\n"
                    f"Carné: {estudiante.carne}"
                ),
            )

            self.nuevo()

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
        if self.carne_seleccionado is None:
            mostrar_error(
                self,
                ErrorValidacion(
                    (
                        "Seleccione un estudiante "
                        "antes de modificar."
                    )
                ),
            )

            return

        try:
            estudiante = modificar_estudiante(
                carne=(
                    self.carne_seleccionado
                ),
                nombre=(
                    self.campo_nombre.text()
                ),
                correo=(
                    self.campo_correo.text()
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
                    "Estudiante modificado "
                    "correctamente.\n\n"
                    f"Carné: {estudiante.carne}"
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
            estudiante = buscar_estudiante(
                item.text(),
                self.ruta_base_datos,
            )

            if estudiante is None:
                return

            self.carne_seleccionado = (
                estudiante.carne
            )

            self.campo_carne.setText(
                estudiante.carne
            )

            self.campo_carne.setEnabled(
                False
            )

            self.campo_nombre.setText(
                estudiante.nombre
            )

            self.campo_correo.setText(
                estudiante.correo
            )

            indice = self.combo_estado.findData(
                estudiante.estado
            )

            if indice >= 0:
                self.combo_estado.setCurrentIndex(
                    indice
                )

            # Solo al modificar un registro existente
            # se permite cambiar su estado.
            self.combo_estado.setEnabled(
                True
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
            estudiantes = consultar_estudiantes(
                self.ruta_base_datos
            )

            cargar_tabla(
                self.tabla,
                estudiantes,
                [
                    "carne",
                    "nombre",
                    "correo",
                    "estado",
                ],
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )