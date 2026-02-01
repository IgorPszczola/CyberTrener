import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.gui.main_window import MainWindow

# Importujemy styles.py z src/gui
# Musimy dodać ścieżkę do sys.path, jeśli Python nie widzi folderów
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Ustawienie domyślnej czcionki
    app.setFont(QFont("Roboto", 12))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())