import numpy as np
import time
import math
from collections import deque


class BicepCurl:
    def __init__(self, detector):
        self.detector = detector

        # --- USTAWIENIA KALIBRACJI ---
        self.up_angle = 50  # Kąt pełnego zgięcia (GÓRA)
        self.down_angle = 145  # Kąt wyprostu (DÓŁ) - lekka tolerancja

        # Limity błędów
        self.back_threshold = 12  # MAX 12 stopni odchylenia tułowia od pionu!
        self.elbow_threshold = 30  # Tolerancja uciekania łokcia do przodu

        self.reset()

    def reset(self):
        """Resetuje stan przed nową serią"""
        self.dir = 0  # 0 = idzie w górę, 1 = wraca w dół
        self.good_reps = 0
        self.bad_reps = 0
        self.feedback = "OK"

        self.angle_history = deque(maxlen=4)
        self.is_rep_clean = True
        self.last_rep_time = 0

    def process(self, img):
        lm_list = self.detector.find_position(img, draw=False)
        pct = 0

        if len(lm_list) != 0:
            # --- 1. GEOMETRIA RĘKI (Do liczenia) ---
            # Bark(12) - Łokieć(14) - Nadgarstek(16)
            arm_angle = self.detector.find_angle(img, 12, 14, 16, draw=False)

            # --- 2. NOWA DETEKCJA PLECÓW (PIONOWA) ---
            # Zamiast łączyć z kolanem, liczymy odchylenie tułowia od idealnego pionu.
            # Pobieramy koordynaty Barku (12) i Biodra (24)
            x_shoulder, y_shoulder = lm_list[12][1], lm_list[12][2]
            x_hip, y_hip = lm_list[24][1], lm_list[24][2]

            # Obliczamy kąt nachylenia linii Bark-Biodro względem osi Y (Pionu)
            # Jeśli stoisz prosto, delta X jest bliska 0.
            if (y_hip - y_shoulder) != 0:
                torso_inclination = math.degrees(math.atan2(abs(x_shoulder - x_hip), abs(y_hip - y_shoulder)))
            else:
                torso_inclination = 0

            # --- 3. DETEKCJA ŁOKCIA (DRIFT) ---
            # Kąt: Biodro(24) - Bark(12) - Łokieć(14)
            # Jeśli ręka wisi luźno wzdłuż ciała -> kąt ~0-10.
            # Jeśli unosisz łokcie do przodu -> kąt rośnie.
            elbow_drift_angle = self.detector.find_angle(img, 24, 12, 14, draw=False)

            # Wygładzanie kąta ręki
            self.angle_history.append(arm_angle)
            avg_angle = sum(self.angle_history) / len(self.angle_history)

            # --- PASEK POSTĘPU ---
            pct = np.interp(avg_angle, (self.up_angle, self.down_angle), (100, 0))

            # --- WYKRYWANIE BŁĘDÓW ---

            # Błąd 1: BUJANIE PLECAMI
            # Jeśli tułów odchyla się od pionu o więcej niż 12 stopni -> BŁĄD
            if torso_inclination > self.back_threshold:
                self.feedback = "PLECY!"
                self.is_rep_clean = False

            # Błąd 2: ŁOKCIE DO PRZODU
            if elbow_drift_angle > self.elbow_threshold:
                self.feedback = "LOKCIE!"
                self.is_rep_clean = False

            # --- ZLICZANIE (Góra -> Dół) ---

            # Szczyt (Zgięcie)
            if avg_angle < self.up_angle:
                if self.dir == 0:
                    self.dir = 1

                    # Dół (Wyprost + Cooldown)
            if avg_angle > self.down_angle:
                if self.dir == 1:
                    if time.time() - self.last_rep_time > 0.8:
                        if self.is_rep_clean:
                            self.good_reps += 1
                        else:
                            self.bad_reps += 1

                        self.last_rep_time = time.time()
                        self.dir = 0
                        self.is_rep_clean = True
                        self.feedback = "OK"

        return {
            "reps_good": self.good_reps,
            "reps_bad": self.bad_reps,
            "percentage": pct,
            "feedback": self.feedback,
            "landmarks": lm_list,
            "is_clean": self.is_rep_clean
        }