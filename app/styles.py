"""
Estilos modernos (QSS) para el widget de Reloj y Temporizador flotante.
Diseño oscuro minimalista con esquinas redondeadas y acentos visuales vibrantes.
"""

MAIN_STYLE = """
/* Ventana principal */
QWidget#MainContainer {
    background-color: #141419;
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
    color: #ffffff;
    background-color: #242432;
}

QPushButton.NavButton:checked {
    color: #00d2ff;
    background-color: #172233;
    border: 1px solid #00d2ff44;
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
    color: #ffffff;
    background-color: #242432;
}

QPushButton.WindowControl#CloseButton:hover {
    background-color: #e63946;
    color: #ffffff;
}

QPushButton.WindowControl#PinButton:checked,
QPushButton.WindowControl#SettingsButton:checked {
    color: #00d2ff;
    background-color: #172233;
    border: 1px solid #00d2ff55;
}

QPushButton.WindowControl#MiniHudButton:hover {
    color: #00d2ff;
    background-color: #172233;
}




/* Textos principales */
QLabel.TimeDisplay {
    color: #ffffff;
    font-family: 'Monospace', 'Consolas', 'Courier New', 'DejaVu Sans Mono';
    font-weight: 700;
    qproperty-alignment: AlignCenter;
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
    background-color: #00d2ff;
    color: #080c14;
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
    background-color: #38e1ff;
}

QPushButton.PrimaryAction:pressed {
    background-color: #00b4db;
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
    color: #ffffff;
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
    color: #00d2ff;
    border-color: #00d2ff;
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
    color: #00d2ff;
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
    background-color: #00d2ff;
    color: #0d0d14;
    border-color: #00d2ff;
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
    color: #ffffff;
}

QPushButton.LangButton:checked {
    background-color: #00d2ff;
    color: #0c1017;
    border-color: #00d2ff;
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
    border-color: #00d2ff88;
    color: #ffffff;
}

QComboBox#SoundCombo::drop-down {
    border: none;
    width: 14px;
}

QComboBox#SoundCombo QAbstractItemView {
    background-color: #1a1a26;
    color: #e0e0ee;
    border: 1px solid #2d2d3f;
    selection-background-color: #00d2ff;
    selection-color: #0c1017;
    outline: 0;
    padding: 2px;
}

/* Botones circulares para Mini-HUD */
QPushButton.MiniAction {
    background-color: #00d2ff;
    color: #0c1017;
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
    background-color: #38e1ff;
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
    color: #ffffff;
}

/* Control deslizante de opacidad / settings */
QSlider::groove:horizontal {
    height: 4px;
    background: #252533;
    border-radius: 2px;
}


QSlider::sub-page:horizontal {
    background: #00d2ff;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #ffffff;
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
"""

