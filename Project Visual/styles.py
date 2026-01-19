# STYLE UNTUK LOGIN & REGISTER

AUTH_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}

QLabel {
    color: #333;
}

/* Input field login/register */
QLineEdit {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 5px;
    background-color: white;
    color: black;
    font-size: 14px;
}

QLineEdit:focus {
    border: 2px solid #4CAF50;
}

QLineEdit::placeholder {
    color: #95a5a6;
}

/* Tombol login/register */
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    font-weight: bold;
    padding: 10px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

/* Link "Daftar di sini" / "Login di sini" */
QPushButton[flat="true"] {
    background-color: transparent;
    color: #4CAF50;
    text-decoration: underline;
    font-size: 14px;
}

QPushButton[flat="true"]:hover {
    color: #45a049;
}
"""


# STYLE UTAMA (KLINIK)

MAIN_APP_STYLE = """
/* Background utama */
QWidget {
    font-family: "Segoe UI";
    font-size: 14px;
    background: #f7f4f4;
    color:black;
}

/* Label judul */
QLabel#label_section {
    font-size: 50px;
    font-weight: bold;
    color: #555;
    margin: 5px 0;
}

/* Input fields (LineEdit, DateEdit, ComboBox) */
QLineEdit, QDateEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #ccd1d9;
    border-radius: 6px;
    padding: 6px 8px;
    color: black;
}

QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 2px solid #3498db;
}

QLineEdit::placeholder {
    color: #95a5a6;
}

/* Dropdown ComboBox */
QComboBox QAbstractItemView {
    background: white;
    selection-background-color: #3498db;
    selection-color: white;
    color: black;
}

/* Tombol default (biru) */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f618d;
}

/* Tombol HAPUS (merah) */
QPushButton[text="Hapus"] {
    background-color: #e74c3c;
}

QPushButton[text="Hapus"]:hover {
    background-color: #c0392b;
}

/* Tombol SELESAI (hijau) */
QPushButton[text="Selesai"] {
    background-color: #27ae60;
}

QPushButton[text="Selesai"]:hover {
    background-color: #1e8449;
}

/* Tombol REFRESH (orange) */
QPushButton[text="Refresh"] {
    background-color: #FFA500;
}

QPushButton[text="Refresh"]:hover {
    background-color: #FF8C00;
}

/* Tabel */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    gridline-color: #ecf0f1;
    selection-background-color: #3498db;
    selection-color: white;
    color: black;
}

/* Header tabel */
QHeaderView::section {
    background-color: #f2f4f7;
    color: #2c3e50;
    padding: 6px;
    border: 1px solid #dcdcdc;
    font-weight: bold;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #ecf0f1;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #bdc3c7;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #95a5a6;
}

/* MenuBar */
QMenuBar {
    background-color: #ecf0f1;
    color: black;
    font-weight: bold;
    padding: 1px;
}

QMenuBar::item:selected {
    background-color: #3498db;
    color: white;
    border-radius:5px;
}

QMenu {
    background-color: white;
    color: black;
    border: 1px solid #ccd1d9;
    border-radius:5px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
    border-radius:5px;
}
"""