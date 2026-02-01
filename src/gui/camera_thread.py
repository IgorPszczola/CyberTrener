import cv2
import numpy as np
import time
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
from src.logic.pose_detector import PoseDetector
from src.logic.bicep_curl import BicepCurl


class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    update_data_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()

    def __init__(self, camera_id=0, settings=None):
        super().__init__()
        self.camera_id = camera_id
        self._run_flag = True
        self.settings = settings or {}

        self.detector = PoseDetector()
        self.trener = BicepCurl(self.detector)

        # --- ZMIENNE STANU ---
        self.state = "ODLICZANIE"
        self.start_time = time.time()

        # Pobieramy czasy z ustawień
        self.countdown_duration = 10  # Czas na start
        self.break_duration = int(self.settings.get("break_time", 30))  # Czas przerwy

        self.current_set = 1
        self.total_sets = int(self.settings.get("series_count", 3))
        self.target_reps = int(self.settings.get("target_reps", 10))
        self.mode = self.settings.get("exercise_type", "UPADEK")

    def run(self):
        src = self.camera_id
        if isinstance(src, str) and src.isdigit():
            src = int(src)

        print(f"--- START KAMERY: {src} ---")

        cap = cv2.VideoCapture(src)
        if isinstance(src, str):
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            print("BŁĄD KAMERY")
            self._run_flag = False

        while self._run_flag:
            ret, cv_img = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            # Skalowanie dla wydajności
            cv_img = cv2.resize(cv_img, (640, 480))

            # Detekcja pozy
            cv_img = self.detector.find_pose(cv_img, draw=False)

            elapsed = time.time() - self.start_time

            # Domyślne dane dla UI
            ui_data = {
                "state": self.state,
                "reps_good": self.trener.good_reps,
                "reps_bad": self.trener.bad_reps,
                "percentage": 0,
                "feedback": "",
                "set_info": f"{self.current_set} / {self.total_sets}",
                "timer": ""
            }

            # --- MASZYNA STANÓW ---

            # 1. ODLICZANIE (Przed serią)
            if self.state == "ODLICZANIE":
                left = int(self.countdown_duration - elapsed) + 1
                ui_data["timer"] = str(left)
                ui_data["feedback"] = "USTAW SIĘ"

                # Wizualizacja na obrazie
                cv2.putText(cv_img, str(left), (280, 240), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 4)

                if elapsed > self.countdown_duration:
                    self.state = "POZYCJA"
                    self.start_time = time.time()

            # 2. POZYCJA (Sprawdzanie czy stoisz w kadrze - uproszczone na 3s)
            elif self.state == "POZYCJA":
                ui_data["feedback"] = "START ZA CHWILĘ..."
                if elapsed > 2:
                    self.state = "TRENING"
                    self.trener.reset()  # Resetujemy liczniki na nową serię

            # 3. TRENING (Właściwe ćwiczenie)
            elif self.state == "TRENING":
                logic_data = self.trener.process(cv_img)

                # Aktualizacja UI z danych trenera
                ui_data.update({
                    "percentage": logic_data["percentage"],
                    "feedback": logic_data["feedback"],
                    "reps_good": logic_data["reps_good"],
                    "reps_bad": logic_data["reps_bad"]
                })

                self.draw_skeleton(cv_img, logic_data["landmarks"], logic_data["is_clean"])

                # SPRAWDZANIE KOŃCA SERII
                current_reps = logic_data["reps_good"] + logic_data["reps_bad"]

                # Warunek: Osiągnięto cel (w trybie ILOSC) LUB np. w trybie UPADEK (tu można dodać przycisk)
                if self.mode == "ILOSC" and current_reps >= self.target_reps:
                    self.state = "KONIEC_SERII_LOGIKA"

            # 4. LOGIKA PRZEJŚCIA (Decyzja: Przerwa czy Koniec Treningu?)
            elif self.state == "KONIEC_SERII_LOGIKA":
                if self.current_set < self.total_sets:
                    # Idziemy na przerwę
                    self.state = "PRZERWA"
                    self.start_time = time.time()
                else:
                    # Koniec wszystkiego
                    self.state = "KONIEC_TRENINGU"
                    self.finished_signal.emit()  # Sygnał do okna, że koniec
                    self._run_flag = False  # Zatrzymujemy pętlę

            # 5. PRZERWA
            elif self.state == "PRZERWA":
                left = int(self.break_duration - elapsed) + 1
                ui_data["timer"] = str(left)
                ui_data["feedback"] = "ODPOCZNIJ"

                # Nakładka graficzna przerwy
                overlay = cv_img.copy()
                cv2.rectangle(overlay, (0, 0), (640, 480), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, cv_img, 0.3, 0, cv_img)
                cv2.putText(cv_img, f"PRZERWA: {left}", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                if elapsed > self.break_duration:
                    # Nowa seria!
                    self.current_set += 1
                    self.state = "ODLICZANIE"  # Wracamy do odliczania
                    self.countdown_duration = 5  # Krótsze odliczanie przed kolejnymi seriami
                    self.start_time = time.time()

            # --- WYSYŁANIE DANYCH ---
            if self._run_flag:
                qt_img = self.convert_cv_qt(cv_img)
                self.change_pixmap_signal.emit(qt_img)
                self.update_data_signal.emit(ui_data)

        cap.release()
        print("--- ZAMKNIĘTO WĄTEK KAMERY ---")

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return convert_to_Qt_format

    def draw_skeleton(self, img, lm, is_clean):
        color = (0, 255, 0) if is_clean else (0, 0, 255)
        if lm:
            try:
                cv2.line(img, (lm[12][1], lm[12][2]), (lm[14][1], lm[14][2]), (255, 255, 255), 3)
                cv2.line(img, (lm[14][1], lm[14][2]), (lm[16][1], lm[16][2]), (255, 255, 255), 3)
                cv2.circle(img, (lm[14][1], lm[14][2]), 8, color, -1)
            except:
                pass

    def stop(self):
        self._run_flag = False
        self.wait()  # WAŻNE: Czekamy aż wątek faktycznie się zamknie