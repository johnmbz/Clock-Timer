"""
Estilos modernos (QSS) para el widget de Reloj y Temporizador flotante.
Diseño oscuro minimalista con esquinas redondeadas y acentos visuales vibrantes.

Todos los colores de la aplicación viven en este archivo. Los colores con
significado (acento, alerta, etc.) se definen una sola vez en PALETTE y se
insertan en las hojas QSS con la sintaxis $nombre / ${nombre}: cambiar el
acento de toda la app es cambiar una línea.

Los estados dinámicos (temporizador en marcha, alarma) usan la propiedad Qt
"state" y se aplican con `apply_state(widget, "running")`.
"""
from string import Template

PALETTE = {
    "bg": "#141419",              # Fondo de la ventana
    "surface": "#14141c",         # Fondo de menús y diálogos
    "text": "#ffffff",
    "accent": "#00d2ff",          # Cian principal
    "accent_hover": "#38e1ff",
    "accent_pressed": "#00b4db",
    "accent_bg": "#172233",       # Fondo de botones activos
    "on_accent": "#0c1017",       # Texto sobre el acento
    "warning": "#ff9f1c",         # Botón de pausa con el temporizador en marcha
    "danger": "#ff3366",          # Parpadeo de alarma
    "danger_bg": "#331122",
    "close_hover": "#e63946",
}


def _qss(template):
    return Template(template).substitute(PALETTE)


def apply_state(widget, state):
    """Asigna la propiedad 'state' usada por los selectores QSS y re-pule el estilo."""
    if widget.property("state") == state:
        return
    widget.setProperty("state", state)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)


MAIN_STYLE = _qss("""
/* Ventana principal */
QWidget#MainContainer {
    background-color: $bg;
    border: 1.5px solid #2a2a35;
    border-radius: 16px;
}

/* Barra superior de control / arrastre */
QWidget#TitleBar {
    background-color: transparent;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}

/* Botones de navegación (Reloj / Timer) con iconos */
QPushButton.NavButton {
    background-color: transparent;
    color: #9292a8;
    border: none;
    border-radius: 6px;
    font-size: 15px;
    padding: 2px;
    min-width: 28px;
    max-width: 28px;
    min-height: 26px;
    max-height: 26px;
}

QPushButton.NavButton:hover {
    color: $text;
    background-color: #242432;
}

QPushButton.NavButton:checked {
    color: $accent;
    background-color: $accent_bg;
    border: 1px solid ${accent}44;
}

/* Botones de control de ventana (Mini-HUD, Pin, Ajustes, Cerrar) */
QPushButton.WindowControl {
    background-color: transparent;
    color: #a0a0ba;
    border: none;
    border-radius: 6px;
    padding: 2px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}

QPushButton.WindowControl#PinButton {
    font-size: 13px;
}

QPushButton.WindowControl#SettingsButton {
    font-size: 16px;
}

QPushButton.WindowControl#MiniHudButton {
    font-size: 16px;
    font-weight: bold;
}

QPushButton.WindowControl#CloseButton {
    font-size: 14px;
    font-weight: bold;
}

QPushButton.WindowControl:hover {
    color: $text;
    background-color: #242432;
}

QPushButton.WindowControl#CloseButton:hover {
    background-color: $close_hover;
    color: $text;
}

QPushButton.WindowControl#PinButton:checked,
QPushButton.WindowControl#SettingsButton:checked {
    color: $accent;
    background-color: $accent_bg;
    border: 1px solid ${accent}55;
}

QPushButton.WindowControl#MiniHudButton:hover {
    color: $accent;
    background-color: $accent_bg;
}

/* Textos principales */
QLabel.TimeDisplay {
    color: $text;
    background-color: transparent;
    font-family: 'Monospace', 'Consolas', 'Courier New', 'DejaVu Sans Mono';
    font-weight: 700;
    qproperty-alignment: AlignCenter;
}

QLabel.TimeDisplay[state="running"] {
    color: $accent;
}

QLabel.TimeDisplay[state="alarm"] {
    color: $danger;
    background-color: $danger_bg;
    border-radius: 8px;
}

QLabel.DateDisplay {
    color: #82829b;
    font-size: 12px;
    font-weight: 500;
    qproperty-alignment: AlignCenter;
}

QLabel.SecondaryText {
    color: #6b6b80;
    font-size: 11px;
    qproperty-alignment: AlignCenter;
}

/* Botones de acción del temporizador (Iconos minimalistas) */
QPushButton.PrimaryAction {
    background-color: $accent;
    color: $on_accent;
    font-weight: bold;
    font-size: 16px;
    border: none;
    border-radius: 19px;
    min-width: 44px;
    max-width: 44px;
    min-height: 38px;
    max-height: 38px;
    padding: 0;
}

QPushButton.PrimaryAction:hover {
    background-color: $accent_hover;
}

QPushButton.PrimaryAction:pressed {
    background-color: $accent_pressed;
}

QPushButton.SecondaryAction {
    background-color: #1a1a26;
    color: #a0a0ba;
    font-weight: bold;
    font-size: 15px;
    border: 1px solid #2d2d3e;
    border-radius: 19px;
    min-width: 38px;
    max-width: 38px;
    min-height: 38px;
    max-height: 38px;
    padding: 0;
}

QPushButton.SecondaryAction:hover {
    background-color: #272738;
    color: $text;
    border-color: #404058;
}

QPushButton.PrimaryAction[mini="true"] {
    padding: 3px 10px;
    font-size: 11px;
    border-radius: 6px;
}

QPushButton.SecondaryAction[mini="true"] {
    padding: 3px 8px;
    font-size: 11px;
    border-radius: 6px;
}

/* Botones rápidos de preajustes (+1m, +5m, etc.) */
QPushButton.PresetButton {
    background-color: #1a1a24;
    color: #9d9db5;
    border: 1px solid #282837;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 4px;
}

QPushButton.PresetButton:hover {
    background-color: #272738;
    color: $accent;
    border-color: $accent;
}

/* Barra de control de opacidad */
QWidget#OpacityBar {
    background-color: #1a1a26;
    border: 1px solid #2b2b3d;
    border-radius: 8px;
    padding: 3px 8px;
}

QLabel#OpacityLabel {
    color: #9d9db5;
    font-size: 10px;
    font-weight: 600;
}

QLabel#OpacityValue {
    color: $accent;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Monospace', 'Consolas', 'DejaVu Sans Mono';
    min-width: 28px;
}

QPushButton.OpacityPreset {
    background-color: #242436;
    color: #a0a0b8;
    border: 1px solid #333348;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 4px;
}

QPushButton.OpacityPreset:hover {
    background-color: $accent;
    color: $on_accent;
    border-color: $accent;
}

/* Panel desplegable unificado de Ajustes */
QWidget#SettingsPanel {
    background-color: #1a1a26;
    border: 1px solid #2b2b3d;
    border-radius: 10px;
    padding: 4px 6px;
}

QLabel#SettingsLabel {
    color: #9d9db5;
    font-size: 11px;
    font-weight: 600;
}

QPushButton.LangButton {
    background-color: #242436;
    color: #a0a0b8;
    border: 1px solid #333348;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
}

QPushButton.LangButton:hover {
    background-color: #2d2d42;
    color: $text;
}

QPushButton.LangButton:checked {
    background-color: $accent;
    color: $on_accent;
    border-color: $accent;
    font-weight: 700;
}

/* Selector de sonido de alarma */
QComboBox#SoundCombo {
    background-color: #242436;
    color: #d0d0e2;
    border: 1px solid #333348;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    min-height: 16px;
}

QComboBox#SoundCombo:hover {
    border-color: ${accent}88;
    color: $text;
}

QComboBox#SoundCombo::drop-down {
    border: none;
    width: 14px;
}

QComboBox#SoundCombo QAbstractItemView {
    background-color: #1a1a26;
    color: #e0e0ee;
    border: 1px solid #2d2d3f;
    selection-background-color: $accent;
    selection-color: $on_accent;
    outline: 0;
    padding: 2px;
}

/* Botones circulares para Mini-HUD */
QPushButton.MiniAction {
    background-color: $accent;
    color: $on_accent;
    font-weight: 700;
    font-size: 11px;
    border: none;
    border-radius: 13px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}

QPushButton.MiniAction:hover {
    background-color: $accent_hover;
}

/* Botón Iniciar/Pausar con el temporizador en marcha (va tras :hover para prevalecer) */
QPushButton.PrimaryAction[state="running"],
QPushButton.PrimaryAction[state="running"]:hover,
QPushButton.PrimaryAction[state="running"]:pressed,
QPushButton.MiniAction[state="running"],
QPushButton.MiniAction[state="running"]:hover {
    background-color: $warning;
    color: $bg;
}

QPushButton.MiniReset {
    background-color: #22222e;
    color: #d1d1e0;
    font-weight: 600;
    font-size: 11px;
    border: 1px solid #333344;
    border-radius: 13px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}

QPushButton.MiniReset:hover {
    background-color: #2d2d3d;
    color: $text;
}

/* Control deslizante de opacidad / settings */
QSlider::groove:horizontal {
    height: 4px;
    background: #252533;
    border-radius: 2px;
}


QSlider::sub-page:horizontal {
    background: $accent;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: $text;
    width: 12px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 6px;
}

/* Grip de redimensionamiento */
QSizeGrip {
    width: 16px;
    height: 16px;
    background: transparent;
}
""")


TRAY_MENU_STYLE = _qss("""
QMenu {
    background-color: $surface;
    color: $text;
    border: 1.5px solid #2d2d3f;
    border-radius: 8px;
    padding: 4px;
    font-size: 12px;
}
QMenu::item {
    padding: 6px 18px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: $accent;
    color: $on_accent;
    font-weight: bold;
}
QMenu::separator {
    height: 1px;
    background-color: #282838;
    margin: 4px 6px;
}
""")


DIALOG_STYLE = _qss("""
QDialog {
    background-color: $surface;
    color: $text;
    border-radius: 16px;
    border: 1.5px solid #2d2d3f;
}
QLabel.SectionTitle {
    color: #8c8ca8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#DialogSeparator {
    color: #4a4a66;
    font-size: 30px;
    font-weight: bold;
    margin-top: 14px;
}
/* Stepper Card unificado */
QWidget.StepperCard {
    background-color: #1c1c28;
    border: 1.5px solid #2f2f44;
    border-radius: 12px;
}
QSpinBox {
    background-color: transparent;
    color: $accent;
    border: none;
    font-size: 30px;
    font-weight: 800;
    font-family: 'Monospace', 'Consolas', 'DejaVu Sans Mono';
    qproperty-alignment: AlignCenter;
    min-width: 80px;
    max-width: 80px;
    min-height: 44px;
}
QPushButton.StepperBtn {
    background-color: transparent;
    color: #7b7b99;
    border: none;
    font-size: 13px;
    font-weight: bold;
    min-width: 80px;
    max-width: 80px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton.StepperBtn:hover {
    color: $accent;
    background-color: #262638;
}
QPushButton.StepperBtn#BtnUp {
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
QPushButton.StepperBtn#BtnDown {
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}
/* Chips de presets rápidos */
QPushButton.PresetChip {
    background-color: #1a1a26;
    color: #9090aa;
    border: 1px solid #2a2a3c;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 8px;
}
QPushButton.PresetChip:hover {
    background-color: #252538;
    color: $accent;
    border-color: ${accent}55;
}
/* Botón Aceptar primario */
QPushButton#BtnOk {
    background-color: $accent;
    color: $on_accent;
    font-weight: 700;
    font-size: 12px;
    border: none;
    border-radius: 8px;
    padding: 7px 18px;
}
QPushButton#BtnOk:hover {
    background-color: $accent_hover;
}
/* Botón Cancelar secundario */
QPushButton#BtnCancel {
    background-color: #222230;
    color: #c0c0d4;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid #333346;
    border-radius: 8px;
    padding: 7px 16px;
}
QPushButton#BtnCancel:hover {
    background-color: #2a2a3e;
    color: $text;
}
""")
