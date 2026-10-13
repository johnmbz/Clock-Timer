"""
Modelo del temporizador: estado y reglas de la cuenta regresiva, sin interfaz.

La vista (ui/widgets/timer_widget.py) solo escucha sus señales y llama a sus
métodos, así que esta lógica puede probarse sin abrir ventanas y reutilizarse
para futuras funciones (Pomodoro, varias alarmas, etc.).
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TimerState:
    IDLE = "idle"        # Detenido (con o sin tiempo configurado)
    RUNNING = "running"  # Contando hacia atrás
    PAUSED = "paused"    # Detenido a mitad de una cuenta


def format_seconds(total):
    """Devuelve 'MM:SS' o 'HH:MM:SS' si hay horas."""
    hours, rest = divmod(max(0, int(total)), 3600)
    mins, secs = divmod(rest, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


class TimerModel(QObject):
    """Cuenta regresiva con inicio, pausa, reinicio y suma de preajustes."""

    time_changed = pyqtSignal(int)    # Segundos restantes
    state_changed = pyqtSignal(str)   # Uno de TimerState
    finished = pyqtSignal()           # La cuenta llegó a su fin

    def __init__(self, parent=None, interval_ms=1000):
        super().__init__(parent)
        self.initial_seconds = 0   # Inicia en 00:00 por defecto
        self.remaining_seconds = 0
        self.is_running = False

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.tick)

    # ------------------------------------------------------------ consultas
    @property
    def state(self):
        if self.is_running:
            return TimerState.RUNNING
        if 0 < self.remaining_seconds < self.initial_seconds:
            return TimerState.PAUSED
        return TimerState.IDLE

    @property
    def has_time(self):
        return self.remaining_seconds > 0

    def text(self):
        return format_seconds(self.remaining_seconds)

    # ------------------------------------------------------------- acciones
    def add_time(self, seconds):
        """Suma un preajuste respetando si la cuenta está en curso, en pausa o terminada."""
        if self.remaining_seconds == 0:
            self.initial_seconds = seconds
            self.remaining_seconds = seconds
        elif self.is_running or (0 < self.remaining_seconds < self.initial_seconds):
            self.remaining_seconds += seconds
            self.initial_seconds += seconds
        else:
            self.initial_seconds += seconds
            self.remaining_seconds = self.initial_seconds
        self._emit_all()

    def set_time(self, seconds):
        """Fija un tiempo exacto (diálogo de configuración)."""
        self.initial_seconds = seconds
        self.remaining_seconds = seconds
        self._emit_all()

    def start(self):
        """Inicia la cuenta. Devuelve False si no hay tiempo configurado."""
        if self.remaining_seconds <= 0:
            return False
        self.is_running = True
        self._timer.start()
        self.state_changed.emit(self.state)
        return True

    def pause(self):
        self.is_running = False
        self._timer.stop()
        self.state_changed.emit(self.state)

    def reset(self):
        """Vuelve al último tiempo configurado."""
        self._stop()
        self.remaining_seconds = self.initial_seconds
        self._emit_all()

    def clear(self):
        """Restablece a 00:00."""
        self._stop()
        self.initial_seconds = 0
        self.remaining_seconds = 0
        self._emit_all()

    def tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_changed.emit(self.remaining_seconds)
            return
        # Al terminar se borra la duración histórica para que los preajustes no se acumulen
        self._stop()
        self.initial_seconds = 0
        self.remaining_seconds = 0
        self._emit_all()
        self.finished.emit()

    # ------------------------------------------------------------ internos
    def _stop(self):
        self._timer.stop()
        self.is_running = False

    def _emit_all(self):
        self.time_changed.emit(self.remaining_seconds)
        self.state_changed.emit(self.state)
