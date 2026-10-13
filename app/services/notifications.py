"""
Notificaciones de escritorio multiplataforma con auto-cierre.

Orden de preferencia:
  1. notify-send (Linux / Flatpak con org.freedesktop.Notifications).
  2. Globo nativo de QSystemTrayIcon (Windows, o Linux sin notify-send).
"""
import os
import shutil
import subprocess

from PyQt6.QtWidgets import QSystemTrayIcon

APP_NAME = "Clock & Timer"
APP_ID = "io.github.JohnmaDev.Clock-Timer"
TIMEOUT_MS = 5000


class DesktopNotifier:
    def __init__(self, icon_path=None, tray=None):
        self.icon_path = icon_path   # Ruta .png o nombre de icono del tema
        self.tray = tray             # QSystemTrayIcon opcional para el fallback

    def notify(self, title, message):
        if self._notify_send(title, message):
            return
        self._tray_message(title, message)

    def _notify_send(self, title, message):
        if not shutil.which("notify-send"):
            return False
        try:
            cmd = ["notify-send", "-a", APP_NAME, "-u", "normal", "-t", str(TIMEOUT_MS)]
            if self.icon_path and os.path.exists(str(self.icon_path)):
                cmd.extend(["-i", str(self.icon_path)])
            else:
                cmd.extend(["-i", APP_ID])
            cmd.extend([title, message])
            subprocess.Popen(cmd)
            return True
        except Exception:
            return False

    def _tray_message(self, title, message):
        if self.tray is not None and self.tray.isVisible():
            try:
                self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, TIMEOUT_MS)
            except Exception:
                pass
