"""
Paquete principal de la aplicación Reloj y Temporizador flotante.

Estructura:
  core/      Lógica pura sin interfaz (configuración, idioma, modelo del temporizador).
  services/  Integraciones con el sistema (sonido, notificaciones, bandeja).
  ui/        Interfaz Qt (ventana, barra de título, panel de ajustes, páginas).
"""
from .ui.window import FloatingClockTimerWindow

__all__ = ["FloatingClockTimerWindow"]
