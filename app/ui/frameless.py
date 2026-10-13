"""
Ventana sin marco: arrastre desde cualquier zona libre y redimensionado por los bordes.

Uso:
    class MiVentana(FramelessWindowMixin, QWidget):
        def __init__(self):
            super().__init__()
            self.init_frameless()
            self.watch_frameless_cursor(self.container)  # widget que cubre la ventana

Los widgets hijos que quieran iniciar el arrastre (etiquetas, pestañas, páginas)
llaman a `request_window_drag(self)`.
"""
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QCursor

BORDER_MARGIN = 8


def request_window_drag(widget):
    """Pide a la ventana contenedora que inicie el arrastre (si lo soporta)."""
    win = widget.window()
    if hasattr(win, "start_window_drag"):
        win.start_window_drag()


class FramelessWindowMixin:
    """Mixin para QWidget de nivel superior con Qt.WindowType.FramelessWindowHint."""

    def init_frameless(self):
        self.old_pos = None
        self._cursor_watched = None
        self.setMouseTracking(True)

    def watch_frameless_cursor(self, widget):
        """Restaura el cursor de flecha al entrar al contenido y muestra flechas de redimensión en el borde."""
        self._cursor_watched = widget
        widget.setMouseTracking(True)
        widget.setCursor(Qt.CursorShape.ArrowCursor)
        widget.installEventFilter(self)

    def start_window_drag(self):
        """Inicia el arrastre nativo de la ventana del sistema (Wayland/X11/Windows)."""
        handle = self.windowHandle()
        if handle and hasattr(handle, "startSystemMove"):
            if handle.startSystemMove():
                return
        self.old_pos = QCursor.pos()

    # --- Filtro de eventos para restaurar el cursor de flecha inmediatamente ---
    def eventFilter(self, watched, event):
        if watched is self._cursor_watched:
            if event.type() == QEvent.Type.Enter:
                self._reset_cursor()
            elif event.type() == QEvent.Type.MouseMove:
                edge = self._get_edge_at(self.mapFromGlobal(QCursor.pos()))
                self._update_cursor(edge)
        return super().eventFilter(watched, event)

    def leaveEvent(self, event):
        """Restaura el cursor cuando el mouse sale de la ventana."""
        self._reset_cursor()
        super().leaveEvent(event)

    # --- Manejo de arrastre de la ventana y bordes de redimensionamiento ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_edge_at(event.position().toPoint())
            handle = self.windowHandle()
            if edge != Qt.Edge(0) and hasattr(handle, "startSystemResize"):
                # Redimensionamiento nativo del sistema
                handle.startSystemResize(edge)
            else:
                # Arrastre fluido desde cualquier parte libre o cabecera
                self.start_window_drag()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._update_cursor(self._get_edge_at(event.position().toPoint()))

        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        super().mouseReleaseEvent(event)

    # ------------------------------------------------------------ internos
    def _get_edge_at(self, pos):
        """Determina si el cursor está cerca del borde para redimensionar."""
        edge = Qt.Edge(0)
        m = BORDER_MARGIN
        if pos.x() <= m:
            edge |= Qt.Edge.LeftEdge
        elif pos.x() >= self.width() - m:
            edge |= Qt.Edge.RightEdge
        if pos.y() <= m:
            edge |= Qt.Edge.TopEdge
        elif pos.y() >= self.height() - m:
            edge |= Qt.Edge.BottomEdge
        return edge

    def _update_cursor(self, edge):
        """Cambia el cursor según el borde que se esté tocando o lo restaura si no está en el borde."""
        if edge in (Qt.Edge.TopEdge | Qt.Edge.LeftEdge, Qt.Edge.BottomEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in (Qt.Edge.TopEdge | Qt.Edge.RightEdge, Qt.Edge.BottomEdge | Qt.Edge.LeftEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self._reset_cursor()

    def _reset_cursor(self):
        self.unsetCursor()
        self.setCursor(Qt.CursorShape.ArrowCursor)
