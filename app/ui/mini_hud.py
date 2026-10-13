"""
Modo Mini-HUD: transición animada entre la vista completa y la compacta.

Anima en paralelo la geometría de la ventana y la opacidad de los controles
(iconos de la barra, grip y elementos secundarios de cada página).
"""
from PyQt6.QtCore import (
    QEasingCurve, QObject, QParallelAnimationGroup, QPropertyAnimation, QRect, QSize,
    pyqtProperty, pyqtSignal
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect

NORMAL_MIN_SIZE = QSize(235, 210)
NORMAL_DEFAULT_SIZE = QSize(255, 230)
MINI_MIN_SIZE = QSize(200, 80)
MINI_SIZE = QSize(230, 92)
ANIMATION_MIN_SIZE = QSize(100, 40)   # Mínimo relajado durante la animación


class MiniHudController(QObject):
    finished = pyqtSignal(bool)   # True si terminó en modo mini

    def __init__(self, window, pages_provider):
        """`pages_provider`: función que devuelve la lista actual de páginas."""
        super().__init__(window)
        self._window = window
        self._pages = pages_provider
        self._fade_widgets = []
        self._fade_effects = []
        self._controls_opacity = 1.0
        self._saved_size = None
        self._target_normal_geom = None
        self.is_mini = False
        self.is_animating = False

        self._group = QParallelAnimationGroup(self)
        self._geom_anim = QPropertyAnimation(window, b"geometry", self._group)
        self._fade_anim = QPropertyAnimation(self, b"controls_opacity", self._group)
        self._group.addAnimation(self._geom_anim)
        self._group.addAnimation(self._fade_anim)
        self._group.finished.connect(self._on_finished)

    def add_fade_widget(self, widget):
        """Registra un control que se desvanece y se oculta en modo mini."""
        eff = QGraphicsOpacityEffect(widget)
        eff.setOpacity(self._controls_opacity)
        widget.setGraphicsEffect(eff)
        self._fade_widgets.append(widget)
        self._fade_effects.append(eff)

    # ------------------------------------------------ propiedad animable
    @pyqtProperty(float)
    def controls_opacity(self):
        """Propiedad animable para la opacidad de los controles e iconos."""
        return self._controls_opacity

    @controls_opacity.setter
    def controls_opacity(self, value):
        self._controls_opacity = max(0.0, min(1.0, float(value)))
        for eff in self._fade_effects:
            eff.setOpacity(self._controls_opacity)
        for page in self._pages():
            page.set_secondary_opacity(self._controls_opacity)

    # ------------------------------------------------------------ transición
    def toggle(self):
        """Alterna entre el Modo Normal y el Modo Mini-HUD con una transición suave y sutil estilo macOS / Ubuntu."""
        if self._group.state() == QParallelAnimationGroup.State.Running:
            self._group.stop()

        self.is_mini = not self.is_mini
        self.is_animating = True
        if self.is_mini:
            self._animate_to_mini()
        else:
            self._animate_to_normal()
        self._group.start()

    def _animate_to_mini(self):
        win = self._window
        # Guardamos el tamaño que tenía en la vista completa (no la posición)
        self._saved_size = win.size()
        win.setMinimumSize(ANIMATION_MIN_SIZE)
        target = QRect(win.pos(), MINI_SIZE)

        self._configure(self._geom_anim, 230, QEasingCurve.Type.OutCubic, win.geometry(), target)
        # Desvanecimiento gradual de salida de los iconos (1.0 -> 0.0)
        self._configure(self._fade_anim, 160, QEasingCurve.Type.OutQuad, self.controls_opacity, 0.0)

    def _animate_to_normal(self):
        win = self._window
        # Mostrar widgets con opacidad inicial 0.0 para que emerjan gradualmente junto con el crecimiento
        self.controls_opacity = 0.0
        for w in self._fade_widgets:
            w.show()
        for page in self._pages():
            page.set_mini_mode(False)
        win.setMinimumSize(ANIMATION_MIN_SIZE)

        # Restaurar el tamaño manteniendo la posición actual donde el usuario colocó la ventana
        size = self._saved_size or NORMAL_DEFAULT_SIZE
        w = max(NORMAL_MIN_SIZE.width(), size.width())
        h = max(NORMAL_MIN_SIZE.height(), size.height())
        x, y = self._fit_on_screen(win.x(), win.y(), w, h)
        self._target_normal_geom = QRect(x, y, w, h)

        self._configure(self._geom_anim, 240, QEasingCurve.Type.OutCubic, win.geometry(), self._target_normal_geom)
        # Animación de aparición suave y sutil de los iconos (0.0 -> 1.0)
        self._configure(self._fade_anim, 240, QEasingCurve.Type.OutCubic, 0.0, 1.0)

    def _fit_on_screen(self, x, y, w, h):
        """Asegura que no quede fuera de los límites de la pantalla si se expande pegado al borde."""
        screen = self._window.screen()
        if not screen:
            return x, y
        area = screen.availableGeometry()
        if x + w > area.right():
            x = max(area.left(), area.right() - w)
        if y + h > area.bottom():
            y = max(area.top(), area.bottom() - h)
        return max(x, area.left()), max(y, area.top())

    @staticmethod
    def _configure(anim, duration, curve, start, end):
        anim.setDuration(duration)
        anim.setEasingCurve(curve)
        anim.setStartValue(start)
        anim.setEndValue(end)

    def _on_finished(self):
        """Ajusta restricciones y restaura controles al concluir la transición animada."""
        win = self._window
        self.is_animating = False
        if self.is_mini:
            # Ocultar los widgets ya desvanecidos
            for w in self._fade_widgets:
                w.hide()
            for page in self._pages():
                page.set_mini_mode(True)
            win.setMinimumSize(MINI_MIN_SIZE)
            win.resize(MINI_SIZE)
        else:
            # Asegurar opacidad al 100% y fijar geometría final
            self.controls_opacity = 1.0
            for w in self._fade_widgets:
                w.show()
            win.setMinimumSize(NORMAL_MIN_SIZE)
            if self._target_normal_geom:
                win.setGeometry(self._target_normal_geom)

        # Actualizar tipografía al estado estático final
        for page in self._pages():
            page.refresh_fonts()
        self.finished.emit(self.is_mini)
