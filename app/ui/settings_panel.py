"""
Panel desplegable de ajustes: opacidad, idioma y sonido de alarma.

Lee y escribe directamente en config.ini y se sincroniza si el archivo se
edita a mano. Para añadir un ajuste nuevo: crea su fila en un método
_build_*_row() y añádela en __init__.
"""
import os

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from ..core.config import config
from ..core.i18n import i18n

OPACITY_MIN = 30
OPACITY_MAX = 100

# Sonidos disponibles en el selector del panel (el valor 'custom' solo aparece si hay ruta en config.ini)
SOUND_CHOICES = ("chime", "bell", "digital", "soft", "system", "none")


class SettingsPanel(QWidget):
    opacity_changed = pyqtSignal(int)    # Porcentaje 30-100
    preview_requested = pyqtSignal()     # Probar el sonido de alarma

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPanel")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)
        layout.addLayout(self._build_opacity_row())
        layout.addLayout(self._build_language_row())
        layout.addLayout(self._build_sound_row())

        # Restaurar preferencias persistidas y escuchar cambios hechos a mano en config.ini
        self.opacity_slider.setValue(config.get("general.opacity"))
        self.retranslate_ui()
        i18n.subscribe(self.retranslate_ui)
        config.changed.connect(self._on_config_changed)

    # ---------------------------------------------------------------- filas
    def _build_opacity_row(self):
        row = QHBoxLayout()
        row.setSpacing(4)
        self.lbl_op = QLabel(self)
        self.lbl_op.setObjectName("OpacityLabel")

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity_slider.setRange(OPACITY_MIN, OPACITY_MAX)
        self.opacity_slider.setValue(OPACITY_MAX)
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)

        self.lbl_opacity_value = QLabel("100%", self)
        self.lbl_opacity_value.setObjectName("OpacityValue")

        row.addWidget(self.lbl_op)
        row.addWidget(self.opacity_slider, 1)
        row.addWidget(self.lbl_opacity_value)
        for value in (50, 75, 100):
            btn = QPushButton(f"{value}%", self)
            btn.setProperty("class", "OpacityPreset")
            btn.clicked.connect(lambda _=False, v=value: self.opacity_slider.setValue(v))
            row.addWidget(btn)
        return row

    def _build_language_row(self):
        row = QHBoxLayout()
        row.setSpacing(6)
        self.lbl_lang_setting = QLabel(self)
        self.lbl_lang_setting.setObjectName("SettingsLabel")
        row.addWidget(self.lbl_lang_setting)
        row.addStretch()

        self.lang_buttons = {}
        for code, name in (("es", "Español"), ("en", "English")):
            btn = QPushButton(name, self)
            btn.setProperty("class", "LangButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, c=code: self._switch_language(c))
            row.addWidget(btn)
            self.lang_buttons[code] = btn
        return row

    def _build_sound_row(self):
        """Sonido de alarma (selector + probar) y acceso a config.ini."""
        row = QHBoxLayout()
        row.setSpacing(4)
        self.lbl_sound_setting = QLabel(self)
        self.lbl_sound_setting.setObjectName("SettingsLabel")

        self.sound_combo = QComboBox(self)
        self.sound_combo.setObjectName("SoundCombo")
        self.sound_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sound_combo.activated.connect(self._on_sound_selected)

        self.btn_sound_preview = QPushButton("▶", self)
        self.btn_sound_preview.setProperty("class", "OpacityPreset")
        self.btn_sound_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sound_preview.clicked.connect(self.preview_requested.emit)

        self.btn_open_config = QPushButton("…", self)
        self.btn_open_config.setProperty("class", "OpacityPreset")
        self.btn_open_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_config.clicked.connect(self.open_config_file)

        row.addWidget(self.lbl_sound_setting)
        row.addWidget(self.sound_combo, 1)
        row.addWidget(self.btn_sound_preview)
        row.addWidget(self.btn_open_config)
        return row

    # ------------------------------------------------------------- opacidad
    def opacity(self):
        return self.opacity_slider.value()

    def set_opacity(self, value):
        self.opacity_slider.setValue(max(OPACITY_MIN, min(OPACITY_MAX, value)))

    def _on_opacity_slider_changed(self, value):
        self.lbl_opacity_value.setText(f"{value}%")
        config.set("general.opacity", value)
        self.opacity_changed.emit(value)

    # ---------------------------------------------------------------- idioma
    def _switch_language(self, lang):
        i18n.set_lang(lang)
        self._update_language_buttons()

    def _update_language_buttons(self):
        current = i18n.get_lang()
        for code, btn in self.lang_buttons.items():
            btn.setChecked(code == current)

    # ---------------------------------------------------------------- sonido
    def _populate_sound_combo(self):
        """Rellena el selector de sonido con textos traducidos y la opción actual seleccionada."""
        choices = list(SOUND_CHOICES)
        if config.get("alarm.custom_sound") or config.get("alarm.sound") == "custom":
            choices.append("custom")
        self.sound_combo.blockSignals(True)
        self.sound_combo.clear()
        for value in choices:
            self.sound_combo.addItem(i18n.t(f"sound_{value}"), value)
        idx = self.sound_combo.findData(config.get("alarm.sound"))
        self.sound_combo.setCurrentIndex(max(0, idx))
        self.sound_combo.blockSignals(False)

    def _on_sound_selected(self, index):
        value = self.sound_combo.itemData(index)
        if value:
            config.set("alarm.sound", value)
            self.preview_requested.emit()

    def open_config_file(self):
        """Abre config.ini con el editor predeterminado del sistema (opciones avanzadas)."""
        config.flush()
        if not os.path.exists(config.path):
            config.save()
        QDesktopServices.openUrl(QUrl.fromLocalFile(config.path))

    # ------------------------------------------------------- sincronización
    def _on_config_changed(self, key):
        """Sincroniza el panel cuando config.ini cambia (desde el panel o editado a mano)."""
        if key == "general.opacity":
            if self.opacity_slider.value() != config.get("general.opacity"):
                self.opacity_slider.setValue(config.get("general.opacity"))
        elif key in ("alarm.sound", "alarm.custom_sound"):
            self._populate_sound_combo()

    def retranslate_ui(self):
        self._update_language_buttons()
        self.lbl_op.setText(i18n.t("opacity_lbl"))
        self.lbl_lang_setting.setText(i18n.t("lang_label"))
        self.lbl_sound_setting.setText(i18n.t("sound_label"))
        self.btn_sound_preview.setToolTip(i18n.t("sound_preview"))
        self.btn_open_config.setToolTip(f"{i18n.t('open_config')}\n{config.path}")
        self._populate_sound_combo()
