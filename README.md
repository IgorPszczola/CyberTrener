# 💪 CyberTrener - AI Personal Trainer

**CyberTrener** to aplikacja desktopowa napisana w Pythonie, która wykorzystuje Sztuczną Inteligencję (Computer Vision) do analizy techniki ćwiczeń w czasie rzeczywistym.

Aplikacja śledzi ruchy użytkownika za pomocą kamery (internetowej lub telefonu), zlicza powtórzenia oraz wykrywa błędy techniczne, takie jak "bujanie" tułowiem czy odrywanie łokci.

## 🚀 Główne Funkcje

* **Analiza w czasie rzeczywistym:** Wykorzystanie MediaPipe do śledzenia punktów na ciele (pose estimation).
* **Inteligentny Licznik:** Zlicza powtórzenia tylko przy pełnym zakresie ruchu (góra -> dół).
* **Wykrywanie Błędów:**
    * 🚫 **Plecy:** Wykrywa odchylenie tułowia od pionu (oszukiwanie poprzez zarzucanie ciężarem).
    * 🚫 **Łokcie:** Wykrywa wysuwanie łokci do przodu (angażowanie barków zamiast bicepsów).
* **Wizualny Feedback:** Pasek postępu zmieniający kolor (Zielony = OK, Czerwony = Błąd) oraz komunikaty tekstowe.
* **System Konta:** Rejestracja i logowanie użytkowników (SQLite).
* **Historia i Ustawienia:** Zapisywanie wyników treningów oraz konfiguracja parametrów (liczba serii, czas przerwy, cel powtórzeń).
* **Obsługa DroidCam:** Możliwość użycia telefonu jako kamery wysokiej jakości.

## 🛠️ Technologie

Projekt został zbudowany przy użyciu:

* **Python 3.x** - Język główny.
* **PyQt6** - Nowoczesny interfejs graficzny (GUI).
* **OpenCV (`cv2`)** - Przetwarzanie obrazu wideo.
* **MediaPipe** - Detekcja pozy i szkieletu człowieka.
* **NumPy** - Obliczenia matematyczne i geometria.
* **SQLite3** - Baza danych użytkowników.

## ⚙️ Instalacja i Uruchomienie

Aby uruchomić projekt na swoim komputerze, wykonaj poniższe kroki.

### 1. Klonowanie repozytorium
Pobierz kod na swój komputer:
```bash
git clone [https://github.com/IgorPszczola/CyberTrener.git](https://github.com/IgorPszczola/CyberTrener.git)
cd CyberTrener