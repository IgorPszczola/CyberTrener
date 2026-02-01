import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET
# Importujemy pozostałe okna, żeby móc je otworzyć
from src.gui.login_window import LoginWindow
from src.gui.register_window import RegisterWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Start")
        self.resize(1200, 850)

        # --- NAPRAWA ŚCIEŻEK ---
        # Zakładamy, że uruchamiasz program z głównego folderu CyberTrener
        self.bg_path = "assets/background.png"  # Zmieniono na jpg i folder assets
        self.logo_path = "assets/logo.png"

        self.init_ui()
        self.setStyleSheet(STYLESHEET)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter
        painter = QPainter(self)

        # Próba załadowania tła
        if os.path.exists(self.bg_path):
            pixmap = QPixmap(self.bg_path)
            scaled_bg = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                      Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_bg.width()) // 2
            y = (self.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)
        else:
            # Debug: Jeśli nie ma tła, wypisz to w konsoli i wypełnij kolorem
            # print(f"Błąd: Nie znaleziono tła w {self.bg_path}")
            painter.fillRect(self.rect(), QColor(20, 20, 20))

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        # Logo
        logo_label = QLabel()
        if os.path.exists(self.logo_path):
            logo_pix = QPixmap(self.logo_path).scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio,
                                                      Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pix)
        else:
            logo_label.setText("CyberTrener")
            logo_label.setProperty("class", "h1")

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        layout.addSpacing(40)

        # Przyciski
        btn_login = QPushButton("ZALOGUJ SIĘ")
        btn_login.setProperty("type", "red")
        btn_login.setFixedWidth(450)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        # --- PODPIĘCIE AKCJI ---
        btn_login.clicked.connect(self.open_login)

        btn_register = QPushButton("ZAREJESTRUJ SIĘ")
        btn_register.setProperty("type", "grey")
        btn_register.setFixedWidth(450)
        btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        # --- PODPIĘCIE AKCJI ---
        btn_register.clicked.connect(self.open_register)

        btn_exit = QPushButton("ZAMKNIJ PROGRAM")
        btn_exit.setProperty("type", "light_grey")
        btn_exit.setFixedWidth(450)
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.clicked.connect(self.close)

        layout.addWidget(btn_login, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_register, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # --- FUNKCJE NAWIGACJI ---
    def open_login(self):
        self.login_window = LoginWindow()  # Tworzymy nowe okno
        self.login_window.show()  # Pokazujemy je
        self.close()  # Zamykamy obecne (Start)

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()