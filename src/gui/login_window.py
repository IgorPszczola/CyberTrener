import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QFormLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET


# USUNIĘTO: from src.gui.main_window import MainWindow <-- TO POWODOWAŁO BŁĄD

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Logowanie")
        self.resize(1200, 850)

        self.bg_pixmap = None
        # Upewnij się, że ta ścieżka jest poprawna względem pliku main.py
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
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_frame = QFrame()
        form_frame.setProperty("class", "form_frame")
        form_frame.setFixedWidth(500)

        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        lbl_title = QLabel("LOGOWANIE")
        lbl_title.setProperty("class", "h2")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl_title)
        form_layout.addSpacing(20)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Nazwa użytkownika")

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Hasło")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addWidget(self.input_user)
        form_layout.addWidget(self.input_pass)
        form_layout.addSpacing(20)

        btn_login = QPushButton("ZALOGUJ SIĘ")
        btn_login.setProperty("type", "red")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_back = QPushButton("POWRÓT")
        btn_back.setProperty("type", "light_grey")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back)

        form_layout.addWidget(btn_login)
        form_layout.addWidget(btn_back)

        layout.addWidget(form_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def go_back(self):
        # Importujemy MainWindow TYLKO tutaj, w momencie kliknięcia.
        # To zapobiega błędowi "Circular Import".
        from src.gui.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())