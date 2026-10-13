"""
Barra de título: pestañas de páginas + controles de ventana (pin, ajustes, Mini-HUD, cerrar).

Solo emite señales; la ventana decide qué hacer con ellas.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ..core.i18n import i18n
from .widgets.draggable import DraggableTabButton


class TitleBar(QWidget):
    tab_selected = pyqtSignal(str)       # PAGE_ID
    pin_toggled = pyqtSignal(bool)
    settings_toggled = pyqtSignal(bool)
    mini_hud_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self._tabs = {}          # PAGE_ID -> (botón, clave i18n del tooltip)
        self._mini_mode = False
        self._pinned = True
        self._opacity = 100

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        # Pestañas (se rellenan con add_tab)
        self._tabs_layout = QHBoxLayout()
        self._tabs_layout.setSpacing(4)
        layout.addLayout(self._tabs_layout)
        layout.addStretch()

        # Botón Pin (Always on top toggle)
        self.btn_pin = self._control("📌", "PinButton", checkable=True)
        self.btn_pin.setChecked(True)
        self.btn_pin.clicked.connect(self._on_pin_clicked)

        # Botón Ajustes (Opacidad, Idioma y Sonido)
        self.btn_settings = self._control("⚙", "SettingsButton", checkable=True)
        self.btn_settings.clicked.connect(self.settings_toggled.emit)

        # Botón Modo Mini-HUD / Enfoque (anclado a la derecha junto al botón cerrar)
        self.btn_mini_hud = self._control("↙", "MiniHudButton")
        self.btn_mini_hud.clicked.connect(self.mini_hud_clicked.emit)

        # Botón Cerrar
        self.btn_close = self._control("✕", "CloseButton")
        self.btn_close.clicked.connect(self.close_clicked.emit)

        for btn in (self.btn_pin, self.btn_settings, self.btn_mini_hud, self.btn_close):
            layout.addWidget(btn)

        self.retranslate_ui()
        i18n.subscribe(self.retranslate_ui)

    def _control(self, text, object_name, checkable=False):
        btn = QPushButton(text, self)
        btn.setProperty("class", "WindowControl")
        btn.setObjectName(object_name)
        btn.setCheckable(checkable)
        return btn

    # ------------------------------------------------------------ pestañas
    def add_tab(self, page_id, icon, title_key):
        """Crea el botón de pestaña de una página y lo devuelve."""
        btn = DraggableTabButton(icon, self)
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(i18n.t(title_key))
        btn.clicked.connect(lambda _=False, pid=page_id: self.tab_selected.emit(pid))
        self._tabs_layout.addWidget(btn)
        self._tabs[page_id] = (btn, title_key)
        return btn

    def set_current_tab(self, page_id):
        for pid, (btn, _key) in self._tabs.items():
            btn.setChecked(pid == page_id)

    # ---------------------------------------------------------------- estado
    def set_mini_mode(self, enabled):
        """En modo mini: flecha ↗ para expandir; en modo normal: ↙ para contraer."""
        self._mini_mode = enabled
        self.btn_mini_hud.setText("↗" if enabled else "↙")
        self.btn_mini_hud.setToolTip(i18n.t("mini_hud_expand" if enabled else "mini_hud_shrink"))

    def set_opacity_hint(self, value):
        self._opacity = value
        self.setToolTip(f"{i18n.t('opacity_tooltip', value=value)} • {i18n.t('title_tooltip')}")

    def close_settings(self):
        self.btn_settings.setChecked(False)

    def _on_pin_clicked(self, checked):
        self._pinned = checked
        self._update_pin_tooltip()
        self.pin_toggled.emit(checked)

    def _update_pin_tooltip(self):
        self.btn_pin.setToolTip(i18n.t("pin_on" if self._pinned else "pin_off"))

    def retranslate_ui(self):
        for btn, key in self._tabs.values():
            btn.setToolTip(i18n.t(key))
        self._update_pin_tooltip()
        self.set_mini_mode(self._mini_mode)
        self.btn_settings.setToolTip(i18n.t("settings_btn"))
        self.btn_close.setToolTip(i18n.t("close"))
        self.set_opacity_hint(self._opacity)
