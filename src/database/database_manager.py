import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="cybertrener.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(base_dir, db_name)
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. TABELA UZYTKOWNICY (Zgodnie z diagramem)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uzytkownicy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imie TEXT NOT NULL,
                nazwa_uzytkownika TEXT NOT NULL UNIQUE,
                haslo TEXT NOT NULL
            )
        """)

        # 2. TABELA TRENINGI (Zgodnie z diagramem)
        # Łączymy się kluczem obcym (id_uzytkownika)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS treningi (
                id_treningu INTEGER PRIMARY KEY AUTOINCREMENT,
                id_uzytkownika INTEGER NOT NULL,
                data_treningu TEXT NOT NULL,
                opis_treningu TEXT,
                obciazenie TEXT,
                wynik INTEGER,
                FOREIGN KEY(id_uzytkownika) REFERENCES uzytkownicy(id)
            )
        """)
        
        # Tworzymy domyślnego użytkownika "Gość", żeby kod działał bez logowania
        cursor.execute("INSERT OR IGNORE INTO uzytkownicy (imie, nazwa_uzytkownika, haslo) VALUES ('Gość', 'gosc', '1234')")
        
        conn.commit()
        conn.close()

    def get_user_id(self, username):
        """Pobiera ID użytkownika na podstawie loginu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM uzytkownicy WHERE nazwa_uzytkownika = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # --- ZAPISYWANIE TRENINGU (Dostosowane do diagramu) ---
    def save_workout(self, username, exercise, weight, good, bad, grade, break_time):
        """
        Mapowanie danych na kolumny z diagramu:
        - opis_treningu -> Ćwiczenie, Szczegóły powtórzeń, Ocena, Czas przerwy
        - obciazenie -> Tekst (np. "12.5 kg")
        - wynik -> Suma powtórzeń (liczba całkowita)
        """
        user_id = self.get_user_id(username)
        
        # Jeśli nie znaleziono usera (np. wpisujesz 'Gość' a go nie ma), użyj domyślnego ID 1
        if not user_id:
            user_id = 1 

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Tworzymy opis zawierający te dane, dla których nie ma osobnych kolumn na diagramie
        full_description = f"{exercise} | Przerwa: {break_time}s | Ocena: {grade} | Szczegóły: {good} OK / {bad} ZŁE"
        
        # Obciążenie jako tekst (zgodnie z diagramem)
        weight_text = f"{weight} kg"
        
        # Wynik jako liczba (suma powtórzeń)
        total_reps = good + bad

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO treningi 
            (id_uzytkownika, data_treningu, opis_treningu, obciazenie, wynik)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, current_time, full_description, weight_text, total_reps))
        
        conn.commit()
        conn.close()
        print(f"--- ZAPISANO DO TABELI TRENINGI: UserID={user_id}, Wynik={total_reps} ---")

    # POBIERANIE HISTORII
    def get_user_history(self, username):
        """Pobiera historię treningów dla danego użytkownika"""
        user_id = self.get_user_id(username)
        
        if not user_id:
            return [] # Jeśli nie ma usera, zwróć pustą listę

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pobieramy dane posortowane od najnowszego (DESC)
        cursor.execute("""
            SELECT data_treningu, opis_treningu, obciazenie, wynik 
            FROM treningi 
            WHERE id_uzytkownika = ? 
            ORDER BY id_treningu DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- Rejestracja i Logowanie bez zmian ---
    def register_user(self, name, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO uzytkownicy (imie, nazwa_uzytkownika, haslo) VALUES (?, ?, ?)",
                           (name, username, password))
            conn.commit()
            return True, "Rejestracja pomyślna!"
        except sqlite3.IntegrityError:
            return False, "Ta nazwa użytkownika jest już zajęta!"
        except Exception as e:
            return False, f"Błąd bazy danych: {e}"
        finally:
            conn.close()

    def check_login(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uzytkownicy WHERE nazwa_uzytkownika = ? AND haslo = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return True if user else False