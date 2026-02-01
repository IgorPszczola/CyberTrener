import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QSizePolicy, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QColor, QFont, QImage
from src.gui.styles import STYLESHEET
from src.gui.camera_thread import CameraThread


class TrainingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Trening")
        self.resize(1200, 850)
        self.setStyleSheet(STYLESHEET)

        self.bg_pixmap = None
        if os.path.exists("assets/background.png"):
            self.bg_pixmap = QPixmap("assets/background.png")

        # --- POPRAWKA TUTAJ ---
        # Ustawiamy None, żeby wymusić pierwsze nałożenie stylu w init_ui
        self.last_bar_color = None

        self.settings = self.load_settings()
        self.init_ui()

        self.is_closing = False
        self.start_camera()

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

        self.lbl_status = QLabel("PRZYGOTUJ SIĘ")
        self.lbl_status.setObjectName("lbl_status")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        sb_layout.addWidget(self.lbl_status)
        sb_layout.addSpacing(30)

        self.card_reps = self.create_info_card("POWTÓRZENIA", "0")
        sb_layout.addWidget(self.card_reps)

        self.card_sets = self.create_info_card("SERIA", "1 / 3")
        sb_layout.addWidget(self.card_sets)

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

        # --- OBSZAR KAMERY I PASKA ---
        visuals_widget = QWidget()
        visuals_layout = QHBoxLayout(visuals_widget)
        visuals_layout.setContentsMargins(20, 20, 20, 20)
        visuals_layout.setSpacing(20)

        self.camera_view = QLabel("Ładowanie kamery...")
        self.camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view.setProperty("class", "camera_placeholder")
        self.camera_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.camera_view.setScaledContents(True)
        visuals_layout.addWidget(self.camera_view, stretch=4)

        self.progress_bar = QProgressBar()
        self.progress_bar.setOrientation(Qt.Orientation.Vertical)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(50)

        # Teraz to zadziała, bo last_bar_color jest None
        self.set_bar_style("green")

        visuals_layout.addWidget(self.progress_bar, stretch=0)

        layout.addWidget(visuals_widget, stretch=1)

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
        card.value_label = l2
        return card

    def set_bar_style(self, color_type):
        # Sprawdzamy czy kolor się zmienił (żeby nie mrugać stylem co klatkę)
        if color_type == self.last_bar_color:
            return
        self.last_bar_color = color_type

        if color_type == "green":
            color_code = "#00FF00"
            bg_color = "#333"
        elif color_type == "blue":
            color_code = "#0088FF"
            bg_color = "#002244"
        else:  # Red
            color_code = "#FF0000"
            bg_color = "#330000"

        style = f"""
            QProgressBar {{
                border: 2px solid #555;
                border-radius: 10px;
                background-color: {bg_color};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color_code};
                border-radius: 8px;
                margin: 2px;
            }}
        """
        self.progress_bar.setStyleSheet(style)

    def start_camera(self):
        ip = self.settings.get("camera_ip", 0)
        self.thread = CameraThread(camera_id=ip, settings=self.settings)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_data_signal.connect(self.update_stats)
        self.thread.finished_signal.connect(self.on_training_finished)
        self.thread.start()

    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        if not self.is_closing:
            self.camera_view.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(dict)
    def update_stats(self, data):
        if self.is_closing: return

        state = data["state"]

        if state == "ODLICZANIE":
            self.lbl_status.setText(f"START ZA: {data['timer']}")
        elif state == "PRZERWA":
            self.lbl_status.setText(f"PRZERWA: {data['timer']}")
            self.set_bar_style("blue")
            self.progress_bar.setValue(100)
            self.lbl_feedback.setText("ODPOCZNIJ")
            self.lbl_feedback.setStyleSheet("color: #0088FF; font-size: 28px; font-weight: bold;")
            return
        else:
            self.lbl_status.setText(state)

        self.card_reps.value_label.setText(f"{data['reps_good']} OK / {data['reps_bad']} ZŁE")
        self.card_sets.value_label.setText(data["set_info"])

        if state == "TRENING":
            fb = data["feedback"]
            self.lbl_feedback.setText(fb)
            if fb == "OK" or fb == "":
                self.lbl_feedback.setStyleSheet("color: #00FF00; font-size: 28px; font-weight: bold;")
                self.set_bar_style("green")
            else:
                self.lbl_feedback.setStyleSheet("color: #FF0000; font-size: 28px; font-weight: bold;")
                self.set_bar_style("red")

            perc = int(data.get("percentage", 0))
            self.progress_bar.setValue(perc)

    def on_training_finished(self):
        if self.is_closing: return
        QMessageBox.information(self, "Koniec", "Trening zakończony! Dobra robota.")
        self.close_training()

    def close_training(self):
        self.is_closing = True

        if hasattr(self, 'thread'):
            self.thread.stop()

        from src.gui.menu_window import MenuWindow
        self.menu = MenuWindow()
        self.menu.show()

        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = TrainingWindow()
    window.show()
    sys.exit(app.exec())