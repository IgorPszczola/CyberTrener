import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET

class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Menu")
        self.resize(1200, 850)

        self.bg_pixmap = None
        if os.path.exists("assets/background.png"):
            self.bg_pixmap = QPixmap("assets/background.png")

        self.logo_pixmap = None
        if os.path.exists("assets/logo.png"):
            self.logo_pixmap = QPixmap("assets/logo.png").scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation)

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
        layout.setSpacing(20)

        # Logo mniejsze niż na starcie
        logo_label = QLabel()
        if self.logo_pixmap:
            logo_label.setPixmap(self.logo_pixmap)
        else:
            logo_label.setText("CyberTrener")
            logo_label.setProperty("class", "h2")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        layout.addSpacing(20)

        # Przyciski
        btn_start = QPushButton("ROZPOCZNIJ TRENING")
        btn_start.setProperty("type", "red")
        btn_start.setFixedWidth(450)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(self.open_training) # <-- Podpięcie

        btn_history = QPushButton("HISTORIA TRENINGÓW")
        btn_history.setProperty("type", "grey")
        btn_history.setFixedWidth(450)
        btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_history.clicked.connect(self.open_history) # <-- Podpięcie

        btn_settings = QPushButton("USTAWIENIA TRENINGU")
        btn_settings.setProperty("type", "grey")
        btn_settings.setFixedWidth(450)
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.clicked.connect(self.open_settings) # <-- Podpięcie

        btn_logout = QPushButton("WYLOGUJ SIĘ")
        btn_logout.setProperty("type", "light_grey")
        btn_logout.setFixedWidth(450)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.logout) # <-- Podpięcie

        layout.addWidget(btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_history, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_settings, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # --- FUNKCJE NAWIGACJI ---

    def open_training(self):
        from src.gui.training_window import TrainingWindow
        self.training_window = TrainingWindow()
        self.training_window.show()
        self.close()

    def open_history(self):
        from src.gui.trainings_history_window import TrainingsHistoryWindow
        self.history_window = TrainingsHistoryWindow()
        self.history_window.show()
        self.close()

    def open_settings(self):
        from src.gui.settings_window import SettingsWindow
        self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.close()

    def logout(self):
        from src.gui.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = MenuWindow()
    window.show()
    sys.exit(app.exec())