import sys,os
import json
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QStackedWidget, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from config import USERS_FILE, SESSION_FILE, ICON_FILE,LOGO_FILE,STYLE_FILE



class AuthSystem(QMainWindow):
    login_success = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.users_file = USERS_FILE
        self.session_file = SESSION_FILE
        self.current_user = None
        
        if os.path.exists(LOGO_FILE):
            self.setWindowIcon(QIcon(LOGO_FILE))
        
        self.init_ui()
        self.load_users()
        
    def init_ui(self):
        self.setWindowTitle("Sistem Login & Register - Puskesmas")
        self.setFixedSize(400, 500)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()
        
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)
        
    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("LOGIN")
        title.setObjectName("Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:24; font-weight:bold;")
        layout.addWidget(title)
        
        subtitle = QLabel("Silakan login untuk melanjutkan")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        username_label = QLabel("Username:")
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Masukkan username")
        self.login_username.returnPressed.connect(self.handle_login)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.login_username)
        
        password_label = QLabel("Password:")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Masukkan password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.returnPressed.connect(self.handle_login)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.login_password)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        login_btn = QPushButton("LOGIN")
        login_btn.setFixedHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        register_link_layout = QHBoxLayout()
        register_text = QLabel("Belum punya akun?")
        register_link = QPushButton("Daftar di sini")
        register_link.setFlat(True)
        register_link.setCursor(Qt.CursorShape.PointingHandCursor)
        register_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        register_link_layout.addStretch()
        register_link_layout.addWidget(register_text)
        register_link_layout.addWidget(register_link)
        register_link_layout.addStretch()
        layout.addLayout(register_link_layout)
        
        page.setLayout(layout)
        return page
    
    def create_register_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("REGISTER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Buat akun petugas baru")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)
        
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(4)
        
        name_label = QLabel("Nama Lengkap:")
        self.register_name = QLineEdit()
        self.register_name.setPlaceholderText("Masukkan nama lengkap")
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.register_name)
        
        username_label = QLabel("Username:")
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Masukkan username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.register_username)
        
        password_label = QLabel("Password:")
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Masukkan password")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.register_password)
        
        confirm_label = QLabel("Konfirmasi Password:")
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Masukkan ulang password")
        self.register_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm.returnPressed.connect(self.handle_register)
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.register_confirm)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        register_btn = QPushButton("DAFTAR")
        register_btn.setFixedHeight(45)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)
        
        login_link_layout = QHBoxLayout()
        login_text = QLabel("Sudah punya akun?")
        login_link = QPushButton("Login di sini")
        login_link.setFlat(True)
        login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        login_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        login_link_layout.addStretch()
        login_link_layout.addWidget(login_text)
        login_link_layout.addWidget(login_link)
        login_link_layout.addStretch()
        layout.addLayout(login_link_layout)
        
        page.setLayout(layout)
        return page
    
    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                content = f.read().strip()
                self.users = json.loads(content) if content else {}
        except FileNotFoundError:
            print(f"File {self.users_file} tidak ditemukan, membuat file baru...")
            self.users = {}
            self.save_users()
        except json.JSONDecodeError:
            print("File users.json rusak, membuat file baru...")
            self.users = {}
            self.save_users()
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)
        print(f"Data user disimpan di: {self.users_file}")
    
    def save_session(self, username):
        with open(self.session_file, 'w') as f:
            json.dump({"username": username, "logged_in": True}, f)
    
    def load_session(self):
        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def clear_session(self):
        try:
            with open(self.session_file, 'w') as f:
                json.dump({"logged_in": False}, f)
        except:
            pass
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username dan password harus diisi!")
            return
        
        if username in self.users:
            if self.users[username]['password'] == self.hash_password(password):
                self.current_user = username
                user_data = self.users[username]
                
                QMessageBox.information(
                    self, 
                    "Login Berhasil", 
                    f"Selamat datang, {user_data['name']}!"
                )
                
                self.save_session(username)
                self.login_success.emit(username, user_data)
                
                self.login_username.clear()
                self.login_password.clear()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Password salah!")
        else:
            QMessageBox.warning(self, "Error", "Username tidak ditemukan!")
    
    def handle_register(self):
        name = self.register_name.text().strip()
        username = self.register_username.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if not all([name, username, password, confirm]):
            QMessageBox.warning(self, "Error", "Semua field harus diisi!")
            return
        
        if len(username) < 4:
            QMessageBox.warning(self, "Error", "Username minimal 4 karakter!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password minimal 6 karakter!")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Password dan konfirmasi tidak sama!")
            return
        
        if username in self.users:
            QMessageBox.warning(self, "Error", "Username sudah digunakan!")
            return
        
        self.users[username] = {
            'name': name,
            'password': self.hash_password(password)
        }
        self.save_users()
        
        QMessageBox.information(
            self, 
            "Sukses", 
            f"Akun petugas {name} berhasil dibuat!\n\nSilakan login dengan username: {username}"
        )
        
        self.register_name.clear()
        self.register_username.clear()
        self.register_password.clear()
        self.register_confirm.clear()
        self.stacked_widget.setCurrentIndex(0)

def load_stylesheet(filename):
        """Load stylesheet dari file QSS"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"File {filename} tidak ditemukan!")
            return ""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    stylesheet = load_stylesheet(STYLE_FILE)
    app.setStyleSheet(stylesheet)
    window = AuthSystem()
    window.show()
    sys.exit(app.exec())