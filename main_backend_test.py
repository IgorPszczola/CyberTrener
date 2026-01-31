import cv2
import time
import numpy as np
from collections import deque
from src.logic.pose_detector import PoseDetector


def main():
    # --- KONFIGURACJA ---
    ip_camera_url = 'http://192.168.18.13:4747/video'

    # Parametry kątowe
    ANGLE_DOWN = 140
    ANGLE_UP = 45

    # Parametry techniki
    ELBOW_THRESHOLD = 30
    BACK_THRESHOLD = 15

    cap = cv2.VideoCapture(ip_camera_url)
    cap.set(3, 640)
    cap.set(4, 480)

    detector = PoseDetector()
    angle_history = deque(maxlen=7)

    # Zmienne licznika
    good_reps = 0
    bad_reps = 0
    dir = 0
    is_rep_clean = True

    pTime = 0

    print("CyberTrener: Poprawiona logika zliczania.")

    while True:
        success, img = cap.read()
        if not success:
            print("Brak klatki.")
            break

        img = detector.find_pose(img)
        lm_list = detector.find_position(img, draw=False)

        final_angle = 0
        per = 0
        bar = 650

        elbow_error = False
        back_error = False

        if len(lm_list) != 0:
            # 1. KĄT GŁÓWNY (Biceps)
            raw_angle = detector.find_angle(img, 12, 14, 16, draw=False)

            # 2. KĄT ŁOKCIA (Technika)
            elbow_drift_angle = detector.find_angle(img, 24, 12, 14, draw=True)

            # 3. KĄT PLECÓW (Technika)
            back_angle = detector.find_angle(img, 12, 24, 26, draw=True)

            # Wygładzanie
            if raw_angle > 0:
                angle_history.append(raw_angle)
            if len(angle_history) > 0:
                final_angle = int(sum(angle_history) / len(angle_history))
            else:
                final_angle = int(raw_angle)

            # Przeliczanie na %
            per = np.interp(final_angle, (ANGLE_UP, ANGLE_DOWN), (100, 0))
            bar = np.interp(final_angle, (ANGLE_UP, ANGLE_DOWN), (100, 650))

            # --- ANALIZA BŁĘDÓW ---
            # WAŻNE: Sprawdzamy błędy TYLKO jeśli zaczęliśmy ruch (np. powyżej 5%)
            # Dzięki temu, jak stoisz luźno na dole, nie zalicza Ci błędu "na zapas".
            if per > 5:
                # A. Łokieć
                if elbow_drift_angle > ELBOW_THRESHOLD:
                    elbow_error = True
                    is_rep_clean = False

                # B. Plecy
                if back_angle > 0:
                    dist_from_straight = abs(180 - back_angle)
                    if dist_from_straight > BACK_THRESHOLD:
                        back_error = True
                        is_rep_clean = False

            # --- RYSOWANIE OSTRZEŻEŃ ---
            if elbow_error:
                cv2.putText(img, "LOKIEC!", (50, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                cv2.line(img, (lm_list[12][1], lm_list[12][2]), (lm_list[14][1], lm_list[14][2]), (0, 0, 255), 5)

            if back_error:
                cv2.putText(img, "PLECY!", (50, 250), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                cv2.line(img, (lm_list[12][1], lm_list[12][2]), (lm_list[24][1], lm_list[24][2]), (0, 0, 255), 5)

            # --- LOGIKA LICZENIA (NAPRAWIONA) ---

            # Szczyt ruchu (100%)
            if per == 100:
                if dir == 0:
                    dir = 1  # Zmiana kierunku na dół

            # Koniec ruchu (0%)
            if per == 0:
                if dir == 1:
                    # 1. NAJPIERW SPRAWDZAMY JAKOŚĆ
                    if is_rep_clean:
                        good_reps += 1
                        print("Dobre +1")
                    else:
                        bad_reps += 1
                        print("Złe +1")

                    # 2. DOPIERO TERAZ RESETUJEMY WSZYSTKO
                    dir = 0
                    is_rep_clean = True  # Reset flagi na następny ruch

            # Kolor paska (zależy od aktualnego stanu flagi)
            bar_color = (0, 255, 0) if is_rep_clean else (0, 0, 255)

            # --- GUI ---
            # Pasek
            cv2.rectangle(img, (550, 100), (625, 650), bar_color, 3)
            cv2.rectangle(img, (550, int(bar)), (625, 650), bar_color, cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (550, 75), cv2.FONT_HERSHEY_PLAIN, 4, bar_color, 4)

            # Szkielet
            x1, y1 = lm_list[12][1], lm_list[12][2]
            x2, y2 = lm_list[14][1], lm_list[14][2]
            x3, y3 = lm_list[16][1], lm_list[16][2]
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 8, (0, 0, 255), cv2.FILLED)

            # Tabela wyników
            cv2.rectangle(img, (0, 500), (300, 720), (50, 50, 50), cv2.FILLED)
            cv2.putText(img, f"DOBRE: {good_reps}", (20, 580), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            cv2.putText(img, f"ZLE:   {bad_reps}", (20, 650), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

            # Status
            status_text = "OK" if is_rep_clean else "BLAD"
            status_col = (0, 255, 0) if is_rep_clean else (0, 0, 255)
            cv2.putText(img, f"STAN: {status_text}", (20, 700), cv2.FONT_HERSHEY_PLAIN, 2, status_col, 2)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        cv2.imshow("CyberTrener - Final Logic", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()