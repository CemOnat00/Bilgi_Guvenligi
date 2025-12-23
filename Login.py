import sys
import warnings
import datetime
# Kendi dosyalarim
import client
import dess

# Gereksiz uyarilari kapat
warnings.filterwarnings("ignore")

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.uic import loadUi


# -------------------------
# SOHBET EKRANI
# -------------------------
class ChatScreen(QWidget):
    def __init__(self):
        super().__init__()  # Modern kullanim
        loadUi("untitled.ui", self)

        self.setWindowTitle("Mesajlasma")

        # Butonlari bagla
        self.sendButton.clicked.connect(self.mesajGonder)
        self.messageInput.returnPressed.connect(self.mesajGonder)
        self.userList.itemClicked.connect(self.kisiSecildi)

        # Listeyi doldur (Test verileri)
        self.logEkle("Sisteme baglandiniz...")
        self.userList.addItem("Ahmet")
        self.userList.addItem("Mehmet")
        self.userList.addItem("Ayse")

    def kisiSecildi(self, item):
        secilen = item.text()
        # Basligi guncelle html ile
        self.chatTitle.setText(
            f"<html><head/><body><p><span style='font-size:14pt; font-weight:600;'>Sohbet: {secilen}</span></p></body></html>")
        print("Secilen kisi:", secilen)  # debug

    def mesajGonder(self):
        mesaj = self.messageInput.text()

        if mesaj != "":
            saat = datetime.datetime.now().strftime("%H:%M")

            # Html formatinda renkli yazi
            yazi = f"<span style='color: #4CAF50; font-weight: bold;'>Ben ({saat}):</span> <span style='color: white;'>{mesaj}</span>"

            self.chatArea.append(yazi)
            self.messageInput.clear()

            # Client gonderme islemi burada yapilacak
            print("Giden mesaj:", mesaj)
        else:
            print("Bos mesaj gonderilemez")

    def logEkle(self, text):
        self.chatArea.append(f"<span style='color: gray;'>{text}</span>")


# -------------------------
# GIRIS EKRANI
# -------------------------
class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("Login.ui", self)
        self.setWindowTitle("Giris")

        # UI baglantilari
        self.loginb.clicked.connect(self.girisYap)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.registera.clicked.connect(self.kayitEkraninaGit)

    def girisYap(self):
        kadi = self.username.text()
        sifre = self.password.text()

        # print(kadi, sifre) # kontrol amacli
        print("Giris yapiliyor:", kadi)

        # Simdilik sifre kontrolu yok direk geciyoruz
        if kadi and sifre:
            print("Giris basarili, sohbet aciliyor")

            chat = ChatScreen()
            widget.addWidget(chat)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            print("Kullanici adi sifre bos olamaz!")

    def kayitEkraninaGit(self):
        print("Kayit ekranina gidiliyor...")
        kayit = CreateAcc()
        widget.addWidget(kayit)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# -------------------------
# KAYIT EKRANI
# -------------------------
class CreateAcc(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("creation.ui", self)

        self.registera_2.clicked.connect(self.kayitOl)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmp.setEchoMode(QtWidgets.QLineEdit.Password)

        self.resimYolu = ""
        self.photobtn.clicked.connect(self.fotoSec)

    def fotoSec(self):
        print("Foto sec butonuna basildi")
        dosya, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Resim Sec", "", "Resimler (*.png *.jpg *.bmp)")
        if dosya:
            self.resimYolu = dosya
            print("Secilen dosya:", self.resimYolu)

    def kayitOl(self):
        kadi = self.username.text()
        sifre = self.password.text()
        sifre_tekrar = self.confirmp.text()

        if sifre != sifre_tekrar:
            print("Sifreler ayni degil!")
            return

        if self.resimYolu == "":
            print("Resim secmediniz!")
            return
        print("Kayit islemi basladi...", kadi)
        try:
            # Client dosyasindaki fonksiyonu cagiriyoruz
            client.register_user(kadi, sifre, self.resimYolu)
            print("Kayit istegi yollandi, girise donuluyor")
            widget.setCurrentIndex(0)  # Giris ekranina don
        except Exception as hata:
            print("Hata cikti:", hata)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ekran yonetimi
    widget = QtWidgets.QStackedWidget()
    giris_ekrani = Login()
    widget.addWidget(giris_ekrani)
    # Boyut ayarlari
    widget.setFixedWidth(1100)
    widget.setFixedHeight(650)
    widget.setWindowTitle("Guvenli Mesajlasma")
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Cikis yapildi")