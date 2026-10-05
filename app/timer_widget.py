import subprocess
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDialog, QSpinBox, QApplication,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import QTimer, Qt
from .i18n import i18n
from .config import config
from .sounds import AlarmPlayer
from .draggable_widgets import DualActionLabel

class TimeSetupDialog(QDialog):
    """Diálogo modal moderno para configurar minutos y segundos con precisión."""
    def __init__(self, current_seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("dialog_title"))
        self.setFixedSize(300, 270)

        self.setStyleSheet("""
            QDialog {
                background-color: #14141c;
                color: #ffffff;
                border-radius: 16px;
                border: 1.5px solid #2d2d3f;
            }
            QLabel.SectionTitle {
                color: #8c8ca8;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            /* Stepper Card unificado */
            QWidget.StepperCard {
                background-color: #1c1c28;
                border: 1.5px solid #2f2f44;
                border-radius: 12px;
            }
            QSpinBox {
                background-color: transparent;
                color: #00d2ff;
                border: none;
                font-size: 30px;
                font-weight: 800;
                font-family: 'Monospace', 'Consolas', 'DejaVu Sans Mono';
                qproperty-alignment: AlignCenter;
                min-width: 80px;
                max-width: 80px;
                min-height: 44px;
            }
            QPushButton.StepperBtn {
                background-color: transparent;
                color: #7b7b99;
                border: none;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
                max-width: 80px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton.StepperBtn:hover {
                color: #00d2ff;
                background-color: #262638;
            }
            QPushButton.StepperBtn#BtnUp {
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QPushButton.StepperBtn#BtnDown {
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            /* Chips de presets rápidos */
            QPushButton.PresetChip {
                background-color: #1a1a26;
                color: #9090aa;
                border: 1px solid #2a2a3c;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 8px;
            }
            QPushButton.PresetChip:hover {
                background-color: #252538;
                color: #00d2ff;
                border-color: #00d2ff55;
            }
            /* Botón Aceptar primario */
            QPushButton#BtnOk {
                background-color: #00d2ff;
                color: #0a0e17;
                font-weight: 700;
                font-size: 12px;
                border: none;
                border-radius: 8px;
                padding: 7px 18px;
            }
            QPushButton#BtnOk:hover {
                background-color: #38e1ff;
            }
            /* Botón Cancelar secundario */
            QPushButton#BtnCancel {
                background-color: #222230;
                color: #c0c0d4;
                font-weight: 600;
                font-size: 12px;
                border: 1px solid #333346;
                border-radius: 8px;
                padding: 7px 16px;
            }
            QPushButton#BtnCancel:hover {
                background-color: #2a2a3e;
                color: #ffffff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Contenedor de diales (Minutos y Segundos)
        dials_layout = QHBoxLayout()
        dials_layout.setSpacing(12)
        dials_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_stepper(title, max_val, cur_val):
            container = QVBoxLayout()
            container.setSpacing(4)
            container.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl = QLabel(title)
            lbl.setProperty("class", "SectionTitle")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(lbl)

            card = QWidget()
            card.setProperty("class", "StepperCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)

            btn_up = QPushButton("▲")
            btn_up.setObjectName("BtnUp")
            btn_up.setProperty("class", "StepperBtn")
            btn_up.setAutoRepeat(True)
            btn_up.setAutoRepeatDelay(280)
            btn_up.setAutoRepeatInterval(70)

            spin = QSpinBox()
            spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.setRange(0, max_val)
            spin.setValue(cur_val)

            btn_down = QPushButton("▼")
            btn_down.setObjectName("BtnDown")
            btn_down.setProperty("class", "StepperBtn")
            btn_down.setAutoRepeat(True)
            btn_down.setAutoRepeatDelay(280)
            btn_down.setAutoRepeatInterval(70)

            btn_up.clicked.connect(spin.stepUp)
            btn_down.clicked.connect(spin.stepDown)

            card_layout.addWidget(btn_up)
            card_layout.addWidget(spin)
            card_layout.addWidget(btn_down)

            container.addWidget(card)
            return container, spin

        min_title = i18n.t("dialog_min").upper().replace(":", "")
        sec_title = i18n.t("dialog_sec").upper().replace(":", "")

        min_layout, self.spin_min = create_stepper(min_title, 999, current_seconds // 60)
        sec_layout, self.spin_sec = create_stepper(sec_title, 59, current_seconds % 60)

        sep_label = QLabel(":")
        sep_label.setStyleSheet("color: #4a4a66; font-size: 30px; font-weight: bold; margin-top: 14px;")
        sep_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dials_layout.addLayout(min_layout)
        dials_layout.addWidget(sep_label)
        dials_layout.addLayout(sec_layout)
        layout.addLayout(dials_layout)

        # Chips de presets rápidos
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for text, m in [("+1m", 1), ("+5m", 5), ("+15m", 15), ("00:00", 0)]:
            chip = QPushButton(text)
            chip.setProperty("class", "PresetChip")
            if m == 0:
                chip.clicked.connect(lambda: (self.spin_min.setValue(0), self.spin_sec.setValue(0)))
            else:
                chip.clicked.connect(lambda _, mins=m: self.spin_min.setValue(self.spin_min.value() + mins))
            chips_layout.addWidget(chip)
        layout.addLayout(chips_layout)

        # Botones de Acción (Aceptar / Cancelar)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        btn_cancel = QPushButton(i18n.t("dialog_cancel"))
        btn_cancel.setObjectName("BtnCancel")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton(i18n.t("dialog_ok"))
        btn_ok.setObjectName("BtnOk")
        btn_ok.clicked.connect(self.accept)

        actions_layout.addWidget(btn_cancel)
        actions_layout.addWidget(btn_ok)
        layout.addLayout(actions_layout)

    def get_total_seconds(self):
        return (self.spin_min.value() * 60) + self.spin_sec.value()


class TimerWidget(QWidget):
    """
    Widget de temporizador configurable con inicio, pausa, reinicio,
    preajustes rápidos y alarma visual/sonora al finalizar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initial_seconds = 0  # Inicia en 00:00 por defecto
        self.remaining_seconds = 0
        self.is_running = False
        self.flash_state = False
        self.alarm_player = AlarmPlayer(self)

        self.init_ui()
        self.init_timers()
        self.update_display()
        i18n.subscribe(self.retranslate_ui)
        # Precargar el sonido tras mostrar la ventana para no retrasar el arranque
        QTimer.singleShot(0, self.alarm_player.prepare)
        config.changed.connect(self._on_config_changed)

    def _on_config_changed(self, key):
        if key in ("alarm.sound", "alarm.custom_sound"):
            self.alarm_player.prepare()


    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- VISTA NORMAL ---
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

        presets = [("+1m", 60), ("+5m", 300), ("+15m", 900), ("+25m", 1500), ("+1h", 3600)]
        for label, secs in presets:
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
        self.time_label.setToolTip("Haz clic para escribir el tiempo exacto")
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

        self.btn_toggle = QPushButton("▶", self.view_normal)
        self.btn_toggle.setProperty("class", "PrimaryAction")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setToolTip(i18n.t("btn_start"))
        self.btn_toggle.clicked.connect(self.toggle_timer)

        self.btn_reset = QPushButton("↺", self.view_normal)
        self.btn_reset.setProperty("class", "SecondaryAction")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setToolTip(i18n.t("btn_reset"))
        self.btn_reset.clicked.connect(self.reset_timer)

        self.btn_clear = QPushButton("🗑", self.view_normal)
        self.btn_clear.setProperty("class", "SecondaryAction")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setToolTip(i18n.t("btn_clear_tooltip"))
        self.btn_clear.clicked.connect(self.clear_time)

        controls_layout.addWidget(self.btn_toggle)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(self.btn_clear)
        normal_layout.addLayout(controls_layout)

        root_layout.addWidget(self.view_normal)

        # --- VISTA MINI-HUD (Horizontal compacta) ---
        self.view_mini = QWidget(self)
        self.view_mini.hide()
        mini_layout = QHBoxLayout(self.view_mini)
        mini_layout.setContentsMargins(10, 2, 10, 2)
        mini_layout.setSpacing(10)
        mini_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón Play/Pause circular compacto
        self.btn_mini_toggle = QPushButton("▶", self.view_mini)
        self.btn_mini_toggle.setProperty("class", "MiniAction")
        self.btn_mini_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mini_toggle.setToolTip("Iniciar / Pausar")
        self.btn_mini_toggle.clicked.connect(self.toggle_timer)
        mini_layout.addWidget(self.btn_mini_toggle)

        # Tiempo centrado (efecto dual: clic para pausar/reanudar, arrastre para mover)
        self.mini_time_label = DualActionLabel("", self.view_mini, on_click=self.toggle_timer)
        self.mini_time_label.setProperty("class", "TimeDisplay")
        self.mini_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mini_time_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mini_time_label.setToolTip("Clic para pausar / reanudar")
        mini_layout.addWidget(self.mini_time_label, 1)

        # Botón Reset circular compacto
        self.btn_mini_reset = QPushButton("↺", self.view_mini)
        self.btn_mini_reset.setProperty("class", "MiniReset")
        self.btn_mini_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mini_reset.setToolTip("Reiniciar")
        self.btn_mini_reset.clicked.connect(self.reset_timer)
        mini_layout.addWidget(self.btn_mini_reset)

        root_layout.addWidget(self.view_mini)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.time_label.setToolTip(i18n.t("timer_click_tooltip"))
        self.btn_reset.setText("↺")
        self.btn_reset.setToolTip(i18n.t("btn_reset"))
        self.btn_clear.setText("🗑")
        self.btn_clear.setToolTip(i18n.t("btn_clear_tooltip"))
        if self.is_running:
            self.btn_toggle.setText("⏸")
            self.btn_toggle.setToolTip(i18n.t("btn_pause"))
            self.btn_mini_toggle.setText("⏸")
            self.status_label.setText(i18n.t("timer_hint_running"))
        elif self.remaining_seconds < self.initial_seconds and self.remaining_seconds > 0:
            self.btn_toggle.setText("▶")
            self.btn_toggle.setToolTip(i18n.t("btn_resume"))
            self.btn_mini_toggle.setText("▶")
            self.status_label.setText(i18n.t("timer_hint_paused"))
        elif self.remaining_seconds == 0:
            self.btn_toggle.setText("▶")
            self.btn_toggle.setToolTip(i18n.t("btn_start"))
            self.btn_mini_toggle.setText("▶")
            is_alarming = getattr(self, "alarm_timer", None) is not None and self.alarm_timer.isActive()
            self.status_label.setText(i18n.t("timer_hint_finished") if is_alarming else i18n.t("timer_hint_idle"))
        else:
            self.btn_toggle.setText("▶")
            self.btn_toggle.setToolTip(i18n.t("btn_start"))
            self.btn_mini_toggle.setText("▶")
            self.status_label.setText(i18n.t("timer_hint_idle"))


    def init_timers(self):
        # Timer de cuenta regresiva
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

        # Timer de alarma / parpadeo visual
        self.alarm_timer = QTimer(self)
        self.alarm_timer.setInterval(400)
        self.alarm_timer.timeout.connect(self.flash_alarm)
        self.alarm_count = 0

    def add_time(self, seconds):
        if self.remaining_seconds == 0:
            self.initial_seconds = seconds
            self.remaining_seconds = seconds
        elif self.is_running or (0 < self.remaining_seconds < self.initial_seconds):
            self.remaining_seconds += seconds
            self.initial_seconds += seconds
        else:
            self.initial_seconds += seconds
            self.remaining_seconds = self.initial_seconds
        self.stop_alarm()
        if not self.is_running:
            self.status_label.setText(i18n.t("timer_hint_idle"))
        self.update_display()

    def clear_time(self):
        self.stop_alarm()
        self.timer.stop()
        self.is_running = False
        self.initial_seconds = 0
        self.remaining_seconds = 0
        self.btn_toggle.setText("▶")
        self.btn_toggle.setToolTip(i18n.t("btn_start"))
        self.btn_mini_toggle.setText("▶")
        self.btn_toggle.setStyleSheet("")
        self.btn_mini_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
        self.mini_time_label.setStyleSheet("color: #ffffff;")
        self.status_label.setText(i18n.t("timer_hint_idle"))
        self.update_display()

    def open_setup_dialog(self, event=None):
        if self.is_running:
            return
        dialog = TimeSetupDialog(self.remaining_seconds, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            total = dialog.get_total_seconds()
            self.initial_seconds = total
            self.remaining_seconds = total
            self.stop_alarm()
            self.status_label.setText(i18n.t("timer_hint_idle"))
            self.update_display()

    def toggle_timer(self):
        if self.alarm_timer.isActive():
            self.stop_alarm()
            return

        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.remaining_seconds <= 0:
            self.open_setup_dialog()
            return
        self.is_running = True
        self.timer.start()
        self.btn_toggle.setText("⏸")
        self.btn_toggle.setToolTip(i18n.t("btn_pause"))
        self.btn_mini_toggle.setText("⏸")
        self.status_label.setText(i18n.t("timer_hint_running"))
        self.btn_toggle.setStyleSheet("background-color: #ff9f1c; color: #141419; border-radius: 19px;")
        self.btn_mini_toggle.setStyleSheet("background-color: #ff9f1c; color: #141419; border-radius: 13px;")
        self.time_label.setStyleSheet("color: #00d2ff;")
        self.mini_time_label.setStyleSheet("color: #00d2ff;")

    def pause_timer(self):
        self.is_running = False
        self.timer.stop()
        self.btn_toggle.setText("▶")
        self.btn_toggle.setToolTip(i18n.t("btn_resume"))
        self.btn_mini_toggle.setText("▶")
        self.status_label.setText(i18n.t("timer_hint_paused"))
        self.btn_toggle.setStyleSheet("")
        self.btn_mini_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
        self.mini_time_label.setStyleSheet("color: #ffffff;")

    def reset_timer(self):
        self.stop_alarm()
        self.timer.stop()
        self.is_running = False
        self.remaining_seconds = self.initial_seconds
        self.btn_toggle.setText("▶")
        self.btn_toggle.setToolTip(i18n.t("btn_start"))
        self.btn_mini_toggle.setText("▶")
        self.btn_toggle.setStyleSheet("")
        self.btn_mini_toggle.setStyleSheet("")
        self.time_label.setStyleSheet("color: #ffffff;")
        self.mini_time_label.setStyleSheet("color: #ffffff;")
        self.status_label.setText(i18n.t("timer_hint_idle"))
        self.update_display()

    def tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.initial_seconds = 0
            self.remaining_seconds = 0
            self.btn_toggle.setText("▶")
            self.btn_toggle.setToolTip(i18n.t("btn_start"))
            self.btn_mini_toggle.setText("▶")
            self.btn_toggle.setStyleSheet("")
            self.btn_mini_toggle.setStyleSheet("")
            self.time_label.setStyleSheet("color: #ffffff;")
            self.mini_time_label.setStyleSheet("color: #ffffff;")
            self.status_label.setText(i18n.t("timer_hint_finished"))
            self.trigger_alarm()

    def trigger_alarm(self):
        self.alarm_count = 0
        self.alarm_timer.start()

        # Sonido configurable (config.ini → [alarm] sound / volume / duration)
        self.alarm_player.play_alarm()

        # Notificación de escritorio delegada a la ventana principal (multiplataforma con auto-cierre)
        top_window = self.window()
        if hasattr(top_window, "show_desktop_notification"):
            top_window.show_desktop_notification(i18n.t("notif_title"), i18n.t("notif_msg"))
        elif shutil.which("notify-send"):
            try:
                subprocess.Popen([
                    "notify-send", 
                    "-a", "Clock & Timer",
                    "-u", "normal", 
                    "-t", "5000", 
                    i18n.t("notif_title"), 
                    i18n.t("notif_msg")
                ])
            except Exception:
                pass


    def flash_alarm(self):
        self.alarm_count += 1
        self.flash_state = not self.flash_state
        if self.flash_state:
            alert_style = "color: #ff3366; background-color: #331122; border-radius: 8px;"
            self.time_label.setStyleSheet(alert_style)
            self.mini_time_label.setStyleSheet(alert_style)
            self.alarm_player.on_flash()
        else:
            self.time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.mini_time_label.setStyleSheet("color: #ffffff; background-color: transparent;")

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
            self.time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.mini_time_label.setStyleSheet("color: #ffffff; background-color: transparent;")
            self.status_label.setText(i18n.t("timer_hint_ready"))


    def update_display(self):
        hours = self.remaining_seconds // 3600
        mins = (self.remaining_seconds % 3600) // 60
        secs = self.remaining_seconds % 60

        if hours > 0:
            text = f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            text = f"{mins:02d}:{secs:02d}"

        old_text = self.mini_time_label.text()
        self.time_label.setText(text)
        self.mini_time_label.setText(text)

        # Si cambió el formato (ej. de MM:SS a HH:MM:SS o viceversa), reajustar fuente al instante
        if len(text) != len(old_text):
            self.resizeEvent(None)

    def set_secondary_opacity(self, opacity: float):
        """Ajusta la opacidad de los controles normales del temporizador durante transiciones."""
        if hasattr(self, "normal_opacity_eff"):
            self.normal_opacity_eff.setOpacity(opacity)

    def set_mini_mode(self, enabled: bool):
        self.is_mini_mode = enabled
        self.view_normal.setVisible(not enabled)
        self.view_mini.setVisible(enabled)
        self.btn_mini_toggle.setText("⏸" if self.is_running else "▶")
        self.resizeEvent(None)

    def resizeEvent(self, event):
        """Ajusta proporcionalmente el tamaño de fuente según el tamaño de la ventana."""
        if event is not None:
            super().resizeEvent(event)

        win = self.window()
        if getattr(win, "is_animating_hud", False):
            return

        w = self.width()
        h = self.height()
        if getattr(self, "is_mini_mode", False):
            text = self.mini_time_label.text()
            font_size = 20 if len(text) > 5 else 24
            font = self.mini_time_label.font()
            font.setPointSize(font_size)
            font.setBold(True)
            self.mini_time_label.setFont(font)
        else:
            base_size = min(w, h)
            font_size = max(22, min(32, int(base_size / 6.5)))
            font = self.time_label.font()
            font.setPointSize(font_size)
            font.setBold(True)
            self.time_label.setFont(font)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            if hasattr(win, "start_window_drag"):
                win.start_window_drag()
        super().mousePressEvent(event)
