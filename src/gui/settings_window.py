import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider, QRadioButton, QButtonGroup, QFrame, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET

SETTINGS_FILE = "settings.json"


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Ustawienia")
        self.resize(1200, 850)

        self.bg_pixmap = None
        if os.path.exists("assets/background.png"):
            self.bg_pixmap = QPixmap("assets/background.png")

        self.init_ui()
        self.load_current_settings()  # Wczytujemy dane przy starcie
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
        main_layout.setContentsMargins(150, 60, 150, 60)
        main_layout.setSpacing(25)

        lbl_title = QLabel("USTAWIENIA TRENINGU")
        lbl_title.setProperty("class", "h1")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_title)
        main_layout.addSpacing(20)

        # --- RZĄD 1: LICZBA SERII ---
        row1 = QFrame()
        row1.setProperty("class", "setting_row")
        r1_layout = QHBoxLayout(row1)
        r1_layout.setContentsMargins(20, 15, 20, 15)

        r1_label = QLabel("Liczba serii:")
        r1_label.setProperty("class", "label")

        self.lbl_sets_val = QLabel("3")  # Zmieniamy na self, żeby mieć dostęp w kodzie
        self.lbl_sets_val.setProperty("class", "value")
        self.lbl_sets_val.setFixedWidth(80)
        self.lbl_sets_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_minus = QPushButton("-")
        btn_minus.setProperty("class", "settings_control_btn")
        btn_minus.setFixedSize(60, 60)
        btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_minus.clicked.connect(self.decrease_sets)  # Podpięcie logiki

        btn_plus = QPushButton("+")
        btn_plus.setProperty("class", "settings_control_btn")
        btn_plus.setFixedSize(60, 60)
        btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_plus.clicked.connect(self.increase_sets)  # Podpięcie logiki

        r1_layout.addWidget(r1_label)
        r1_layout.addStretch()
        r1_layout.addWidget(btn_minus)
        r1_layout.addWidget(self.lbl_sets_val)
        r1_layout.addWidget(btn_plus)
        main_layout.addWidget(row1)

        # --- RZĄD 2: OBCIĄŻENIE ---
        row2 = QFrame()
        row2.setProperty("class", "setting_row")
        r2_layout = QHBoxLayout(row2)
        r2_layout.setContentsMargins(20, 15, 20, 15)

        lbl_weight = QLabel("Obciążenie (kg):")
        lbl_weight.setProperty("class", "label")

        self.input_weight = QLineEdit("10")
        self.input_weight.setFixedSize(120, 60)
        self.input_weight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_weight.setProperty("class", "big_input")

        r2_layout.addWidget(lbl_weight)
        r2_layout.addStretch()
        r2_layout.addWidget(self.input_weight)
        main_layout.addWidget(row2)

        # --- RZĄD 3: CZAS PRZERWY ---
        row3 = QFrame()
        row3.setProperty("class", "setting_row")
        r3_layout = QVBoxLayout(row3)
        r3_layout.setContentsMargins(20, 15, 20, 15)

        self.lbl_rest_info = QLabel(f"Czas przerwy: 30s")
        self.lbl_rest_info.setProperty("class", "label")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(10)  # Minimum 10 sekund
        self.slider.setMaximum(180)  # Maksimum 3 minuty
        self.slider.setValue(30)
        self.slider.setFixedHeight(40)
        # Podpięcie logiki: aktualizacja napisu przy przesuwaniu
        self.slider.valueChanged.connect(self.update_slider_label)

        r3_layout.addWidget(self.lbl_rest_info)
        r3_layout.addSpacing(10)
        r3_layout.addWidget(self.slider)
        main_layout.addWidget(row3)

        # --- RZĄD 4: TRYB ---
        row4 = QFrame()
        row4.setProperty("class", "setting_row")
        r4_layout = QVBoxLayout(row4)
        r4_layout.setContentsMargins(20, 15, 20, 15)

        lbl_mode = QLabel("Tryb ćwiczenia:")
        lbl_mode.setProperty("class", "label")
        r4_layout.addWidget(lbl_mode)
        r4_layout.addSpacing(15)

        self.radio_group = QButtonGroup(self)

        # Opcja 1: Do upadku
        self.rb_fail = QRadioButton("Do upadku mięśniowego")
        self.rb_fail.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rb_fail.setChecked(True)
        self.radio_group.addButton(self.rb_fail, 1)
        r4_layout.addWidget(self.rb_fail)

        r4_layout.addSpacing(10)

        # Opcja 2: Na ilość
        hbox_reps = QHBoxLayout()
        self.rb_reps = QRadioButton("Na ilość powtórzeń:")
        self.rb_reps.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_group.addButton(self.rb_reps, 2)

        self.input_reps = QLineEdit("10")
        self.input_reps.setFixedSize(100, 50)
        self.input_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_reps.setProperty("class", "reps_input")

        hbox_reps.addWidget(self.rb_reps)
        hbox_reps.addSpacing(10)
        hbox_reps.addWidget(self.input_reps)
        hbox_reps.addStretch()

        r4_layout.addLayout(hbox_reps)

        main_layout.addWidget(row4)
        main_layout.addStretch()

        # --- STOPKA ---
        footer = QHBoxLayout()
        footer.setSpacing(30)

        btn_back = QPushButton("POWRÓT")
        btn_back.setProperty("type", "grey")
        btn_back.setFixedSize(250, 70)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back_to_menu)

        btn_save = QPushButton("ZAPISZ")
        btn_save.setProperty("type", "red")
        btn_save.setFixedSize(250, 70)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_settings)  # Podpięcie zapisu

        footer.addStretch()
        footer.addWidget(btn_back)
        footer.addWidget(btn_save)
        footer.addStretch()

        main_layout.addLayout(footer)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # --- LOGIKA UI ---

    def increase_sets(self):
        current = int(self.lbl_sets_val.text())
        if current < 10:  # Limit max 10 serii
            self.lbl_sets_val.setText(str(current + 1))

    def decrease_sets(self):
        current = int(self.lbl_sets_val.text())
        if current > 1:  # Limit min 1 seria
            self.lbl_sets_val.setText(str(current - 1))

    def update_slider_label(self, value):
        self.lbl_rest_info.setText(f"Czas przerwy: {value}s")

    # --- LOGIKA PLIKÓW ---

    def load_current_settings(self):
        """Wczytuje ustawienia z pliku JSON przy starcie okna"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)

                    # Serie
                    self.lbl_sets_val.setText(str(data.get("series_count", 3)))
                    # Przerwa
                    rest = data.get("break_time", 30)
                    self.slider.setValue(rest)
                    self.lbl_rest_info.setText(f"Czas przerwy: {rest}s")
                    # Tryb
                    mode = data.get("exercise_type", "UPADEK")
                    if mode == "UPADEK":
                        self.rb_fail.setChecked(True)
                    else:
                        self.rb_reps.setChecked(True)
                        self.input_reps.setText(str(data.get("target_reps", 10)))
            except:
                pass  # Błąd odczytu, zostają domyślne

    def save_settings(self):
        """Zapisuje ustawienia do pliku i wraca do menu"""

        # 1. Najpierw wczytujemy stary plik, żeby nie zgubić adresu IP kamery
        old_ip = 0
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    old_ip = data.get("camera_ip", 0)
            except:
                pass

        # 2. Pobieramy nowe dane z UI
        series = int(self.lbl_sets_val.text())
        break_time = self.slider.value()

        mode = "UPADEK"
        target_reps = 10

        if self.rb_reps.isChecked():
            mode = "ILOSC"
            try:
                target_reps = int(self.input_reps.text())
            except:
                target_reps = 10

        # 3. Budujemy słownik, używając starego IP (old_ip)
        settings_data = {
            "camera_ip": old_ip, 
            "exercise_type": mode,
            "target_reps": target_reps,
            "series_count": series,
            "break_time": break_time,
            "weight": self.input_weight.text()
        }

        # Zapis do pliku
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_data, f, indent=4)

        print("Zapisano ustawienia!")
        self.go_back_to_menu()

    def go_back_to_menu(self):
        from src.gui.menu_window import MenuWindow
        self.menu = MenuWindow()
        self.menu.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())