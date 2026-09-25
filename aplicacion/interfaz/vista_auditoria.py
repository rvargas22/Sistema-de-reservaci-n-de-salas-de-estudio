"""
Vista del historial de auditoria.
"""

from PySide6.QtWidgets import (
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
    consultar_historial_auditoria,
)


class VistaAuditoria(QWidget):
    """
    Historial de acciones exitosas.
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
            "Historial de acciones"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        descripcion = QLabel(
            (
                "Este historial es de solo lectura. "
                "Las acciones se registran "
                "automáticamente."
            )
        )

        boton_actualizar = QPushButton(
            "Actualizar historial"
        )

        boton_actualizar.clicked.connect(
            self.refrescar
        )

        self.tabla = QTableWidget()

        configurar_tabla(
            self.tabla,
            [
                "ID",
                "Fecha y hora",
                "Acción",
                "Entidad",
                "Identificador",
                "Detalle",
            ],
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            descripcion
        )

        layout.addWidget(
            boton_actualizar
        )

        layout.addWidget(
            self.tabla
        )

    def refrescar(
        self,
    ):
        try:
            eventos = consultar_historial_auditoria(
                self.ruta_base_datos
            )

            cargar_tabla(
                self.tabla,
                eventos,
                [
                    "id",
                    "fecha_hora",
                    "accion",
                    "entidad",
                    "identificador",
                    "detalle",
                ],
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )