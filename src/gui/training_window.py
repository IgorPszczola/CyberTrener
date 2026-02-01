import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                             QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QColor, QFont, QImage
from src.gui.styles import STYLESHEET
from src.gui.camera_thread import CameraThread  # Import wątku


class TrainingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Trening")
        self.resize(1200, 850)
        self.setStyleSheet(STYLESHEET)

        # Wczytanie ustawień
        self.settings = self.load_settings()

        self.init_ui()

        # Start Kamery
        self.start_camera()

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except:
            return {}

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()

        # --- PASEK BOCZNY ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(400)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.addSpacing(50)
        layout.addWidget(sidebar)

        # Status
        self.lbl_status = QLabel("PRZYGOTUJ SIĘ")
        self.lbl_status.setObjectName("lbl_status")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        sb_layout.addWidget(self.lbl_status)
        sb_layout.addSpacing(30)

        # Karty info
        self.card_reps = self.create_info_card("POWTÓRZENIA", "0")
        sb_layout.addWidget(self.card_reps)

        self.card_sets = self.create_info_card("SERIA", "1 / 3")
        sb_layout.addWidget(self.card_sets)

        # Feedback
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setStyleSheet("color: yellow; font-size: 24px; font-weight: bold;")
        self.lbl_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(self.lbl_feedback)

        sb_layout.addStretch()

        btn_stop = QPushButton("ZAKOŃCZ TRENING")
        btn_stop.setObjectName("btn_stop")
        btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_stop.clicked.connect(self.close_training)
        sb_layout.addWidget(btn_stop)

        # --- OBSZAR KAMERY ---
        cameras_widget = QWidget()
        cameras_layout = QHBoxLayout(cameras_widget)

        # Główny podgląd
        self.camera_view = QLabel("Ładowanie kamery...")
        self.camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view.setProperty("class", "camera_placeholder")
        self.camera_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Skalowanie obrazu
        self.camera_view.setScaledContents(True)

        cameras_layout.addWidget(self.camera_view)
        layout.addWidget(cameras_widget, stretch=1)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_info_card(self, title, val):
        card = QFrame()
        card.setProperty("class", "info_card")
        cl = QVBoxLayout(card)
        l1 = QLabel(title)
        l1.setProperty("class", "card_title")
        l2 = QLabel(val)
        l2.setProperty("class", "card_value")
        cl.addWidget(l1)
        cl.addWidget(l2)
        # Przechowujemy referencję do labela z wartością, żeby go aktualizować
        card.value_label = l2
        return card

    def start_camera(self):
        # Pobieramy IP z ustawień
        ip = self.settings.get("camera_ip", 0)
        self.thread = CameraThread(camera_id=ip, settings=self.settings)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_data_signal.connect(self.update_stats)
        self.thread.start()

    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        """Odbiera obraz z wątku i wyświetla w oknie"""
        self.camera_view.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(dict)
    def update_stats(self, data):
        """Odbiera dane z wątku i aktualizuje napisy"""
        # Status
        if data["state"] == "ODLICZANIE":
            self.lbl_status.setText(f"START ZA: {data['timer']}")
        else:
            self.lbl_status.setText(data["state"])

        # Powtórzenia
        total = data["reps_good"] + data["reps_bad"]
        self.card_reps.value_label.setText(f"{data['reps_good']} OK / {data['reps_bad']} ZŁE")

        # Seria
        self.card_sets.value_label.setText(data["set_info"])

        # Feedback (błędy)
        fb = data["feedback"]
        self.lbl_feedback.setText(fb)
        if "OK" in fb or fb == "":
            self.lbl_feedback.setStyleSheet("color: #00FF00; font-size: 28px; font-weight: bold;")
        else:
            self.lbl_feedback.setStyleSheet("color: #FF0000; font-size: 28px; font-weight: bold;")

    def close_training(self):
        if hasattr(self, 'thread'):
            self.thread.stop()
        self.close()
        # Tu można dodać powrót do Menu