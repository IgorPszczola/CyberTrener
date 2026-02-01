import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QRadioButton, QButtonGroup, QFrame, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Ustawienia")
        self.resize(1200, 850)

        self.bg_pixmap = None
        if os.path.exists("assets/background.jpg"):
            self.bg_pixmap = QPixmap("assets/background.jpg")

        self.init_ui()
        self.setStyleSheet(STYLESHEET)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter
        painter = QPainter(self)
        if self.bg_pixmap:
            scaled_bg = self.bg_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                              Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_bg.width()) // 2
            y = (self.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)
        else:
            painter.fillRect(self.rect(), QColor(20, 20, 20))

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(150, 80, 150, 80)
        main_layout.setSpacing(30)

        lbl_title = QLabel("USTAWIENIA TRENINGU")
        lbl_title.setProperty("class", "h1")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_title)
        main_layout.addSpacing(30)

        # Rząd 1: Liczba serii
        row1 = QFrame()
        row1.setProperty("class", "setting_row")
        r1_layout = QHBoxLayout(row1)
        r1_layout.setContentsMargins(20, 20, 20, 20)

        r1_label = QLabel("Liczba serii:")
        r1_label.setProperty("class", "label")

        lbl_sets_val = QLabel("1")  # Hardcoded for GUI view
        lbl_sets_val.setProperty("class", "value")
        lbl_sets_val.setFixedWidth(80)
        lbl_sets_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_minus = QPushButton("-")
        btn_minus.setProperty("class", "settings_control_btn")
        btn_minus.setFixedSize(60, 60)
        btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_plus = QPushButton("+")
        btn_plus.setProperty("class", "settings_control_btn")
        btn_plus.setFixedSize(60, 60)
        btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)

        r1_layout.addWidget(r1_label)
        r1_layout.addStretch()
        r1_layout.addWidget(btn_minus)
        r1_layout.addWidget(lbl_sets_val)
        r1_layout.addWidget(btn_plus)
        main_layout.addWidget(row1)

        # Rząd 2: Obciążenie
        row2 = QFrame()
        row2.setProperty("class", "setting_row")
        r2_layout = QHBoxLayout(row2)
        r2_layout.setContentsMargins(20, 20, 20, 20)

        lbl_weight = QLabel("Obciążenie (kg):")
        lbl_weight.setProperty("class", "label")

        self.weight = QLineEdit("1")
        self.weight.setFixedSize(120, 60)
        self.weight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weight.setProperty("class", "big_input")

        r2_layout.addWidget(lbl_weight)
        r2_layout.addStretch()
        r2_layout.addWidget(self.weight)
        main_layout.addWidget(row2)

        # Rząd 3: Czas przerwy
        row3 = QFrame()
        row3.setProperty("class", "setting_row")
        r3_layout = QVBoxLayout(row3)
        r3_layout.setContentsMargins(20, 20, 20, 20)

        lbl_rest_info = QLabel(f"Czas przerwy: 30s")
        lbl_rest_info.setProperty("class", "label")

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(30)
        slider.setMaximum(120)
        slider.setValue(30)
        slider.setSingleStep(10)
        slider.setFixedHeight(40)

        r3_layout.addWidget(lbl_rest_info)
        r3_layout.addSpacing(15)
        r3_layout.addWidget(slider)
        main_layout.addWidget(row3)

        # Rząd 4: Tryb
        row4 = QFrame()
        row4.setProperty("class", "setting_row")
        r4_layout = QVBoxLayout(row4)
        r4_layout.setContentsMargins(20, 15, 20, 15)

        lbl_mode = QLabel("Tryb ćwiczenia:")
        lbl_mode.setProperty("class", "label")
        r4_layout.addWidget(lbl_mode)
        r4_layout.addSpacing(10)

        radio_group = QButtonGroup(self)
        rb_fail = QRadioButton("Do upadku mięśniowego")
        rb_fail.setCursor(Qt.CursorShape.PointingHandCursor)
        rb_fail.setChecked(True)
        radio_group.addButton(rb_fail, 1)

        hbox_reps = QHBoxLayout()
        rb_reps = QRadioButton("Na ilość powtórzeń")
        rb_reps.setCursor(Qt.CursorShape.PointingHandCursor)
        radio_group.addButton(rb_reps, 2)

        entry_reps = QLineEdit("10")
        entry_reps.setFixedSize(100, 50)
        entry_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        entry_reps.setProperty("class", "reps_input")

        hbox_reps.addWidget(rb_reps)
        hbox_reps.addSpacing(15)
        hbox_reps.addWidget(entry_reps)
        hbox_reps.addStretch()

        r4_layout.addWidget(rb_fail)
        r4_layout.addSpacing(5)
        r4_layout.addLayout(hbox_reps)
        main_layout.addWidget(row4)

        main_layout.addStretch()

        # Stopka
        footer = QHBoxLayout()
        footer.setSpacing(30)

        btn_back = QPushButton("POWRÓT")
        btn_back.setProperty("type", "grey")
        btn_back.setFixedSize(250, 70)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_save = QPushButton("ZAPISZ")
        btn_save.setProperty("type", "red")
        btn_save.setFixedSize(250, 70)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)

        footer.addStretch()
        footer.addWidget(btn_back)
        footer.addWidget(btn_save)
        footer.addStretch()

        main_layout.addLayout(footer)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())