import cv2
import time
import numpy as np
import json
from src.logic.pose_detector import PoseDetector
from src.logic.bicep_curl import BicepCurl


def main():
    # ==========================================
    # 1. KONFIGURACJA TRENINGU
    # ==========================================
    ILOSC_SERII = 3
    CZAS_PRZERWY = 30

    # Tryb ćwiczenia: "ILOSC" lub "UPADEK"
    TRYB_CWICZENIA = "UPADEK"
    CEL_POWTORZEN = 10

    IP_CAMERA_URL = 'http://192.168.18.13:4747/video'
    # IP_CAMERA_URL = 0 # Laptop camera

    # ==========================================
    # 2. INICJALIZACJA
    # ==========================================
    cap = cv2.VideoCapture(IP_CAMERA_URL)
    cap.set(3, 640)
    cap.set(4, 480)

    detector = PoseDetector()
    trener = BicepCurl(detector)

    aktualna_seria = 1

    # Stany
    STAN_ODLICZANIE = 1
    STAN_POZYCJA = 2  # Tutaj robimy walidację
    STAN_TRENING = 3
    STAN_PRZERWA = 4
    STAN_KONIEC = 5

    aktualny_stan = STAN_ODLICZANIE
    timer_start = time.time()
    historia_treningu = []

    print(f"START TRENINGU: {TRYB_CWICZENIA}, Serie: {ILOSC_SERII}")

    while True:
        success, img = cap.read()
        if not success:
            print("Brak klatki z kamery.")
            break

        img = detector.find_pose(img, draw=False)
        lm_list = detector.find_position(img, draw=False)
        czas_trwania_stanu = time.time() - timer_start

        # =========================================================
        # MASZYNA STANÓW
        # =========================================================

        # --- KROK 4: ODLICZANIE (10s) ---
        if aktualny_stan == STAN_ODLICZANIE:
            CZAS_NA_START = 10
            pozostalo = int(CZAS_NA_START - czas_trwania_stanu) + 1

            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (640, 480), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)

            cv2.putText(img, f"SERIA {aktualna_seria}/{ILOSC_SERII}", (180, 100), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 255, 255), 3)
            cv2.putText(img, str(pozostalo), (280, 300), cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 255), 10)
            cv2.putText(img, "PRZYGOTUJ SIE", (160, 400), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

            if czas_trwania_stanu > CZAS_NA_START:
                aktualny_stan = STAN_POZYCJA
                timer_start = time.time()

        # --- KROK 5: SPRAWDZENIE POSTAWY (TERAZ DZIAŁA NAPRAWDĘ!) ---
        elif aktualny_stan == STAN_POZYCJA:
            # 1. Pobieramy aktualne kąty (bez rysowania, tylko obliczenia)
            # Używamy progów z klasy trenera (11 stopni dla pleców, 30 dla łokcia)

            postawa_ok = True
            komunikat = "TRZYMAJ POZYCJE..."
            kolor_komunikatu = (0, 255, 0)  # Zielony

            if len(lm_list) != 0:
                # Kąt pleców
                back_angle = detector.find_angle(img, 12, 24, 26, draw=False)
                # Kąt łokcia (czy przy ciele)
                elbow_drift = detector.find_angle(img, 24, 12, 14, draw=False)

                # WALIDACJA PLECÓW
                if back_angle > 0:  # Jeśli widać nogi
                    if abs(180 - back_angle) > trener.back_threshold:
                        postawa_ok = False
                        komunikat = "WYPROSTUJ PLECY!"
                        kolor_komunikatu = (0, 0, 255)  # Czerwony

                        # Rysujemy linię błędu
                        p12 = (lm_list[12][1], lm_list[12][2])
                        p24 = (lm_list[24][1], lm_list[24][2])
                        cv2.line(img, p12, p24, (0, 0, 255), 4)

                # WALIDACJA ŁOKCIA (Tylko jeśli plecy są OK, żeby nie zasypać błędami)
                if postawa_ok and elbow_drift > trener.elbow_threshold:
                    postawa_ok = False
                    komunikat = "LOKCIE DO CIALA!"
                    kolor_komunikatu = (0, 0, 255)

                    p12 = (lm_list[12][1], lm_list[12][2])
                    p14 = (lm_list[14][1], lm_list[14][2])
                    cv2.line(img, p12, p14, (0, 0, 255), 4)

            # LOGIKA CZASOWA
            if not postawa_ok:
                # Jeśli pozycja zła -> RESETUJEMY licznik czasu!
                timer_start = time.time()
                czas_trwania_stanu = 0

            # Wyświetlanie
            pozostalo_do_startu = 3.0 - czas_trwania_stanu
            if pozostalo_do_startu < 0: pozostalo_do_startu = 0

            # Pasek postępu sprawdzania
            bar_width = int(np.interp(czas_trwania_stanu, (0, 3), (0, 400)))
            cv2.rectangle(img, (120, 350), (520, 380), (50, 50, 50), -1)
            cv2.rectangle(img, (120, 350), (120 + bar_width, 380), kolor_komunikatu, -1)

            cv2.putText(img, komunikat, (50, 250), cv2.FONT_HERSHEY_PLAIN, 3, kolor_komunikatu, 3)

            if postawa_ok:
                cv2.putText(img, f"START ZA: {pozostalo_do_startu:.1f}s", (180, 450), cv2.FONT_HERSHEY_PLAIN, 2,
                            (255, 255, 255), 2)

            # PRZEJŚCIE DALEJ (Tylko jeśli utrzymano pozycję przez 3 sekundy)
            if czas_trwania_stanu > 3:
                aktualny_stan = STAN_TRENING
                trener.reset()
                timer_start = time.time()

        # --- KROK 7 & 8: TRENING WŁAŚCIWY ---
        elif aktualny_stan == STAN_TRENING:
            data = trener.process(img)
            zakoncz_serie = False

            # WARUNKI ZAKOŃCZENIA
            if TRYB_CWICZENIA == "ILOSC":
                limit = CEL_POWTORZEN
                cv2.putText(img, f"CEL: {limit}", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                if (data["reps_good"] + data["reps_bad"]) >= limit:
                    zakoncz_serie = True

            elif TRYB_CWICZENIA == "UPADEK":
                cv2.putText(img, "TRYB: UPADEK", (400, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                lm = data["landmarks"]
                if len(lm) != 0:
                    try:
                        # Warunek: Nadgarstek (16) niżej niż Kolano (26) + margines
                        wrist_y = lm[16][2]
                        knee_y = lm[26][2]
                        wykonane = data["reps_good"] + data["reps_bad"]

                        if wrist_y > (knee_y - 50) and wykonane > 0:
                            zakoncz_serie = True
                    except:
                        pass

            # WIZUALIZACJA
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

            # RYSOWANIE SZKIELETU
            lm = data["landmarks"]
            if len(lm) != 0:
                p12, p14, p16 = (lm[12][1], lm[12][2]), (lm[14][1], lm[14][2]), (lm[16][1], lm[16][2])
                cv2.line(img, p12, p14, (255, 255, 255), 3)
                cv2.line(img, p14, p16, (255, 255, 255), 3)
                cv2.circle(img, p14, 8, col, cv2.FILLED)

            if zakoncz_serie:
                print(f"KONIEC SERII {aktualna_seria}.")
                historia_treningu.append({
                    "seria": aktualna_seria,
                    "dobre": data["reps_good"],
                    "zle": data["reps_bad"]
                })
                if aktualna_seria < ILOSC_SERII:
                    aktualny_stan = STAN_PRZERWA
                    aktualna_seria += 1
                    timer_start = time.time()
                else:
                    aktualny_stan = STAN_KONIEC
                    timer_start = time.time()

        # --- KROK 11: PRZERWA ---
        elif aktualny_stan == STAN_PRZERWA:
            czas_do_konca = int(CZAS_PRZERWY - czas_trwania_stanu) + 1
            cv2.rectangle(img, (0, 0), (640, 480), (50, 50, 50), -1)
            cv2.putText(img, "PRZERWA", (200, 150), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 4)
            cv2.putText(img, str(czas_do_konca), (280, 300), cv2.FONT_HERSHEY_PLAIN, 10, (255, 255, 255), 10)

            ost_seria = historia_treningu[-1]
            cv2.putText(img, f"Ostatnia: {ost_seria['dobre']} OK / {ost_seria['zle']} BLAD", (50, 50),
                        cv2.FONT_HERSHEY_PLAIN, 1.5, (200, 200, 200), 1)

            if czas_trwania_stanu > CZAS_PRZERWY:
                aktualny_stan = STAN_ODLICZANIE
                timer_start = time.time()

        # --- KROK 12: KONIEC ---
        elif aktualny_stan == STAN_KONIEC:
            cv2.rectangle(img, (0, 0), (640, 480), (0, 0, 0), -1)
            cv2.putText(img, "TRENING UKONCZONY", (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            y_pos = 200
            for seria in historia_treningu:
                tekst = f"Seria {seria['seria']}: {seria['dobre']} OK, {seria['zle']} ZLE"
                cv2.putText(img, tekst, (50, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
                y_pos += 40
            cv2.putText(img, "'Q' - Wyjscie", (200, 450), cv2.FONT_HERSHEY_PLAIN, 2, (100, 100, 100), 2)

        cv2.imshow("CyberTrener", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            with open("raport_treningu.json", "w") as f:
                json.dump(historia_treningu, f)
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()