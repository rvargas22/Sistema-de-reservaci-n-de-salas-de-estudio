"""
Ventana principal de la aplicacion.
"""

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.interfaz.vista_auditoria import (
    VistaAuditoria,
)

from aplicacion.interfaz.vista_disponibilidad import (
    VistaDisponibilidad,
)

from aplicacion.interfaz.vista_estudiantes import (
    VistaEstudiantes,
)

from aplicacion.interfaz.vista_panel import (
    VistaPanel,
)

from aplicacion.interfaz.vista_reportes import (
    VistaReportes,
)

from aplicacion.interfaz.vista_reservaciones import (
    VistaReservaciones,
)

from aplicacion.interfaz.vista_salas import (
    VistaSalas,
)


class VentanaPrincipal(QMainWindow):
    """
    Ventana principal del sistema.
    """

    NOMBRES_MODULOS = [
        "Panel de control",
        "Estudiantes",
        "Salas",
        "Disponibilidad",
        "Reservaciones",
        "Reportes",
        "Historial de acciones",
    ]

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

        self.setWindowTitle(
            "Sistema de reservación de salas de estudio"
        )

        self.resize(
            1350,
            820,
        )

        self.setMinimumSize(
            1050,
            680,
        )

        self._crear_vistas()
        self._crear_interfaz()
        self._conectar_senales()
        self._aplicar_estilo()

    def _crear_vistas(
        self,
    ):
        self.vista_panel = VistaPanel(
            self.ruta_base_datos
        )

        self.vista_estudiantes = (
            VistaEstudiantes(
                self.ruta_base_datos
            )
        )

        self.vista_salas = VistaSalas(
            self.ruta_base_datos
        )

        self.vista_disponibilidad = (
            VistaDisponibilidad(
                self.ruta_base_datos
            )
        )

        self.vista_reservaciones = (
            VistaReservaciones(
                self.ruta_base_datos
            )
        )

        self.vista_reportes = (
            VistaReportes(
                self.ruta_base_datos
            )
        )

        self.vista_auditoria = (
            VistaAuditoria(
                self.ruta_base_datos
            )
        )

        self.vistas = [
            self.vista_panel,
            self.vista_estudiantes,
            self.vista_salas,
            self.vista_disponibilidad,
            self.vista_reservaciones,
            self.vista_reportes,
            self.vista_auditoria,
        ]

    def _crear_interfaz(
        self,
    ):
        contenedor = QWidget()

        self.setCentralWidget(
            contenedor
        )

        layout_principal = QHBoxLayout(
            contenedor
        )

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout_principal.setSpacing(
            0
        )

        barra_lateral = QFrame()

        barra_lateral.setObjectName(
            "barraLateral"
        )

        barra_lateral.setFixedWidth(
            235
        )

        layout_lateral = QVBoxLayout(
            barra_lateral
        )

        titulo = QLabel(
            "RESERVAS"
        )

        titulo.setObjectName(
            "tituloAplicacion"
        )

        subtitulo = QLabel(
            "Salas de estudio"
        )

        subtitulo.setObjectName(
            "subtituloAplicacion"
        )

        self.menu = QListWidget()

        self.menu.addItems(
            self.NOMBRES_MODULOS
        )

        self.menu.setCurrentRow(
            0
        )

        layout_lateral.addWidget(
            titulo
        )

        layout_lateral.addWidget(
            subtitulo
        )

        layout_lateral.addSpacing(
            20
        )

        layout_lateral.addWidget(
            self.menu
        )

        layout_lateral.addStretch()

        contenido = QWidget()

        layout_contenido = QVBoxLayout(
            contenido
        )

        layout_contenido.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        self.etiqueta_modulo = QLabel(
            self.NOMBRES_MODULOS[0]
        )

        self.etiqueta_modulo.setObjectName(
            "encabezadoModulo"
        )

        self.stack = QStackedWidget()

        for vista in self.vistas:
            self.stack.addWidget(
                vista
            )

        layout_contenido.addWidget(
            self.etiqueta_modulo
        )

        layout_contenido.addWidget(
            self.stack
        )

        layout_principal.addWidget(
            barra_lateral
        )

        layout_principal.addWidget(
            contenido
        )

        self.menu.currentRowChanged.connect(
            self.cambiar_modulo
        )

    def _conectar_senales(
        self,
    ):
        self.vista_estudiantes.datos_cambiados.connect(
            self.refrescar_todo
        )

        self.vista_salas.datos_cambiados.connect(
            self.refrescar_todo
        )

        self.vista_reservaciones.datos_cambiados.connect(
            self.refrescar_todo
        )

    def cambiar_modulo(
        self,
        indice,
    ):
        if not (
            0 <= indice < len(
                self.vistas
            )
        ):
            return

        self.stack.setCurrentIndex(
            indice
        )

        self.etiqueta_modulo.setText(
            self.NOMBRES_MODULOS[
                indice
            ]
        )

        vista = self.vistas[
            indice
        ]

        if hasattr(
            vista,
            "refrescar",
        ):
            vista.refrescar()

    def refrescar_todo(
        self,
    ):
        """
        Refresca las vistas que dependen de datos
        que pueden haber cambiado.
        """

        for vista in self.vistas:
            if hasattr(
                vista,
                "refrescar",
            ):
                vista.refrescar()

    def _aplicar_estilo(
    self,
    ):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f3f4f6;
                color: #1f2937;
            }

            QWidget {
                background-color: #f3f4f6;
                color: #1f2937;
                font-size: 13px;
            }

            #barraLateral {
                background-color: #1e293b;
            }

            #tituloAplicacion {
                color: #ffffff;
                font-size: 22px;
                font-weight: 700;
                padding-top: 20px;
                background-color: transparent;
            }

            #subtituloAplicacion {
                color: #cbd5e1;
                font-size: 13px;
                background-color: transparent;
            }

            #encabezadoModulo {
                color: #111827;
                font-size: 22px;
                font-weight: 700;
                padding-bottom: 4px;
                background-color: transparent;
            }

            #tituloVista {
                color: #111827;
                font-size: 18px;
                font-weight: 600;
                padding-bottom: 8px;
                background-color: transparent;
            }

            QLabel {
                color: #1f2937;
                background-color: transparent;
            }

            QListWidget {
                border: none;
                background-color: transparent;
                color: #e5e7eb;
                outline: 0;
            }

            QListWidget::item {
                padding: 13px 12px;
                margin: 2px 0px;
                border-radius: 6px;
                background-color: transparent;
                color: #e5e7eb;
            }

            QListWidget::item:hover {
                background-color: #334155;
                color: #ffffff;
            }

            QListWidget::item:selected {
                background-color: #475569;
                color: #ffffff;
                font-weight: 600;
            }

            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: 1px solid #1d4ed8;
                border-radius: 6px;
                padding: 7px 12px;
                min-height: 20px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }

            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #6b7280;
                border: 1px solid #cbd5e1;
            }

            QLineEdit,
            QComboBox,
            QSpinBox,
            QDateEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 5px;
                min-height: 22px;
                selection-background-color: #bfdbfe;
                selection-color: #111827;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QSpinBox:focus,
            QDateEdit:focus {
                border: 1px solid #2563eb;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #111827;
                selection-background-color: #dbeafe;
                selection-color: #111827;
                border: 1px solid #cbd5e1;
            }

            QTableWidget {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                gridline-color: #e5e7eb;
                selection-background-color: #dbeafe;
                selection-color: #111827;
                alternate-background-color: #f9fafb;
            }

            QHeaderView::section {
                background-color: #e5e7eb;
                color: #111827;
                padding: 7px;
                font-weight: 700;
                border: 1px solid #d1d5db;
            }

            QTableCornerButton::section {
                background-color: #e5e7eb;
                border: 1px solid #d1d5db;
            }

            QTabWidget::pane {
                border: 1px solid #d1d5db;
                background-color: #ffffff;
                border-radius: 6px;
                top: -1px;
            }

            QTabBar::tab {
                background-color: #e5e7eb;
                color: #374151;
                padding: 8px 14px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #d1d5db;
            }

            QTabBar::tab:selected {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: 700;
            }

            QTabBar::tab:hover {
                background-color: #dbeafe;
                color: #1e3a8a;
            }

            QCalendarWidget QWidget {
                alternate-background-color: #ffffff;
            }

            QCalendarWidget QToolButton {
                color: #111827;
                background-color: #e5e7eb;
                border: none;
                padding: 6px;
                font-weight: 600;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #dbeafe;
            }

            QCalendarWidget QMenu {
                background-color: #ffffff;
                color: #111827;
            }

            QCalendarWidget QSpinBox {
                background-color: #ffffff;
                color: #111827;
            }

            QCalendarWidget QAbstractItemView:enabled {
                background-color: #ffffff;
                color: #111827;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }

            QCheckBox {
                color: #111827;
                spacing: 6px;
                background-color: transparent;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }

            QGroupBox {
                color: #111827;
                font-weight: 600;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ffffff;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #111827;
                background-color: #ffffff;
            }

            QFrame {
                color: #111827;
            }
            """
        )