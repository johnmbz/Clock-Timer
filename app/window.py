"""
Módulo de compatibilidad hacia atrás para importaciones existentes.
Redirige a la nueva ubicación en app.ui.window.
"""
from .ui.window import FloatingClockTimerWindow

__all__ = ["FloatingClockTimerWindow"]
