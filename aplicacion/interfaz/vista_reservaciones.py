"""
Vista de gestion de reservaciones individuales
y recurrentes.
"""

from PySide6.QtCore import (
    QDate,
    Signal,
)

from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.interfaz.utilidades import (
    cargar_tabla,
    configurar_tabla,
    mostrar_error,
    mostrar_exito,
    seleccionar_combo_por_dato,
)

from aplicacion.servicios import (
    analizar_serie_recurrente,
    buscar_reservaciones_estudiante,
    cancelar_ocurrencia_recurrente,
    cancelar_ocurrencias_futuras,
    cancelar_reservacion,
    consultar_estudiantes,
    consultar_historial_reservaciones,
    consultar_ocurrencias_serie,
    consultar_salas,
    crear_reservacion,
    crear_serie_recurrente,
    modificar_reservacion,
)

from aplicacion.validaciones import (
    ErrorValidacion,
)


class VistaReservaciones(QWidget):
    """
    Gestion de reservaciones individuales
    y recurrentes.
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

        self.reservacion_id_seleccionada = None

        self._crear_interfaz()

        self.refrescar()

    def _crear_interfaz(
        self,
    ):
        titulo = QLabel(
            "Gestión de reservaciones"
        )

        titulo.setObjectName(
            "tituloVista"
        )

        self.tabs = QTabWidget()

        self.tabs.addTab(
            self._crear_tab_individual(),
            "Reservación individual",
        )

        self.tabs.addTab(
            self._crear_tab_recurrente(),
            "Recurrencia semanal",
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            self.tabs
        )

    def _crear_tab_individual(
        self,
    ):
        pagina = QWidget()

        self.combo_estudiante = QComboBox()

        self.combo_sala = QComboBox()

        self.fecha_reserva = QDateEdit(
            QDate.currentDate().addDays(
                1
            )
        )

        self.fecha_reserva.setCalendarPopup(
            True
        )

        self.fecha_reserva.setDisplayFormat(
            "yyyy-MM-dd"
        )

        self.combo_hora = QComboBox()

        for hora in range(
            8,
            20,
        ):
            texto = f"{hora:02d}:00"

            self.combo_hora.addItem(
                texto,
                texto,
            )

        self.combo_duracion = QComboBox()

        self.combo_duracion.addItem(
            "1 hora",
            1,
        )

        self.combo_duracion.addItem(
            "2 horas",
            2,
        )

        self.cantidad_personas = QSpinBox()

        self.cantidad_personas.setRange(
            1,
            10000,
        )

        formulario = QFormLayout()

        formulario.addRow(
            "Estudiante:",
            self.combo_estudiante,
        )

        formulario.addRow(
            "Sala:",
            self.combo_sala,
        )

        formulario.addRow(
            "Fecha:",
            self.fecha_reserva,
        )

        formulario.addRow(
            "Hora:",
            self.combo_hora,
        )

        formulario.addRow(
            "Duración:",
            self.combo_duracion,
        )

        formulario.addRow(
            "Personas:",
            self.cantidad_personas,
        )

        boton_nueva = QPushButton(
            "Nueva"
        )

        boton_crear = QPushButton(
            "Crear"
        )

        boton_modificar = QPushButton(
            "Modificar seleccionada"
        )

        boton_cancelar = QPushButton(
            "Cancelar seleccionada"
        )

        boton_actualizar = QPushButton(
            "Actualizar"
        )

        boton_nueva.clicked.connect(
            self.nueva_reservacion
        )

        boton_crear.clicked.connect(
            self.crear_reservacion
        )

        boton_modificar.clicked.connect(
            self.modificar_reservacion
        )

        boton_cancelar.clicked.connect(
            self.cancelar_reservacion
        )

        boton_actualizar.clicked.connect(
            self.refrescar
        )

        botones = QHBoxLayout()

        botones.addWidget(
            boton_nueva
        )

        botones.addWidget(
            boton_crear
        )

        botones.addWidget(
            boton_modificar
        )

        botones.addWidget(
            boton_cancelar
        )

        botones.addWidget(
            boton_actualizar
        )

        self.campo_busqueda_carne = QLineEdit()

        self.campo_busqueda_carne.setPlaceholderText(
            "Buscar por carné del estudiante"
        )

        boton_buscar_estudiante = QPushButton(
            "Buscar por estudiante"
        )

        boton_mostrar_todas = QPushButton(
            "Mostrar todas"
        )

        boton_buscar_estudiante.clicked.connect(
            self.buscar_por_estudiante
        )

        boton_mostrar_todas.clicked.connect(
            self.mostrar_todas_reservaciones
        )

        self.campo_busqueda_carne.returnPressed.connect(
            self.buscar_por_estudiante
        )

        busqueda = QHBoxLayout()

        busqueda.addWidget(
            QLabel(
                "Buscar estudiante:"
            )
        )

        busqueda.addWidget(
            self.campo_busqueda_carne
        )

        busqueda.addWidget(
            boton_buscar_estudiante
        )

        busqueda.addWidget(
            boton_mostrar_todas
        )

        self.etiqueta_resultados = QLabel(
            "Historial de reservaciones"
        )

        self.tabla_reservaciones = QTableWidget()

        configurar_tabla(
            self.tabla_reservaciones,
            [
                "ID",
                "Carné",
                "Sala",
                "Fecha",
                "Hora inicio",
                "Hora fin",
                "Duración",
                "Personas",
                "Estado",
            ],
        )

        self.tabla_reservaciones.cellClicked.connect(
            self.cargar_reservacion_seleccionada
        )

        layout = QVBoxLayout(
            pagina
        )

        layout.addLayout(
            formulario
        )

        layout.addLayout(
            botones
        )

        layout.addLayout(
            busqueda
        )

        layout.addWidget(
            self.etiqueta_resultados
        )

        layout.addWidget(
            self.tabla_reservaciones
        )

        return pagina

    def _crear_tab_recurrente(
        self,
    ):
        pagina = QWidget()

        self.combo_estudiante_recurrente = (
            QComboBox()
        )

        self.combo_sala_recurrente = (
            QComboBox()
        )

        self.fecha_recurrente = QDateEdit(
            QDate.currentDate().addDays(
                1
            )
        )

        self.fecha_recurrente.setCalendarPopup(
            True
        )

        self.fecha_recurrente.setDisplayFormat(
            "yyyy-MM-dd"
        )

        self.combo_hora_recurrente = (
            QComboBox()
        )

        for hora in range(
            8,
            20,
        ):
            texto = f"{hora:02d}:00"

            self.combo_hora_recurrente.addItem(
                texto,
                texto,
            )

        self.combo_duracion_recurrente = (
            QComboBox()
        )

        self.combo_duracion_recurrente.addItem(
            "1 hora",
            1,
        )

        self.combo_duracion_recurrente.addItem(
            "2 horas",
            2,
        )

        self.personas_recurrente = QSpinBox()

        self.personas_recurrente.setRange(
            1,
            10000,
        )

        self.ocurrencias = QSpinBox()

        self.ocurrencias.setRange(
            2,
            8,
        )

        formulario = QFormLayout()

        formulario.addRow(
            "Estudiante:",
            self.combo_estudiante_recurrente,
        )

        formulario.addRow(
            "Sala:",
            self.combo_sala_recurrente,
        )

        formulario.addRow(
            "Fecha inicial:",
            self.fecha_recurrente,
        )

        formulario.addRow(
            "Hora:",
            self.combo_hora_recurrente,
        )

        formulario.addRow(
            "Duración:",
            self.combo_duracion_recurrente,
        )

        formulario.addRow(
            "Personas:",
            self.personas_recurrente,
        )

        formulario.addRow(
            "Ocurrencias:",
            self.ocurrencias,
        )

        boton_analizar = QPushButton(
            "Analizar serie"
        )

        boton_crear = QPushButton(
            "Crear serie"
        )

        boton_analizar.clicked.connect(
            self.analizar_serie
        )

        boton_crear.clicked.connect(
            self.crear_serie
        )

        botones = QHBoxLayout()

        botones.addWidget(
            boton_analizar
        )

        botones.addWidget(
            boton_crear
        )

        self.tabla_analisis = QTableWidget()

        configurar_tabla(
            self.tabla_analisis,
            [
                "#",
                "Fecha",
                "Hora",
                "Disponible",
                "Motivo",
            ],
        )

        self.serie_id = QSpinBox()

        self.serie_id.setRange(
            1,
            999999999,
        )

        self.numero_ocurrencia = QSpinBox()

        self.numero_ocurrencia.setRange(
            1,
            8,
        )

        boton_consultar = QPushButton(
            "Consultar serie"
        )

        boton_cancelar_una = QPushButton(
            "Cancelar ocurrencia"
        )

        boton_cancelar_futuras = QPushButton(
            "Cancelar posteriores"
        )

        boton_cancelar_desde = QPushButton(
            "Cancelar esta y posteriores"
        )

        boton_consultar.clicked.connect(
            self.consultar_serie
        )

        boton_cancelar_una.clicked.connect(
            self.cancelar_ocurrencia
        )

        boton_cancelar_futuras.clicked.connect(
            self.cancelar_futuras
        )

        boton_cancelar_desde.clicked.connect(
            self.cancelar_desde
        )

        gestion = QHBoxLayout()

        gestion.addWidget(
            QLabel(
                "Serie ID:"
            )
        )

        gestion.addWidget(
            self.serie_id
        )

        gestion.addWidget(
            QLabel(
                "Ocurrencia:"
            )
        )

        gestion.addWidget(
            self.numero_ocurrencia
        )

        gestion.addWidget(
            boton_consultar
        )

        gestion.addWidget(
            boton_cancelar_una
        )

        gestion.addWidget(
            boton_cancelar_futuras
        )

        gestion.addWidget(
            boton_cancelar_desde
        )

        self.tabla_ocurrencias = QTableWidget()

        configurar_tabla(
            self.tabla_ocurrencias,
            [
                "#",
                "ID reservación",
                "Fecha",
                "Hora inicio",
                "Hora fin",
                "Estado",
            ],
        )

        layout = QVBoxLayout(
            pagina
        )

        layout.addLayout(
            formulario
        )

        layout.addLayout(
            botones
        )

        layout.addWidget(
            QLabel(
                "Análisis previo"
            )
        )

        layout.addWidget(
            self.tabla_analisis
        )

        layout.addLayout(
            gestion
        )

        layout.addWidget(
            self.tabla_ocurrencias
        )

        return pagina

    def _cargar_combo_estudiantes(
        self,
        combo,
    ):
        dato_actual = combo.currentData()

        combo.clear()

        estudiantes = consultar_estudiantes(
            self.ruta_base_datos
        )

        for estudiante in estudiantes:
            combo.addItem(
                (
                    f"{estudiante.carne} - "
                    f"{estudiante.nombre} "
                    f"({estudiante.estado})"
                ),
                estudiante.carne,
            )

        if dato_actual is not None:
            seleccionar_combo_por_dato(
                combo,
                dato_actual,
            )

    def _cargar_combo_salas(
        self,
        combo,
    ):
        dato_actual = combo.currentData()

        combo.clear()

        salas = consultar_salas(
            self.ruta_base_datos
        )

        for sala in salas:
            combo.addItem(
                (
                    f"{sala.codigo} - "
                    f"{sala.nombre} "
                    f"({sala.estado})"
                ),
                sala.codigo,
            )

        if dato_actual is not None:
            seleccionar_combo_por_dato(
                combo,
                dato_actual,
            )

    def refrescar_opciones(
        self,
    ):
        self._cargar_combo_estudiantes(
            self.combo_estudiante
        )

        self._cargar_combo_estudiantes(
            self.combo_estudiante_recurrente
        )

        self._cargar_combo_salas(
            self.combo_sala
        )

        self._cargar_combo_salas(
            self.combo_sala_recurrente
        )

    def _cargar_reservaciones_tabla(
        self,
        reservaciones,
    ):
        """
        Carga el historial utilizando el
        identificador publico R0001.
        """

        cargar_tabla(
            self.tabla_reservaciones,
            reservaciones,
            [
                "identificador",
                "carne_estudiante",
                "codigo_sala",
                "fecha",
                "hora_inicio",
                "hora_fin",
                "duracion_horas",
                "cantidad_personas",
                "estado",
            ],
        )

    def refrescar_historial(
        self,
    ):
        reservaciones = (
            consultar_historial_reservaciones(
                self.ruta_base_datos
            )
        )

        self._cargar_reservaciones_tabla(
            reservaciones
        )

        self.etiqueta_resultados.setText(
            (
                "Historial de reservaciones: "
                f"{len(reservaciones)}"
            )
        )

    def refrescar(
        self,
    ):
        try:
            self.refrescar_opciones()

            self.refrescar_historial()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def nueva_reservacion(
        self,
    ):
        self.reservacion_id_seleccionada = None

        self.fecha_reserva.setDate(
            QDate.currentDate().addDays(
                1
            )
        )

        self.combo_hora.setCurrentIndex(
            0
        )

        self.combo_duracion.setCurrentIndex(
            0
        )

        self.cantidad_personas.setValue(
            1
        )

        self.tabla_reservaciones.clearSelection()

    def crear_reservacion(
        self,
    ):
        try:
            reservacion = crear_reservacion(
                carne_estudiante=(
                    self.combo_estudiante.currentData()
                ),
                codigo_sala=(
                    self.combo_sala.currentData()
                ),
                fecha=(
                    self.fecha_reserva.date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                ),
                hora_inicio=(
                    self.combo_hora.currentData()
                ),
                duracion_horas=(
                    self.combo_duracion.currentData()
                ),
                cantidad_personas=(
                    self.cantidad_personas.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            mostrar_exito(
                self,
                (
                    "Reservación creada "
                    "correctamente.\n\n"
                    "ID: "
                    f"{reservacion.identificador}"
                ),
            )

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def buscar_por_estudiante(
        self,
    ):
        carne = (
            self.campo_busqueda_carne
            .text()
            .strip()
        )

        if not carne:
            mostrar_error(
                self,
                ErrorValidacion(
                    (
                        "Ingrese el carné del "
                        "estudiante que desea buscar."
                    )
                ),
            )

            return

        try:
            reservaciones = (
                buscar_reservaciones_estudiante(
                    carne,
                    self.ruta_base_datos,
                )
            )

            self._cargar_reservaciones_tabla(
                reservaciones
            )

            if reservaciones:
                self.etiqueta_resultados.setText(
                    (
                        "Reservaciones encontradas "
                        f"para {carne.upper()}: "
                        f"{len(reservaciones)}"
                    )
                )

            else:
                self.etiqueta_resultados.setText(
                    (
                        "El estudiante "
                        f"{carne.upper()} no posee "
                        "reservaciones."
                    )
                )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def mostrar_todas_reservaciones(
        self,
    ):
        self.campo_busqueda_carne.clear()

        self.refrescar_historial()

    def cargar_reservacion_seleccionada(
        self,
        fila,
        columna,
    ):
        del columna

        try:
            item_id = (
                self.tabla_reservaciones.item(
                    fila,
                    0,
                )
            )

            if item_id is None:
                return

            self.reservacion_id_seleccionada = (
                item_id.text()
            )

            carne = (
                self.tabla_reservaciones.item(
                    fila,
                    1,
                ).text()
            )

            sala = (
                self.tabla_reservaciones.item(
                    fila,
                    2,
                ).text()
            )

            fecha = (
                self.tabla_reservaciones.item(
                    fila,
                    3,
                ).text()
            )

            hora = (
                self.tabla_reservaciones.item(
                    fila,
                    4,
                ).text()
            )

            duracion = int(
                self.tabla_reservaciones.item(
                    fila,
                    6,
                ).text()
            )

            personas = int(
                self.tabla_reservaciones.item(
                    fila,
                    7,
                ).text()
            )

            seleccionar_combo_por_dato(
                self.combo_estudiante,
                carne,
            )

            seleccionar_combo_por_dato(
                self.combo_sala,
                sala,
            )

            self.fecha_reserva.setDate(
                QDate.fromString(
                    fecha,
                    "yyyy-MM-dd",
                )
            )

            seleccionar_combo_por_dato(
                self.combo_hora,
                hora,
            )

            seleccionar_combo_por_dato(
                self.combo_duracion,
                duracion,
            )

            self.cantidad_personas.setValue(
                personas
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def modificar_reservacion(
        self,
    ):
        if self.reservacion_id_seleccionada is None:
            mostrar_error(
                self,
                ErrorValidacion(
                    "Seleccione una reservación."
                ),
            )

            return

        try:
            reservacion = modificar_reservacion(
                identificador=(
                    self.reservacion_id_seleccionada
                ),
                carne_estudiante=(
                    self.combo_estudiante.currentData()
                ),
                codigo_sala=(
                    self.combo_sala.currentData()
                ),
                fecha=(
                    self.fecha_reserva.date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                ),
                hora_inicio=(
                    self.combo_hora.currentData()
                ),
                duracion_horas=(
                    self.combo_duracion.currentData()
                ),
                cantidad_personas=(
                    self.cantidad_personas.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            mostrar_exito(
                self,
                (
                    "Reservación modificada.\n\n"
                    "ID: "
                    f"{reservacion.identificador}"
                ),
            )

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def cancelar_reservacion(
        self,
    ):
        if self.reservacion_id_seleccionada is None:
            mostrar_error(
                self,
                ErrorValidacion(
                    "Seleccione una reservación."
                ),
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar cancelación",
            (
                "¿Desea cancelar la reservación "
                f"{self.reservacion_id_seleccionada}?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            respuesta
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            reservacion = cancelar_reservacion(
                self.reservacion_id_seleccionada,
                self.ruta_base_datos,
            )

            mostrar_exito(
                self,
                (
                    "Reservación cancelada.\n\n"
                    "ID: "
                    f"{reservacion.identificador}"
                ),
            )

            self.reservacion_id_seleccionada = None

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def analizar_serie(
        self,
    ):
        try:
            resumen = analizar_serie_recurrente(
                carne_estudiante=(
                    self.combo_estudiante_recurrente
                    .currentData()
                ),
                codigo_sala=(
                    self.combo_sala_recurrente
                    .currentData()
                ),
                fecha_inicio=(
                    self.fecha_recurrente.date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                ),
                hora_inicio=(
                    self.combo_hora_recurrente
                    .currentData()
                ),
                duracion_horas=(
                    self.combo_duracion_recurrente
                    .currentData()
                ),
                cantidad_personas=(
                    self.personas_recurrente.value()
                ),
                cantidad_ocurrencias=(
                    self.ocurrencias.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            filas = []

            for ocurrencia in resumen[
                "ocurrencias"
            ]:
                filas.append(
                    {
                        "numero":
                            ocurrencia["numero"],

                        "fecha":
                            ocurrencia["fecha"],

                        "hora":
                            ocurrencia["hora_inicio"],

                        "disponible":
                            (
                                "Sí"
                                if ocurrencia[
                                    "disponible"
                                ]
                                else "No"
                            ),

                        "motivo":
                            (
                                ocurrencia["motivo"]
                                or ""
                            ),
                    }
                )

            cargar_tabla(
                self.tabla_analisis,
                filas,
                [
                    "numero",
                    "fecha",
                    "hora",
                    "disponible",
                    "motivo",
                ],
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def crear_serie(
        self,
    ):
        try:
            resultado = crear_serie_recurrente(
                carne_estudiante=(
                    self.combo_estudiante_recurrente
                    .currentData()
                ),
                codigo_sala=(
                    self.combo_sala_recurrente
                    .currentData()
                ),
                fecha_inicio=(
                    self.fecha_recurrente.date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                ),
                hora_inicio=(
                    self.combo_hora_recurrente
                    .currentData()
                ),
                duracion_horas=(
                    self.combo_duracion_recurrente
                    .currentData()
                ),
                cantidad_personas=(
                    self.personas_recurrente.value()
                ),
                cantidad_ocurrencias=(
                    self.ocurrencias.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            self.serie_id.setValue(
                resultado["serie_id"]
            )

            mostrar_exito(
                self,
                (
                    "Serie recurrente creada. "
                    f"ID: {resultado['serie_id']}"
                ),
            )

            self.consultar_serie()

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def consultar_serie(
        self,
    ):
        try:
            ocurrencias = consultar_ocurrencias_serie(
                self.serie_id.value(),
                self.ruta_base_datos,
            )

            filas = []

            for ocurrencia in ocurrencias:
                reservacion = (
                    ocurrencia["reservacion"]
                )

                filas.append(
                    {
                        "numero":
                            ocurrencia[
                                "numero_ocurrencia"
                            ],

                        "identificador":
                            reservacion.identificador,

                        "fecha":
                            reservacion.fecha,

                        "hora_inicio":
                            reservacion.hora_inicio,

                        "hora_fin":
                            reservacion.hora_fin,

                        "estado":
                            reservacion.estado,
                    }
                )

            cargar_tabla(
                self.tabla_ocurrencias,
                filas,
                [
                    "numero",
                    "identificador",
                    "fecha",
                    "hora_inicio",
                    "hora_fin",
                    "estado",
                ],
            )

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def cancelar_ocurrencia(
        self,
    ):
        try:
            cancelar_ocurrencia_recurrente(
                serie_id=(
                    self.serie_id.value()
                ),
                numero_ocurrencia=(
                    self.numero_ocurrencia.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
            )

            self.consultar_serie()

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def cancelar_futuras(
        self,
    ):
        try:
            cancelar_ocurrencias_futuras(
                serie_id=(
                    self.serie_id.value()
                ),
                numero_ocurrencia_desde=(
                    self.numero_ocurrencia.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
                incluir_seleccionada=False,
            )

            self.consultar_serie()

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )

    def cancelar_desde(
        self,
    ):
        try:
            cancelar_ocurrencias_futuras(
                serie_id=(
                    self.serie_id.value()
                ),
                numero_ocurrencia_desde=(
                    self.numero_ocurrencia.value()
                ),
                ruta_base_datos=(
                    self.ruta_base_datos
                ),
                incluir_seleccionada=True,
            )

            self.consultar_serie()

            self.refrescar()

            self.datos_cambiados.emit()

        except Exception as error:
            mostrar_error(
                self,
                error,
            )