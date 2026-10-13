import os
import sys
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication

# Instancia global de QApplication para las pruebas
app = QApplication.instance() or QApplication(sys.argv)

from app.core.timer_model import TimerModel, TimerState, format_seconds
from app.core.i18n import i18n
from app.core.config import config
from app.ui.window import FloatingClockTimerWindow
from app.ui.widgets.page import PageWidget
from app.ui.widgets.clock_widget import ClockWidget
from app.ui.widgets.timer_widget import TimerWidget


class TestTimerModel(unittest.TestCase):
    def test_format_seconds(self):
        self.assertEqual(format_seconds(0), "00:00")
        self.assertEqual(format_seconds(59), "00:59")
        self.assertEqual(format_seconds(60), "01:00")
        self.assertEqual(format_seconds(3599), "59:59")
        self.assertEqual(format_seconds(3600), "01:00:00")
        self.assertEqual(format_seconds(3665), "01:01:05")

    def test_initial_state(self):
        model = TimerModel()
        self.assertEqual(model.state, TimerState.IDLE)
        self.assertEqual(model.remaining_seconds, 0)
        self.assertEqual(model.initial_seconds, 0)
        self.assertFalse(model.has_time)

    def test_add_and_set_time(self):
        model = TimerModel()
        model.add_time(300)
        self.assertEqual(model.remaining_seconds, 300)
        self.assertEqual(model.initial_seconds, 300)
        self.assertEqual(model.state, TimerState.IDLE)

        model.set_time(60)
        self.assertEqual(model.remaining_seconds, 60)
        self.assertEqual(model.initial_seconds, 60)

    def test_start_pause_reset_clear(self):
        model = TimerModel()
        # No se puede iniciar sin tiempo
        self.assertFalse(model.start())

        model.set_time(100)
        self.assertTrue(model.start())
        self.assertEqual(model.state, TimerState.RUNNING)

        model.pause()
        # Si no hubo ticks pero está en pausa tras iniciar, se detiene
        self.assertFalse(model.is_running)

        model.tick()
        self.assertEqual(model.remaining_seconds, 99)
        self.assertEqual(model.state, TimerState.PAUSED)

        model.reset()
        self.assertEqual(model.remaining_seconds, 100)
        self.assertEqual(model.state, TimerState.IDLE)

        model.clear()
        self.assertEqual(model.remaining_seconds, 0)
        self.assertEqual(model.initial_seconds, 0)
        self.assertEqual(model.state, TimerState.IDLE)

    def test_countdown_finishes(self):
        model = TimerModel()
        model.set_time(1)
        model.start()

        finished_called = []
        model.finished.connect(lambda: finished_called.append(True))

        model.tick()  # 1 -> 0
        self.assertEqual(model.remaining_seconds, 0)
        self.assertEqual(len(finished_called), 0)

        model.tick()  # 0 -> finished
        self.assertEqual(len(finished_called), 1)
        self.assertEqual(model.state, TimerState.IDLE)
        self.assertEqual(model.remaining_seconds, 0)
        self.assertEqual(model.initial_seconds, 0)


class TestI18n(unittest.TestCase):
    def test_translations_and_formatting(self):
        orig_lang = i18n.get_lang()
        try:
            i18n.set_lang("es")
            self.assertEqual(i18n.t("tab_clock"), "Reloj")
            self.assertIn("75%", i18n.t("opacity_tooltip", value=75))

            i18n.set_lang("en")
            self.assertEqual(i18n.t("tab_clock"), "Clock")
            self.assertIn("75%", i18n.t("opacity_tooltip", value=75))
        finally:
            i18n.set_lang(orig_lang)


class TestConfig(unittest.TestCase):
    def test_get_and_validate(self):
        self.assertIn(config.get("general.language"), ("es", "en"))
        self.assertIsInstance(config.get("general.opacity"), int)
        self.assertGreaterEqual(config.get("general.opacity"), 30)
        self.assertLessEqual(config.get("general.opacity"), 100)


class TestWindowAndPageArchitecture(unittest.TestCase):
    def setUp(self):
        self.win = FloatingClockTimerWindow()
        self.win.show()

    def tearDown(self):
        self.win.close()

    def test_pages_registered(self):
        page_ids = [p.PAGE_ID for p in self.win.pages]
        self.assertIn("clock", page_ids)
        self.assertIn("timer", page_ids)

    def test_page_navigation(self):
        self.win.show_clock()
        self.assertEqual(self.win.current_page.PAGE_ID, "clock")

        self.win.show_timer()
        self.assertEqual(self.win.current_page.PAGE_ID, "timer")

        self.win.show_next_page()
        self.assertEqual(self.win.current_page.PAGE_ID, "clock")

    def test_mini_hud_toggle(self):
        initial = self.win.is_mini_mode
        self.win.toggle_mini_hud()
        # Se activa la transición o modo
        self.win.toggle_mini_hud()

    def test_settings_visibility(self):
        self.win.set_settings_visible(True)
        self.assertTrue(self.win.settings_panel.isVisible())
        self.win.set_settings_visible(False)
        self.assertFalse(self.win.settings_panel.isVisible())

    def test_add_custom_page(self):
        """Demuestra la facilidad de añadir una nueva funcionalidad (ej. Cronómetro)."""
        class DummyStopwatchPage(PageWidget):
            PAGE_ID = "stopwatch"
            ICON = "⏱"
            TITLE_KEY = "tab_stopwatch"
            TRAY_KEY = "tray_stopwatch"

        custom_page = DummyStopwatchPage(self.win.stack)
        self.win.add_page(custom_page)

        self.assertIn("stopwatch", [p.PAGE_ID for p in self.win.pages])
        self.win.show_page("stopwatch")
        self.assertEqual(self.win.current_page.PAGE_ID, "stopwatch")


if __name__ == "__main__":
    unittest.main()
