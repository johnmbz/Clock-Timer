from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QSpinBox
)
from PyQt6.QtCore import Qt
from ...core.i18n import i18n
from ..styles import DIALOG_STYLE


class TimeSetupDialog(QDialog):
    """Diálogo modal moderno para configurar minutos y segundos con precisión."""
    def __init__(self, current_seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("dialog_title"))
        self.setFixedSize(300, 270)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Contenedor de diales (Minutos y Segundos)
        dials_layout = QHBoxLayout()
        dials_layout.setSpacing(12)
        dials_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        min_title = i18n.t("dialog_min").upper().replace(":", "")
        sec_title = i18n.t("dialog_sec").upper().replace(":", "")

        min_layout, self.spin_min = self._create_stepper(min_title, 999, current_seconds // 60)
        sec_layout, self.spin_sec = self._create_stepper(sec_title, 59, current_seconds % 60)

        sep_label = QLabel(":")
        sep_label.setObjectName("DialogSeparator")
        sep_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dials_layout.addLayout(min_layout)
        dials_layout.addWidget(sep_label)
        dials_layout.addLayout(sec_layout)
        layout.addLayout(dials_layout)

        # Chips de presets rápidos
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for text, m in [("+1m", 1), ("+5m", 5), ("+15m", 15), ("00:00", 0)]:
            chip = QPushButton(text)
            chip.setProperty("class", "PresetChip")
            if m == 0:
                chip.clicked.connect(lambda: (self.spin_min.setValue(0), self.spin_sec.setValue(0)))
            else:
                chip.clicked.connect(lambda _, mins=m: self.spin_min.setValue(self.spin_min.value() + mins))
            chips_layout.addWidget(chip)
        layout.addLayout(chips_layout)

        # Botones de Acción (Aceptar / Cancelar)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        btn_cancel = QPushButton(i18n.t("dialog_cancel"))
        btn_cancel.setObjectName("BtnCancel")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton(i18n.t("dialog_ok"))
        btn_ok.setObjectName("BtnOk")
        btn_ok.clicked.connect(self.accept)

        actions_layout.addWidget(btn_cancel)
        actions_layout.addWidget(btn_ok)
        layout.addLayout(actions_layout)

    @staticmethod
    def _create_stepper(title, max_val, cur_val):
        container = QVBoxLayout()
        container.setSpacing(4)
        container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(title)
        lbl.setProperty("class", "SectionTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(lbl)

        card = QWidget()
        card.setProperty("class", "StepperCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        btn_up = QPushButton("▲")
        btn_up.setObjectName("BtnUp")
        btn_up.setProperty("class", "StepperBtn")
        btn_up.setAutoRepeat(True)
        btn_up.setAutoRepeatDelay(280)
        btn_up.setAutoRepeatInterval(70)

        spin = QSpinBox()
        spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setRange(0, max_val)
        spin.setValue(cur_val)

        btn_down = QPushButton("▼")
        btn_down.setObjectName("BtnDown")
        btn_down.setProperty("class", "StepperBtn")
        btn_down.setAutoRepeat(True)
        btn_down.setAutoRepeatDelay(280)
        btn_down.setAutoRepeatInterval(70)

        btn_up.clicked.connect(spin.stepUp)
        btn_down.clicked.connect(spin.stepDown)

        card_layout.addWidget(btn_up)
        card_layout.addWidget(spin)
        card_layout.addWidget(btn_down)

        container.addWidget(card)
        return container, spin

    def get_total_seconds(self):
        return (self.spin_min.value() * 60) + self.spin_sec.value()
