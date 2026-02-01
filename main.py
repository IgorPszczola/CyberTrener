import cv2
import time
import numpy as np
import json
import os
from datetime import datetime
from src.logic.pose_detector import PoseDetector
from src.logic.bicep_curl import BicepCurl

# --- KONFIGURACJA PLIKÓW ---
SETTINGS_FILE = "settings.json"
HISTORY_FILE = "user_history.json"


def load_settings():
    """Wczytuje ustawienia z pliku (komunikacja z Frontendem)"""
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("! Nie znaleziono settings.json - używam domyślnych.")
        return {
            "camera_ip": 0,
            "exercise_type": "ILOSC",
            "target_reps": 10,
            "series_count": 3,
            "break_time": 30
        }


def save_to_history(session_data):
    """Dopisuje trening do historii użytkownika (Baza Danych)"""
    history = []

    # 1. Wczytaj istniejącą historię (jeśli jest)
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except:
            pass  # Plik pusty lub uszkodzony

    # 2. Dodaj nowy wpis
    wpis = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exercise": "BICEPS",
        "mode": session_data["mode"],
        "total_series": len(session_data["series_data"]),
        "details": session_data["series_data"]
    }
    history.append(wpis)

    # 3. Zapisz całość
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
    print(f"--- ZAPISANO DO HISTORII ({len(history)} treningów) ---")


# --- PLACEHOLDER DLA KOLEGI OD GŁOSU ---
def play_voice(command):
    """
    Tu kolega wstawi kod odtwarzający dźwięk.
    Dostępne komendy: 'start', 'break', 'error_back', 'error_elbow', 'good_job', 'finish'
    """
    pass


# ==========================================
# GŁÓWNA PĘTLA
# ==========================================
def main():
    # 1. WCZYTANIE USTAWIEŃ Z FRONTENDU
    config = load_settings()

    IP_CAMERA_URL = config.get("camera_ip", 0)
    ILOSC_SERII = config.get("series_count", 3)
    CZAS_PRZERWY = config.get("break_time", 30)
    TRYB_CWICZENIA = config.get("exercise_type", "UPADEK")
    CEL_POWTORZEN = config.get("target_reps", 10)

    # 2. INICJALIZACJA
    cap = cv2.VideoCapture(IP_CAMERA_URL)
    cap.set(3, 640)
    cap.set(4, 480)

    detector = PoseDetector()
    trener = BicepCurl(detector)

    aktualna_seria = 1

    # Stany
    STAN_ODLICZANIE = 1
    STAN_POZYCJA = 2
    STAN_TRENING = 3
    STAN_PRZERWA = 4
    STAN_KONIEC = 5

    aktualny_stan = STAN_ODLICZANIE
    timer_start = time.time()
    historia_treningu = []

    print(f"START TRENINGU: {TRYB_CWICZENIA}, Serie: {ILOSC_SERII}")
    play_voice("start")

    while True:
        success, img = cap.read()
        if not success:
            print("Brak klatki.")
            break

        img = detector.find_pose(img, draw=False)
        lm_list = detector.find_position(img, draw=False)
        czas_trwania_stanu = time.time() - timer_start

        # --- MASZYNA STANÓW ---

        # 1. ODLICZANIE
        if aktualny_stan == STAN_ODLICZANIE:
            CZAS_NA_START = 10
            pozostalo = int(CZAS_NA_START - czas_trwania_stanu) + 1

            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (640, 480), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)

            cv2.putText(img, f"SERIA {aktualna_seria}/{ILOSC_SERII}", (180, 100), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 255, 255), 3)
            cv2.putText(img, str(pozostalo), (280, 300), cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 255), 10)
            # --- DODANO NAPIS ---
            cv2.putText(img, "USTAW SIE", (180, 400), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

            if czas_trwania_stanu > CZAS_NA_START:
                aktualny_stan = STAN_POZYCJA
                timer_start = time.time()

        # 2. POZYCJA
        elif aktualny_stan == STAN_POZYCJA:
            postawa_ok = True
            komunikat = "TRZYMAJ..."
            col_kom = (0, 255, 0)

            if len(lm_list) != 0:
                back_angle = detector.find_angle(img, 12, 24, 26, draw=False)
                elbow_drift = detector.find_angle(img, 24, 12, 14, draw=False)

                if back_angle > 0 and abs(180 - back_angle) > trener.back_threshold:
                    postawa_ok = False
                    komunikat = "PLECY!"
                    col_kom = (0, 0, 255)
                    play_voice("error_back")

                if postawa_ok and elbow_drift > trener.elbow_threshold:
                    postawa_ok = False
                    komunikat = "LOKCIE!"
                    col_kom = (0, 0, 255)
                    play_voice("error_elbow")

            if not postawa_ok:
                timer_start = time.time()
                czas_trwania_stanu = 0

            bar_w = int(np.interp(czas_trwania_stanu, (0, 3), (0, 400)))
            cv2.rectangle(img, (120, 350), (120 + bar_w, 380), col_kom, -1)
            cv2.putText(img, komunikat, (50, 250), cv2.FONT_HERSHEY_PLAIN, 3, col_kom, 3)

            if czas_trwania_stanu > 3:
                aktualny_stan = STAN_TRENING
                trener.reset()
                timer_start = time.time()
                play_voice("good_job")

        # 3. TRENING
        elif aktualny_stan == STAN_TRENING:
            data = trener.process(img)
            zakoncz = False

            if data["feedback"] == "PLECY!": play_voice("error_back")
            if data["feedback"] == "LOKIEC!": play_voice("error_elbow")

            if TRYB_CWICZENIA == "ILOSC":
                limit = CEL_POWTORZEN
                cv2.putText(img, f"CEL: {limit}", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                if (data["reps_good"] + data["reps_bad"]) >= limit: zakoncz = True

            elif TRYB_CWICZENIA == "UPADEK":
                cv2.putText(img, "UPADEK", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                lm = data["landmarks"]
                if len(lm) != 0:
                    try:
                        if lm[16][2] > (lm[26][2] - 50) and (data["reps_good"] + data["reps_bad"]) > 0:
                            zakoncz = True
                    except:
                        pass

            per = data["percentage"]
            col = (0, 255, 0) if data["is_clean"] else (0, 0, 255)
            bar_y = int(np.interp(per, (0, 100), (650, 100)))
            cv2.rectangle(img, (550, 100), (625, 650), col, 3)
            cv2.rectangle(img, (550, bar_y), (625, 650), col, cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (550, 75), cv2.FONT_HERSHEY_PLAIN, 4, col, 4)

            cv2.rectangle(img, (0, 500), (350, 720), (50, 50, 50), cv2.FILLED)
            cv2.putText(img, f'DOBRE: {data["reps_good"]}', (20, 580), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            cv2.putText(img, f'ZLE:   {data["reps_bad"]}', (20, 650), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

            if data["feedback"] != "OK":
                cv2.putText(img, f'{data["feedback"]}', (150, 250), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), 4)

            lm = data["landmarks"]
            if len(lm) != 0:
                p12, p14, p16 = (lm[12][1], lm[12][2]), (lm[14][1], lm[14][2]), (lm[16][1], lm[16][2])
                cv2.line(img, p12, p14, (255, 255, 255), 3)
                cv2.line(img, p14, p16, (255, 255, 255), 3)
                cv2.circle(img, p14, 8, col, cv2.FILLED)

            if zakoncz:
                historia_treningu.append({"seria": aktualna_seria, "dobre": data["reps_good"], "zle": data["reps_bad"]})
                if aktualna_seria < ILOSC_SERII:
                    aktualny_stan = STAN_PRZERWA
                    aktualna_seria += 1
                    timer_start = time.time()
                    play_voice("break")
                else:
                    aktualny_stan = STAN_KONIEC
                    play_voice("finish")

        # 4. PRZERWA
        elif aktualny_stan == STAN_PRZERWA:
            left = int(CZAS_PRZERWY - czas_trwania_stanu) + 1
            cv2.rectangle(img, (0, 0), (640, 480), (50, 50, 50), -1)
            cv2.putText(img, "PRZERWA", (200, 150), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 4)
            cv2.putText(img, str(left), (280, 300), cv2.FONT_HERSHEY_PLAIN, 10, (255, 255, 255), 10)

            if left <= 10: cv2.putText(img, "PRZYGOTUJ SIE...", (150, 400), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 3)

            if czas_trwania_stanu > CZAS_PRZERWY:
                aktualny_stan = STAN_ODLICZANIE
                timer_start = time.time()

        # 5. KONIEC
        elif aktualny_stan == STAN_KONIEC:
            cv2.rectangle(img, (0, 0), (640, 480), (0, 0, 0), -1)
            cv2.putText(img, "KONIEC TRENINGU", (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            y = 200
            for s in historia_treningu:
                cv2.putText(img, f"S{s['seria']}: {s['dobre']} OK / {s['zle']} ZLE", (50, y), cv2.FONT_HERSHEY_PLAIN,
                            1.5, (255, 255, 255), 2)
                y += 40
            cv2.putText(img, "'Q' - ZAPISZ I WYJDZ", (150, 450), cv2.FONT_HERSHEY_PLAIN, 2, (150, 150, 150), 2)

        cv2.imshow("CyberTrener Final", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            dane_sesji = {
                "mode": TRYB_CWICZENIA,
                "series_data": historia_treningu
            }
            save_to_history(dane_sesji)
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()