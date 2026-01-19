import sys
import os
import requests
from datetime import date, datetime, timedelta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QRadioButton, QButtonGroup,
    QDateEdit, QGroupBox, QGridLayout, QFrame, QTabWidget,
    QFileDialog,QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QPainter, QColor,QIcon
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

from config import API_URL, HEADERS, ICON_FILE,LOGO_FILE


try:
    from openpyxl import Workbook
    from openpyxl.styles import Font as ExcelFont, Alignment, PatternFill
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("openpyxl tidak terinstall. Export Excel tidak tersedia.")


class LaporanWindow(QMainWindow):
    """Window untuk menampilkan laporan lengkap dengan grafik"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Data Pasien - Puskesmas Siantan Tengah")
        self.resize(1200, 700)
        
        if os.path.exists(LOGO_FILE):
            self.setWindowIcon(QIcon(LOGO_FILE))

        self.setStyleSheet("""
        QMainWindow {
            background-color: #ffffff;
        }
        QWidget {
            background-color: #ffffff;
            color: #2c3e50;
        }
        QGroupBox {
            background-color: #ffffff;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 10px;
            padding: 15px;
            font-weight: bold;
            color: #2c3e50;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #2c3e50;
            background-color: #ffffff;
        }
        QRadioButton {
            color: #2c3e50;
            background-color: transparent;
        }
        QLabel {
            color: #2c3e50;
            background-color: transparent;
        }
        QScrollArea {
            background-color: #ffffff;
            border: none;
        }
        QTabWidget::pane {
            background-color: #ffffff;
            border: 1px solid #bdc3c7;
        }
        QTabBar::tab {
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 10px 20px;
            border: 1px solid #bdc3c7;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background-color: #d5dbdb;
        }
        QQRadioButton {
    color: #2c3e50;
    background-color: transparent;
    spacing: 5px;
}



QRadioButton::indicator:unchecked {
    border: 2px solid #95a5a6;
    border-radius: 9px;
    background-color: white;
}

QRadioButton::indicator:checked {
    border: 2px solid #3498db;
    border-radius: 9px;
    background-color: #3498db;
}
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f618d;
}
QTabWidget::pane {
    border: 1px solid #bdc3c7;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #3498db;      /* biru */
    color: white;
    padding: 10px 12px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
    font-weight: bold;
}

/* TAB SAAT HOVER */
QTabBar::tab:hover {
    background-color: #2980b9;      /* biru lebih gelap */
}

/* TAB AKTIF (DIKLIK) */
QTabBar::tab:selected {
    background-color: #1f618d;      /* biru paling gelap */
    color: white;
}

/* TAB TIDAK AKTIF TAPI DI-HOVER */
QTabBar::tab:!selected:hover {
    background-color: #2e86c1;
}

    """)
        
        self.data_pasien = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI dengan tab"""
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("LAPORAN DATA PENGUNJUNG")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 10px 0; font-size:20px; font-weight:bold;")
        
        self.tabs = QTabWidget()
        
        self.tab_statistik = self.create_tab_statistik()
        self.tab_grafik = self.create_tab_grafik()
        self.tab_detail = self.create_tab_detail()
        
        self.tabs.addTab(self.tab_statistik, "Statistik")
        self.tabs.addTab(self.tab_grafik, "Grafik")
        self.tabs.addTab(self.tab_detail, "Detail Data")
        
        layout.addWidget(title)
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def create_tab_statistik(self):
        tab = QWidget()

        # === Scroll Area ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)

        # ================= FILTER =================
        filter_group = QGroupBox("Jenis Laporan")
        filter_layout = QVBoxLayout()

        self.btn_group = QButtonGroup()
        self.radio_hari = QRadioButton("Hari ini")
        self.radio_minggu = QRadioButton("Minggu ini")
        self.radio_bulan = QRadioButton("Bulan ini")
        self.radio_tahun = QRadioButton("Tahun ini")
        self.radio_custom = QRadioButton("Custom (Pilih Tanggal)")

        for r in [
            self.radio_hari,
            self.radio_minggu,
            self.radio_bulan,
            self.radio_tahun,
            self.radio_custom
        ]:
            self.btn_group.addButton(r)
            filter_layout.addWidget(r)

        self.radio_hari.setChecked(True)

        custom_date_layout = QHBoxLayout()
        custom_date_layout.addWidget(QLabel("Dari:"))
        self.date_dari = QDateEdit(calendarPopup=True)
        self.date_dari.setDate(QDate.currentDate())
        custom_date_layout.addWidget(self.date_dari)

        custom_date_layout.addWidget(QLabel("Sampai:"))
        self.date_sampai = QDateEdit(calendarPopup=True)
        self.date_sampai.setDate(QDate.currentDate())
        custom_date_layout.addWidget(self.date_sampai)

        filter_layout.addLayout(custom_date_layout)

        btn_tampilkan = QPushButton("🔍 Tampilkan Laporan")
        btn_tampilkan.setMinimumHeight(40)
        btn_tampilkan.clicked.connect(self.load_laporan)
        filter_layout.addWidget(btn_tampilkan)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # ================= STAT CARD =================
        stats_layout = QGridLayout()

        self.card_total = self.create_stat_card("TOTAL PASIEN", "0", "#1abc9c")
        self.card_laki = self.create_stat_card("LAKI-LAKI", "0", "#3498db")
        self.card_perempuan = self.create_stat_card("PEREMPUAN", "0", "#e73cbc")

        stats_layout.addWidget(self.card_total, 0, 0)
        stats_layout.addWidget(self.card_laki, 0, 1)
        stats_layout.addWidget(self.card_perempuan, 0, 2)


        layout.addLayout(stats_layout)

        # ================= TOP 10 =================
        keluhan_group = QGroupBox("Top 5 Keluhan Terbanyak")
        self.keluhan_layout = QVBoxLayout()
        keluhan_group.setLayout(self.keluhan_layout)
        layout.addWidget(keluhan_group)

        # ================= BUTTON =================
        btn_layout = QHBoxLayout()

        btn_excel = QPushButton("Export Excel")
        btn_excel.setMinimumHeight(40)
        btn_excel.clicked.connect(self.export_excel)

        # btn_print = QPushButton("Print Laporan")
        # btn_print.setMinimumHeight(40)
        # btn_print.clicked.connect(self.print_laporan)

        btn_layout.addWidget(btn_excel)
        # btn_layout.addWidget(btn_print)

        layout.addLayout(btn_layout)
        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)

        return tab

    
    def create_tab_grafik(self):
        """Tab untuk menampilkan grafik"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Visualisasi Data Pasien")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        grafik_layout = QHBoxLayout()
        
        self.chart_view_pie = QChartView()
        self.chart_view_pie.setMinimumHeight(400)
        self.chart_view_pie.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.chart_view_bar = QChartView()
        self.chart_view_bar.setMinimumHeight(400)
        self.chart_view_bar.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        grafik_layout.addWidget(self.chart_view_pie)
        grafik_layout.addWidget(self.chart_view_bar)
        
        layout.addLayout(grafik_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_tab_detail(self):
        """Tab untuk menampilkan detail data"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Detail Data Pasien")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Antrian", "Nama", "Jenis Kelamin", "Keluhan", 
            "Tanggal Lahir", "Tanggal Periksa", "Alamat", "No Telepon"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        tab.setLayout(layout)
        return tab
    
    def create_stat_card(self, title, value, color):
        """Buat card statistik"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value_label")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def load_laporan(self):
        """Load data laporan berdasarkan filter"""
        try:
            date_from, date_to = self.get_date_range()
            
            url = f"{API_URL}?tanggal=gte.{date_from}&tanggal=lte.{date_to}&order=tanggal.asc"
            
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code != 200:
                QMessageBox.warning(self, "Error", f"Gagal mengambil data: {response.text}")
                return
            
            self.data_pasien = response.json()
            
            if len(self.data_pasien) == 0:
                QMessageBox.information(self, "Info", "Tidak ada data pasien pada periode ini.")
                return
            
            self.update_statistik()
            self.update_grafik()
            self.update_table()
            
            QMessageBox.information(self, "Sukses", f"Data berhasil dimuat!\nTotal: {len(self.data_pasien)} pasien")
            
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error Koneksi", f"Tidak dapat terhubung ke server:\n{str(e)}")
    
    def get_date_range(self):
        """Dapatkan range tanggal berdasarkan filter"""
        today = date.today()
        
        if self.radio_hari.isChecked():
            return today.isoformat(), today.isoformat()
        
        elif self.radio_minggu.isChecked():
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start.isoformat(), end.isoformat()
        
        elif self.radio_bulan.isChecked():
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(day=31)
            else:
                end = (today.replace(month=today.month+1, day=1) - timedelta(days=1))
            return start.isoformat(), end.isoformat()
        
        elif self.radio_tahun.isChecked():
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return start.isoformat(), end.isoformat()
        
        else:
            start = self.date_dari.date().toPyDate().isoformat()
            end = self.date_sampai.date().toPyDate().isoformat()
            return start, end
    
    def update_statistik(self):
        """Update card statistik"""
        total = len(self.data_pasien)
        laki = len([x for x in self.data_pasien if x.get('jenis_kelamin') == 'Laki-laki'])
        perempuan = len([x for x in self.data_pasien if x.get('jenis_kelamin') == 'Perempuan'])
        
        self.card_total.findChild(QLabel, "value_label").setText(str(total))
        self.card_laki.findChild(QLabel, "value_label").setText(str(laki))
        self.card_perempuan.findChild(QLabel, "value_label").setText(str(perempuan))
        
        keluhan_count = {}
        for p in self.data_pasien:
            keluhan = p.get('keluhan', 'Tidak ada keluhan')
            keluhan_count[keluhan] = keluhan_count.get(keluhan, 0) + 1
        
        top_keluhan = sorted(keluhan_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        while self.keluhan_layout.count():
            child = self.keluhan_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for idx, (keluhan, jumlah) in enumerate(top_keluhan, 1):
            persentase = (jumlah / total * 100) if total > 0 else 0
            label = QLabel(f"{idx}. {keluhan}: {jumlah} pasien ({persentase:.1f}%)")
            label.setStyleSheet("font-size: 14px; padding: 5px;")
            self.keluhan_layout.addWidget(label)
    
    def update_grafik(self):
        """Update grafik pie dan bar"""
        laki = len([x for x in self.data_pasien if x.get('jenis_kelamin') == 'Laki-laki'])
        perempuan = len([x for x in self.data_pasien if x.get('jenis_kelamin') == 'Perempuan'])
        
        pie_series = QPieSeries()
        slice_laki = pie_series.append(f"Laki-laki ({laki})", laki)
        slice_perempuan = pie_series.append(f"Perempuan ({perempuan})", perempuan)
        
        slice_laki.setBrush(QColor("#3498db"))
        slice_perempuan.setBrush(QColor("#e73cbc"))
        
        slice_laki.setLabelVisible(True)
        slice_perempuan.setLabelVisible(True)
        
        pie_chart = QChart()
        pie_chart.addSeries(pie_series)
        pie_chart.setTitle("Perbandingan Jenis Kelamin Pasien")
        pie_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        pie_chart.legend().setVisible(True)
        pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        self.chart_view_pie.setChart(pie_chart)
        
        keluhan_count = {}
        for p in self.data_pasien:
            keluhan = p.get('keluhan', 'Tidak ada keluhan')
            keluhan_count[keluhan] = keluhan_count.get(keluhan, 0) + 1
        
        top_keluhan = sorted(keluhan_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        bar_set = QBarSet("Jumlah Pasien")
        categories = []
        
        for keluhan, jumlah in top_keluhan:
            bar_set.append(jumlah)
            categories.append(keluhan[:20])
        
        bar_set.setColor(QColor("#27ae60"))
        
        bar_series = QBarSeries()
        bar_series.append(bar_set)
        
        bar_chart = QChart()
        bar_chart.addSeries(bar_series)
        bar_chart.setTitle("Top 5 Keluhan Terbanyak")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        bar_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        bar_series.attachAxis(axis_x)
        
        max_value = max([jumlah for _, jumlah in top_keluhan]) if top_keluhan else 10
        axis_y = QValueAxis()
        axis_y.setRange(0, max_value + 2)
        bar_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        bar_series.attachAxis(axis_y)
        
        bar_chart.legend().setVisible(False)
        
        self.chart_view_bar.setChart(bar_chart)
    
    def update_table(self):
        """Update tabel detail"""
        self.table.setRowCount(0)
        
        for row, pasien in enumerate(self.data_pasien):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(pasien.get('id','_'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(pasien.get('no_antrian', '-'))))
            self.table.setItem(row, 2, QTableWidgetItem(pasien.get('nama', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(pasien.get('jenis_kelamin', '-')))
            self.table.setItem(row, 4, QTableWidgetItem(pasien.get('keluhan', '-')))
            self.table.setItem(row, 5, QTableWidgetItem(pasien.get('tgl_lahir', '-')))
            self.table.setItem(row, 6, QTableWidgetItem(pasien.get('tanggal', '-')))
            self.table.setItem(row, 7, QTableWidgetItem(pasien.get('alamat', '-')))
            self.table.setItem(row, 8, QTableWidgetItem(pasien.get('No_Telepon', '-')))
    
    def export_excel(self):
        """Export laporan ke Excel"""
        if not EXCEL_AVAILABLE:
            QMessageBox.warning(self, "Error", "Library openpyxl tidak terinstall!\n\nInstall dengan: pip install openpyxl")
            return
        
        if not self.data_pasien:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk di-export!\n\nSilakan tampilkan laporan terlebih dahulu.")
            return
        
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Simpan Laporan",
                f"Laporan_Pasien_{date.today()}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_name:
                return
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Laporan Pasien"
            
            ws['A1'] = "LAPORAN DATA PASIEN"
            ws['A1'].font = ExcelFont(size=16, bold=True)
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A1:I1')
            
            ws['A2'] = "PUSKESMAS SIANTAN TENGAH"
            ws['A2'].font = ExcelFont(size=12, bold=True)
            ws['A2'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A2:I2')
            
            date_from, date_to = self.get_date_range()
            ws['A3'] = f"Periode: {date_from} s/d {date_to}"
            ws['A3'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A3:I3')
            
            total = len(self.data_pasien)
            laki = len([x for x in self.data_pasien if x.get('jenis_kelamin') == 'Laki-laki'])
            perempuan = len([x for x in self.data_pasien if x.get('jenis_kelamin') == 'Perempuan'])
            
            ws['A5'] = f"Total Pasien: {total}"
            ws['A5'].font = ExcelFont(bold=True)
            ws['B5'] = f"Laki-laki: {laki}"
            ws['C5'] = f"Perempuan: {perempuan}"
            
            headers = ["No", "ID", "No Antrian", "Nama", "Jenis Kelamin", "Keluhan", "Tgl Lahir", "Tanggal Periksa", "Alamat", "No Telepon"]
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=7, column=col)
                cell.value = header
                cell.font = ExcelFont(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="3498db", end_color="3498db", fill_type="solid")
                cell.alignment = Alignment(horizontal='center')
            
            for idx, pasien in enumerate(self.data_pasien, start=8):
                ws.cell(row=idx, column=1, value=idx-7)
                ws.cell(row=idx, column=2, value=pasien.get('id', '-'))
                ws.cell(row=idx, column=3, value=pasien.get('no_antrian', '-'))
                ws.cell(row=idx, column=4, value=pasien.get('nama', '-'))
                ws.cell(row=idx, column=5, value=pasien.get('jenis_kelamin', '-'))
                ws.cell(row=idx, column=6, value=pasien.get('keluhan', '-'))
                ws.cell(row=idx, column=7, value=pasien.get('tgl_lahir', '-'))
                ws.cell(row=idx, column=8, value=pasien.get('tanggal', '-'))
                ws.cell(row=idx, column=9, value=pasien.get('alamat', '-'))
                ws.cell(row=idx, column=10, value=pasien.get('No_Telepon', '-'))
            
            for col in range(1, 10):
                ws.column_dimensions[chr(64+col)].width = 15
            
            wb.save(file_name)
            
            QMessageBox.information(self, "Sukses", f"Laporan berhasil di-export ke:\n{file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export Excel:\n{str(e)}")
    
    def print_laporan(self):
        """Print laporan"""
        if not self.data_pasien:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk di-print!\n\nSilakan tampilkan laporan terlebih dahulu.")
            return
        
        QMessageBox.information(
            self,
            "Print Laporan",
            "Fitur print akan membuka dialog print.\n\nAnda bisa save as PDF atau print langsung ke printer."
        )