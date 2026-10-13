"""
Clase base para las páginas de la ventana (Reloj, Temporizador, ...).

Para añadir una pestaña nueva:
  1. Crea una subclase de PageWidget en ui/widgets/ y define PAGE_ID, ICON,
     TITLE_KEY y TRAY_KEY (añade esas claves a core/i18n.py).
  2. Regístrala en FloatingClockTimerWindow._register_pages() con add_page().
La barra de título, el menú de la bandeja, la tecla Tab y el modo Mini-HUD
la incluyen automáticamente.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from ..frameless import request_window_drag


class PageWidget(QWidget):
    PAGE_ID = ""     # Identificador único ("clock", "timer", ...)
    ICON = ""        # Emoji de la pestaña
    TITLE_KEY = ""   # Clave i18n del tooltip de la pestaña
    TRAY_KEY = ""    # Clave i18n de la entrada del menú de la bandeja

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_mini_mode = False

    # ---------------------------------------------- ganchos para subclases
    def set_mini_mode(self, enabled: bool):
        """Cambia entre la vista completa y la compacta del Mini-HUD."""
        self.is_mini_mode = enabled
        self.refresh_fonts()

    def set_secondary_opacity(self, opacity: float):
        """Desvanece los elementos secundarios durante la animación del Mini-HUD."""

    def on_primary_action(self):
        """Acción de la barra espaciadora cuando la página está visible."""

    def update_fonts(self):
        """Escala la tipografía al tamaño actual. Las subclases la redefinen."""

    # ----------------------------------------------------------- comunes
    def refresh_fonts(self):
        # Durante la animación del Mini-HUD se omite para evitar saltos de tamaño
        if getattr(self.window(), "is_animating_hud", False):
            return
        self.update_fonts()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_fonts()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            request_window_drag(self)
        super().mousePressEvent(event)
