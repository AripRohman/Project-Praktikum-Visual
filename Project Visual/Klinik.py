import sys,os
import requests
from datetime import date
import calendar
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView,
    QComboBox, QDateEdit, QGridLayout, QFrame, QMainWindow
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QAction, QPixmap, QIcon

# Import dari file lain
from Laporan import LaporanWindow
from Login_Register import AuthSystem
from config import API_URL, HEADERS, APP_DIR, STYLE_FILE,ICON_FILE, LOGO_FILE


#Window Riwayat Pasien
class RiwayatWindow(QMainWindow):
    """Window untuk menampilkan riwayat pasien yang sudah selesai"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Riwayat Pasien - Puskesmas Siantan Tengah")
        self.resize(1300, 600)

        if os.path.exists(LOGO_FILE):
            self.setWindowIcon(QIcon(LOGO_FILE))
            

        #SETUP UI 
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Filter/Search
        filter_layout = QHBoxLayout()
        self.search = QLineEdit()   
        self.search.setPlaceholderText("🔍 Cari nama pasien...")
        self.search.textChanged.connect(self.load_data)
        filter_layout.addWidget(self.search)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Antrian", "Nama", "Jenis Kelamin", "Keluhan", 
            "Status", "Tanggal Periksa", "Alamat", "No Telepon", "Tanggal Lahir"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Label judul
        label_section1 = QLabel("DATA PENGUNJUNG YANG SDUAH SELESAI PERIKSA")
        label_section1.setObjectName("label_section1")
        label_section1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_section1.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        """)

        # Susun layout
        layout.addWidget(label_section1)
        layout.addLayout(filter_layout) 
        layout.addWidget(self.table)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Load data
        self.load_data()

    def load_data(self):
        """Load data pasien yang sudah selesai dari API"""
        nama = self.search.text().strip()
        url = f"{API_URL}?status=eq.Selesai&order=tanggal.desc,no_antrian.asc"

        if nama:
            url += f"&nama=ilike.*{nama}*"

        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                QMessageBox.warning(self, "Error", f"Gagal mengambil data: {r.text}")
                return

            self.table.setRowCount(0)
            for row, item in enumerate(r.json()):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(item["no_antrian"])))
                self.table.setItem(row, 2, QTableWidgetItem(item["nama"]))
                self.table.setItem(row, 3, QTableWidgetItem(item["jenis_kelamin"]))
                self.table.setItem(row, 4, QTableWidgetItem(item["keluhan"]))
                self.table.setItem(row, 5, QTableWidgetItem(item["status"]))
                self.table.setItem(row, 6, QTableWidgetItem(item["tanggal"]))
                self.table.setItem(row, 7, QTableWidgetItem(item["alamat"]))        
                self.table.setItem(row, 8, QTableWidgetItem(item["No_Telepon"]))
                self.table.setItem(row, 9, QTableWidgetItem(item["tgl_lahir"]))
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error Koneksi", f"Tidak dapat terhubung ke server:\n{str(e)}")



# APLIKASI UTAMA KLINIK

class KlinikApp(QMainWindow):
    """Aplikasi utama untuk manajemen pasien puskesmas"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Data Pasien - Puskesmas Siantan Tengah")
        self.resize(1300, 800)
        self.editing_id = None

        if os.path.exists(LOGO_FILE):
            self.setWindowIcon(QIcon(LOGO_FILE))
        
        #SETUP UI
        self.setup_ui()
        
        #LOAD DATA AWAL
        self.load_data()

    def setup_ui(self):
        """Setup semua komponen UI"""
        central_widget = QWidget()
        layout = QVBoxLayout()

        #FORM INPUT PASIEN
        form = self.create_form_input()
        
        #SEPARATOR
        separator1 = self.create_separator()
        separator2 = self.create_separator()
        separator3 = self.create_separator()
        separator4 = self.create_separator()

        #LABEL JUDUL
        label_section = QLabel("PUSKESMAS SIANTAN TENGAH")
        label_section.setObjectName("label_section")
        label_section.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #TOMBOL AKSI
        btn_layout = self.create_buttons()

        #TABEL DATA PASIEN
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Antrian", "Nama", "Jenis Kelamin", "Keluhan", 
            "Status", "Tanggal Periksa", "Alamat", "No Telepon", "Tanggal Lahir"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.table_clicked)

        #SUSUN LAYOUT
        layout.addWidget(label_section)
        layout.addWidget(separator1)
        layout.addLayout(form)
        layout.addWidget(separator2)
        layout.addWidget(self.table)
        layout.addWidget(separator3)
        layout.addLayout(btn_layout)
        layout.addWidget(separator4)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_form_input(self):
        """Membuat form input data pasien"""
        form = QHBoxLayout()

        #FIELD NAMA
        row_nama = QHBoxLayout()
        self.nama = QLabel("Nama : ")
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama Pasien")
        row_nama.addWidget(self.nama)
        row_nama.addWidget(self.input_nama)
        form.addLayout(row_nama)

        #FIELD ALAMAT
        row_alamat = QHBoxLayout()
        self.alamat = QLabel("Alamat : ")
        self.input_alamat = QLineEdit()
        self.input_alamat.setPlaceholderText("Alamat Lengkap")
        row_alamat.addWidget(self.alamat)
        row_alamat.addWidget(self.input_alamat)
        form.addLayout(row_alamat)

        #FIELD NO TELEPON
        row_hp = QHBoxLayout()
        self.no_hp = QLabel("No Telepon : ")
        self.input_No_Hp = QLineEdit()
        self.input_No_Hp.setPlaceholderText("No Telepon")
        row_hp.addWidget(self.no_hp)
        row_hp.addWidget(self.input_No_Hp)
        form.addLayout(row_hp)

        #FIELD TANGGAL LAHIR
        row_tgl = QHBoxLayout()
        self.tgl = QLabel("Tanggal Lahir : ")
        self.tgl_lahir = QDateEdit()
        self.tgl_lahir.setCalendarPopup(True)
        self.tgl_lahir.setDate(QDate.currentDate())
        row_tgl.addWidget(self.tgl)
        row_tgl.addWidget(self.tgl_lahir)
        form.addLayout(row_tgl)

        #FIELD JENIS KELAMIN
        row_jk = QHBoxLayout()
        self.kelamin = QLabel("Jenis Kelamin : ")
        self.combo_jk = QComboBox()
        self.combo_jk.addItems(["Laki-laki", "Perempuan"])
        self.combo_jk.setFixedWidth(140)
        row_jk.addWidget(self.kelamin)
        row_jk.addWidget(self.combo_jk)
        form.addLayout(row_jk)

        #FIELD KELUHAN
        row_keluhan = QHBoxLayout()
        self.keluhan = QLabel("Keluhan : ")
        self.input_keluhan = QLineEdit()
        self.input_keluhan.setPlaceholderText("Keluhan Pasien")
        row_keluhan.addWidget(self.keluhan)
        row_keluhan.addWidget(self.input_keluhan)
        form.addLayout(row_keluhan)

        return form    


    def create_buttons(self):
        """Membuat tombol-tombol aksi"""
        btn_layout = QGridLayout()
        
        # Buat tombol
        self.btn_add = QPushButton("Tambah")
        self.btn_update = QPushButton("Update")
        self.btn_call = QPushButton("Panggil")
        self.btn_selesai = QPushButton("Selesai")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_delete = QPushButton("Hapus")

        # Set ukuran tombol
        for btn in [self.btn_add, self.btn_update, self.btn_call, 
                    self.btn_selesai, self.btn_refresh, self.btn_delete]:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Susun tombol dalam grid
        btn_layout.addWidget(self.btn_add, 0, 0)
        btn_layout.addWidget(self.btn_update, 0, 1)
        btn_layout.addWidget(self.btn_call, 0, 2)
        btn_layout.addWidget(self.btn_selesai, 1, 0)
        btn_layout.addWidget(self.btn_refresh, 1, 1)
        btn_layout.addWidget(self.btn_delete, 1, 2)

        # Connect ke fungsi
        self.btn_add.clicked.connect(self.add_data)
        self.btn_update.clicked.connect(self.update_data)
        self.btn_call.clicked.connect(self.call_patient)
        self.btn_selesai.clicked.connect(self.selesai_pasien)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_delete.clicked.connect(self.delete_data)

        return btn_layout

    def create_separator(self):
        """Membuat garis pemisah"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(10)
        return separator

    
    # FUNGSI LOAD DATA

    def load_data(self):
        """Load data pasien dari API"""
        url = f"{API_URL}?status=neq.Selesai&order=no_antrian.asc"
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            
            if r.status_code != 200:
                QMessageBox.warning(self, "Error", f"Gagal mengambil data: {r.text}")
                return

            self.table.setRowCount(0)
            for row, item in enumerate(r.json()):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(item["no_antrian"])))
                self.table.setItem(row, 2, QTableWidgetItem(item["nama"]))
                self.table.setItem(row, 3, QTableWidgetItem(item["jenis_kelamin"]))
                self.table.setItem(row, 4, QTableWidgetItem(item["keluhan"]))
                self.table.setItem(row, 5, QTableWidgetItem(item["status"]))
                self.table.setItem(row, 6, QTableWidgetItem(item["tanggal"]))
                self.table.setItem(row, 7, QTableWidgetItem(item["alamat"]))
                self.table.setItem(row, 8, QTableWidgetItem(item["No_Telepon"]))
                self.table.setItem(row, 9, QTableWidgetItem(item["tgl_lahir"]))
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error Koneksi", f"Tidak dapat terhubung ke server:\n{str(e)}")


    # FUNGSI TAMBAH DATA

    def add_data(self):
        """Tambah data pasien baru"""
        if not self.input_nama.text() or not self.input_keluhan.text():
            QMessageBox.warning(self, "Error", "Nama dan Keluhan harus diisi!")
            return

        today = date.today().isoformat()
        
        # Ambil nomor antrian terakhir
        url_last = f"{API_URL}?tanggal=eq.{today}&select=no_antrian&order=no_antrian.desc&limit=1"
        try:
            r = requests.get(url_last, headers=HEADERS, timeout=10)
            last_no = r.json()[0]["no_antrian"] if r.json() else 0
        except:
            last_no = 0

        # Buat payload
        payload = {
            "no_antrian": last_no + 1,
            "nama": self.input_nama.text(),
            "jenis_kelamin": self.combo_jk.currentText(),
            "keluhan": self.input_keluhan.text(),
            "status": "Menunggu",
            "tanggal": today,
            "alamat": self.input_alamat.text(),
            "No_Telepon": self.input_No_Hp.text(),
            "tgl_lahir": self.tgl_lahir.date().toString("yyyy-MM-dd")
        }

        try:
            requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
            QMessageBox.information(self, "Sukses", f"Pasien {payload['nama']} berhasil ditambahkan!\nNomor Antrian: {payload['no_antrian']}")
            self.clear_input()
            self.load_data()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Gagal menambah data:\n{str(e)}")


    # FUNGSI UPDATE DATA

    def update_data(self):
        """Update data pasien"""
        if not self.editing_id:
            QMessageBox.warning(self, "Info", "Pilih data yang ingin diupdate dengan double-click pada tabel!")
            return

        payload = {
            "nama": self.input_nama.text(),
            "jenis_kelamin": self.combo_jk.currentText(),
            "keluhan": self.input_keluhan.text(),
            "alamat": self.input_alamat.text(),
            "No_Telepon": self.input_No_Hp.text(),
            "tgl_lahir": self.tgl_lahir.date().toString("yyyy-MM-dd")
        }

        try:
            url = f"{API_URL}?id=eq.{self.editing_id}"
            requests.patch(url, json=payload, headers=HEADERS, timeout=10)
            QMessageBox.information(self, "Sukses", "Data berhasil diupdate!")
            self.clear_input()
            self.load_data()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Gagal update data:\n{str(e)}")


    # FUNGSI PANGGIL PASIEN

    def call_patient(self):
        """Panggil pasien berikutnya"""
        today = date.today().isoformat()
        url = f"{API_URL}?status=eq.Menunggu&tanggal=eq.{today}&order=no_antrian.asc&limit=1"
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            
            if not r.json():
                QMessageBox.information(self, "Info", "Tidak ada pasien yang menunggu!")
                return

            pasien = r.json()[0]
            requests.patch(
                f"{API_URL}?id=eq.{pasien['id']}",
                json={"status": "Dipanggil"}, 
                headers=HEADERS,
                timeout=10
            )
            
            QMessageBox.information(
                self, 
                "Pasien Dipanggil", 
                f"Pasien {pasien['nama']}\nNomor Antrian: {pasien['no_antrian']}\n\nSilakan masuk ke ruang pemeriksaan!"
            )
            self.load_data()
            
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Gagal memanggil pasien:\n{str(e)}")


    # FUNGSI SELESAI PASIEN

    def selesai_pasien(self):
        """Tandai pasien sudah selesai diperiksa"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih pasien yang sudah selesai diperiksa!")
            return

        id_pasien = self.table.item(row, 0).text()
        nama_pasien = self.table.item(row, 2).text()

        try:
            response = requests.patch(
                f"{API_URL}?id=eq.{id_pasien}",
                json={"status": "Selesai"},
                headers=HEADERS,
                timeout=10
            )

            if response.status_code in (200, 204):
                QMessageBox.information(self, "Sukses", f"Pasien {nama_pasien} sudah selesai diperiksa!")
                self.clear_input()
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", response.text)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Gagal update status:\n{str(e)}")


    # FUNGSI HAPUS DATA

    def delete_data(self):
        """Hapus data pasien"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang ingin dihapus!")
            return

        id_pasien = self.table.item(row, 0).text()
        nama_pasien = self.table.item(row, 2).text()

        konfirmasi = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus data pasien:\n\n{nama_pasien} (ID: {id_pasien})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if konfirmasi == QMessageBox.StandardButton.No:
            return

        try:
            delete_url = f"{API_URL}?id=eq.{id_pasien}"
            response = requests.delete(delete_url, headers=HEADERS, timeout=10)

            if response.status_code in (200, 204):
                QMessageBox.information(self, "Sukses", "Data berhasil dihapus!")
                self.clear_input()
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", response.text)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Gagal menghapus data:\n{str(e)}")


    # FUNGSI KLIK TABEL

    def table_clicked(self, row, col):
        """Handler saat double-click pada tabel"""
        self.editing_id = self.table.item(row, 0).text()
        self.input_nama.setText(self.table.item(row, 2).text())
        self.combo_jk.setCurrentText(self.table.item(row, 3).text())
        self.input_keluhan.setText(self.table.item(row, 4).text())
        self.input_alamat.setText(self.table.item(row, 7).text())
        self.input_No_Hp.setText(self.table.item(row, 8).text())
        self.tgl_lahir.setDate(QDate.fromString(self.table.item(row, 9).text(), "yyyy-MM-dd"))


    # FUNGSI CLEAR INPUT

    def clear_input(self):
        """Bersihkan semua input field"""
        self.input_nama.clear()
        self.input_keluhan.clear()
        self.input_alamat.clear()
        self.input_No_Hp.clear()
        self.combo_jk.setCurrentIndex(0)
        self.tgl_lahir.setDate(QDate.currentDate())
        self.editing_id = None


    # FUNGSI KLIK DI LUAR TABEL

    def mousePressEvent(self, event):
        """Clear input saat klik di luar tabel"""
        widget = self.childAt(event.position().toPoint())
        if widget is None or not self.table.isAncestorOf(widget):
            self.clear_input()
        super().mousePressEvent(event)


    # FUNGSI BUKA RIWAYAT

    def open_riwayat(self):
        """Buka window riwayat pasien"""
        self.riwayat = RiwayatWindow()
        self.riwayat.show()        


    def open_laporan(self):
        """Buka window laporan"""
        self.laporan = LaporanWindow()
        self.laporan.show()


def load_stylesheet(filename):
    """Load stylesheet dari file QSS"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan!")
        return ""


# FUNGSI MAIN

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Terapkan style
    stylesheet = load_stylesheet(STYLE_FILE)
    app.setStyleSheet(stylesheet)
    

    # SETUP LOGIN DAN MAIN WINDOW

    login_window = AuthSystem()
    klinik_window = KlinikApp()
    
    # SETUP MENUBAR DAN PROFIL

    def setup_menubar_and_profile():
        """Setup MenuBar dengan menu dan profil user"""
        menubar = klinik_window.menuBar()
        
        # MENU FILE 
        file_menu = menubar.addMenu("📁 Menu")
                
        # Action Riwayat
        riwayat_action = QAction("Riwayat Pasien", klinik_window)
        riwayat_action.triggered.connect(klinik_window.open_riwayat)
        file_menu.addAction(riwayat_action)

        laporan_action = QAction("Laporan", klinik_window)
        laporan_action.triggered.connect(klinik_window.open_laporan)
        file_menu.addAction(laporan_action)
        
        # PANEL USER + LOGOUT 
        profile_widget = QWidget()
        profile_layout = QHBoxLayout(profile_widget)
        profile_layout.setContentsMargins(5, 0, 10, 0)
        profile_layout.setSpacing(10)
        
        # Icon user
        user_icon = QLabel()

        pixmap = QPixmap(ICON_FILE)
        if not pixmap.isNull():
            user_icon.setPixmap(
                pixmap.scaled(
                    35, 35,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            user_icon.setText("👤")
            user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # Label nama user
        klinik_window.user_name_label = QLabel()
        klinik_window.user_name_label.setStyleSheet("""
            color: #2c3e50;
            font-weight: bold;
            font-size: 14px;
            border-radius:4px;
        """)
        
        # Tombol Logout
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(90, 32)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(handle_logout)
        
        profile_layout.addWidget(user_icon)
        profile_layout.addWidget(klinik_window.user_name_label)
        profile_layout.addWidget(logout_btn)
        
        menubar.setCornerWidget(profile_widget, Qt.Corner.TopRightCorner)
    

    # fungsi set user (siapa yang login)

    def set_user_info(username, user_data):
        
        klinik_window.current_user = username
        klinik_window.user_data = user_data
        klinik_window.user_name_label.setText(f"{user_data['name']}")
        klinik_window.setWindowTitle(f"Aplikasi Data Pasien - Petugas {user_data['name']}")

    

    # FUNGSI HANDLE LOGOUT

    def handle_logout():
        """Handler untuk logout"""
        reply = QMessageBox.question(
            klinik_window,
            'Konfirmasi Logout',
            'Apakah Anda yakin ingin logout?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            login_window.clear_session()
            klinik_window.close()
            login_window.show()
            login_window.login_username.clear()
            login_window.login_password.clear()
            login_window.stacked_widget.setCurrentIndex(0)
    

    # FUNGSI SAAT LOGIN BERHASIL

    def on_login_success(username, user_data):
        """Callback saat login berhasil"""
        set_user_info(username, user_data)
        klinik_window.show()
        login_window.close()
    
    # === CONNECT SIGNAL ===
    login_window.login_success.connect(on_login_success)
    
    # === SETUP MENUBAR ===
    setup_menubar_and_profile()
    
    # CEK SESSION (AUTO-LOGIN)

    session = login_window.load_session()
    
    if session and session.get("logged_in") and session.get("username"):
        username = session["username"]
        if username in login_window.users:
            user_data = login_window.users[username]
            set_user_info(username, user_data)
            klinik_window.show()
        else:
            login_window.clear_session()
            login_window.show()
    else:
        login_window.show()
    
    sys.exit(app.exec())