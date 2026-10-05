"""
Sonidos de alarma de Clock & Timer.

Los sonidos se sintetizan con Python puro (sin archivos binarios en el repositorio
ni licencias de terceros) y se guardan en caché como .wav la primera vez:
  ~/.cache/clock-timer/sounds/
La reproducción usa QSoundEffect (QtMultimedia), con fallback a QApplication.beep().
"""
import math
import os
import struct
import wave

from PyQt6.QtCore import QObject, QStandardPaths, QUrl
from PyQt6.QtWidgets import QApplication

from .config import config

try:
    from PyQt6.QtMultimedia import QSoundEffect
except ImportError:  # QtMultimedia no disponible: se usará el beep del sistema
    QSoundEffect = None

SAMPLE_RATE = 44100
# Incrementar al cambiar la síntesis para regenerar la caché
SOUND_VERSION = 1

SYNTH_SOUNDS = ("chime", "bell", "digital", "soft")


# ----------------------------------------------------------------- síntesis
def _render(duration, voices):
    """Mezcla voces (inicio, frecuencia, amplitud, decaimiento, ataque) en muestras flotantes."""
    n = int(duration * SAMPLE_RATE)
    buf = [0.0] * n
    two_pi = 2.0 * math.pi
    for start, freq, amp, decay, attack in voices:
        first = int(start * SAMPLE_RATE)
        w = two_pi * freq / SAMPLE_RATE
        for i in range(first, n):
            t = (i - first) / SAMPLE_RATE
            env = math.exp(-decay * t)
            if env < 0.0005:
                break
            if t < attack:
                env *= t / attack
            buf[i] += amp * env * math.sin(w * (i - first))
    return buf


def _synth_chime():
    # Dos notas cristalinas descendentes (Mi6 -> Do6), estilo "ding-dong" suave
    voices = []
    for start, f in ((0.0, 1318.51), (0.38, 1046.50)):
        voices += [
            (start, f, 1.0, 3.2, 0.004),
            (start, f * 2.0, 0.28, 5.0, 0.004),
            (start, f * 3.0, 0.08, 7.0, 0.004),
        ]
    return _render(1.9, voices)


def _synth_bell():
    # Campana con parciales inarmónicos (hum, prime, tierce, quint, nominal...)
    f0 = 523.25
    partials = (
        (0.5, 0.35, 0.9), (1.0, 1.0, 1.4), (1.19, 0.45, 1.8), (1.5, 0.30, 2.2),
        (2.0, 0.55, 2.0), (2.5, 0.20, 3.0), (2.67, 0.15, 3.4), (3.0, 0.10, 4.0),
    )
    voices = [(0.0, f0 * r, a, d, 0.003) for r, a, d in partials]
    return _render(2.8, voices)


def _synth_digital():
    # Clásico despertador digital: cuatro pitidos cortos y una pausa
    n = int(1.1 * SAMPLE_RATE)
    buf = [0.0] * n
    freq = 2048.0
    beep_len, gap, fade = 0.085, 0.065, 0.004
    w = 2.0 * math.pi * freq / SAMPLE_RATE
    for b in range(4):
        first = int(b * (beep_len + gap) * SAMPLE_RATE)
        length = int(beep_len * SAMPLE_RATE)
        for j in range(length):
            t = j / SAMPLE_RATE
            env = min(1.0, t / fade, (beep_len - t) / fade)
            phase = w * j
            # Onda casi cuadrada suavizada (fundamental + 3º y 5º armónico)
            buf[first + j] += env * (math.sin(phase) + 0.30 * math.sin(3 * phase) + 0.12 * math.sin(5 * phase))
    return buf


def _synth_soft():
    # Arpegio ascendente tipo marimba (Do5, Mi5, Sol5, Do6)
    voices = []
    for idx, f in enumerate((523.25, 659.25, 783.99, 1046.50)):
        start = idx * 0.16
        voices += [
            (start, f, 1.0, 5.5, 0.006),
            (start, f * 4.0, 0.12, 14.0, 0.002),
        ]
    return _render(1.6, voices)


_SYNTHS = {
    "chime": _synth_chime,
    "bell": _synth_bell,
    "digital": _synth_digital,
    "soft": _synth_soft,
}


def _write_wav(path, samples):
    peak = max((abs(s) for s in samples), default=1.0) or 1.0
    scale = 0.8 * 32767 / peak
    frames = b"".join(struct.pack("<h", int(s * scale)) for s in samples)
    tmp_path = path + ".tmp"
    with wave.open(tmp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)
    os.replace(tmp_path, path)


def sounds_cache_dir():
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericCacheLocation)
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "clock-timer", "sounds")


def ensure_sound_file(name):
    """Devuelve la ruta del .wav sintetizado, generándolo si aún no existe en caché."""
    if name not in _SYNTHS:
        return None
    directory = sounds_cache_dir()
    path = os.path.join(directory, f"{name}_v{SOUND_VERSION}.wav")
    if not os.path.exists(path):
        os.makedirs(directory, exist_ok=True)
        _write_wav(path, _SYNTHS[name]())
    return path


def wav_duration(path):
    try:
        with wave.open(path, "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())
    except (wave.Error, OSError, EOFError, ZeroDivisionError):
        return None


# -------------------------------------------------------------- reproducción
class AlarmPlayer(QObject):
    """Reproduce el sonido de alarma configurado en config.ini."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._effect = QSoundEffect(self) if QSoundEffect is not None else None
        self._source_path = None

    def _resolve(self):
        """Devuelve (modo, ruta). Modo: 'file', 'system' o 'none'."""
        sound = config.get("alarm.sound")
        if sound == "none":
            return "none", None
        if sound == "custom":
            custom = os.path.expanduser(config.get("alarm.custom_sound"))
            if custom and os.path.isfile(custom) and custom.lower().endswith(".wav"):
                return ("file", custom) if self._effect else ("system", None)
            sound = "chime"  # Ruta inválida: volver al sonido por defecto
        if sound == "system" or self._effect is None:
            return "system", None
        try:
            return "file", ensure_sound_file(sound)
        except OSError:
            return "system", None

    def prepare(self):
        """Precarga el sonido actual para que la alarma suene sin retraso."""
        mode, path = self._resolve()
        if mode == "file":
            self._set_source(path)

    def _set_source(self, path):
        if path != self._source_path:
            self._effect.setSource(QUrl.fromLocalFile(path))
            self._source_path = path

    def _play(self, loops):
        mode, path = self._resolve()
        if mode == "none":
            return
        if mode == "system":
            QApplication.beep()
            return
        self._set_source(path)
        self._effect.stop()
        self._effect.setVolume(config.get("alarm.volume") / 100.0)
        self._effect.setLoopCount(max(1, loops))
        self._effect.play()

    def play_alarm(self):
        """Repite el sonido el número de veces necesario para cubrir la duración configurada."""
        mode, path = self._resolve()
        loops = 1
        if mode == "file":
            length = wav_duration(path) or 1.0
            loops = max(1, math.ceil(config.get("alarm.duration") / max(length, 0.2)))
        self._play(loops)

    def preview(self):
        self._play(1)

    def on_flash(self):
        """En modo 'system' el beep acompaña cada parpadeo, como en versiones anteriores."""
        if config.get("alarm.sound") == "system":
            QApplication.beep()

    def stop(self):
        if self._effect is not None:
            self._effect.stop()
