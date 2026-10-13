"""
Vista del temporizador. La lógica de la cuenta regresiva vive en core/timer_model.py;
este widget solo traduce las acciones del usuario a llamadas al modelo y refleja
su estado (textos, colores, alarma visual y sonora).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import QTimer, Qt
from ...core.config import config
from ...core.i18n import i18n
from ...core.timer_model import TimerModel, TimerState
from ...services.sounds import AlarmPlayer
from ..styles import apply_state
from .draggable import DualActionLabel
from .page import PageWidget
from .time_setup_dialog import TimeSetupDialog

# Botones rápidos de preajustes
PRESETS = [("+1m", 60), ("+5m", 300), ("+15m", 900), ("+25m", 1500), ("+1h", 3600)]
FLASH_INTERVAL_MS = 400


class TimerWidget(PageWidget):
    """
    Widget de temporizador configurable con inicio, pausa, reinicio,
    preajustes rápidos y alarma visual/sonora al finalizar.
    """
    PAGE_ID = "timer"
    ICON = "⏳"
    TITLE_KEY = "tab_timer"
    TRAY_KEY = "tray_timer"

    def __init__(self, parent=None, alarm_player=None):
        super().__init__(parent)
        self.model = TimerModel(self)
        self.alarm_player = alarm_player or AlarmPlayer(self)
        self.flash_state = False
        self.alarm_count = 0
        self._status_key = "timer_hint_idle"

        self.alarm_timer = QTimer(self)
        self.alarm_timer.setInterval(FLASH_INTERVAL_MS)
        self.alarm_timer.timeout.connect(self.flash_alarm)

        self.init_ui()
        self.model.time_changed.connect(self.update_display)
        self.model.state_changed.connect(self._render_controls)
        self.model.finished.connect(self._on_finished)
        self.update_display()
        i18n.subscribe(self.retranslate_ui)

    # ------------------------------------------------------------------ UI
    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_normal_view())
        root_layout.addWidget(self._build_mini_view())
        self.retranslate_ui()

    def _build_normal_view(self):
        self.view_normal = QWidget(self)
        self.normal_opacity_eff = QGraphicsOpacityEffect(self.view_normal)
        self.normal_opacity_eff.setOpacity(1.0)
        self.view_normal.setGraphicsEffect(self.normal_opacity_eff)

        normal_layout = QVBoxLayout(self.view_normal)
        normal_layout.setContentsMargins(10, 6, 10, 6)
        normal_layout.setSpacing(4)
        normal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones rápidos de preajustes (+1m, +5m, +15m, +25m, +1h)
        self.presets_widget = QWidget(self.view_normal)
        self.presets_layout = QHBoxLayout(self.presets_widget)
        self.presets_layout.setContentsMargins(0, 0, 0, 0)
        self.presets_layout.setSpacing(4)
        self.presets_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for label, secs in PRESETS:
            btn = QPushButton(label, self.presets_widget)
            btn.setProperty("class", "PresetButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=secs: self.add_time(s))
            self.presets_layout.addWidget(btn)
        normal_layout.addWidget(self.presets_widget)

        # Pantalla con el tiempo restante (efecto dual: clic para configurar, arrastre para mover)
        self.time_label = DualActionLabel("", self.view_normal, on_click=self.open_setup_dialog)
        self.time_label.setProperty("class", "TimeDisplay")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setCursor(Qt.CursorShape.PointingHandCursor)
        normal_layout.addWidget(self.time_label)

        # Subtítulo de estado
        self.status_label = QLabel(self.view_normal)
        self.status_label.setProperty("class", "SecondaryText")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        normal_layout.addWidget(self.status_label)

        # Controles principales: Iniciar/Pausar, Reiniciar y Borrar/Papelera (iconos puros)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_toggle = self._make_button("▶", "PrimaryAction", self.view_normal, self.toggle_timer)
        self.btn_reset = self._make_button("↺", "SecondaryAction", self.view_normal, self.reset_timer)
        self.btn_clear = self._make_button("🗑", "SecondaryAction", self.view_normal, self.clear_time)
        controls_layout.addWidget(self.btn_toggle)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(self.btn_clear)
        normal_layout.addLayout(controls_layout)
        return self.view_normal

    def _build_mini_view(self):
        """Vista Mini-HUD (horizontal compacta)."""
        self.view_mini = QWidget(self)
        self.view_mini.hide()
        mini_layout = QHBoxLayout(self.view_mini)
        mini_layout.setContentsMargins(10, 2, 10, 2)
        mini_layout.setSpacing(10)
        mini_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón Play/Pause circular compacto
        self.btn_mini_toggle = self._make_button("▶", "MiniAction", self.view_mini, self.toggle_timer)
        mini_layout.addWidget(self.btn_mini_toggle)

        # Tiempo centrado (efecto dual: clic para pausar/reanudar, arrastre para mover)
        self.mini_time_label = DualActionLabel("", self.view_mini, on_click=self.toggle_timer)
        self.mini_time_label.setProperty("class", "TimeDisplay")
        self.mini_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mini_time_label.setCursor(Qt.CursorShape.PointingHandCursor)
        mini_layout.addWidget(self.mini_time_label, 1)

        # Botón Reset circular compacto
        self.btn_mini_reset = self._make_button("↺", "MiniReset", self.view_mini, self.reset_timer)
        mini_layout.addWidget(self.btn_mini_reset)
        return self.view_mini

    @staticmethod
    def _make_button(text, css_class, parent, slot):
        btn = QPushButton(text, parent)
        btn.setProperty("class", css_class)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def retranslate_ui(self):
        self.time_label.setToolTip(i18n.t("timer_click_tooltip"))
        self.btn_reset.setToolTip(i18n.t("btn_reset"))
        self.btn_clear.setToolTip(i18n.t("btn_clear_tooltip"))
        self.btn_mini_toggle.setToolTip(i18n.t("mini_toggle_tooltip"))
        self.mini_time_label.setToolTip(i18n.t("mini_time_tooltip"))
        self.btn_mini_reset.setToolTip(i18n.t("btn_reset"))
        self.status_label.setText(i18n.t(self._status_key))
        self._render_controls()

    # ------------------------------------------------------ render del estado
    def _set_status(self, key):
        self._status_key = key
        self.status_label.setText(i18n.t(key))

    def _render_controls(self, _state=None):
        """Refleja el estado del modelo en los botones y en el color del tiempo."""
        state = self.model.state
        running = state == TimerState.RUNNING
        icon = "⏸" if running else "▶"
        tooltip = {TimerState.RUNNING: "btn_pause", TimerState.PAUSED: "btn_resume"}.get(state, "btn_start")

        self.btn_toggle.setText(icon)
        self.btn_toggle.setToolTip(i18n.t(tooltip))
        self.btn_mini_toggle.setText(icon)

        visual = "running" if running else ""
        apply_state(self.btn_toggle, visual)
        apply_state(self.btn_mini_toggle, visual)
        if not self.alarm_timer.isActive():
            self._set_time_labels_state(visual)

    def _set_time_labels_state(self, state):
        apply_state(self.time_label, state)
        apply_state(self.mini_time_label, state)

    def update_display(self, _remaining=None):
        text = self.model.text()
        old_text = self.mini_time_label.text()
        self.time_label.setText(text)
        self.mini_time_label.setText(text)

        # Si cambió el formato (ej. de MM:SS a HH:MM:SS o viceversa), reajustar fuente al instante
        if len(text) != len(old_text):
            self.refresh_fonts()

    # ------------------------------------------------- acciones del usuario
    def add_time(self, seconds):
        self.stop_alarm()
        self.model.add_time(seconds)
        if not self.model.is_running:
            self._set_status("timer_hint_idle")

    def clear_time(self):
        self.stop_alarm()
        self.model.clear()
        self._set_status("timer_hint_idle")

    def open_setup_dialog(self, event=None):
        if self.model.is_running:
            return
        dialog = TimeSetupDialog(self.model.remaining_seconds, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.stop_alarm()
            self.model.set_time(dialog.get_total_seconds())
            self._set_status("timer_hint_idle")

    def toggle_timer(self):
        if self.alarm_timer.isActive():
            self.stop_alarm()
            return

        if self.model.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if not self.model.start():
            self.open_setup_dialog()
            return
        self._set_status("timer_hint_running")

    def pause_timer(self):
        self.model.pause()
        self._set_status("timer_hint_paused")

    def reset_timer(self):
        self.stop_alarm()
        self.model.reset()
        self._set_status("timer_hint_idle")

    def on_primary_action(self):
        """Barra espaciadora: inicia / pausa."""
        self.toggle_timer()

    # --------------------------------------------------------------- alarma
    def _on_finished(self):
        self._set_status("timer_hint_finished")
        self.alarm_count = 0
        self.alarm_timer.start()
        # Sonido configurable (config.ini → [alarm] sound / volume / duration)
        self.alarm_player.play_alarm()

    def flash_alarm(self):
        self.alarm_count += 1
        self.flash_state = not self.flash_state
        if self.flash_state:
            self._set_time_labels_state("alarm")
            self.alarm_player.on_flash()
        else:
            self._set_time_labels_state("")

        # Detener el parpadeo automáticamente al cumplirse la duración configurada.
        # El sonido no se corta: termina su última repetición de forma natural.
        max_flashes = max(2, round(config.get("alarm.duration") * 1000 / self.alarm_timer.interval()))
        if self.alarm_count >= max_flashes:
            self.stop_alarm(silence=False)

    def stop_alarm(self, silence=True):
        if self.alarm_timer.isActive():
            self.alarm_timer.stop()
            if silence:
                self.alarm_player.stop()
            self._set_time_labels_state("")
            self._set_status("timer_hint_ready")

    # ------------------------------------------------------ Mini-HUD / fuentes
    def set_secondary_opacity(self, opacity: float):
        """Ajusta la opacidad de los controles normales del temporizador durante transiciones."""
        self.normal_opacity_eff.setOpacity(opacity)

    def set_mini_mode(self, enabled: bool):
        self.view_normal.setVisible(not enabled)
        self.view_mini.setVisible(enabled)
        super().set_mini_mode(enabled)

    def update_fonts(self):
        """Ajusta proporcionalmente el tamaño de fuente según el tamaño de la ventana."""
        if self.is_mini_mode:
            label = self.mini_time_label
            font_size = 20 if len(label.text()) > 5 else 24
        else:
            label = self.time_label
            font_size = max(22, min(32, int(min(self.width(), self.height()) / 6.5)))
        font = label.font()
        font.setPointSize(font_size)
        font.setBold(True)
        label.setFont(font)
