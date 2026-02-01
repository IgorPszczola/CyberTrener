import pyttsx3
import threading
import time

# Próba importu pythoncom (niezbędne dla Windowsa w wątkach)
try:
    import pythoncom
except ImportError:
    pythoncom = None

class VoiceService:
    def __init__(self):
        self.lock = threading.Lock() # Zapobiega mówieniu dwóch rzeczy naraz

    def speak(self, text):
        """
        Uruchamia nowy wątek dla każdego zdania.
        To zapobiega blokowaniu kamery.
        """
        # Uruchamiamy wątek, który żyje tylko chwilę (tyle ile trwa zdanie)
        t = threading.Thread(target=self._speak_thread, args=(text,), daemon=True)
        t.start()

    def _speak_thread(self, text):
        # Sprawdzamy, czy ktoś inny już nie mówi (żeby się nie nakładało)
        if self.lock.locked():
            return
        
        with self.lock:
            if pythoncom:
                pythoncom.CoInitialize() # Ważne na Windowsie!

            try:
                # 1. Tworzymy silnik OD NOWA za każdym razem
                engine = pyttsx3.init()
                engine.setProperty('rate', 160)
                
                # Ustawiamy głos (opcjonalnie)
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "pl" in voice.id.lower() or "pol" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break

                # 2. Mówimy
                engine.say(text)
                engine.runAndWait() # To blokuje tylko ten wątek, nie kamerę
                
                # 3. Zamykamy silnik (dla pewności)
                engine.stop()
                del engine

            except Exception as e:
                print(f"Błąd głosu: {e}")

            if pythoncom:
                pythoncom.CoUninitialize()

    def stop(self):
        pass # W tej metodzie "One-Shot" nie musimy nic zatrzymywać ręcznie