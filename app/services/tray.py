"""
Icono de la bandeja del sistema (System Tray / flecha ^).

No conoce la ventana: emite señales y la ventana decide qué hacer. Las entradas
"Modo ..." se generan a partir de las páginas registradas, así que una página
nueva aparece en el menú sin tocar este archivo.
"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from ..core.i18n import i18n
from ..ui.styles import TRAY_MENU_STYLE
from .notifications import APP_NAME


class TrayIcon(QSystemTrayIcon):
    toggle_requested = pyqtSignal()
    page_requested = pyqtSignal(str)   # PAGE_ID de la página a mostrar

    def __init__(self, icon, pages, parent=None):
        """`pages`: lista de páginas con atributos PAGE_ID, ICON y TRAY_KEY."""
        super().__init__(icon, parent)
        self._pages = pages
        self.setToolTip(APP_NAME)

        self._menu = QMenu()
        self._menu.setStyleSheet(TRAY_MENU_STYLE)
        self.setContextMenu(self._menu)
        self.activated.connect(self._on_activated)

        self._build_menu()
        i18n.subscribe(self._build_menu)

    @classmethod
    def create(cls, icon, pages, parent=None):
        """Devuelve el icono ya visible, o None si el escritorio no tiene bandeja."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return None
        tray = cls(icon, pages, parent)
        tray.show()
        return tray

    def _build_menu(self):
        menu = self._menu
        menu.clear()

        # Título de cabecera en el menú
        header = menu.addAction(APP_NAME)
        header.setEnabled(False)
        menu.addSeparator()

        menu.addAction(i18n.t("tray_toggle")).triggered.connect(self.toggle_requested.emit)
        for page in self._pages:
            action = menu.addAction(f"{page.ICON} {i18n.t(page.TRAY_KEY)}")
            action.triggered.connect(lambda _=False, pid=page.PAGE_ID: self.page_requested.emit(pid))

        menu.addSeparator()
        menu.addAction(i18n.t("tray_quit")).triggered.connect(QApplication.instance().quit)

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_requested.emit()
