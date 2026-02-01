import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from src.gui.styles import STYLESHEET

class TrainingsHistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTrener - Historia")
        self.resize(1200, 850)

        self.bg_pixmap = None
        if os.path.exists("assets/background.jpg"):
            self.bg_pixmap = QPixmap("assets/background.jpg")

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

        # Tabela
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Data treningu", "Opis", "Obciążenie", "Wynik"])

        # Blokada zaznaczania i fokusa
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Wyłączamy pionowy pasek przewijania (skoro tabela ma się dopasować do treści)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Ustawienia nagłówków poziomych
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Stała wysokość wiersza
        ROW_HEIGHT = 70

        # Ustawienia nagłówków pionowych
        v_header = table.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        v_header.setDefaultSectionSize(ROW_HEIGHT)
        v_header.setVisible(False)

        # Przykładowe dane
        data = [
            ("2023-10-27", "3 serie po 15 powtórzeń", "20 kg", "73/100"),
            ("2023-10-25", "3 serie po 15 powtórzeń", "25 kg", "78/100"),
            ("2023-10-20", "3 serie po 15 powtórzeń", "35 kg", "85/100"),
        ]

        table.setRowCount(len(data))

        for row, (date, desc, weight, result) in enumerate(data):
            item_date = QTableWidgetItem(date)
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, item_date)

            item_desc = QTableWidgetItem(desc)
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 1, item_desc)

            item_weight = QTableWidgetItem(weight)
            item_weight.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, item_weight)

            item_res = QTableWidgetItem(result)
            item_res.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 3, item_res)

        total_height = ROW_HEIGHT + (len(data) * ROW_HEIGHT)

        table.setFixedHeight(total_height)

        layout.addWidget(table)
        layout.addStretch()

        btn_back = QPushButton("POWRÓT")
        btn_back.setProperty("type", "light_grey")
        btn_back.setFixedSize(250, 70)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 12))
    window = TrainingsHistoryWindow()
    window.show()
    sys.exit(app.exec())