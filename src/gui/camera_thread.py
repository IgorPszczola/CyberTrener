import cv2
import numpy as np
import time
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
from src.logic.pose_detector import PoseDetector
from src.logic.bicep_curl import BicepCurl


class CameraThread(QThread):
    # Sygnały do aktualizacji interfejsu
    change_pixmap_signal = pyqtSignal(QImage)  # Obraz kamery
    update_data_signal = pyqtSignal(dict)  # Dane (powtórzenia, feedback)
    finished_signal = pyqtSignal()  # Koniec treningu

    def __init__(self, camera_id=0, settings=None):
        super().__init__()
        self.camera_id = camera_id
        self._run_flag = True
        self.settings = settings or {}

        # Inicjalizacja logiki (Twoja klasa!)
        self.detector = PoseDetector()
        self.trener = BicepCurl(self.detector)

        # Logika stanów (przeniesiona ze starego main.py)
        self.state = "ODLICZANIE"  # ODLICZANIE, POZYCJA, TRENING
        self.start_time = time.time()
        self.countdown_duration = 10

        # Obsługa serii
        self.current_set = 1
        self.total_sets = int(self.settings.get("series_count", 3))
        self.target_reps = int(self.settings.get("target_reps", 10))
        self.mode = self.settings.get("exercise_type", "UPADEK")  # ILOSC lub UPADEK

    def run(self):
        # Obsługa strumienia wideo (IP lub USB)
        # Jeśli string to IP, jeśli int to USB
        src = self.camera_id
        if isinstance(src, str) and src.isdigit():
            src = int(src)

        cap = cv2.VideoCapture(src)

        while self._run_flag:
            ret, cv_img = cap.read()
            if not ret:
                break

            # 1. Detekcja (Zawsze)
            cv_img = self.detector.find_pose(cv_img, draw=False)
            lm_list = self.detector.find_position(cv_img, draw=False)

            elapsed = time.time() - self.start_time

            ui_data = {
                "state": self.state,
                "reps_good": self.trener.good_reps,
                "reps_bad": self.trener.bad_reps,
                "percentage": 0,
                "feedback": "",
                "set_info": f"{self.current_set} / {self.total_sets}",
                "timer": ""
            }

            # --- MASZYNA STANÓW (Uproszczona pod GUI) ---

            if self.state == "ODLICZANIE":
                left = int(self.countdown_duration - elapsed) + 1
                ui_data["timer"] = str(left)
                ui_data["feedback"] = "USTAW SIĘ"

                # Rysowanie na obrazie (opcjonalne, bo mamy GUI, ale pomaga)
                cv2.putText(cv_img, str(left), (280, 240), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 5)

                if elapsed > self.countdown_duration:
                    self.state = "POZYCJA"
                    self.start_time = time.time()

            elif self.state == "POZYCJA":
                # Tutaj wstawiamy logikę sprawdzania pozycji (tę co robiliśmy ostatnio)
                # Dla uproszczenia teraz: czekamy 3 sekundy
                ui_data["feedback"] = "SPRAWDZAM POZYCJĘ..."
                if elapsed > 3:
                    self.state = "TRENING"
                    self.trener.reset()

            elif self.state == "TRENING":
                # Procesowanie logiki Bicepsa
                logic_data = self.trener.process(cv_img)

                # Przepisanie danych do UI
                ui_data.update({
                    "percentage": logic_data["percentage"],
                    "feedback": logic_data["feedback"],
                    "reps_good": logic_data["reps_good"],
                    "reps_bad": logic_data["reps_bad"]
                })

                # Rysowanie szkieletu na obrazie
                self.draw_skeleton(cv_img, logic_data["landmarks"], logic_data["is_clean"])

                # Logika końca serii (zostawiam do dopracowania, na razie pętla)
                if self.mode == "ILOSC" and (logic_data["reps_good"] + logic_data["reps_bad"] >= self.target_reps):
                    self.state = "KONIEC_SERII"

            # 2. Konwersja OpenCV -> PyQt Image
            qt_img = self.convert_cv_qt(cv_img)

            # 3. Wysyłanie sygnałów do okna
            self.change_pixmap_signal.emit(qt_img)
            self.update_data_signal.emit(ui_data)

            # Ograniczenie FPS (żeby nie zajechać procesora)
            time.sleep(0.01)

        cap.release()
        self.finished_signal.emit()

    def convert_cv_qt(self, cv_img):
        """Konwertuje obraz z OpenCV (BGR) na format PyQt (RGB)"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        return p

    def draw_skeleton(self, img, lm, is_clean):
        color = (0, 255, 0) if is_clean else (0, 0, 255)
        if lm:
            # Uproszczone rysowanie ręki
            try:
                cv2.line(img, (lm[12][1], lm[12][2]), (lm[14][1], lm[14][2]), (255, 255, 255), 3)
                cv2.line(img, (lm[14][1], lm[14][2]), (lm[16][1], lm[16][2]), (255, 255, 255), 3)
                cv2.circle(img, (lm[14][1], lm[14][2]), 8, color, -1)
            except:
                pass

    def stop(self):
        self._run_flag = False
        self.wait()