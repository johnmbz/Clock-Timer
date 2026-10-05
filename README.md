# Clock & Timer

<p align="center">
  <img src="assets/icons/io.github.JohnmaDev.Clock-Timer.png" width="128" height="128" alt="Clock & Timer Logo" />
</p>

<p align="center">
  <strong>A modern, minimalist, always-on-top desktop clock and countdown timer widget.</strong><br>
  <em>Diseñado para Linux (Ubuntu, Fedora, Arch) y compatible con Windows.</em>
</p>

<p align="center">
  <a href="https://github.com/JohnmaDev/Clock-Timer/releases"><img src="https://img.shields.io/github/v/release/JohnmaDev/Clock-Timer?color=00d2ff&style=flat-square" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue.svg?style=flat-square" alt="Platform Support">
  <img src="https://img.shields.io/badge/Python-3.10%2B-yellow.svg?style=flat-square" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-PyQt6-blueviolet.svg?style=flat-square" alt="PyQt6">
</p>

---

## Screenshots

<p align="center">
  <img src="assets/screenshots/preview_clock.png" width="48%" alt="Clock View" />
  <img src="assets/screenshots/preview_timer.png" width="48%" alt="Timer View" />
</p>
<p align="center">
  <em>Clock View (24h/12h toggle) &nbsp;&bull;&nbsp; Minimalist Timer View (Icon actions & quick presets)</em>
</p>

<p align="center">
  <img src="assets/screenshots/preview_mini_hud.png" width="60%" alt="Mini-HUD Focus Mode" />
</p>
<p align="center">
  <em>Mini-HUD Focus Mode (Ultra-compact 230x92 px floating strip)</em>
</p>

<p align="center">
  <img src="assets/screenshots/preview_time_setup.png" width="48%" alt="Time Setup Stepper Dialog" />
  <img src="assets/screenshots/preview_settings.png" width="48%" alt="Settings & Opacity Control" />
</p>
<p align="center">
  <em>Precision Stepper Setup Dialog &nbsp;&bull;&nbsp; Unified Opacity & Language Settings</em>
</p>

---

## Features

- **Always on Top**: Permanece visible por encima de navegadores, editores de código, IDEs y juegos. Se activa o desactiva con el botón de fijación en la cabecera.
- **Wayland and X11 Support**: Detección y fallback automático a XWayland (`QT_QPA_PLATFORM="xcb;wayland"`) para garantizar compatibilidad con el modo siempre al frente en escritorios Wayland modernos.
- **Frameless and Ultra-Compact**: Interfaz oscura moderna sin barras toscas del sistema. Redimensionable desde sus cuatro bordes o esquina inferior (mínimo: 235 x 210 px).
- **Ultra-Lightweight** (~87 MB RAM, <0.2% CPU): Rendimiento nativo Qt6 sin el sobrecosto de Chromium ni frameworks web pesados. Significativamente más ligero que herramientas basadas en Electron.
- **Clock Mode**: Visualización limpia de hora con segundos y fecha completa localizada. Clic en los dígitos para alternar al instante entre formato 24h y formato 12h AM/PM.
- **Timer Mode**:
  - Controles minimalistas por iconos: Iniciar/Pausar (`▶`/`⏸`), Reiniciar (`↺`) y Borrar/Restablecer (`🗑`).
  - Presets rápidos: Botones inmediatos de `+1m`, `+5m`, `+15m`, `+25m (Pomodoro)` y `+1h`.
  - Selector dial de precisión: Clic en los números para abrir el configurador visual con botones paso a paso (`▲`/`▼`) y chips rápidos (`+1m`, `+5m`, `+15m`, `00:00`).
- **Mini-HUD Focus Mode**:
  - Tira horizontal ultra-compacta de 230 x 92 px que ocupa el mínimo espacio en pantalla.
  - Transición fluida con animaciones de morphing geométrico y desvanecimiento de controles inspiradas en macOS y Ubuntu.
  - Preserva la posición exacta donde colocaste la ventana sin saltar al centro al restaurarla.
  - Atajo rápido: Tecla `M` o `F`, o botón en la cabecera.
- **Desktop Notifications & Alarm Sounds**:
  - En Linux: Alarma de escritorio con nombre de aplicación (`Clock & Timer`), icono oficial y auto-cierre a los 5 segundos.
  - En Windows: Notificaciones nativas integradas con el Action Center.
  - Varios temas de sonido sintetizados en Python puro: *Campanilla (Chime)*, *Campana (Bell)*, *Digital*, *Suave (Soft)*, *Beep del sistema*, *Silencio* o archivo `.wav` personalizado.
  - Botón de preescucha (`▶`) en el panel de ajustes y parpadeo visual de alerta.
- **Centralized Configuration (`~/.config/clock-timer/config.ini`)**:
  - Archivo INI estándar, legible y comentado para usuarios de Linux y dotfiles.
  - Recarga en vivo automática al editar el archivo con cualquier editor de texto.
  - Acceso directo mediante el botón `…` en el panel de ajustes.
- **System Tray Integration**:
  - Icono residente en la bandeja del sistema para mostrar u ocultar la ventana, alternar entre modos o salir limpiamente.
- **Interactive Opacity Control**:
  - Barra deslizante de opacidad del 30% al 100% con saltos rápidos (`50%`, `75%`, `100%`) y persistencia automática.
  - Rueda del ratón: Gira la rueda del mouse en cualquier parte de la ventana para ajustar la transparencia al vuelo.
- **Bilingual Support (Español / English)**:
  - Selector instantáneo en el panel de ajustes con persistencia en `config.ini`.

---

## Keyboard and Mouse Controls

| Action | Control / Gesture |
| :--- | :--- |
| **Move window** | Clic y arrastre desde la cabecera, pestañas o dígitos del reloj |
| **Resize** | Arrastrar cualquiera de los 4 bordes o la esquina inferior derecha |
| **Adjust opacity on the fly** | Rueda del ratón en cualquier parte de la ventana |
| **Toggle Mini-HUD Mode** | Tecla `M`, tecla `F` o botón en la cabecera |
| **Start / Pause Timer** | Tecla `Space` o botón de reproducción / pausa |
| **Reset / Clear** | Botón de reinicio o papelera |
| **Switch Clock / Timer tab** | Tecla `Tab` o botones de navegación |
| **Toggle Settings Panel** | Botón de ajustes en la cabecera |
| **Toggle Always on Top** | Botón de fijación en la cabecera |
| **System Tray** | Clic en el icono de la bandeja para mostrar u ocultar |
| **Close app** | Tecla `Escape` o botón de cerrar |

---

## Installation and Usage

### Linux (Ubuntu / Debian / Fedora / Arch)

#### Option 1: Quick Launcher (Recommended)
```bash
git clone https://github.com/JohnmaDev/Clock-Timer.git
cd Clock-Timer
chmod +x run.sh
./run.sh
```
El script `run.sh` valida automáticamente la versión del entorno Python (incluyendo compatibilidad con Ubuntu 26.04 y Python 3.14), recrea el entorno virtual si es necesario e inicia con soporte XWayland automático.

#### Option 2: Run with Python venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

#### Option 3: Add to Desktop Menu / Dock
```bash
cp io.github.JohnmaDev.Clock-Timer.desktop ~/.local/share/applications/
```

---

### Windows

#### Portable Windows Executable
Descarga el ejecutable precompilado **`Clock & Timer.exe`** directamente desde la página de [GitHub Releases](https://github.com/JohnmaDev/Clock-Timer/releases).

O compílalo tú mismo con PyInstaller:
```cmd
pip install pyinstaller
pyinstaller --onefile --windowed --name "Clock & Timer" --icon "icon.ico" --add-data "app;app" --add-data "icon.png;." main.py
```

---

## Continuous Integration

El repositorio cuenta con integración continua automatizada en [`.github/workflows/release.yml`](.github/workflows/release.yml):
1. Valida los metadatos AppStream y `.desktop` con `appstreamcli` y `desktop-file-validate`.
2. Compila el binario independiente para Linux (`Clock-Timer-Linux-x86_64`), paquetes nativos `.deb` y `.rpm`, y `AppImage`.
3. Compila el ejecutable nativo para Windows (`Clock & Timer.exe`).
4. Genera automáticamente las notas de lanzamiento categorizadas ([`.github/release.yml`](.github/release.yml)) y publica la Release en GitHub con todos los archivos descargables.
5. Registra el historial de versiones en el [`CHANGELOG.md`](CHANGELOG.md) siguiendo el estándar *Keep a Changelog*.

---

## Project Structure

```text
Clock-Timer/
├── .github/
│   ├── release.yml                     # GitHub automated release notes categories
│   └── workflows/
│       └── release.yml                 # Automated Linux & Windows CI/CD release workflow
├── app/
│   ├── __init__.py                     # Package initialization
│   ├── clock_widget.py                 # Responsive clock display & 12h/24h toggle
│   ├── draggable_widgets.py            # GNOME-style dual click/drag gesture labels
│   ├── i18n.py                         # Internationalization engine (EN / ES) & settings
│   ├── styles.py                       # Modern dark-mode QSS stylesheets & minimalist icons
│   ├── timer_widget.py                 # Countdown timer, presets, alarms & stepper dialog
│   └── window.py                       # Frameless floating window, resizing, HUD & system tray
├── assets/
│   ├── branding/                       # Design concepts & exploration artwork
│   ├── icons/                          # Application icon (512x512 circular PNG)
│   └── screenshots/                    # UI preview screenshots
├── CHANGELOG.md                        # Standardized release changelog
├── io.github.JohnmaDev.Clock-Timer.desktop     # FreeDesktop desktop entry
├── io.github.JohnmaDev.Clock-Timer.metainfo.xml# AppStream 1.0 metadata
├── io.github.JohnmaDev.Clock-Timer.png         # Standard App ID icon
├── io.github.JohnmaDev.Clock-Timer.yaml        # Flatpak build manifest
├── LICENSE                             # MIT License
├── main.py                             # Application entry point
├── README.md                           # Documentation & showcase
├── requirements.txt                    # Python dependencies (PyQt6)
└── run.sh                              # Linux auto-launcher script
```

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more details.

Developed by [JohnmaDev](https://github.com/JohnmaDev).
