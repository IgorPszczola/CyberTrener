import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_name="cybertrener.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(base_dir, db_name)
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # WAŻNE: 'nazwa_uzytkownika TEXT NOT NULL UNIQUE' - to UNIQUE robi całą robotę
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uzytkownicy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imie TEXT NOT NULL,
                nazwa_uzytkownika TEXT NOT NULL UNIQUE,
                haslo TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def register_user(self, name, username, password):
        """Próbuje zarejestrować użytkownika. Zwraca (Sukces: bool, Wiadomość: str)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO uzytkownicy (imie, nazwa_uzytkownika, haslo) VALUES (?, ?, ?)",
                           (name, username, password))
            conn.commit()
            return True, "Rejestracja pomyślna!"

        except sqlite3.IntegrityError:
            # Ten błąd wyskakuje, gdy naruszymy zasadę UNIQUE (zajęty login)
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