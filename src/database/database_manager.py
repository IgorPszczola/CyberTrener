import sqlite3

def create_database():
    db_name = "cybertrener.db"

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    user_table_query = """CREATE TABLE IF NOT EXISTS uzytkownicy (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            imie TEXT NOT NULL, 
                            nazwa_uzytkownika TEXT NOT NULL UNIQUE, 
                            haslo TEXT NOT NULL
                          );"""
    cursor.execute(user_table_query)

    training_table_query = """CREATE TABLE IF NOT EXISTS treningi (
                                id_treningu INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_uzytkownika INTEGER NOT NULL,
                                data_treningu TEXT NOT NULL,
                                opis_treningu TEXT NOT NULL,
                                obciazenie TEXT NOT NULL,
                                wynik INTEGER,
                                FOREIGN KEY(id_uzytkownika) REFERENCES uzytkownicy(id) ON DELETE CASCADE);"""
    cursor.execute(training_table_query)

    conn.commit()
    conn.close()

    print(f"Baza danych '{db_name}' oraz tabele 'uzytkownicy' i 'treningi' zostały pomyślnie utworzone.")

if __name__ == "__main__":
    create_database()