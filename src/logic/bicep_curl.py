import cv2
import numpy as np
from collections import deque
from src.logic.pose_detector import PoseDetector


class BicepCurl:
    def __init__(self, detector):
        self.detector = detector

        # Parametry
        self.angle_down = 140
        self.angle_up = 50
        self.elbow_threshold = 30
        self.back_threshold = 11

        # Stan
        self.angle_history = deque(maxlen=7)
        self.good_reps = 0
        self.bad_reps = 0
        self.dir = 0
        self.is_rep_clean = True
        self.feedback = "OK"  # Komunikat dla użytkownika

    def process(self, img):
        # 1. Znajdź punkty (bez rysowania tutaj, rysowanie zrobimy w main)
        lm_list = self.detector.find_position(img, draw=False)

        data = {
            "reps_good": self.good_reps,
            "reps_bad": self.bad_reps,
            "percentage": 0,
            "feedback": "SZUKAM CIE...",
            "is_clean": True,
            "landmarks": lm_list  # Przekazujemy punkty, żeby main mógł rysować
        }

        if len(lm_list) != 0:
            # Kąty
            raw_angle = self.detector.find_angle(img, 12, 14, 16, draw=False)
            elbow_drift = self.detector.find_angle(img, 24, 12, 14, draw=False)
            back_angle = self.detector.find_angle(img, 12, 24, 26, draw=False)

            # Wygładzanie
            if raw_angle > 0: self.angle_history.append(raw_angle)
            final_angle = int(sum(self.angle_history) / len(self.angle_history)) if self.angle_history else int(
                raw_angle)

            # Procenty
            per = np.interp(final_angle, (self.angle_up, self.angle_down), (100, 0))

            # --- DETEKCJA BŁĘDÓW ---
            self.feedback = "OK"
            if per > 5:
                if elbow_drift > self.elbow_threshold:
                    self.is_rep_clean = False
                    self.feedback = "LOKIEC!"

                if back_angle > 0 and abs(180 - back_angle) > self.back_threshold:
                    self.is_rep_clean = False
                    self.feedback = "PLECY!"

            # --- ZLICZANIE ---
            if per == 100:
                if self.dir == 0: self.dir = 1

            if per == 0:
                if self.dir == 1:
                    if self.is_rep_clean:
                        self.good_reps += 1
                    else:
                        self.bad_reps += 1
                    self.dir = 0
                    self.is_rep_clean = True

            # Aktualizacja danych wyjściowych
            data["percentage"] = int(per)
            data["feedback"] = self.feedback
            data["is_clean"] = self.is_rep_clean

        return data