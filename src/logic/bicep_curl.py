import numpy as np
import time
import math
from collections import deque
from src.logic.voice_service import VoiceService

class BicepCurl:
    def __init__(self, detector):
        self.detector = detector

        # --- 1. USTAWIENIA (Kalibracja od Igora - jest lepsza) ---
        self.up_angle = 50      # Kąt pełnego zgięcia
        self.down_angle = 145   # Kąt wyprostu
        self.back_threshold = 12   # Tolerancja pleców (stopnie)
        self.elbow_threshold = 30  # Tolerancja łokcia (stopnie)

        # --- 2. MODUŁ GŁOSOWY (Twój dodatek) ---
        print("--- INICJALIZACJA TRENERA ---")
        try:
            self.voice = VoiceService()
            self.voice.speak("Gotowy do treningu")
            print("--- GŁOS ZAŁADOWANY ---")
        except Exception as e:
            print(f"--- BŁĄD GŁOSU: {e} ---")
            self.voice = None

        self.last_feedback_time = 0
        self.FEEDBACK_COOLDOWN = 3.0 # Żeby nie gadał za często

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
        
        if self.voice:
            self.voice.speak("Zaczynamy serię")

    def process(self, img):
        lm_list = self.detector.find_position(img, draw=False)
        pct = 0
        current_time = time.time()

        if len(lm_list) != 0:
            # --- MATEMATYKA IGORA (Lepsze wykrywanie) ---
            
            # 1. Kąt ręki
            arm_angle = self.detector.find_angle(img, 12, 14, 16, draw=False)

            # 2. Plecy (Nowa metoda Igora - odchylenie od pionu)
            x_shoulder, y_shoulder = lm_list[12][1], lm_list[12][2]
            x_hip, y_hip = lm_list[24][1], lm_list[24][2]
            
            if (y_hip - y_shoulder) != 0:
                torso_inclination = math.degrees(math.atan2(abs(x_shoulder - x_hip), abs(y_hip - y_shoulder)))
            else:
                torso_inclination = 0

            # 3. Łokieć (Drift)
            elbow_drift_angle = self.detector.find_angle(img, 24, 12, 14, draw=False)

            # Wygładzanie
            self.angle_history.append(arm_angle)
            avg_angle = sum(self.angle_history) / len(self.angle_history)

            # Pasek postępu
            pct = np.interp(avg_angle, (self.up_angle, self.down_angle), (100, 0))

            # --- DETEKCJA BŁĘDÓW + GŁOS (Połączenie) ---

            # Błąd 1: PLECY
            if torso_inclination > self.back_threshold:
                self.feedback = "PLECY!"
                self.is_rep_clean = False
                
                # Głos (Twoja logika)
                if current_time - self.last_feedback_time > self.FEEDBACK_COOLDOWN:
                    if self.voice: self.voice.speak("Wyprostuj plecy!")
                    self.last_feedback_time = current_time

            # Błąd 2: ŁOKCIE
            elif elbow_drift_angle > self.elbow_threshold:
                self.feedback = "LOKCIE!"
                self.is_rep_clean = False
                
                # Głos
                if current_time - self.last_feedback_time > self.FEEDBACK_COOLDOWN:
                    if self.voice: self.voice.speak("Trzymaj łokcie blisko ciała")
                    self.last_feedback_time = current_time

            # --- ZLICZANIE (Logika Igora + Twój głos) ---
            
            # Ruch w górę
            if avg_angle < self.up_angle:
                if self.dir == 0:
                    self.dir = 1
                    self.feedback = "GORA"

            # Ruch w dół (Zaliczenie)
            if avg_angle > self.down_angle:
                if self.dir == 1:
                    # Cooldown żeby nie zaliczyło 2 razy
                    if time.time() - self.last_rep_time > 0.8:
                        if self.is_rep_clean:
                            self.good_reps += 1
                            self.feedback = "DOBRZE!"
                            # Twój głos liczenia
                            if self.voice: self.voice.speak(str(self.good_reps))
                        else:
                            self.bad_reps += 1
                            self.feedback = "ZLE TECHNICZNIE"
                            # Twój głos błędu
                            if self.voice: self.voice.speak("Niezaliczone")

                        self.last_rep_time = time.time()
                        self.dir = 0
                        self.is_rep_clean = True

        # Tworzymy słownik danych (Format Igora, ale zwracamy tuple dla Twojego wątku)
        data = {
            "reps_good": self.good_reps,
            "reps_bad": self.bad_reps,
            "percentage": pct,
            "feedback": self.feedback,
            "landmarks": lm_list,
            "is_clean": self.is_rep_clean,
            # Dodatkowe pola diagnostyczne
            "debug_torso": int(torso_inclination) if 'torso_inclination' in locals() else 0,
            "debug_elbow": int(elbow_drift_angle) if 'elbow_drift_angle' in locals() else 0
        }

        # Zwracamy img i data (Żeby Twój CameraThread był zadowolony)
        return img, data