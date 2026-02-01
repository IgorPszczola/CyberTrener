import cv2
import time
import numpy as np
# Importujemy nasze moduły z folderu src/logic
from src.logic.pose_detector import PoseDetector
from src.logic.bicep_curl import BicepCurl


def main():
    # 1. Konfiguracja Kamery
    ip_camera_url = 'http://192.168.18.13:4747/video'  # Sprawdź IP!
    cap = cv2.VideoCapture(ip_camera_url)
    cap.set(3, 640)
    cap.set(4, 480)

    # 2. Inicjalizacja Silnika
    print("Inicjalizacja modułów...")
    detector = PoseDetector()

    # Tworzymy obiekt ćwiczenia i przekazujemy mu detektor
    # Pamiętaj, żeby w bicep_curl.py ustawić self.back_threshold = 11 !
    trener = BicepCurl(detector)

    # 3. Zmienne pomocnicze
    start_time = time.time()
    COUNTDOWN = 10  # Czas na start

    print("START: Masz 10 sekund na ustawienie się.")

    while True:
        success, img = cap.read()
        if not success:
            print("Brak klatki z kamery.")
            break

        # Detekcja (wymagana w każdej klatce)
        # Detektor rysuje tylko kropki, linie narysujemy sami niżej
        img = detector.find_pose(img, draw=False)

        # --- LOGIKA APLIKACJI ---

        elapsed = time.time() - start_time

        # FAZA 1: ODLICZANIE
        if elapsed < COUNTDOWN:
            time_left = int(COUNTDOWN - elapsed) + 1

            # Przyciemnienie tła
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (640, 480), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)

            cv2.putText(img, str(time_left), (280, 280),
                        cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 255), 10)
            cv2.putText(img, "USTAW SIE", (180, 380),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        # FAZA 2: TRENING
        else:
            # To jest kluczowy moment!
            # Main pyta logikę: "Masz tu obraz, powiedz mi co się dzieje".
            # Logika zwraca same DANE (słownik).
            data = trener.process(img)

            # --- SYMULACJA FRONTENDU (WIZUALIZACJA DANYCH) ---
            # Tutaj rysujemy to, co zwróciła logika.

            # Kolor w zależności od tego, czy powtórzenie jest czyste
            col = (0, 255, 0) if data["is_clean"] else (0, 0, 255)

            # 1. Pasek postępu
            per = data["percentage"]
            bar_y = int(np.interp(per, (0, 100), (650, 100)))
            cv2.rectangle(img, (550, 100), (625, 650), col, 3)
            cv2.rectangle(img, (550, bar_y), (625, 650), col, cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (550, 75), cv2.FONT_HERSHEY_PLAIN, 4, col, 4)

            # 2. Statystyki
            cv2.rectangle(img, (0, 500), (350, 720), (50, 50, 50), cv2.FILLED)
            cv2.putText(img, f'DOBRE: {data["reps_good"]}', (20, 580), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            cv2.putText(img, f'ZLE:   {data["reps_bad"]}', (20, 650), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

            # 3. Komunikaty Trenera
            status_col = (0, 255, 0) if data["feedback"] == "OK" else (0, 0, 255)
            cv2.putText(img, f'STAN: {data["feedback"]}', (20, 700), cv2.FONT_HERSHEY_PLAIN, 2, status_col, 2)

            # 4. Rysowanie szkieletu (Opcjonalne - dla pewności)
            # Logika zwróciła nam listę punktów w data['landmarks'], możemy ich użyć
            lm_list = data["landmarks"]
            if len(lm_list) != 0:
                # Rysujemy proste linie ręki dla podglądu
                try:
                    p12 = (lm_list[12][1], lm_list[12][2])  # Bark
                    p14 = (lm_list[14][1], lm_list[14][2])  # Łokieć
                    p16 = (lm_list[16][1], lm_list[16][2])  # Nadgarstek
                    cv2.line(img, p12, p14, (255, 255, 255), 3)
                    cv2.line(img, p14, p16, (255, 255, 255), 3)
                    cv2.circle(img, p14, 8, col, cv2.FILLED)
                except:
                    pass

        cv2.imshow("CyberTrener - Wersja Modularna", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()