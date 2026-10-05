"""
Configuración centralizada de Clock & Timer.

Única fuente de verdad: un archivo INI legible y editable a mano.
  - Linux:   ~/.config/clock-timer/config.ini
  - Flatpak: ~/.var/app/io.github.JohnmaDev.Clock-Timer/config/clock-timer/config.ini
  - Windows: %LOCALAPPDATA%/clock-timer/config.ini

El panel de ajustes (⚙) y el archivo editan exactamente los mismos valores.
Los cambios hechos a mano en el archivo se aplican en vivo (QFileSystemWatcher).
La variable de entorno CLOCK_TIMER_CONFIG permite usar otra ruta (útil para pruebas).
"""
import configparser
import os

from PyQt6.QtCore import (
    QObject, QStandardPaths, QFileSystemWatcher, QSettings,
    QTimer, QCoreApplication, pyqtSignal
)

# (sección, clave, valor por defecto, comentario, validación)
# Validación: tupla de opciones válidas, o (min, max) para enteros.
SCHEMA = [
    ("general", "language", "es",
     "Interface language: es | en",
     ("es", "en")),
    ("general", "opacity", 100,
     "Window opacity in percent (30-100)",
     (30, 100)),
    ("alarm", "sound", "chime",
     "Sound played when the timer ends:\n"
     "chime | bell | digital | soft | system | none | custom",
     ("chime", "bell", "digital", "soft", "system", "none", "custom")),
    ("alarm", "volume", 80,
     "Alarm volume in percent (0-100)",
     (0, 100)),
    ("alarm", "duration", 5,
     "How long the alarm lasts (flashing + repeated sound), in seconds (1-60)",
     (1, 60)),
    ("alarm", "custom_sound", "",
     "Absolute path to your own .wav file, used when sound = custom\n"
     "Example: custom_sound = /home/user/Music/gong.wav",
     None),
]

HEADER = """\
# Clock & Timer configuration
#
# This file is read on startup and reloaded automatically when it changes.
# The settings panel (gear icon) edits this same file.
# Invalid values are ignored and replaced by their defaults.
"""


def _default_config_path():
    override = os.environ.get("CLOCK_TIMER_CONFIG")
    if override:
        return override
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericConfigLocation)
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "clock-timer", "config.ini")


class Config(QObject):
    """Gestor de configuración con validación, guardado atómico y recarga en vivo."""

    # Emite la clave completa ("seccion.clave") cada vez que un valor cambia
    changed = pyqtSignal(str)

    def __init__(self, path=None):
        super().__init__()
        self.path = path or _default_config_path()
        self._schema = {f"{s}.{k}": (default, comment, rule) for s, k, default, comment, rule in SCHEMA}
        self._values = {key: spec[0] for key, spec in self._schema.items()}
        self._watcher = None
        self._save_timer = None
        self._reload_timer = None

        if os.path.exists(self.path):
            self._load_from_disk()
        else:
            self._migrate_legacy_settings()
            self.save()

    # ------------------------------------------------------------------ API
    def get(self, key):
        return self._values[key]

    def set(self, key, value):
        """Valida y guarda un valor. Devuelve True si cambió."""
        value = self._validate(key, value)
        if value is None or value == self._values[key]:
            return False
        self._values[key] = value
        self._schedule_save()
        self.changed.emit(key)
        return True

    def enable_live_reload(self):
        """Activa la recarga automática al editar el archivo (requiere QApplication)."""
        if self._watcher is not None:
            return
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.setInterval(150)
        self._reload_timer.timeout.connect(self._reload)
        self._watch()

    def save(self):
        """Escribe el archivo completo con comentarios (escritura atómica)."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        lines = [HEADER]
        current_section = None
        for section, key, _default, comment, _rule in SCHEMA:
            if section != current_section:
                lines.append(("\n" if current_section is None else "") + f"[{section}]\n")
                current_section = section
            for c in comment.split("\n"):
                lines.append(f"# {c}\n")
            lines.append(f"{key} = {self._values[f'{section}.{key}']}\n\n")

        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write("".join(lines).rstrip("\n") + "\n")
        os.replace(tmp_path, self.path)
        # os.replace sustituye el inodo: hay que volver a vigilar el archivo
        self._watch()

    # ------------------------------------------------------------ internos
    def _validate(self, key, value):
        if key not in self._schema:
            return None
        default, _comment, rule = self._schema[key]
        try:
            if isinstance(default, int):
                value = int(str(value).strip())
                lo, hi = rule
                if not lo <= value <= hi:
                    return None
            else:
                value = str(value).strip()
                if rule is not None and value not in rule:
                    return None
        except (TypeError, ValueError):
            return None
        return value

    def _read_disk_values(self):
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(self.path, encoding="utf-8")
        except (configparser.Error, OSError, UnicodeDecodeError):
            return None
        values = {}
        for key, (default, _c, _r) in self._schema.items():
            section, name = key.split(".", 1)
            raw = parser.get(section, name, fallback=None)
            parsed = self._validate(key, raw) if raw is not None else None
            values[key] = default if parsed is None else parsed
        return values

    def _load_from_disk(self):
        values = self._read_disk_values()
        if values is not None:
            self._values.update(values)

    def _migrate_legacy_settings(self):
        """Importa el idioma guardado por versiones <= 1.3.x (QSettings 'RelojFlotante')."""
        try:
            legacy = QSettings("RelojFlotante", "Settings")
            lang = legacy.value("language", None)
            if lang is not None:
                validated = self._validate("general.language", lang)
                if validated:
                    self._values["general.language"] = validated
        except Exception:
            pass

    def _schedule_save(self):
        # Agrupa ráfagas de cambios (ej. rueda del ratón sobre la opacidad) en una sola escritura
        if QCoreApplication.instance() is None:
            self.save()
            return
        if self._save_timer is None:
            self._save_timer = QTimer(self)
            self._save_timer.setSingleShot(True)
            self._save_timer.setInterval(400)
            self._save_timer.timeout.connect(self.save)
        self._save_timer.start()

    def flush(self):
        """Fuerza el guardado pendiente (usar al cerrar la aplicación)."""
        if self._save_timer is not None and self._save_timer.isActive():
            self._save_timer.stop()
            self.save()

    def _watch(self):
        if self._watcher is None:
            return
        if os.path.exists(self.path) and self.path not in self._watcher.files():
            self._watcher.addPath(self.path)

    def _on_file_changed(self, _path):
        # Los editores suelen guardar reemplazando el archivo: volver a vigilarlo
        self._watch()
        self._reload_timer.start()

    def _reload(self):
        self._watch()
        if not os.path.exists(self.path):
            return
        values = self._read_disk_values()
        if values is None:
            return
        for key, value in values.items():
            if value != self._values[key]:
                self._values[key] = value
                self.changed.emit(key)


# Instancia global única
config = Config()
