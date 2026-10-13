"""
Ventana principal: ensambla barra de título, panel de ajustes, páginas y servicios.

Cada responsabilidad vive en su propio módulo:
  frameless.py       arrastre y redimensionado sin marco
  title_bar.py       pestañas y controles de ventana
  settings_panel.py  opacidad, idioma y sonido
  mini_hud.py        transición animada al modo compacto
  services/          sonido, notificaciones y bandeja del sistema
"""
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QSizeGrip, QStackedWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import QEvent, Qt, QTimer

from ..core.config import config
from ..core.i18n import i18n
from ..services.notifications import DesktopNotifier
from ..services.sounds import AlarmPlayer
from ..services.tray import TrayIcon
from .frameless import FramelessWindowMixin
from .mini_hud import NORMAL_DEFAULT_SIZE, NORMAL_MIN_SIZE, MiniHudController
from .settings_panel import SettingsPanel
from .styles import MAIN_STYLE
from .title_bar import TitleBar
from .widgets.clock_widget import ClockWidget
from .widgets.timer_widget import TimerWidget

KEEP_ON_TOP_INTERVAL_MS = 1200
OPACITY_WHEEL_STEP = 5


class FloatingClockTimerWindow(FramelessWindowMixin, QWidget):
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
        self.pages = []
        self.tray_icon = None
        self.notifier = DesktopNotifier()
        self.alarm_player = AlarmPlayer(self)

        self.init_window_flags()
        self.init_frameless()
        self.init_ui()
        self._register_pages()
        self._init_keep_on_top()

        # Recarga en vivo de config.ini y guardado pendiente al salir
        config.enable_live_reload()
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(config.flush)

    # ------------------------------------------------------------- montaje
    def init_window_flags(self):
        """Configura los flags de ventana para que sea flotante y sin marco feo."""
        # WA_TranslucentBackground permite bordes redondeados limpios y elegantes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Flags: Tipo Dialog (inmune a reordenamiento de mosaico Aero Snap) + Sin marco + Siempre Flotante (Always On Top)
        flags = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # Dimensiones iniciales y mínimas: Diseño compacto y minimalista
        self.resize(NORMAL_DEFAULT_SIZE)
        self.setMinimumSize(NORMAL_MIN_SIZE)

    def init_ui(self):
        # Layout raíz que deja espacio transparente para el borde
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        # Contenedor principal con fondo oscuro y bordes redondeados
        self.container = QWidget(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet(MAIN_STYLE)
        self.watch_frameless_cursor(self.container)
        root_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(8, 6, 8, 6)
        container_layout.setSpacing(2)

        # 1. Barra de título y controles
        self.title_bar = TitleBar(self.container)
        self.title_bar.tab_selected.connect(self.show_page)
        self.title_bar.pin_toggled.connect(self.set_always_on_top)
        self.title_bar.settings_toggled.connect(self.set_settings_visible)
        self.title_bar.mini_hud_clicked.connect(self.toggle_mini_hud)
        self.title_bar.close_clicked.connect(self.close)
        container_layout.addWidget(self.title_bar)

        # 2. Panel desplegable unificado de Ajustes
        self.settings_panel = SettingsPanel(self.container)
        self.settings_panel.opacity_changed.connect(self._apply_opacity)
        self.settings_panel.preview_requested.connect(self.alarm_player.preview)
        container_layout.addWidget(self.settings_panel)

        # 3. Pila de contenido (una página por pestaña)
        self.stack = QStackedWidget(self.container)
        container_layout.addWidget(self.stack, 1)

        # 4. Barra inferior con SizeGrip para redimensionar con el mouse
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)
        bottom_bar.addStretch()
        self.size_grip = QSizeGrip(self.container)
        self.size_grip.setToolTip(i18n.t("resize_tooltip"))
        bottom_bar.addWidget(self.size_grip)
        container_layout.addLayout(bottom_bar)

        # 5. Modo Mini-HUD: controles que se desvanecen al compactar
        self.mini_hud = MiniHudController(self, lambda: self.pages)
        self.mini_hud.finished.connect(self.title_bar.set_mini_mode)
        for w in (self.title_bar.btn_pin, self.title_bar.btn_settings, self.size_grip):
            self.mini_hud.add_fade_widget(w)

        # Aplicar opacidad persistida
        self._apply_opacity(self.settings_panel.opacity())
        i18n.subscribe(self.retranslate_ui)

    def _register_pages(self):
        """Páginas disponibles. Para añadir una nueva, ver ui/widgets/page.py."""
        self.clock_widget = ClockWidget(self.stack)
        self.timer_widget = TimerWidget(self.stack, alarm_player=self.alarm_player)
        self.timer_widget.model.finished.connect(self._notify_timer_finished)

        self.add_page(self.clock_widget)
        self.add_page(self.timer_widget)
        self.show_page(self.clock_widget.PAGE_ID)

    def add_page(self, page):
        """Registra una página: crea su pestaña, la añade a la pila y al Mini-HUD."""
        self.pages.append(page)
        self.stack.addWidget(page)
        tab = self.title_bar.add_tab(page.PAGE_ID, page.ICON, page.TITLE_KEY)
        self.mini_hud.add_fade_widget(tab)

    def _page_by_id(self, page_id):
        return next((p for p in self.pages if p.PAGE_ID == page_id), None)

    # --------------------------------------------------------- navegación
    def show_page(self, page_id):
        page = self._page_by_id(page_id)
        if page is None:
            return
        self.stack.setCurrentWidget(page)
        self.title_bar.set_current_tab(page_id)

    def show_clock(self):
        self.show_page(ClockWidget.PAGE_ID)

    def show_timer(self):
        self.show_page(TimerWidget.PAGE_ID)

    def show_next_page(self):
        if not self.pages:
            return
        idx = self.pages.index(self.stack.currentWidget())
        self.show_page(self.pages[(idx + 1) % len(self.pages)].PAGE_ID)

    @property
    def current_page(self):
        return self.stack.currentWidget()

    # ------------------------------------------------------------ Mini-HUD
    @property
    def is_mini_mode(self):
        return self.mini_hud.is_mini

    @property
    def is_animating_hud(self):
        """Las páginas lo consultan para no recalcular fuentes a mitad de animación."""
        return self.mini_hud.is_animating

    def toggle_mini_hud(self):
        if not self.mini_hud.is_mini:
            self.set_settings_visible(False)
        self.mini_hud.toggle()

    # ------------------------------------------------------------- ajustes
    def set_settings_visible(self, visible):
        """Muestra u oculta el panel unificado de ajustes."""
        self.settings_panel.setVisible(visible)
        if not visible:
            self.title_bar.close_settings()

    def _apply_opacity(self, value):
        """Aplica el valor del slider a la opacidad de la ventana."""
        self.setWindowOpacity(value / 100.0)
        self.title_bar.set_opacity_hint(value)

    def retranslate_ui(self):
        self.size_grip.setToolTip(i18n.t("resize_tooltip"))

    # ---------------------------------------------------- siempre al frente
    def _init_keep_on_top(self):
        # Guardián de capa superior contra reordenamiento de Aero Snap
        self.keep_top_timer = QTimer(self)
        self.keep_top_timer.setInterval(KEEP_ON_TOP_INTERVAL_MS)
        self.keep_top_timer.timeout.connect(self._ensure_always_on_top)
        self.keep_top_timer.start()

    def _ensure_always_on_top(self):
        """Mantiene la ventana al frente de la pila Z incluso si GNOME/Aero Snap reorganiza las capas."""
        if self.always_on_top and not self.isMinimized() and self.isVisible():
            self.raise_()

    def changeEvent(self, event):
        """Garantiza la prioridad superior en eventos de activación o mosaico del sistema."""
        if getattr(self, "always_on_top", False):
            if event.type() in (QEvent.Type.ActivationChange, QEvent.Type.WindowStateChange):
                self.raise_()
        super().changeEvent(event)

    def set_always_on_top(self, enabled):
        """Alterna el modo 'Siempre al frente' (Always on top)."""
        self.always_on_top = enabled
        flags = self.windowFlags()
        if enabled:
            flags |= (Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            self.keep_top_timer.start()
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.keep_top_timer.stop()

        # Al cambiar flags en Qt, se debe re-mostrar la ventana
        pos = self.pos()
        self.setWindowFlags(flags)
        self.move(pos)
        self.show()
        if enabled:
            self.raise_()

    # ---------------------------------------------- bandeja y notificaciones
    def set_app_icon(self, icon, icon_path=None):
        """Aplica el icono a la ventana, las notificaciones y la bandeja del sistema."""
        self.icon_path = icon_path
        self.notifier.icon_path = icon_path
        if icon.isNull():
            return
        self.setWindowIcon(icon)
        self.init_tray_icon(icon, icon_path)

    def init_tray_icon(self, icon, icon_path=None):
        """Inicializa el icono en la bandeja del sistema (System Tray / flecha ^)."""
        if icon_path:
            self.icon_path = icon_path
            self.notifier.icon_path = icon_path
        self.tray_icon = TrayIcon.create(icon, self.pages, self)
        if self.tray_icon is None:
            return
        self.tray_icon.toggle_requested.connect(self.toggle_window_visibility)
        self.tray_icon.page_requested.connect(lambda pid: (self.show_page(pid), self.show_and_raise()))
        self.notifier.tray = self.tray_icon

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

    def _notify_timer_finished(self):
        self.notifier.notify(i18n.t("notif_title"), i18n.t("notif_msg"))

    # ------------------------------------------------------ eventos de Qt
    def closeEvent(self, event):
        config.flush()
        super().closeEvent(event)

    def wheelEvent(self, event):
        """Ajusta suavemente la opacidad de la ventana con la rueda del mouse sincronizado con el slider."""
        step = OPACITY_WHEEL_STEP if event.angleDelta().y() > 0 else -OPACITY_WHEEL_STEP
        self.settings_panel.set_opacity(self.settings_panel.opacity() + step)
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        """Atajos de teclado rápidos."""
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key == Qt.Key.Key_Tab:
            # Alternar pestaña con Tab
            self.show_next_page()
        elif key == Qt.Key.Key_Space:
            # Barra espaciadora: acción principal de la página visible (ej. iniciar/pausar el temporizador)
            self.current_page.on_primary_action()
        elif key in (Qt.Key.Key_M, Qt.Key.Key_F):
            # 'M' (Mini) o 'F' (Focus) para alternar Modo Mini-HUD
            self.toggle_mini_hud()
        super().keyPressEvent(event)
