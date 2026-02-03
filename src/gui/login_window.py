import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET
from src.database.database_manager import DatabaseManager
from src.gui.menu_window import MenuWindow

# --- KLASA: ŁADNE OKNO BŁĘDU ---
class ErrorDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Główna ramka - CZERWONA
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #FF0000;
                border-radius: 15px;
            }
        """)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(20)

        # Ikona X
        lbl_icon = QLabel("✘")
        lbl_icon.setStyleSheet(
            "color: #FF0000; font-size: 80px; font-weight: bold; border: none; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tekst błędu
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(
            "color: white; font-size: 20px; font-weight: bold; border: none; background: transparent;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Przycisk
        btn_ok = QPushButton("SPRÓBUJ PONOWNIE")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton { background-color: #FF0000; color: white; font-weight: bold; border-radius: 5px; padding: 10px 20px; font-size: 16px; }
            QPushButton:hover { background-color: #CC0000; }
        """)
        btn_ok.clicked.connect(self.accept)

        frame_layout.addWidget(lbl_icon)
        frame_layout.addWidget(lbl_msg)
        frame_layout.addWidget(btn_ok)

        layout.addWidget(self.frame)
        self.setLayout(layout)


# --- GŁÓWNE OKNO LOGOWANIA ---
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Logowanie")
        self.resize(1200, 850)
        self.db = DatabaseManager()

        self.bg_pixmap = None
        if os.path.exists("assets/background.png"):
            self.bg_pixmap = QPixmap("assets/background.png")

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
        btn_login.clicked.connect(self.handle_login)

        btn_back = QPushButton("POWRÓT")
        btn_back.setProperty("type", "light_grey")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back)

        form_layout.addWidget(btn_login)
        form_layout.addWidget(btn_back)

        layout.addWidget(form_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_login(self):
        user = self.input_user.text()
        pwd = self.input_pass.text()

        # 1. Walidacja pustych pól
        if not user or not pwd:
            dialog = ErrorDialog("Wpisz login i hasło!", self)
            dialog.exec()
            return

        # 2. Sprawdzenie w bazie
        if self.db.check_login(user, pwd):
            self.menu = MenuWindow()
            self.menu.show()
            self.close()
        else:
            # Błąd
            dialog = ErrorDialog("Nieprawidłowa nazwa użytkownika lub hasło.", self)
            dialog.exec()
            self.input_pass.clear()

    def go_back(self):
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