import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QDialog,
    QFormLayout, QTextEdit, QComboBox, QListWidget, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon


# Veritabannı oluşturma
def init_db():
    conn = sqlite3.connect("appointments.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, phone TEXT, date TEXT, time TEXT, doctor TEXT, note TEXT)''')
    conn.commit()
    conn.close()

data = {
    '22.06.25': ['10.00', '10.30', '11.00', '11.30'],
    '23.06.25': ['10.00', '10.30', '11.00', '11.30'],
    '24.06.25': ['10.00', '10.30', '11.00', '11.30']
}

policlinics = {
    "Dahiliye": ["Dr. John Watson", "Dr. Shaun Murphy"],
    "Kardiyoloji": ["Dr. Stephen Strange", "Dr. Gregory House"],
    "Nöroloji": ["Dr. Hannibal Lecter", "Dr. Derek Shepherd", "Dr. Ali Asaf Denizoğlu"],
    "Göz Hastalıkları": ["Dr. Meredith Grey", "Dr. Leo Spaceman"]
}


class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.selected_doctor = None
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                border: none;
                gridline-color: lightgray;
                padding: 2px;
            }
            QTableWidget::item {
                padding: 2px;
            }
        """)
        self.verileri_ayarla()
        self.resizeColumnsToContents()
        self.setFixedHeight(200)
        self.cellClicked.connect(self.hucre_tiklandi)

    def randevu_dolu_mu(self, tarih, saat):
        conn = sqlite3.connect("appointments.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM appointments WHERE date=? AND time=? AND doctor=?", (tarih, saat, self.selected_doctor))
        result = c.fetchone()[0]
        conn.close()
        return result > 0

    def verileri_ayarla(self):
        self.setRowCount(max(len(v) for v in self.data.values()))
        self.setColumnCount(len(self.data))
        horHeaders = []
        for n, key in enumerate(sorted(self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                if self.selected_doctor and self.randevu_dolu_mu(key, item):
                    newitem.setFlags(Qt.ItemIsEnabled)
                    newitem.setBackground(QColor('#d3d3d3'))
                self.setItem(m, n, newitem)
                self.setRowHeight(m, 30)
        self.setHorizontalHeaderLabels(horHeaders)

    def hucre_tiklandi(self, satir, sutun):
        secilen_tarih = sorted(self.data.keys())[sutun]
        secilen_saat = self.item(satir, sutun).text()
        if self.selected_doctor and not self.randevu_dolu_mu(secilen_tarih, secilen_saat):
            self.randevu_olustur_penceresi(secilen_tarih, secilen_saat)

    def randevu_olustur_penceresi(self, tarih, saat):
        dialog = RandevuDialog(tarih, saat, self.selected_doctor, self)
        dialog.exec_()
        self.setWindowIcon(QIcon("aiyaprak.ico"))

    def doktor_ayarla(self, doktor_adi):
        self.selected_doctor = doktor_adi
        self.verileri_ayarla()

class RandevuDialog(QDialog):
    def __init__(self, tarih, saat, doktor_adi, tablo_gorunumu):
        super().__init__()
        self.setWindowTitle("Randevu Oluştur")
        self.setGeometry(200, 200, 300, 250)
        self.setWindowIcon(QIcon("aiyaprak.ico"))

        self.tarih = tarih
        self.saat = saat
        self.doktor_adi = doktor_adi
        self.tablo_gorunumu = tablo_gorunumu

        layout = QFormLayout()
        self.label = QLabel(f"Seçilen Tarih: {tarih} - Saat: {saat}")
        layout.addWidget(self.label)

        self.isim_girisi = QLineEdit()
        self.telefon_girisi = QLineEdit()
        self.not_girisi = QTextEdit()
        layout.addRow("Ad Soyad:", self.isim_girisi)
        layout.addRow("Telefon No:", self.telefon_girisi)
        layout.addRow("Doktora Not:", self.not_girisi)

        self.onay_butonu = QPushButton("Randevu Oluştur", self)
        self.onay_butonu.clicked.connect(self.randevu_olustur)
        layout.addWidget(self.onay_butonu)

        self.setLayout(layout)

    def randevu_olustur(self):
        isim = self.isim_girisi.text()
        telefon = self.telefon_girisi.text()
        not_metni = self.not_girisi.toPlainText()
        if isim and telefon:
            conn = sqlite3.connect("appointments.db")
            c = conn.cursor()
            c.execute("INSERT INTO appointments (name, phone, date, time, doctor, note) VALUES (?, ?, ?, ?, ?, ?)",
                      (isim, telefon, self.tarih, self.saat, self.doktor_adi, not_metni))
            conn.commit()
            conn.close()
            self.accept()
            self.tablo_gorunumu.verileri_ayarla()
            self.onay_penceresi_goster(isim, not_metni)
        else:
            self.label.setText("Lütfen tüm bilgileri doldurun.")
    
        self.setWindowIcon(QIcon("aiyaprak.ico"))

    def onay_penceresi_goster(self, isim, not_metni):
        onay_penceresi = OnayPenceresi(self.tarih, self.saat, self.doktor_adi, isim, not_metni)
        onay_penceresi.exec_()
        self.setWindowIcon(QIcon("aiyaprak.ico"))

class OnayPenceresi(QDialog):
    def __init__(self, tarih, saat, doktor_adi, isim, not_metni):
        super().__init__()
        self.setWindowTitle("Randevu Onayı")
        self.setGeometry(200, 200, 300, 200)
        self.setWindowIcon(QIcon("aiyaprak.ico"))

        layout = QVBoxLayout()
        onay_metni = f"Randevunuz başarıyla oluşturuldu!\nAd Soyad: {isim}\nDoktor: {doktor_adi}\nTarih: {tarih} Saat: {saat}\nNot: {not_metni}"
        layout.addWidget(QLabel(onay_metni))

        tamam_butonu = QPushButton("Tamam", self)
        tamam_butonu.clicked.connect(self.accept)
        layout.addWidget(tamam_butonu)
        self.setLayout(layout)
        self.setWindowIcon(QIcon("aiyaprak.ico"))

class RandevuListesiDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Randevu Listesi")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowIcon(QIcon("aiyaprak.ico"))

        layout = QVBoxLayout()
        self.liste_elemani = QListWidget()
        layout.addWidget(self.liste_elemani)

        self.randevular = []

        conn = sqlite3.connect("appointments.db")
        c = conn.cursor()
        c.execute("SELECT id, name, phone, date, time, doctor, note FROM appointments")
        satirlar = c.fetchall()
        conn.close()

        for satir in satirlar:
            self.randevular.append(satir)
            goruntuleme = f"{satir[1]} | {satir[2]} | {satir[5]} | {satir[3]} {satir[4]}"
            self.liste_elemani.addItem(goruntuleme)

        self.liste_elemani.itemClicked.connect(self.eleman_tiklandi)
        self.liste_elemani.itemDoubleClicked.connect(self.detaylari_ac)

        kapat_butonu = QPushButton("Kapat")
        kapat_butonu.clicked.connect(self.accept)
        layout.addWidget(kapat_butonu)

        sil_butonu = QPushButton("Seçili Randevuyu Sil")
        sil_butonu.clicked.connect(self.secileni_sil)
        layout.addWidget(sil_butonu)

        temizle_butonu = QPushButton("Tüm Randevuları Sil")
        temizle_butonu.clicked.connect(self.tumunu_sil)
        layout.addWidget(temizle_butonu)

        self.setLayout(layout)
        self.secilen_randevu = None

    def eleman_tiklandi(self, eleman):
        indeks = self.liste_elemani.currentRow()
        self.secilen_randevu = self.randevular[indeks]

    def detaylari_ac(self, eleman):
        if self.secilen_randevu:
            detay_dialog = RandevuDetayDialog(self.secilen_randevu)
            detay_dialog.exec_()

    def secileni_sil(self):
        if self.secilen_randevu:
            conn = sqlite3.connect("appointments.db")
            c = conn.cursor()
            c.execute("DELETE FROM appointments WHERE id=?", (self.secilen_randevu[0],))
            conn.commit()
            conn.close()

            self.randevular.remove(self.secilen_randevu)
            self.liste_elemani.takeItem(self.liste_elemani.currentRow())
            self.secilen_randevu = None
        else:
            self.liste_elemani.addItem("Lütfen önce bir randevu seçin.")

    def tumunu_sil(self):
        conn = sqlite3.connect("appointments.db")
        c = conn.cursor()
        c.execute("DELETE FROM appointments")
        conn.commit()
        conn.close()

        self.randevular.clear()
        self.liste_elemani.clear()
        self.liste_elemani.addItem("Tüm randevular başarıyla silindi.")

class RandevuDetayDialog(QDialog):
    def __init__(self, randevu):
        super().__init__()
        self.setWindowTitle("Randevu Detayları")
        self.setGeometry(300, 250, 350, 250)
        self.setWindowIcon(QIcon("aiyaprak.ico"))

        layout = QVBoxLayout()

        detay_metni = (
            f"<b>Ad Soyad:</b> {randevu[1]}<br>"
            f"<b>Telefon:</b> {randevu[2]}<br>"
            f"<b>Tarih:</b> {randevu[3]}<br>"
            f"<b>Saat:</b> {randevu[4]}<br>"
            f"<b>Doktor:</b> {randevu[5]}<br>"
            f"<b>Not:</b><br>{randevu[6]}"
        )

        etiket = QLabel(detay_metni)
        etiket.setWordWrap(True)
        layout.addWidget(etiket)

        pdf_butonu = QPushButton("PDF'e Kaydet")
        pdf_butonu.clicked.connect(lambda: self.pdf_olustur(randevu))
        layout.addWidget(pdf_butonu)

        kapat_butonu = QPushButton("Kapat")
        kapat_butonu.clicked.connect(self.accept)
        layout.addWidget(kapat_butonu)

        self.setLayout(layout)

    def pdf_olustur(self, randevu):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        dosya_adi = f"Randevu_{randevu[1]}_{randevu[3]}_{randevu[4]}.pdf"
        c = canvas.Canvas(dosya_adi, pagesize=A4)
        text = c.beginText(50, 800)
        text.setFont("Helvetica", 12)

        satirlar = [
            f"Randevu Bilgileri",
            f"Ad Soyad: {randevu[1]}",
            f"Telefon: {randevu[2]}",
            f"Tarih: {randevu[3]}",
            f"Saat: {randevu[4]}",
            f"Doktor: {randevu[5]}",
            f"Not: {randevu[6]}"
        ]

        for satir in satirlar:
            text.textLine(satir)

        c.drawText(text)
        c.showPage()
        c.save()
        QMessageBox.information(self, "PDF Oluşturuldu", f"{dosya_adi} başarıyla kaydedildi.")

class PoliklinikSecimPenceresi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poliklinik Seçimi")
        self.setGeometry(200, 100, 400, 250)
        self.setWindowIcon(QIcon("aiyaprak.ico"))

        layout = QVBoxLayout()
        self.etiket = QLabel("Lütfen bir poliklinik seçin:")
        layout.addWidget(self.etiket)

        self.combo = QComboBox()
        self.combo.addItems(policlinics.keys())
        layout.addWidget(self.combo)

        self.buton = QPushButton("Devam Et")
        self.buton.clicked.connect(self.doktor_secim_ac)
        layout.addWidget(self.buton)

        self.liste_butonu = QPushButton("Randevuları Listele")
        self.liste_butonu.clicked.connect(self.randevu_listesi_goster)
        layout.addWidget(self.liste_butonu)

        merkezi_widget = QWidget()
        merkezi_widget.setLayout(layout)
        self.setCentralWidget(merkezi_widget)

        self.setWindowIcon(QIcon("aiyaprak.ico"))

    def doktor_secim_ac(self):
        secilen_poliklinik = self.combo.currentText()
        doktorlar = policlinics[secilen_poliklinik]
        self.doktor_penceresi = Pencere2(doktorlar, self)
        self.doktor_penceresi.show()
        self.hide()

    def randevu_listesi_goster(self):
        dialog = RandevuListesiDialog()
        dialog.exec_()

class Pencere2(QMainWindow):
    def __init__(self, doktor_listesi, ana_penceresi):
        super().__init__()
        self.setWindowTitle("Randevu Seçim")
        self.setGeometry(200, 100, 600, 370)
        self.ana_penceresi = ana_penceresi

        self.tabwidget = QTabWidget()
        for doktor in doktor_listesi:
            self.tabwidget.addTab(QLabel("İstediğiniz tarih ve saati seçiniz."), doktor)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Lütfen istediğiniz doktoru seçiniz"))
        layout.addWidget(self.tabwidget)

        self.zaman_tablosu = TableView(data, 4, 3)
        layout.addWidget(self.zaman_tablosu)

        geri_butonu = QPushButton("← Geri")
        geri_butonu.clicked.connect(self.geri_don)
        layout.addWidget(geri_butonu)

        merkeziWidget = QWidget(self)
        merkeziWidget.setLayout(layout)
        self.setCentralWidget(merkeziWidget)

        self.tabwidget.currentChanged.connect(self.tab_degisti)
        self.tab_degisti(0)

        self.setWindowIcon(QIcon("aiyaprak.ico"))

    def tab_degisti(self, indeks):
        self.zaman_tablosu.doktor_ayarla(self.tabwidget.tabText(indeks))

    def geri_don(self):
        self.ana_penceresi.show()
        self.close()

class Pencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Randevu Giriş Ekranı")
        self.setGeometry(100, 100, 650, 450)

        self.etiket = QLabel("Hoş geldiniz! Lütfen giriş yapın.", self)
        self.etiket.setAlignment(Qt.AlignCenter)
        self.etiket.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.etiket.setGeometry(0, 75, 650, 40)

        self.kullanici_etiket = QLabel("İsim:", self)
        self.kullanici_etiket.move(200, 150)
        self.kullanici_girisi = QLineEdit(self)
        self.kullanici_girisi.move(300, 150)
        self.kullanici_girisi.setFixedWidth(150)

        self.sifre_etiket = QLabel("Şifre:", self)
        self.sifre_etiket.move(200, 200)
        self.sifre_girisi = QLineEdit(self)
        self.sifre_girisi.setEchoMode(QLineEdit.Password)
        self.sifre_girisi.move(300, 200)
        self.sifre_girisi.setFixedWidth(150)

        self.sifre_goster_checkbox = QCheckBox("Şifreyi Göster", self)
        self.sifre_goster_checkbox.move(300, 230)
        self.sifre_goster_checkbox.stateChanged.connect(self.sifre_gorunurlugu_degistir)

        self.giris_butonu = QPushButton("Giriş", self)
        self.giris_butonu.move(275, 260)
        self.giris_butonu.clicked.connect(self.giris_yap)

        self.setWindowIcon(QIcon("aiyaprak.ico"))

        self.show()

    def sifre_gorunurlugu_degistir(self, durum):
        if durum == Qt.Checked:
            self.sifre_girisi.setEchoMode(QLineEdit.Normal)
        else:
            self.sifre_girisi.setEchoMode(QLineEdit.Password)

    def giris_yap(self):
        if self.kullanici_girisi.text() == "ceren" and self.sifre_girisi.text() == "12345":
            self.pol_penceresi = PoliklinikSecimPenceresi()
            self.pol_penceresi.show()
            self.hide()
        else:
            self.etiket.setText("Tekrar deneyin! Yanlış giriş.")
            self.kullanici_girisi.clear()
            self.sifre_girisi.clear()

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    pencere = Pencere()
    sys.exit(app.exec_())