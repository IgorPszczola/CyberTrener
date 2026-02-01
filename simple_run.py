import cv2
import time
from src.logic.pose_detector import PoseDetector
from src.logic.bicep_curl import BicepCurl

def main():
    # 1. Konfiguracja kamery
    cap = cv2.VideoCapture('http://192.168.0.198:4747/video')
    cap.set(3, 1280)
    cap.set(4, 720)

    # 2. Inicjalizacja Twojej logiki (z głosem)
    detector = PoseDetector()
    trener = BicepCurl(detector)

    print("--- URUCHAMIAM TRYB SZYBKI (BEZ LOGOWANIA) ---")
    print("Wciśnij 'q' aby zakończyć.")

    while True:
        success, img = cap.read()
        if not success: 
            print("Nie widzę kamery!")
            break

        # 3. Przetwarzanie obrazu
        img = detector.find_pose(img)
        
        # Tutaj logika zwraca obraz oraz dane (słownik)
        img, data = trener.process(img)

        # 4. Rysowanie interfejsu (bo w wersji GUI robi to PyQt, a tu musimy ręcznie)
        
        # Pasek postępu
        per = data["percentage"]
        # Mapowanie 0-100% na wysokość paska (100 -> 650, 650 -> 650? Nie, odwrotnie)
        bar = 650 - (per * 5.5) # Prosta matematyka do paska
        
        cv2.rectangle(img, (1100, 100), (1175, 650), (0, 255, 0), 3)
        cv2.rectangle(img, (1100, int(bar)), (1175, 650), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(per)}%', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 4)

        # Liczniki
        cv2.rectangle(img, (0, 550), (300, 720), (50, 50, 50), cv2.FILLED)
        cv2.putText(img, f"DOBRE: {data['reps_good']}", (20, 610), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        cv2.putText(img, f"ZLE:   {data['reps_bad']}", (20, 680), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

        # Komunikaty błędów na ekranie (Głos działa w tle w bicep_curl.py)
        feedback = data["feedback"]
        if feedback in ["LOKIEC!", "PLECY!", "Niezaliczone"]:
             cv2.putText(img, feedback, (300, 150), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        elif feedback == "SZUKAM CIE...":
             cv2.putText(img, feedback, (300, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,0), 3)

        # 5. Wyświetlenie
        cv2.imshow("CyberTrener - Tryb Prosty", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 6. Sprzątanie (Ważne, żeby wyłączyć głos!)
    if hasattr(trener, 'voice'):
        trener.voice.stop()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()