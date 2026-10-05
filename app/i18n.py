"""
Módulo de Internacionalización (i18n) para soporte de Español e Inglés.
Guarda la preferencia del usuario en config.ini (ver config.py).
"""
from .config import config

TRANSLATIONS = {
    "es": {
        "tab_clock": "Reloj",
        "tab_timer": "Timer",
        "pin_on": "Siempre al frente (Activado)",
        "pin_off": "Modo normal (no fijado)",
        "opacity_btn": "Ajustar transparencia",
        "opacity_lbl": "Opacidad:",
        "settings_btn": "Ajustes de idioma",
        "minimize": "Minimizar",
        "close": "Cerrar",
        "title_tooltip": "Arrastra para mover • Rueda del mouse para ajustar opacidad",
        "resize_tooltip": "Arrastra aquí para cambiar el tamaño",
        "clock_click_tooltip": "Haz clic para alternar entre formato 24h y 12h",
        "clock_24h_hint": "Formato 24h (clic para cambiar)",
        "clock_12h_hint": "Formato 12h AM/PM (clic para cambiar)",
        "days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
        "timer_click_tooltip": "Haz clic para escribir el tiempo exacto",
        "timer_hint_idle": "Clic en números para configurar",
        "timer_hint_running": "En progreso...",
        "timer_hint_paused": "En pausa",
        "timer_hint_finished": "¡Tiempo finalizado!",
        "timer_hint_ready": "Listo",
        "btn_start": "▶ Iniciar",
        "btn_pause": "⏸ Pausar",
        "btn_resume": "▶ Reanudar",
        "btn_reset": "↺ Reiniciar",
        "btn_clear": "Borrar",
        "btn_clear_tooltip": "Restablecer a 00:00",
        "notif_title": "⏰ ¡Temporizador!",
        "notif_msg": "El tiempo ha llegado a su fin.",
        "dialog_title": "Configurar Temporizador",
        "dialog_min": "Minutos:",
        "dialog_sec": "Segundos:",
        "dialog_ok": "Aceptar",
        "dialog_cancel": "Cancelar",
        "lang_label": "🌐 Idioma:",
        "mini_hud_shrink": "Modo Mini-HUD (Compactar)",
        "mini_hud_expand": "Expandir a vista completa",
        "sound_label": "🔔 Sonido:",
        "sound_chime": "Campanilla",
        "sound_bell": "Campana",
        "sound_digital": "Digital",
        "sound_soft": "Suave",
        "sound_system": "Beep del sistema",
        "sound_none": "Silencio",
        "sound_custom": "Personalizado (.wav)",
        "sound_preview": "Probar sonido",
        "open_config": "Abrir config.ini (opciones avanzadas)"
    },
    "en": {
        "tab_clock": "Clock",
        "tab_timer": "Timer",
        "pin_on": "Always on top (Enabled)",
        "pin_off": "Normal mode (unpinned)",
        "opacity_btn": "Adjust transparency",
        "opacity_lbl": "Opacity:",
        "settings_btn": "Settings (Opacity & Language)",
        "minimize": "Minimize",
        "close": "Close",
        "title_tooltip": "Drag to move • Mouse wheel to adjust opacity",
        "resize_tooltip": "Drag here to resize",
        "clock_click_tooltip": "Click to toggle between 24h and 12h format",
        "clock_24h_hint": "24h format (click to toggle)",
        "clock_12h_hint": "12h format AM/PM (click to toggle)",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "timer_click_tooltip": "Click to set exact time",
        "timer_hint_idle": "Click numbers to configure",
        "timer_hint_running": "In progress...",
        "timer_hint_paused": "Paused",
        "timer_hint_finished": "Time is up!",
        "timer_hint_ready": "Ready",
        "btn_start": "▶ Start",
        "btn_pause": "⏸ Pause",
        "btn_resume": "▶ Resume",
        "btn_reset": "↺ Reset",
        "btn_clear": "Clear",
        "btn_clear_tooltip": "Reset to 00:00",
        "notif_title": "⏰ Timer!",
        "notif_msg": "Time has run out.",
        "dialog_title": "Set Timer",
        "dialog_min": "Minutes:",
        "dialog_sec": "Seconds:",
        "dialog_ok": "OK",
        "dialog_cancel": "Cancel",
        "lang_label": "🌐 Lang:",
        "mini_hud_shrink": "Mini-HUD Mode (Compact)",
        "mini_hud_expand": "Expand to full view",
        "sound_label": "🔔 Sound:",
        "sound_chime": "Chime",
        "sound_bell": "Bell",
        "sound_digital": "Digital",
        "sound_soft": "Soft",
        "sound_system": "System beep",
        "sound_none": "Silent",
        "sound_custom": "Custom (.wav)",
        "sound_preview": "Preview sound",
        "open_config": "Open config.ini (advanced options)"
    }

}

class I18nManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # Idioma por defecto: español ('es'), validado por config.py
        self.current_lang = config.get("general.language")
        self._listeners = []
        # Si el usuario edita config.ini a mano, aplicar el idioma en vivo
        config.changed.connect(self._on_config_changed)

    def _on_config_changed(self, key):
        if key == "general.language":
            self._apply(config.get("general.language"))

    def get_lang(self):
        return self.current_lang

    def set_lang(self, lang):
        if lang in ("es", "en"):
            config.set("general.language", lang)
            self._apply(lang)

    def _apply(self, lang):
        if lang == self.current_lang:
            return
        self.current_lang = lang
        # Notificar a los widgets suscritos para que se actualicen en vivo
        for listener in self._listeners:
            try:
                listener()
            except Exception:
                pass

    def t(self, key):
        """Retorna la traducción para la clave solicitada en el idioma actual."""
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["es"])
        return lang_dict.get(key, key)

    def subscribe(self, callback):
        """Permite a los componentes suscribirse al cambio de idioma."""
        if callback not in self._listeners:
            self._listeners.append(callback)

# Instancia global única
i18n = I18nManager()
