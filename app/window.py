import os
import shutil
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QStackedWidget, QSizeGrip, QLabel, QSlider, QComboBox,
    QSystemTrayIcon, QMenu, QApplication, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QEvent, QTimer, QSize, QPropertyAnimation, 
    QEasingCurve, QRect, QParallelAnimationGroup, pyqtProperty, QUrl
)
from PyQt6.QtGui import QCursor, QDesktopServices


from .clock_widget import ClockWidget
from .timer_widget import TimerWidget
from .draggable_widgets import DraggableTabButton
from .styles import MAIN_STYLE
from .i18n import i18n
from .config import config

BORDER_MARGIN = 8

# Sonidos disponibles en el selector del panel (el valor 'custom' solo aparece si hay ruta en config.ini)
SOUND_CHOICES = ("chime", "bell", "digital", "soft", "system", "none")


class FloatingClockTimerWindow(QWidget):
    """
    Ventana flotante redimensionable para Ubuntu / Linux y Windows.
    Características:
      - 'Always on Top' permanente (siempre por encima de cualquier app).
      - Redimensionable desde los bordes o con el grip inferior.
      - Arrastrable haciendo clic en la barra superior o fondo.
      - Control de transparencia/opacidad con barra visual y rueda del ratón.
      - Alternancia fluida entre Reloj y Temporizador.
      - Aspecto oscuro moderno sin marcos toscos del sistema.
    """
    def __init__(self):
        super().__init__()
        self.always_on_top = True
        self.old_pos = None
        self.is_mini_mode = False
        self.is_animating_hud = False
        self._controls_opacity = 1.0
        self.icon_path = None

        self.init_window_flags()
        self.init_ui()
        self.init_animations()

    def init_window_flags(self):
        """Configura los flags de ventana para que sea flotante y sin marco feo."""
        # WA_TranslucentBackground permite bordes redondeados limpios y elegantes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        # Flags: Tipo Dialog (inmune a reordenamiento de mosaico Aero Snap) + Sin marco + Siempre Flotante (Always On Top)
        flags = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # Dimensiones iniciales y mínimas: Diseño compacto y minimalista
        self.resize(255, 230)
        self.setMinimumSize(235, 210)


    def init_ui(self):
        # Layout raíz que deja espacio transparente para el borde
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        # Contenedor principal con fondo oscuro y bordes redondeados
        self.container = QWidget(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet(MAIN_STYLE)
        self.container.setMouseTracking(True)
        self.container.setCursor(Qt.CursorShape.ArrowCursor)
        self.container.installEventFilter(self)
        root_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(8, 6, 8, 6)
        container_layout.setSpacing(2)

        # 1. Barra de título y controles
        self.title_bar = QWidget(self.container)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setToolTip("Arrastra para mover • Rueda del mouse para ajustar opacidad")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(2, 2, 2, 2)
        title_layout.setSpacing(4)

        # Botones para cambiar entre Reloj y Temporizador (Iconos minimalistas)
        self.btn_clock_tab = DraggableTabButton("🕒", self.title_bar)
        self.btn_clock_tab.setProperty("class", "NavButton")
        self.btn_clock_tab.setCheckable(True)
        self.btn_clock_tab.setChecked(True)
        self.btn_clock_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clock_tab.setToolTip(i18n.t("tab_clock"))
        self.btn_clock_tab.clicked.connect(self.show_clock)

        self.btn_timer_tab = DraggableTabButton("⏳", self.title_bar)
        self.btn_timer_tab.setProperty("class", "NavButton")
        self.btn_timer_tab.setCheckable(True)
        self.btn_timer_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_timer_tab.setToolTip(i18n.t("tab_timer"))
        self.btn_timer_tab.clicked.connect(self.show_timer)

        title_layout.addWidget(self.btn_clock_tab)
        title_layout.addWidget(self.btn_timer_tab)
        title_layout.addStretch()

        # Botón Pin (Always on top toggle)
        self.btn_pin = QPushButton("📌", self.title_bar)
        self.btn_pin.setProperty("class", "WindowControl")
        self.btn_pin.setObjectName("PinButton")
        self.btn_pin.setCheckable(True)
        self.btn_pin.setChecked(True)
        self.btn_pin.setToolTip("Siempre al frente (Activado)")
        self.btn_pin.clicked.connect(self.toggle_pin)
        title_layout.addWidget(self.btn_pin)

        # Botón Ajustes (Opacidad e Idioma unificados)
        self.btn_settings = QPushButton("⚙", self.title_bar)
        self.btn_settings.setProperty("class", "WindowControl")
        self.btn_settings.setObjectName("SettingsButton")
        self.btn_settings.setCheckable(True)
        self.btn_settings.clicked.connect(self.toggle_settings_panel)
        title_layout.addWidget(self.btn_settings)

        # Botón Modo Mini-HUD / Enfoque (anclado a la derecha junto al botón cerrar)
        self.btn_mini_hud = QPushButton("↙", self.title_bar)
        self.btn_mini_hud.setProperty("class", "WindowControl")
        self.btn_mini_hud.setObjectName("MiniHudButton")
        self.btn_mini_hud.clicked.connect(self.toggle_mini_hud)
        title_layout.addWidget(self.btn_mini_hud)

        # Botón Cerrar
        self.btn_close = QPushButton("✕", self.title_bar)
        self.btn_close.setProperty("class", "WindowControl")
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.setToolTip("Cerrar")
        self.btn_close.clicked.connect(self.close)
        title_layout.addWidget(self.btn_close)

        container_layout.addWidget(self.title_bar)

        # 2. Panel desplegable unificado de Ajustes (Opacidad e Idioma)
        self.settings_panel = QWidget(self.container)
        self.settings_panel.setObjectName("SettingsPanel")
        self.settings_panel.hide()

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(6, 6, 6, 6)
        panel_layout.setSpacing(5)

        # Fila 1: Control de Opacidad
        op_row = QHBoxLayout()
        op_row.setSpacing(4)
        self.lbl_op = QLabel(self.settings_panel)
        self.lbl_op.setObjectName("OpacityLabel")

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self.settings_panel)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_slider_changed)

        self.lbl_opacity_value = QLabel("100%", self.settings_panel)
        self.lbl_opacity_value.setObjectName("OpacityValue")

        btn_p50 = QPushButton("50%", self.settings_panel)
        btn_p50.setProperty("class", "OpacityPreset")
        btn_p50.clicked.connect(lambda: self.opacity_slider.setValue(50))

        btn_p75 = QPushButton("75%", self.settings_panel)
        btn_p75.setProperty("class", "OpacityPreset")
        btn_p75.clicked.connect(lambda: self.opacity_slider.setValue(75))

        btn_p100 = QPushButton("100%", self.settings_panel)
        btn_p100.setProperty("class", "OpacityPreset")
        btn_p100.clicked.connect(lambda: self.opacity_slider.setValue(100))

        op_row.addWidget(self.lbl_op)
        op_row.addWidget(self.opacity_slider, 1)
        op_row.addWidget(self.lbl_opacity_value)
        op_row.addWidget(btn_p50)
        op_row.addWidget(btn_p75)
        op_row.addWidget(btn_p100)
        panel_layout.addLayout(op_row)

        # Fila 2: Idioma
        lang_row = QHBoxLayout()
        lang_row.setSpacing(6)
        self.lbl_lang_setting = QLabel(self.settings_panel)
        self.lbl_lang_setting.setObjectName("SettingsLabel")

        self.btn_lang_es = QPushButton("Español", self.settings_panel)
        self.btn_lang_es.setProperty("class", "LangButton")
        self.btn_lang_es.setCheckable(True)
        self.btn_lang_es.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_es.clicked.connect(lambda: self.switch_language("es"))

        self.btn_lang_en = QPushButton("English", self.settings_panel)
        self.btn_lang_en.setProperty("class", "LangButton")
        self.btn_lang_en.setCheckable(True)
        self.btn_lang_en.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_en.clicked.connect(lambda: self.switch_language("en"))

        lang_row.addWidget(self.lbl_lang_setting)
        lang_row.addStretch()
        lang_row.addWidget(self.btn_lang_es)
        lang_row.addWidget(self.btn_lang_en)
        panel_layout.addLayout(lang_row)

        # Fila 3: Sonido de alarma (selector + probar) y acceso a config.ini
        sound_row = QHBoxLayout()
        sound_row.setSpacing(4)
        self.lbl_sound_setting = QLabel(self.settings_panel)
        self.lbl_sound_setting.setObjectName("SettingsLabel")

        self.sound_combo = QComboBox(self.settings_panel)
        self.sound_combo.setObjectName("SoundCombo")
        self.sound_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sound_combo.activated.connect(self.on_sound_selected)

        self.btn_sound_preview = QPushButton("▶", self.settings_panel)
        self.btn_sound_preview.setProperty("class", "OpacityPreset")
        self.btn_sound_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sound_preview.clicked.connect(self.preview_sound)

        self.btn_open_config = QPushButton("…", self.settings_panel)
        self.btn_open_config.setProperty("class", "OpacityPreset")
        self.btn_open_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_config.clicked.connect(self.open_config_file)

        sound_row.addWidget(self.lbl_sound_setting)
        sound_row.addWidget(self.sound_combo, 1)
        sound_row.addWidget(self.btn_sound_preview)
        sound_row.addWidget(self.btn_open_config)
        panel_layout.addLayout(sound_row)

        container_layout.addWidget(self.settings_panel)

        # 4. Pila de contenido (Reloj o Temporizador)
        self.stack = QStackedWidget(self.container)
        self.clock_widget = ClockWidget(self.stack)
        self.timer_widget = TimerWidget(self.stack)


        self.stack.addWidget(self.clock_widget)
        self.stack.addWidget(self.timer_widget)
        container_layout.addWidget(self.stack, 1)

        # 5. Barra inferior con SizeGrip para redimensionar con el mouse
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)
        bottom_bar.addStretch()

        self.size_grip = QSizeGrip(self.container)
        bottom_bar.addWidget(self.size_grip)
        container_layout.addLayout(bottom_bar)

        # Configurar efectos de opacidad para transiciones suaves y sutiles de los iconos
        self.fade_widgets = [
            self.btn_clock_tab,
            self.btn_timer_tab,
            self.btn_pin,
            self.btn_settings,
            self.size_grip
        ]
        self.fade_effects = []
        for w in self.fade_widgets:
            eff = QGraphicsOpacityEffect(w)
            eff.setOpacity(1.0)
            w.setGraphicsEffect(eff)
            self.fade_effects.append(eff)

        # 6. Guardián de capa superior contra reordenamiento de Aero Snap
        self.keep_top_timer = QTimer(self)
        self.keep_top_timer.setInterval(1200)
        self.keep_top_timer.timeout.connect(self._ensure_always_on_top)
        self.keep_top_timer.start()

        # Aplicar textos y traducciones iniciales
        self.retranslate_ui()
        i18n.subscribe(self.retranslate_ui)

        # Restaurar preferencias persistidas y escuchar cambios hechos a mano en config.ini
        self.opacity_slider.setValue(config.get("general.opacity"))
        config.changed.connect(self._on_config_changed)
        config.enable_live_reload()
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(config.flush)

    def _on_config_changed(self, key):
        """Sincroniza el panel cuando config.ini cambia (desde el panel o editado a mano)."""
        if key == "general.opacity":
            if self.opacity_slider.value() != config.get("general.opacity"):
                self.opacity_slider.setValue(config.get("general.opacity"))
        elif key in ("alarm.sound", "alarm.custom_sound"):
            self._populate_sound_combo()

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

    def on_sound_selected(self, index):
        value = self.sound_combo.itemData(index)
        if value:
            config.set("alarm.sound", value)
            self.preview_sound()

    def preview_sound(self):
        self.timer_widget.alarm_player.preview()

    def open_config_file(self):
        """Abre config.ini con el editor predeterminado del sistema (opciones avanzadas)."""
        config.flush()
        if not os.path.exists(config.path):
            config.save()
        QDesktopServices.openUrl(QUrl.fromLocalFile(config.path))

    def closeEvent(self, event):
        config.flush()
        super().closeEvent(event)


    def _ensure_always_on_top(self):
        """Mantiene la ventana al frente de la pila Z incluso si GNOME/Aero Snap reorganiza las capas."""
        if self.always_on_top and not self.isMinimized() and self.isVisible():
            self.raise_()

    def changeEvent(self, event):
        """Garantiza la prioridad superior en eventos de activación o mosaico del sistema."""
        if hasattr(self, 'always_on_top') and self.always_on_top:
            if event.type() in (QEvent.Type.ActivationChange, QEvent.Type.WindowStateChange):
                self.raise_()
        super().changeEvent(event)

    def show_clock(self):
        self.btn_clock_tab.setChecked(True)
        self.btn_timer_tab.setChecked(False)
        self.stack.setCurrentWidget(self.clock_widget)

    def show_timer(self):
        self.btn_clock_tab.setChecked(False)
        self.btn_timer_tab.setChecked(True)
        self.stack.setCurrentWidget(self.timer_widget)

    @pyqtProperty(float)
    def controls_opacity(self):
        """Propiedad animable para la opacidad de los controles e iconos."""
        return getattr(self, "_controls_opacity", 1.0)

    @controls_opacity.setter
    def controls_opacity(self, value):
        self._controls_opacity = max(0.0, min(1.0, float(value)))
        for eff in getattr(self, "fade_effects", []):
            eff.setOpacity(self._controls_opacity)
        if hasattr(self, "clock_widget") and hasattr(self.clock_widget, "set_secondary_opacity"):
            self.clock_widget.set_secondary_opacity(self._controls_opacity)
        if hasattr(self, "timer_widget") and hasattr(self.timer_widget, "set_secondary_opacity"):
            self.timer_widget.set_secondary_opacity(self._controls_opacity)

    def init_animations(self):
        """Inicializa animaciones fluidas paralelas para la geometría y el desvanecimiento de iconos."""
        self.hud_anim_group = QParallelAnimationGroup(self)

        self.hud_geom_anim = QPropertyAnimation(self, b"geometry", self.hud_anim_group)
        self.hud_geom_anim.setDuration(240)
        self.hud_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.hud_fade_anim = QPropertyAnimation(self, b"controls_opacity", self.hud_anim_group)
        self.hud_fade_anim.setDuration(240)
        self.hud_fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.hud_anim_group.addAnimation(self.hud_geom_anim)
        self.hud_anim_group.addAnimation(self.hud_fade_anim)
        self.hud_anim_group.finished.connect(self._on_hud_anim_finished)

    def _on_hud_anim_finished(self):
        """Ajusta restricciones y restaura controles al concluir la transición animada."""
        self.is_animating_hud = False
        if getattr(self, "is_mini_mode", False):
            # En modo mini: flecha ↗ para expandir y volver al tamaño normal
            self.btn_mini_hud.setText("↗")
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_expand"))
            # Ocultar los widgets ya desvanecidos
            for w in self.fade_widgets:
                w.hide()
            self.timer_widget.set_mini_mode(True)
            self.clock_widget.set_mini_mode(True)
            self.setMinimumSize(200, 80)
            self.resize(230, 92)
        else:
            # En modo normal: flecha ↙ para contraer al modo mini
            self.btn_mini_hud.setText("↙")
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_shrink"))
            # Asegurar opacidad al 100% y fijar geometría final
            self.controls_opacity = 1.0
            for w in self.fade_widgets:
                w.show()
            self.setMinimumSize(235, 210)
            if hasattr(self, "target_normal_geom") and self.target_normal_geom:
                self.setGeometry(self.target_normal_geom)

        # Actualizar tipografía al estado estático final
        if hasattr(self, "clock_widget"):
            self.clock_widget.resizeEvent(None)
        if hasattr(self, "timer_widget"):
            self.timer_widget.resizeEvent(None)

    def toggle_mini_hud(self):
        """Alterna entre el Modo Normal y el Modo Mini-HUD con una transición suave y sutil estilo macOS / Ubuntu."""
        if hasattr(self, "hud_anim_group") and self.hud_anim_group.state() == QParallelAnimationGroup.State.Running:
            self.hud_anim_group.stop()

        self.is_mini_mode = not getattr(self, "is_mini_mode", False)
        self.is_animating_hud = True

        if self.is_mini_mode:
            # Guardamos el tamaño que tenía en la vista completa (no la posición)
            self.saved_size = self.size()
            cur_pos = self.pos()

            if hasattr(self, "settings_panel") and self.settings_panel.isVisible():
                self.settings_panel.hide()
                self.btn_settings.setChecked(False)

            # Relajar temporalmente el mínimo para permitir la animación de encogimiento suave
            self.setMinimumSize(100, 40)
            target_rect = QRect(cur_pos.x(), cur_pos.y(), 230, 92)

            # Animación de geometría
            self.hud_geom_anim.setDuration(230)
            self.hud_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.hud_geom_anim.setStartValue(self.geometry())
            self.hud_geom_anim.setEndValue(target_rect)

            # Desvanecimiento gradual de salida de los iconos (1.0 -> 0.0)
            self.hud_fade_anim.setDuration(160)
            self.hud_fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.hud_fade_anim.setStartValue(self.controls_opacity)
            self.hud_fade_anim.setEndValue(0.0)

            self.hud_anim_group.start()
        else:
            # Mostrar widgets con opacidad inicial 0.0 para que emerjan gradualmente junto con el crecimiento
            self.controls_opacity = 0.0
            for w in self.fade_widgets:
                w.show()

            self.timer_widget.set_mini_mode(False)
            self.clock_widget.set_mini_mode(False)

            self.setMinimumSize(100, 40)

            # Restaurar el tamaño manteniendo la posición actual donde el usuario colocó la ventana
            target_size = getattr(self, "saved_size", QSize(255, 230))
            cur_x = self.x()
            cur_y = self.y()
            w = max(235, target_size.width())
            h = max(210, target_size.height())

            # Asegurar que no quede fuera de los límites de la pantalla si se expande pegado al borde
            screen = self.screen().availableGeometry() if self.screen() else None
            if screen:
                if cur_x + w > screen.right():
                    cur_x = max(screen.left(), screen.right() - w)
                if cur_y + h > screen.bottom():
                    cur_y = max(screen.top(), screen.bottom() - h)
                if cur_x < screen.left():
                    cur_x = screen.left()
                if cur_y < screen.top():
                    cur_y = screen.top()

            self.target_normal_geom = QRect(cur_x, cur_y, w, h)

            # Animación de expansión geométrica
            self.hud_geom_anim.setDuration(240)
            self.hud_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.hud_geom_anim.setStartValue(self.geometry())
            self.hud_geom_anim.setEndValue(self.target_normal_geom)

            # Animación de aparición suave y sutil de los iconos (0.0 -> 1.0)
            self.hud_fade_anim.setDuration(240)
            self.hud_fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.hud_fade_anim.setStartValue(0.0)
            self.hud_fade_anim.setEndValue(1.0)

            self.hud_anim_group.start()

    def init_tray_icon(self, icon, icon_path=None):
        """Inicializa el icono en la bandeja del sistema (System Tray / flecha ^)."""
        if icon_path:
            self.icon_path = icon_path
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Clock & Timer")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #14141c;
                color: #ffffff;
                border: 1.5px solid #2d2d3f;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00d2ff;
                color: #080c14;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #282838;
                margin: 4px 6px;
            }
        """)

        # Título de cabecera en el menú
        header_action = tray_menu.addAction("Clock & Timer")
        header_action.setEnabled(False)
        tray_menu.addSeparator()

        action_toggle = tray_menu.addAction("Mostrar / Ocultar")
        action_toggle.triggered.connect(self.toggle_window_visibility)

        action_clock = tray_menu.addAction("🕒 Modo Reloj")
        action_clock.triggered.connect(lambda: (self.show_clock(), self.show_and_raise()))

        action_timer = tray_menu.addAction("⏳ Modo Temporizador")
        action_timer.triggered.connect(lambda: (self.show_timer(), self.show_and_raise()))

        tray_menu.addSeparator()

        action_quit = tray_menu.addAction("✕ Salir")
        action_quit.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_window_visibility()

    def toggle_window_visibility(self):
        """Alterna visibilidad de la ventana al hacer clic en el System Tray."""
        if self.isVisible():
            self.hide()
        else:
            self.show_and_raise()

    def show_and_raise(self):
        """Muestra y trae la ventana al frente con foco."""
        self.show()
        self.raise_()
        self.activateWindow()

    def show_desktop_notification(self, title, message):
        """Muestra una notificación nativa no intrusiva con auto-cierre en Linux y Windows."""
        # 1. En Linux, si notify-send está disponible, usarlo con identidad y auto-cierre normal
        if shutil.which("notify-send"):
            try:
                cmd = ["notify-send", "-a", "Clock & Timer", "-u", "normal", "-t", "5000"]
                icon_arg = getattr(self, "icon_path", None)
                if icon_arg and os.path.exists(str(icon_arg)):
                    cmd.extend(["-i", str(icon_arg)])
                else:
                    cmd.extend(["-i", "io.github.JohnmaDev.Clock-Timer"])
                cmd.extend([title, message])
                subprocess.Popen(cmd)
                return
            except Exception:
                pass

        # 2. En Windows (o Linux si notify-send no está), usar QSystemTrayIcon nativo
        if hasattr(self, "tray_icon") and self.tray_icon and self.tray_icon.isVisible():
            try:
                self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)
            except Exception:
                pass

    def toggle_pin(self):
        """Alterna el modo 'Siempre al frente' (Always on top)."""
        self.always_on_top = self.btn_pin.isChecked()
        flags = self.windowFlags()
        if self.always_on_top:
            flags |= (Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            self.btn_pin.setToolTip("Siempre al frente (Activado)")
            if hasattr(self, 'keep_top_timer'):
                self.keep_top_timer.start()
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.btn_pin.setToolTip("Modo normal (no fijado)")
            if hasattr(self, 'keep_top_timer'):
                self.keep_top_timer.stop()
        
        # Al cambiar flags en Qt, se debe re-mostrar la ventana
        pos = self.pos()
        self.setWindowFlags(flags)
        self.move(pos)
        self.show()
        if self.always_on_top:
            self.raise_()

    def toggle_settings_panel(self):
        """Muestra u oculta el panel unificado de ajustes (Opacidad e Idioma)."""
        is_visible = self.btn_settings.isChecked()
        self.settings_panel.setVisible(is_visible)

    def switch_language(self, lang):
        """Cambia el idioma global de la aplicación."""
        i18n.set_lang(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Actualiza todos los textos y tooltips de la ventana al idioma actual."""
        current = i18n.get_lang()
        self.btn_lang_es.setChecked(current == "es")
        self.btn_lang_en.setChecked(current == "en")

        self.btn_clock_tab.setToolTip(i18n.t("tab_clock"))
        self.btn_timer_tab.setToolTip(i18n.t("tab_timer"))

        if getattr(self, "is_mini_mode", False):
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_expand"))
        else:
            self.btn_mini_hud.setToolTip(i18n.t("mini_hud_shrink"))

        if self.always_on_top:
            self.btn_pin.setToolTip(i18n.t("pin_on"))
        else:
            self.btn_pin.setToolTip(i18n.t("pin_off"))

        self.btn_settings.setToolTip(i18n.t("settings_btn"))
        self.btn_close.setToolTip(i18n.t("close"))

        self.lbl_op.setText(i18n.t("opacity_lbl"))
        self.lbl_lang_setting.setText(i18n.t("lang_label"))
        self.lbl_sound_setting.setText(i18n.t("sound_label"))
        self.btn_sound_preview.setToolTip(i18n.t("sound_preview"))
        self.btn_open_config.setToolTip(f"{i18n.t('open_config')}\n{config.path}")
        self._populate_sound_combo()
        self.size_grip.setToolTip(i18n.t("resize_tooltip"))
        self.title_bar.setToolTip(f"Opacidad: {self.opacity_slider.value()}% • {i18n.t('title_tooltip')}")

    def on_opacity_slider_changed(self, value):
        """Aplica el valor del slider a la opacidad de la ventana."""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        self.lbl_opacity_value.setText(f"{value}%")
        self.title_bar.setToolTip(f"Opacidad: {value}% • {i18n.t('title_tooltip')}")
        config.set("general.opacity", value)


    # --- Filtro de eventos para restaurar el cursor de flecha inmediatamente ---
    def eventFilter(self, watched, event):
        if watched == self.container:
            if event.type() == QEvent.Type.Enter:
                self.unsetCursor()
                self.setCursor(Qt.CursorShape.ArrowCursor)
            elif event.type() == QEvent.Type.MouseMove:
                pos = self.mapFromGlobal(QCursor.pos())
                edge = self._get_edge_at(pos)
                if edge != Qt.Edge(0):
                    self._update_cursor(edge)
                else:
                    self.unsetCursor()
                    self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().eventFilter(watched, event)

    def leaveEvent(self, event):
        """Restaura el cursor cuando el mouse sale de la ventana."""
        self.unsetCursor()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def start_window_drag(self):
        """Inicia el arrastre nativo de la ventana del sistema (Wayland/X11/Windows)."""
        handle = self.windowHandle()
        if handle and hasattr(handle, "startSystemMove"):
            if handle.startSystemMove():
                return
        self.old_pos = QCursor.pos()

    # --- Manejo de arrastre de la ventana y bordes de redimensionamiento ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edge = self._get_edge_at(pos)

            if edge != Qt.Edge(0) and hasattr(self.windowHandle(), 'startSystemResize'):
                # Redimensionamiento nativo del sistema
                self.windowHandle().startSystemResize(edge)
            else:
                # Arrastre fluido desde cualquier parte libre o cabecera
                self.start_window_drag()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        edge = self._get_edge_at(pos)
        self._update_cursor(edge)

        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        super().mouseReleaseEvent(event)

    def _get_edge_at(self, pos):
        """Determina si el cursor está cerca del borde para redimensionar."""
        edge = Qt.Edge(0)
        m = BORDER_MARGIN
        w = self.width()
        h = self.height()

        if pos.x() <= m:
            edge |= Qt.Edge.LeftEdge
        elif pos.x() >= w - m:
            edge |= Qt.Edge.RightEdge

        if pos.y() <= m:
            edge |= Qt.Edge.TopEdge
        elif pos.y() >= h - m:
            edge |= Qt.Edge.BottomEdge

        return edge

    def _update_cursor(self, edge):
        """Cambia el cursor según el borde que se esté tocando o lo restaura si no está en el borde."""
        if edge == (Qt.Edge.TopEdge | Qt.Edge.LeftEdge) or edge == (Qt.Edge.BottomEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge == (Qt.Edge.TopEdge | Qt.Edge.RightEdge) or edge == (Qt.Edge.BottomEdge | Qt.Edge.LeftEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event):
        """Ajusta suavemente la opacidad de la ventana con la rueda del mouse sincronizado con el slider."""
        delta = event.angleDelta().y()
        step = 5 if delta > 0 else -5
        new_val = max(30, min(100, self.opacity_slider.value() + step))
        self.opacity_slider.setValue(new_val)
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        """Atajos de teclado rápidos."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Tab:
            # Alternar pestaña con Tab
            if self.stack.currentWidget() == self.clock_widget:
                self.show_timer()
            else:
                self.show_clock()
        elif event.key() == Qt.Key.Key_Space:
            # Barra espaciadora inicia/pausa el temporizador si estamos en esa vista
            if self.stack.currentWidget() == self.timer_widget:
                self.timer_widget.toggle_timer()
        elif event.key() in (Qt.Key.Key_M, Qt.Key.Key_F):
            # 'M' (Mini) o 'F' (Focus) para alternar Modo Mini-HUD
            self.toggle_mini_hud()
        super().keyPressEvent(event)


