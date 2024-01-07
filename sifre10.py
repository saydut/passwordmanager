import os
import sqlite3
from PyQt5.QtWidgets import (
    QMenu, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QTableWidget, QCheckBox, QInputDialog, QTableWidgetItem)
from PyQt5.QtCore import Qt
import qdarkstyle
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self):
        self.app = QApplication([])
        self.main_window = QMainWindow()
        self.new_window = None
        self.db_path = os.path.join(os.getcwd(), 'mainpassword.db')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.create_master_password_table()
        self.apply_theme()
        
    def create_theme_selector(self):
        theme_selector = QWidget()
        layout = QVBoxLayout(theme_selector)

        label = QLabel("Lütfen bir tema seçin:")
        layout.addWidget(label)

        theme_combo = QComboBox()
        theme_combo.addItems(["Varsayılan Tema", "Karanlık Tema"])
        layout.addWidget(theme_combo)

        apply_button = QPushButton("Tema")
        apply_button.clicked.connect(self.apply_theme)
        layout.addWidget(apply_button)
        
        frame = QWidget()
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)
        
        button_frame = QWidget()
        button_frame_layout = QHBoxLayout()
        button_frame.setLayout(button_frame_layout)
        
        theme_selector.setLayout(layout)
        theme_selector.show()

    def apply_theme(self):
        current_stylesheet = self.app.styleSheet()
        if "QDarkStyle" in current_stylesheet:
            self.app.setStyleSheet("")
        else:
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def create_master_password_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_password (password TEXT)''')

    def check_master_password(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (hesap TEXT, kullanici TEXT, sifre TEXT)''')
        self.cursor.execute('''SELECT * FROM master_password''')
        row = self.cursor.fetchone()
        if row is None:
            self.create_master_password()
        else:
            self.verify_master_password()

    def create_master_password(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_password (password TEXT)''')
        password, ok = QInputDialog.getText(None, "Ana Şifre", "Lütfen bir ana şifre belirleyin:")
        if ok:
            self.cursor.execute('''INSERT INTO master_password (password) VALUES (?)''', (password,))
            self.conn.commit()
            QMessageBox.information(None, "Başarılı", "Ana şifre oluşturuldu!")
            self.verify_master_password()
        else:
            QMessageBox.warning(None, "Uyarı", "Lütfen bir şifre girin.")
            self.conn.close()

    def verify_master_password(self):
        password, ok = QInputDialog.getText(None, "Ana Şifre", "Lütfen ana şifreyi girin:")
        if ok:
            self.cursor.execute('''SELECT * FROM master_password WHERE password = ?''', (password,))
            row = self.cursor.fetchone()
            if row:
                self.conn.close()
                self.open_main_application()
            else:
                QMessageBox.critical(None, "Hata", "Yanlış şifre!")
                self.conn.close()
        else:
            QMessageBox.warning(None, "Uyarı", "Lütfen bir şifre girin.")
            self.conn.close()

    def open_main_application(self):
        self.main_window.setWindowTitle("Şifre Yönetici")
        self.create_widgets()
        self.main_window.show()
        self.app.exec_()

    def create_widgets(self):
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        frame = QWidget()
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        label1 = QLabel("Hesap İsmi:")
        self.hesap_entry = QLineEdit()
        frame_layout.addWidget(label1)
        frame_layout.addWidget(self.hesap_entry)

        label2 = QLabel("Kullanıcı Adı/E-Posta:")
        self.kullanici_entry = QLineEdit()
        frame_layout.addWidget(label2)
        frame_layout.addWidget(self.kullanici_entry)

        label3 = QLabel("Şifre:")
        self.sifre_entry = QLineEdit()
        self.sifre_entry.setEchoMode(QLineEdit.Password)
        frame_layout.addWidget(label3)
        frame_layout.addWidget(self.sifre_entry)

        button_frame = QWidget()
        button_frame_layout = QHBoxLayout()
        button_frame.setLayout(button_frame_layout)

        self.kaydet_button = QPushButton("Kaydet")
        self.bilgi_al_button = QPushButton("Bilgi Al")
        self.kayitli_bilgiler_button = QPushButton("Kayıtlı Bilgiler")

        self.kaydet_button.clicked.connect(self.kaydet)
        self.bilgi_al_button.clicked.connect(self.bilgi_al)
        self.kayitli_bilgiler_button.clicked.connect(self.kayitli_bilgiler)

        button_frame_layout.addWidget(self.kaydet_button)
        button_frame_layout.addWidget(self.bilgi_al_button)
        button_frame_layout.addWidget(self.kayitli_bilgiler_button)
        
        theme_button = QPushButton("Tema")
        theme_button.clicked.connect(self.apply_theme)  # Tema değiştirme işlevi burada
        layout.addWidget(theme_button)

        layout.addWidget(frame)
        layout.addWidget(button_frame)
        
    def kaydet(self):
        hesap = self.hesap_entry.text()
        kullanici = self.kullanici_entry.text()
        sifre = self.sifre_entry.text()

        if hesap and kullanici and sifre:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (hesap TEXT, kullanici TEXT, sifre TEXT)''')
            cursor.execute('''INSERT INTO passwords VALUES (?, ?, ?)''', (hesap, kullanici, sifre))
            conn.commit()
            conn.close()
            QMessageBox.information(None, "Başarılı", "Bilgiler kaydedildi.")
        else:
            QMessageBox.warning(None, "Hata", "Lütfen tüm alanları doldurun.")

    def bilgi_al(self):
        hesap = self.hesap_entry.text()

        if hesap:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM passwords WHERE hesap = ?''', (hesap,))
            rows = cursor.fetchall()

            if rows:
                info = ""
                for row in rows:
                    info += f"Hesap: {row[0]}, Kullanıcı: {row[1]}, Şifre: {row[2]}\n"
                QMessageBox.information(None, "Bilgiler", info)
            else:
                QMessageBox.warning(None, "Uyarı", "Hesap bulunamadı.")
            conn.close()
        else:
            QMessageBox.warning(None, "Hata", "Lütfen hesap ismi girin.")

    def kayitli_bilgiler(self):
        if self.new_window and self.new_window.isVisible():
            self.new_window.close()
        
        self.new_window = QWidget()
        self.new_window.setWindowTitle("Kayıtlı Bilgiler")
        self.new_window.setGeometry(100, 100, 440, 250)  # Boyutları ayarladım

        layout = QVBoxLayout()
        self.new_window.setLayout(layout)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM passwords''')
        rows = cursor.fetchall()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Hesap", "Kullanıcı Adı/E-Posta", "Şifre", "Seç"])

        self.checkboxes = []

        for i, row in enumerate(rows):
            table.insertRow(i)

            for j, item in enumerate(row):
                if j == 0:
                    if len(item) > 10:
                        item = item[:10] + '...'
                elif j == 1:
                    if len(item) > 25:
                        item += '...' * (25 - len(item))
                elif j == 2:
                    if len(item) > 10:
                        item = item[:10] + '...'
                table.setItem(i, j, QTableWidgetItem(str(item)))
                
            

            checkbox = QCheckBox()
            checkbox.setChecked(False)  # başlangıçta unchecked.
            self.checkboxes.append(checkbox)

            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(checkbox)
            cell_layout.setAlignment(Qt.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            table.setCellWidget(i, 3, cell_widget)  # tabloyu checkboxa ekleme
            table.setColumnWidth(3, 50)  # sütun kalınlığı
            table.setColumnWidth(0, 70)
            table.setColumnWidth(1, 170)
            table.setColumnWidth(2, 100)
            
        def show_context_menu(pos):
            menu = QMenu()
            copy_action = menu.addAction("Kopyala")
            action = menu.exec_(table.viewport().mapToGlobal(pos))
            
            if action == copy_action:
                selected_item = table.itemAt(pos)
                if selected_item:
                    clipboard = QApplication.clipboard()
                    clipboard.setText(selected_item.text())


        def delete_selected():
            selected_indices = [i for i, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()]
            if selected_indices:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                for index in selected_indices:
                    cursor.execute('''DELETE FROM passwords WHERE rowid=?''', (index + 1,))
                conn.commit()
                conn.close()
                QMessageBox.information(self.new_window, "Başarılı", "Seçilen kayıtlar silindi.")
                self.kayitli_bilgiler()  # Yeniden aç

        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(show_context_menu)
        
        delete_button = QPushButton("Seçilenleri Sil")
        delete_button.clicked.connect(delete_selected)

        layout.addWidget(table)
        layout.addWidget(delete_button)

        self.new_window.setLayout(layout)
        self.new_window.show()

    def run(self):
        self.check_master_password()
        self.main_window.close()
        self.app.quit()

if __name__ == "__main__":
    password_manager = PasswordManager()
    password_manager.check_master_password()
