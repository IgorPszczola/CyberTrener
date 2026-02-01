STYLESHEET = """
    /* 1. WSPÓLNE */

    QMainWindow {
        background-color: #1a1a1a;
    }
    QWidget {
        font-family: 'Roboto', 'Arial';
    }
    QLabel {
        color: white;
    }

    /* Typografia (Wspólna) */
    QLabel.h1 { 
        font-size: 62px; 
        font-weight: bold; 
        color: white; 
        background: transparent; 
    }
    QLabel.h2 { 
        font-size: 48px; 
        font-weight: bold; 
        color: white; 
        background: transparent; 
    }

    /* Przyciski (Wspólne) */
    QPushButton {
        border-radius: 5px;
        color: white;
        font-weight: bold;
        padding: 15px;
        font-size: 24px;
        border: 2px solid transparent; 
        background-color: transparent;
    }

    /* Wariant: Czerwony (Start, Zaloguj, Zapisz) */
    QPushButton[type="red"] {
        background-color: #D03B3B;
        border-color: #902020;
    }
    QPushButton[type="red"]:hover {
        background-color: #FF5555;
    }

    /* Wariant: Szary (Historia, Ustawienia) */
    QPushButton[type="grey"] {
        background-color: #333333;
        border-color: #555555;
    }
    QPushButton[type="grey"]:hover {
        background-color: #444444;
    }

    /* Wariant: Jasno-szary (Wyjście, Powrót) */
    QPushButton[type="light_grey"] {
        background-color: #555555;
        border-color: #777777;
    }
    QPushButton[type="light_grey"]:hover {
        background-color: #777777;
    }

    /* Pola tekstowe (Inputy) */
    QLineEdit {
        background-color: #333;
        color: white;
        border: 2px solid #555;
        border-radius: 5px;
        padding: 10px;
        font-size: 20px;
    }
    QLineEdit:focus {
        border-color: #D03B3B;
    }

    /* Radio Buttons */
    QRadioButton {
        color: white;
        font-size: 32px;
        padding: 5px;
        spacing: 10px;
    }
    QRadioButton::indicator {
        width: 20px;
        height: 20px;
    }

    /* Suwaki (Sliders) */
    QSlider::groove:horizontal { 
        height: 10px; 
        background: #555; 
        border-radius: 5px; 
    }
    QSlider::handle:horizontal { 
        background: #D03B3B; 
        width: 30px; 
        margin: -10px 0; 
        border-radius: 15px; 
    }

    /* 2. LOGIN_WINDOW.PY / REGISTER_WINDOW.PY */

    /* Kontener formularza logowania/rejestracji */
    QFrame.form_frame {
        background-color: rgba(30, 30, 30, 220);
        border-radius: 15px;
        padding: 20px;
    }

    /* 3. SETTINGS_WINDOW.PY */

    /* Wiersz pojedynczego ustawienia */
    QFrame.setting_row {
        background-color: rgba(40, 40, 40, 200);
        border-radius: 10px;
        padding: 10px;
    }

    /* Przyciski +/- w ustawieniach */
    QPushButton.settings_control_btn {
        background-color: #444;
        color: white;
        font-size: 30px; 
        border-radius: 10px;
        border: none;
        padding: 0px;
    }
    QPushButton.settings_control_btn:hover {
        background-color: red;
    }

    /* Etykiety tekstowe specyficzne dla ustawień */
    QLabel.label { 
        font-size: 32px; 
        color: #ddd; 
        background: transparent; 
        font-weight: bold; 
    }

    /* Wartości liczbowe w ustawieniach */
    QLabel.value { 
        font-size: 36px; 
        font-weight: bold; 
        color: white; 
        background: transparent; 
    }

    /* Pola tekstowe - Duże (np. Obciążenie) */
    QLineEdit.big_input {
        padding: 5px; 
        font-size: 32px; 
        font-weight: bold;
        background-color: #444; 
        color: white; 
        border: 2px solid #555; 
        border-radius: 5px;
    }
    QLineEdit.big_input:focus {
        border-color: #D03B3B;
        background-color: #555;
    }

    /* Pola tekstowe - Powtórzenia (Input obok Radio Button) */
    QLineEdit.reps_input {
        padding: 5px; 
        font-size: 24px; 
        font-weight: bold; 
        background-color: #444; 
        color: white; 
        border: 2px solid #555; 
        border-radius: 5px;
    }
    QLineEdit.reps_input:focus {
        border-color: #D03B3B;
        background-color: #555;
    }

    /* 4. HISTORY_WINDOW.PY */

    QTableWidget {
        background-color: rgba(40, 40, 40, 200);
        color: white;
        font-size: 24px;
        gridline-color: #555;
        border: none;
    }

    QHeaderView::section {
        background-color: #D03B3B;
        color: white;
        padding: 15px;
        font-size: 28px;
        font-weight: bold;
        border: none;
    }

    QTableWidget::item {
        border-bottom: 1px solid #555;
    }

    /* 5. TRAINING_WINDOW.PY */

    /* Pasek boczny */
    #sidebar {
        background-color: rgba(30, 30, 30, 240);
        border-right: 1px solid #444;
    }

    /* Nagłówek Statusu */
    QLabel#lbl_status {
        background-color: transparent; 
        font-size: 38px; 
        font-weight: bold; 
        color: white;
    }

    /* Specjalny przycisk STOP */
    QPushButton#btn_stop {
        background-color: #D03B3B;
        border: 2px solid #902020;
        color: white;
        font-weight: bold;
        padding: 15px;
        font-size: 24px;
        border-radius: 5px;
    }
    QPushButton#btn_stop:hover {
        background-color: #FF5555;
    }

    /* Karty informacyjne (Seria, Powtórzenia) */
    QFrame.info_card {
        background-color: transparent; 
        border-radius: 5px; 
        padding: 15px;
    }
    QLabel.card_title {
        color: #aaa; 
        font-size: 28px; 
        background-color: transparent;
    }
    QLabel.card_value {
        color: white; 
        font-size: 22px; 
        font-weight: bold; 
        background-color: transparent;
    }

    /* Etykieta celu (Target) */
    QLabel.target_label {
        font-size: 28px;
        color: #ccc;
        padding: 10px;
        background-color: transparent;
    }

    /* Placeholder kamery */
    QLabel.camera_placeholder {
        background-color: black;
        color: white;
        font-size: 30px;
        border: 2px dashed #555;
        border-radius: 10px;
    }
"""