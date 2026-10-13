from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt

from ..frameless import request_window_drag

class DraggableTabButton(QPushButton):
    """
    Botón de pestaña con efecto dual al estilo GNOME / Libadwaita:
    - Clic simple sin mover: activa/cambia de pestaña normalmente.
    - Clic y arrastre (distancia > 5px): mueve la ventana.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.drag_start_pos = None
        self.is_dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
            self.is_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_start_pos and (event.buttons() & Qt.MouseButton.LeftButton):
            distance = (event.globalPosition().toPoint() - self.drag_start_pos).manhattanLength()
            if distance > 6:
                self.is_dragging = True
                self.setDown(False)
                request_window_drag(self)
                self.drag_start_pos = None
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.drag_start_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)


class DualActionLabel(QLabel):
    """
    Etiqueta con efecto dual al estilo GNOME:
    - Clic simple sin mover: ejecuta la acción de clic (callback).
    - Clic y arrastre: inicia el arrastre fluido de la ventana.
    """
    def __init__(self, text="", parent=None, on_click=None):
        super().__init__(text, parent)
        self.on_click = on_click
        self.drag_start_pos = None
        self.is_dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
            self.is_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_start_pos and (event.buttons() & Qt.MouseButton.LeftButton):
            distance = (event.globalPosition().toPoint() - self.drag_start_pos).manhattanLength()
            if distance > 6:
                self.is_dragging = True
                request_window_drag(self)
                self.drag_start_pos = None
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.drag_start_pos = None
            event.accept()
            return
        if self.drag_start_pos and event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = None
            if callable(self.on_click):
                self.on_click()
        super().mouseReleaseEvent(event)
