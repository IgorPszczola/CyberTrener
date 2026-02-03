import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QSizePolicy, QProgressBar, QMessageBox, QInputDialog, QDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QColor, QFont, QImage
from src.gui.styles import STYLESHEET
from src.gui.camera_thread import CameraThread
from src.database.database_manager import DatabaseManager

class SummaryDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Podsumowanie Treningu")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 400)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #00FF00;
                border-radius: 15px;
            }
            QLabel { color: white; font-weight: bold; border: none; }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        # Tytuł
        lbl_title = QLabel("KONIEC TRENINGU!")
        lbl_title.setStyleSheet("font-size: 28px; color: #00FF00;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_title)
        
        frame_layout.addSpacing(10)

        # Statystyki
        stats_text = f"""
        <p style='font-size: 18px;'>Wykonane Serie: <span style='color: #0088FF;'>{stats['sets']}</span></p>
        <p style='font-size: 18px;'>Poprawne powtórzenia: <span style='color: #00FF00;'>{stats['good']}</span></p>
        <p style='font-size: 18px;'>Błędne powtórzenia: <span style='color: #FF0000;'>{stats['bad']}</span></p>
        <hr>
        <p style='font-size: 20px; text-align: center;'>OCENA: <span style='color: yellow;'>{stats['grade']}</span></p>
        """
        lbl_stats = QLabel(stats_text)
        lbl_stats.setTextFormat(Qt.TextFormat.RichText)
        lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_stats)

        frame_layout.addSpacing(20)

        # Przycisk
        btn_ok = QPushButton("WRÓĆ DO MENU")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton { background-color: #00FF00; color: black; font-weight: bold; border-radius: 5px; padding: 10px; font-size: 16px; }
            QPushButton:hover { background-color: #33FF33; }
        """)
        btn_ok.clicked.connect(self.accept)
        frame_layout.addWidget(btn_ok)

        layout.addWidget(frame)
        self.setLayout(layout)

class TrainingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Trening (Dual View)")
        self.resize(1400, 900)
        self.setStyleSheet(STYLESHEET)

        self.bg_pixmap = None
        if os.path.exists("assets/background.png"):
            self.bg_pixmap = QPixmap("assets/background.png")

        self.last_bar_color = None
        self.settings = self.load_settings()
        
        self.init_ui()

        self.is_closing = False
        
        # --- START OBU KAMER ---
        self.start_cameras()

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
        layout = QHBoxLayout() # Główny układ: Lewo (Panel) | Prawo (Kamery)

        # --- 1. PASEK BOCZNY (Statystyki) ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(350)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.addSpacing(30)
        layout.addWidget(sidebar)

        self.lbl_status = QLabel("PRZYGOTUJ SIĘ")
        self.lbl_status.setObjectName("lbl_status")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        sb_layout.addWidget(self.lbl_status)
        sb_layout.addSpacing(20)

        self.card_reps = self.create_info_card("POWTÓRZENIA", "0")
        sb_layout.addWidget(self.card_reps)

        self.card_sets = self.create_info_card("SERIA", "1 / 3")
        sb_layout.addWidget(self.card_sets)

        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setStyleSheet("color: yellow; font-size: 22px; font-weight: bold;")
        self.lbl_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(self.lbl_feedback)

        sb_layout.addStretch()

        btn_stop = QPushButton("ZAKOŃCZ TRENING")
        btn_stop.setObjectName("btn_stop")
        btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_stop.clicked.connect(self.close_training)
        sb_layout.addWidget(btn_stop)

        # --- 2. OBSZAR WIDEO (Dwie kamery) ---
        visuals_widget = QWidget()
        visuals_layout = QVBoxLayout(visuals_widget) # Układ Pionowy: Kamery u góry, Pasek na dole
        visuals_layout.setContentsMargins(10, 10, 10, 10)
        
        # Kontener na kamery (Poziomy)
        cameras_container = QHBoxLayout()
        cameras_container.setSpacing(10)

        # >>> KAMERA GŁÓWNA
        cam1_frame = QFrame()
        cam1_layout = QVBoxLayout(cam1_frame)
        lbl_cam1 = QLabel("KAMERA GŁÓWNA")
        lbl_cam1.setStyleSheet("color: #00FF00; font-weight: bold;")
        lbl_cam1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.camera_view_main = QLabel("Łączenie z kamerą...")
        self.camera_view_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view_main.setProperty("class", "camera_placeholder")
        self.camera_view_main.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.camera_view_main.setScaledContents(True)
        
        cam1_layout.addWidget(lbl_cam1)
        cam1_layout.addWidget(self.camera_view_main)

        # >>> KAMERA DRUGA
        cam2_frame = QFrame()
        cam2_layout = QVBoxLayout(cam2_frame)
        lbl_cam2 = QLabel("PODGLĄD BOCZNY")
        lbl_cam2.setStyleSheet("color: #0088FF; font-weight: bold;")
        lbl_cam2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera_view_sec = QLabel("Łączenie z kamerą...")
        self.camera_view_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view_sec.setProperty("class", "camera_placeholder")
        self.camera_view_sec.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.camera_view_sec.setScaledContents(True)

        cam2_layout.addWidget(lbl_cam2)
        cam2_layout.addWidget(self.camera_view_sec)

        # Dodajemy obie kamery do kontenera
        cameras_container.addWidget(cam1_frame, stretch=1)
        cameras_container.addWidget(cam2_frame, stretch=1)

        visuals_layout.addLayout(cameras_container, stretch=1)

        # Pasek postępu (na samym dole)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(20)
        self.set_bar_style("green")

        visuals_layout.addWidget(self.progress_bar)

        layout.addWidget(visuals_widget, stretch=1)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_cameras(self):
        # ---------------- USTAWIENIA ----------------
        link_telefon = "http://10.105.94.15:4747/video"
        laptop_id = 0
        # --------------------------------------------

        # 1. KAMERA GŁÓWNA (Lewa strona, ta która LICZY powtórzenia)
        # Teraz przypisujemy tu LAPTOPA (id 0)
        self.thread_main = CameraThread(camera_id=laptop_id, settings=self.settings, is_analysis=True)
        self.thread_main.change_pixmap_signal.connect(self.update_image_main)
        self.thread_main.update_data_signal.connect(self.update_stats)
        self.thread_main.finished_signal.connect(self.on_training_finished)
        self.thread_main.start()

        # 2. KAMERA DRUGA (Prawa strona, tylko podgląd)
        # Teraz przypisujemy tu TELEFON (link)
        self.thread_sec = CameraThread(camera_id=link_telefon, settings=self.settings, is_analysis=True)
        self.thread_sec.change_pixmap_signal.connect(self.update_image_sec)
        self.thread_sec.start()

    # --- SLOTY AKTUALIZACJI ---

    @pyqtSlot(QImage)
    def update_image_main(self, qt_img):
        if not self.is_closing:
            self.camera_view_main.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(QImage)
    def update_image_sec(self, qt_img):
        if not self.is_closing:
            self.camera_view_sec.setPixmap(QPixmap.fromImage(qt_img))

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
                border-radius: 5px;
                background-color: {bg_color};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color_code};
                width: 10px; 
            }}
        """
        self.progress_bar.setStyleSheet(style)

    def on_training_finished(self):
        if self.is_closing: return
        
        # Zbieramy statystyki
        good = self.thread_main.trener.good_reps if hasattr(self, 'thread_main') else 0
        bad = self.thread_main.trener.bad_reps if hasattr(self, 'thread_main') else 0
        current_username = "gosc" 
        total = good + bad
        grade = "BRAK DANYCH"
        if total > 0:
            ratio = good / total
            if ratio > 0.8: grade = "MISTRZ!"
            elif ratio > 0.5: grade = "DOBRZE"
            else: grade = "POPRAW TECHNIKĘ"

        try:
            weight = float(self.settings.get("weight", 0.0))
        except (ValueError, TypeError):
            weight = 0.0

        break_time = int(self.settings.get("break_time", 30))

        db = DatabaseManager()
        db.save_workout(current_username, "Biceps", weight, good, bad, grade, break_time)

        # Wyświetlamy podsumowanie
        stats = {
            'sets': f"{self.thread_main.current_set} / {self.thread_main.total_sets}",
            'good': good,
            'bad': bad,
            'grade': grade
        }
        
        dialog = SummaryDialog(stats, self)
        dialog.exec()
        
        self.close_training()

    def close_training(self):
        self.is_closing = True

        # Zatrzymujemy OBA wątki
        if hasattr(self, 'thread_main'):
            self.thread_main.stop()
        if hasattr(self, 'thread_sec'):
            self.thread_sec.stop()

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