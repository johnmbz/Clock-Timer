# Changelog

All notable changes to **Clock & Timer** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] - 2026-10-04

### Bug Fixes
- **Timer Reset on Completion**: Fixed an issue where the previous timer duration remained in memory after the countdown completed. Adding a new duration (e.g. `+1m`) after a timer finished now properly sets the exact requested time (`01:00`) instead of accumulating on top of the previous historical duration (`02:00`).
- **Timer Extension while Paused**: Preserved elapsed time and cleanly added duration when clicking preset buttons while the timer is running or paused.
- **UI Hint Transitions**: Updated idle and finished status hint labels to seamlessly reflect active alarms and state transitions.

---

## [1.3.0] - 2026-09-29

### Added and Enhanced
- **Wayland / XWayland Support**: Added automatic fallback to `QT_QPA_PLATFORM="xcb;wayland"` under Wayland sessions where XWayland is present. This resolves native Wayland protocol restrictions that prevent always-on-top floating desktop widgets and custom placement.
- **Ubuntu 26.04 & Python 3.14 Compatibility**: Updated launcher script (`run.sh`) to automatically detect system Python environment changes, validate PyQt6 integrity, and re-create `.venv` seamlessly upon system upgrades.
- **Fluid macOS / Ubuntu Style Morphing**: Implemented coordinated transition animations using `QParallelAnimationGroup`, an `OutCubic` geometry curve, and gradual opacity fading when switching between standard and Mini-HUD modes.
- **Mini-HUD Proportions & Geometry**: Increased Mini-HUD height from 75px to 92px, providing comfortable vertical breathing room and preventing digits and buttons from clipping against rounded container borders.
- **Circular Control Preservation**: Enforced `border-radius: 13px` (and 19px for full view) on timer toggle buttons during active states to maintain perfect circular geometry without flattening.
- **Title Bar Stability**: Positioned the collapse/expand toggle button adjacent to the close button to eliminate horizontal jumping during mode transitions.

---

## [1.2.0] - 2026-09-28

### Bug Fixes
- **Notifications**: Fixed desktop notification freeze on Linux where the banner remained stuck indefinitely on the screen due to `-u critical`. Urgency is now set to `normal`, strictly honoring the 5-second automatic timeout (`-t 5000`).
- **Notifications**: Fixed missing application title and generic system gear icon in desktop alerts by explicitly passing `--app-name="Clock & Timer"` (`-a`) and the application icon (`-i`).
- **Window Positioning**: Fixed window recentering bug when toggling between standard mode and Mini-HUD mode. The window now remembers and restores the exact user-defined screen position with multi-monitor boundary clamping.
- **UI Layout**: Fixed button text clipping ("Reanud", "Reinicia", "Borra") in compact widths by transitioning to modern minimalist icons (`▶`, `⏸`, `↺`, `🗑`).
- **Dialog Controls**: Fixed broken spinbox arrows in the Time Setup dialog by implementing dedicated auto-repeating stepper cards and quick chip buttons.

### Added and Enhanced
- **System Tray Integration**: Added background system tray icon with a contextual menu to toggle visibility, switch between Clock and Timer modes, and exit cleanly.
- **Windows Native Notifications**: Integrated `QSystemTrayIcon.showMessage()` providing native Windows 10/11 Action Center toast notifications with app branding and sound.
- **Minimalist Icon Navigation**: Streamlined tab navigation using intuitive clock and hourglass icons with full localized tooltips.
- **Executable Naming**: Standardized Windows executable naming to `Clock & Timer.exe` to match the Linux and AppStream metadata identity.

---

## [1.1.1] - 2026-09-27

### UI and UX Improvements
- **Dual Click-or-Drag Gestures**: Implemented GNOME-style dual click-or-drag interaction on navigation tabs and time displays.
- **Window Movement**: Enabled smooth full-window dragging from anywhere across Wayland, X11, and Windows.

---

## [1.1.0] - 2026-09-27

### Added and Enhanced
- **Mini-HUD Focus Mode**: Added ultra-compact Mini-HUD mode with integrated horizontal controls for clutter-free workflows.
- **Dynamic Font Autoscaling**: Implemented responsive font scaling for multi-hour displays.
- **Quick Presets**: Added `+1h` preset button alongside `+1m`, `+5m`, `+15m`, and `+25m`.
- **Quick Clear**: Added dedicated Clear (Trash) button to reset time to `00:00` instantly.
- **Unified Header**: Redesigned minimalist header with unified collapsible Settings panel for opacity and language selection.

---

## [1.0.0] - 2026-09-27

### Initial Release
- **Always-on-Top Floating Widget**: Resizable frameless desktop dialog with smooth rounded corners.
- **Clock Mode**: Responsive 12h/24h digital clock with localized calendar date.
- **Timer Mode**: Countdown timer with presets, audio alerts, and desktop notifications.
- **Opacity Control**: Interactive opacity slider and mouse wheel brightness adjustment.
- **Bilingual Support**: Instant hot-switching between Spanish and English.
