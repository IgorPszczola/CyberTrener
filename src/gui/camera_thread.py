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

    # Dodano parametr is_analysis=True
    def __init__(self, camera_id=0, settings=None, is_analysis=True):
        super().__init__()
        self.camera_id = camera_id
        self.is_analysis = is_analysis # CZY TO KAMERA GŁÓWNA?
        self._run_flag = True
        self.settings = settings or {}

        # Inicjalizacja detektorów TYLKO jeśli robimy analizę
        if self.is_analysis:
            self.detector = PoseDetector()
            self.trener = BicepCurl(self.detector)
        else:
            self.detector = None
            self.trener = None

        # Zmienne stanu (tylko dla kamery głównej)
        self.state = "ODLICZANIE"
        self.start_time = time.time()
        
        self.countdown_duration = 10
        self.break_duration = int(self.settings.get("break_time", 30))
        self.current_set = 1
        self.total_sets = int(self.settings.get("series_count", 3))
        self.target_reps = int(self.settings.get("target_reps", 10))
        self.mode = self.settings.get("exercise_type", "UPADEK")

    def run(self):
        src = self.camera_id
        if isinstance(src, str) and src.isdigit():
            src = int(src)

        print(f"--- START KAMERY ({'ANALIZA' if self.is_analysis else 'PODGLĄD'}): {src} ---")

        cap = cv2.VideoCapture(src)
        if isinstance(src, str):
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self._run_flag:
            ret, cv_img = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            cv_img = cv2.resize(cv_img, (640, 480))

            # --- TRYB 1: TYLKO PODGLĄD (Druga kamera) ---
            if not self.is_analysis:
                # Tylko wysyłamy obraz, żadnej matematyki
                qt_img = self.convert_cv_qt(cv_img)
                self.change_pixmap_signal.emit(qt_img)
                time.sleep(0.03) # 30 FPS
                continue

            # --- TRYB 2: ANALIZA (Główna kamera) ---
            
            # Detekcja
            cv_img = self.detector.find_pose(cv_img, draw=False)
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

            # Maszyna stanów
            if self.state == "ODLICZANIE":
                left = int(self.countdown_duration - elapsed) + 1
                ui_data["timer"] = str(left)
                ui_data["feedback"] = "USTAW SIĘ"
                cv2.putText(cv_img, str(left), (280, 240), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 4)
                if elapsed > self.countdown_duration:
                    self.state = "POZYCJA"
                    self.start_time = time.time()

            elif self.state == "POZYCJA":
                ui_data["feedback"] = "START ZA CHWILĘ..."
                if elapsed > 2:
                    self.state = "TRENING"
                    self.trener.reset()

            elif self.state == "TRENING":
                cv_img, logic_data = self.trener.process(cv_img)
                ui_data.update({
                    "percentage": logic_data["percentage"],
                    "feedback": logic_data["feedback"],
                    "reps_good": logic_data["reps_good"],
                    "reps_bad": logic_data["reps_bad"]
                })
                self.draw_skeleton(cv_img, logic_data["landmarks"], logic_data["is_clean"])
                
                current_reps = logic_data["reps_good"] + logic_data["reps_bad"]
                if self.mode == "ILOSC" and current_reps >= self.target_reps:
                    self.state = "KONIEC_SERII_LOGIKA"

            elif self.state == "KONIEC_SERII_LOGIKA":
                if self.current_set < self.total_sets:
                    self.state = "PRZERWA"
                    self.start_time = time.time()
                else:
                    self.state = "KONIEC_TRENINGU"
                    self.finished_signal.emit() 
                    self._run_flag = False 

            elif self.state == "PRZERWA":
                left = int(self.break_duration - elapsed) + 1
                ui_data["timer"] = str(left)
                ui_data["feedback"] = "ODPOCZNIJ"
                overlay = cv_img.copy()
                cv2.rectangle(overlay, (0, 0), (640, 480), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, cv_img, 0.3, 0, cv_img)
                cv2.putText(cv_img, f"PRZERWA: {left}", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                if elapsed > self.break_duration:
                    self.current_set += 1
                    self.state = "ODLICZANIE"
                    self.countdown_duration = 5 
                    self.start_time = time.time()

            # Wysyłanie
            if self._run_flag:
                qt_img = self.convert_cv_qt(cv_img)
                self.change_pixmap_signal.emit(qt_img)
                self.update_data_signal.emit(ui_data)
            
            time.sleep(0.01)

        # Sprzątanie głosu
        if self.is_analysis and hasattr(self.trener, 'voice') and self.trener.voice:
            try: self.trener.voice.stop()
            except: pass

        cap.release()

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        return QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

    def draw_skeleton(self, img, lm, is_clean):
        color = (0, 255, 0) if is_clean else (0, 0, 255)
        if lm:
            try:
                cv2.line(img, (lm[12][1], lm[12][2]), (lm[14][1], lm[14][2]), (255, 255, 255), 3)
                cv2.line(img, (lm[14][1], lm[14][2]), (lm[16][1], lm[16][2]), (255, 255, 255), 3)
                cv2.circle(img, (lm[14][1], lm[14][2]), 8, color, -1)
            except: pass

    def stop(self):
        self._run_flag = False
        self.wait()