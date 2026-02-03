import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET
from src.database.database_manager import DatabaseManager

class TrainingsHistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Historia")
        self.resize(1200, 850)

        self.bg_pixmap = None
        if os.path.exists("assets/background.png"):
            self.bg_pixmap = QPixmap("assets/background.png")

        self.init_ui()
        self.setStyleSheet(STYLESHEET)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter
        painter = QPainter(self)
        if self.bg_pixmap:
            scaled_bg = self.bg_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                              Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_bg.width()) // 2
            y = (self.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)
        else:
            painter.fillRect(self.rect(), QColor(20, 20, 20))

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        lbl_title = QLabel("HISTORIA TRENINGÓW")
        lbl_title.setProperty("class", "h1")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        table = QTableWidget()
        # Kolumny: Data | Ćwiczenie | Ocena | Obciążenie | Wynik
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Data", "Ćwiczenie", "Ocena", "Obciążenie", "Wynik"])

        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Data dopasowana
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Ćwiczenie szerokie
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Ocena dopasowana
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Obciążenie dopasowane
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Wynik dopasowany

        ROW_HEIGHT = 60
        v_header = table.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        v_header.setDefaultSectionSize(ROW_HEIGHT)
        v_header.setVisible(False)

        # Pobieranie danych
        db = DatabaseManager()
        data_from_db = db.get_user_history("gosc") 

        table.setRowCount(len(data_from_db))
        
        for row, (date, raw_desc, weight, result) in enumerate(data_from_db):
            # --- PARSOWANIE OPISU ---
            exercise = "Trening" # Domyślnie
            grade = "-"
            
            if raw_desc:
                parts = raw_desc.split("|")
                if len(parts) > 0:
                    exercise = parts[0].strip() # Pierwsza część to nazwa
                
                # Szukamy oceny w tekście
                for part in parts:
                    if "Ocena:" in part:
                        grade = part.replace("Ocena:", "").strip()
                        break

            # Kolorowanie Oceny
            grade_item = QTableWidgetItem(grade)
            grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            grade_item.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
            
            if "MISTRZ" in grade:
                grade_item.setForeground(QColor("#00FF00")) # Zielony
            elif "DOBRZE" in grade:
                grade_item.setForeground(QColor("#FFFF00")) # Żółty
            else:
                grade_item.setForeground(QColor("#FFFFFF")) # Biały

            # Data, Ćwiczenie, Ocena, Obciążenie, Wynik
            items = [
                QTableWidgetItem(date),
                QTableWidgetItem(exercise),
                grade_item,
                QTableWidgetItem(weight),
                QTableWidgetItem(str(result))
            ]
            
            # Wstawiamy do tabeli
            table.setItem(row, 0, items[0]) # Data
            table.setItem(row, 1, items[1]) # Ćwiczenie
            table.setItem(row, 2, items[2]) # Ocena (specjalna)
            table.setItem(row, 3, items[3]) # Waga
            table.setItem(row, 4, items[4]) # Wynik

            # Wyśrodkowanie tekstu dla zwykłych komórek
            for i in [0, 1, 3, 4]:
                table.item(row, i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if not data_from_db:
            table.setRowCount(1)
            item = QTableWidgetItem("Brak historii")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, 1, item)

        layout.addWidget(table)
        layout.addStretch()

        btn_back = QPushButton("POWRÓT")
        btn_back.setProperty("type", "light_grey")
        btn_back.setFixedSize(250, 70)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back_to_menu)

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def go_back_to_menu(self):
        from src.gui.menu_window import MenuWindow
        self.menu = MenuWindow()
        self.menu.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = TrainingsHistoryWindow()
    window.show()
    sys.exit(app.exec())