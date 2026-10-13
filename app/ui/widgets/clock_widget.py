from datetime import datetime
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import QTimer, Qt
from ...core.i18n import i18n
from .draggable import DualActionLabel
from .page import PageWidget

class ClockWidget(PageWidget):
    """
    Widget de reloj que muestra la hora y fecha actual.
    Soporta formato de 12 y 24 horas y escala su tipografía según el tamaño del widget.
    Soporta cambio dinámico de idioma (Español / Inglés).
    """
    PAGE_ID = "clock"
    ICON = "🕒"
    TITLE_KEY = "tab_clock"
    TRAY_KEY = "tray_clock"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_24h = True
        self.init_ui()
        self.init_timer()
        self.update_time()
        i18n.subscribe(self.retranslate_ui)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta de la hora (con soporte dual: clic para alternar formato, arrastre para mover)
        self.time_label = DualActionLabel("", self, on_click=self.toggle_format)
        self.time_label.setProperty("class", "TimeDisplay")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setCursor(Qt.CursorShape.PointingHandCursor)

        # Etiqueta de la fecha
        self.date_label = QLabel(self)
        self.date_label.setProperty("class", "DateDisplay")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Formato (indicador discreto)
        self.format_indicator = QLabel(self)
        self.format_indicator.setProperty("class", "SecondaryText")
        self.format_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Efectos de opacidad para apariciones y desvanecimientos suaves
        self.date_opacity_eff = QGraphicsOpacityEffect(self.date_label)
        self.date_label.setGraphicsEffect(self.date_opacity_eff)
        self.format_opacity_eff = QGraphicsOpacityEffect(self.format_indicator)
        self.format_indicator.setGraphicsEffect(self.format_opacity_eff)

        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        layout.addWidget(self.format_indicator)
        layout.addStretch()

        self.retranslate_ui()

    def retranslate_ui(self):
        self.time_label.setToolTip(i18n.t("clock_click_tooltip"))
        if self.is_24h:
            self.format_indicator.setText(i18n.t("clock_24h_hint"))
        else:
            self.format_indicator.setText(i18n.t("clock_12h_hint"))
        self.update_time()

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(500)

    def toggle_format(self, event=None):
        self.is_24h = not self.is_24h
        self.retranslate_ui()


    def update_time(self):
        now = datetime.now()
        if self.is_24h:
            time_str = now.strftime("%H:%M:%S")
        else:
            time_str = now.strftime("%I:%M:%S %p")

        # Nombres de días y meses traducidos
        dias = i18n.t("days")
        meses = i18n.t("months")
        dia_semana = dias[now.weekday()]
        mes_nombre = meses[now.month - 1]
        date_str = f"{dia_semana}, {now.day} {mes_nombre} {now.year}"


        self.time_label.setText(time_str)
        self.date_label.setText(date_str)

    def set_secondary_opacity(self, opacity: float):
        """Ajusta la opacidad de los elementos secundarios (fecha y formato) durante transiciones."""
        self.date_opacity_eff.setOpacity(opacity)
        self.format_opacity_eff.setOpacity(opacity)

    def set_mini_mode(self, enabled: bool):
        self.date_label.setVisible(not enabled)
        self.format_indicator.setVisible(not enabled)
        if enabled:
            self.layout().setContentsMargins(4, 2, 4, 2)
        else:
            self.layout().setContentsMargins(10, 10, 10, 10)
        self.update_time()
        super().set_mini_mode(enabled)

    def update_fonts(self):
        """Ajusta proporcionalmente el tamaño de fuente según el tamaño de la ventana."""
        if self.is_mini_mode:
            font_size = 24
        else:
            base_size = min(self.width(), self.height())
            font_size = max(20, min(30, int(base_size / 7.2)))

        font = self.time_label.font()
        font.setPointSize(font_size)
        font.setBold(True)
        self.time_label.setFont(font)

        if not self.is_mini_mode:
            date_font_size = max(10, int(font_size / 2.6))
            d_font = self.date_label.font()
            d_font.setPointSize(date_font_size)
            self.date_label.setFont(d_font)
