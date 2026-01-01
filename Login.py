import sys
import warnings
import datetime
import os
import client
import dess
import json
import threading
from PyQt5 import QtCore
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QListWidgetItem
from PyQt5.QtGui import QColor, QBrush
from PyQt5.uic import loadUi


warnings.filterwarnings("ignore")

oyun_client = client.GameClient()


# --- GEÇMİŞ YÖNETİMİ ---
def save_message_to_history(my_username, other_user, sender_name, message_content):
    """
    my_username: Kimin geçmiş dosyasına yazılacak (Ben)
    other_user: Sohbet ettiğim kişi (Ahmet)
    sender_name: Mesajı kim attı? (Ben mi Ahmet mi?)
    message_content: Mesaj metni
    """
    filename = f"history_{my_username}.json"
    data = {}

    # Dosya varsa yükle
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            pass

    # Sohbet partneri için liste yoksa oluştur
    if other_user not in data:
        data[other_user] = []

    # Mesajı ekle (Zaman damgasıyla)
    timestamp = datetime.datetime.now().strftime("%H:%M")
    entry = {"sender": sender_name, "msg": message_content, "time": timestamp}
    data[other_user].append(entry)

    # Kaydet
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_history(my_username, other_user):
    filename = f"history_{my_username}.json"
    if not os.path.exists(filename): return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(other_user, [])
    except:
        return []


# -------------------------
# SOHBET EKRANI
# -------------------------
class DinlemeThread(QtCore.QThread):
    yeni_mesaj = QtCore.pyqtSignal(str, str)
    liste_guncelle = QtCore.pyqtSignal(list)

    def run(self):
        oyun_client.dinle(self.mesaj_sinyali, self.liste_sinyali)

    def mesaj_sinyali(self, gonderen, mesaj):
        self.yeni_mesaj.emit(gonderen, mesaj)

    def liste_sinyali(self, users):
        self.liste_guncelle.emit(users)


class ChatScreen(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)
        self.setWindowTitle(f"Mesajlasma - {oyun_client.username}")
        self.secilen_kisi = None

        self.sendButton.clicked.connect(self.mesajGonder)
        self.messageInput.returnPressed.connect(self.mesajGonder)
        self.userList.itemClicked.connect(self.kisiSecildi)

        from dess import DESCipher
        if not oyun_client.des_cipher:
            oyun_client.des_cipher = DESCipher("12345678")

        self.thread = DinlemeThread()
        self.thread.yeni_mesaj.connect(self.mesajGeldi)
        self.thread.liste_guncelle.connect(self.listeyiYenile)
        self.thread.start()

    def kisiSecildi(self, item):
        # item.text() şöyle gelebilir: "Ahmet (Online)"
        # Biz sadece ismi almalıyız.
        raw_text = item.text()
        secilen = raw_text.split(" ")[0]  # İlk kelimeyi al (isim)

        self.secilen_kisi = secilen
        self.chatTitle.setText(
            f"<html><head/><body><p><span style='font-size:14pt; font-weight:600;'>Sohbet: {secilen}</span></p></body></html>")

        # --- GEÇMİŞİ YÜKLE ---
        self.chatArea.clear()
        gecmis = load_history(oyun_client.username, secilen)
        for not_item in gecmis:
            kim = not_item["sender"]
            msg = not_item["msg"]
            zaman = not_item["time"]

            if kim == oyun_client.username:
                self.chatArea.append(
                    f"<span style='color: #4CAF50; font-weight: bold;'>Ben ({zaman}):</span> <span style='color: white;'>{msg}</span>")
            else:
                self.chatArea.append(f"<b style='color:orange'>{kim} ({zaman}):</b> {msg}")

    def mesajGonder(self):
        mesaj = self.messageInput.text()
        if mesaj != "":
            if not self.secilen_kisi:
                self.logEkle("Lutfen listeden bir kullanici secin!")
                return

            saat = datetime.datetime.now().strftime("%H:%M")
            yazi = f"<span style='color: #4CAF50; font-weight: bold;'>Ben ({saat}):</span> <span style='color: white;'>{mesaj}</span>"
            self.chatArea.append(yazi)
            self.messageInput.clear()

            # Server'a yolla
            oyun_client.mesaj_yolla(self.secilen_kisi, mesaj)

            # --- GEÇMİŞE KAYDET ---
            save_message_to_history(oyun_client.username, self.secilen_kisi, oyun_client.username, mesaj)
        else:
            print("Bos mesaj gonderilemez")

    def logEkle(self, text):
        self.chatArea.append(f"<span style='color: gray;'>{text}</span>")

    def mesajGeldi(self, gonderen, mesaj):
        # Eğer şu an o kişiyle konuşuyorsak ekrana bas
        if self.secilen_kisi == gonderen:
            saat = datetime.datetime.now().strftime("%H:%M")
            self.chatArea.append(f"<b style='color:orange'>{gonderen} ({saat}):</b> {mesaj}")

        # Her halükarda geçmişe kaydet
        save_message_to_history(oyun_client.username, gonderen, gonderen, mesaj)

    def listeyiYenile(self, users_data):
        # users_data artık şöyle geliyor: [{"username": "ali", "status": "Online"}, ...]
        self.userList.clear()
        for user_obj in users_data:
            u_name = user_obj["username"]
            status = user_obj["status"]

            if u_name != oyun_client.username:
                display_text = f"{u_name} ({status})"
                item = QListWidgetItem(display_text)

                # Renklendirme
                if status == "Online":
                    item.setForeground(QColor("lightgreen"))  # Yeşil
                else:
                    item.setForeground(QColor("gray"))  # Gri/Kırmızımsı

                self.userList.addItem(item)


# -------------------------
# GIRIS EKRANI
# -------------------------
class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("Login.ui", self)
        self.setWindowTitle("Giris")
        self.loginb.clicked.connect(self.girisYap)
        self.registera.clicked.connect(self.kayitEkraninaGit)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)

    def girisYap(self):
        kadi = self.username.text()
        sifre = self.password.text()
        anahtar_hazirligi = sifre.ljust(8)[:8]

        if kadi and sifre:
            basarili = oyun_client.giris_yap(kadi, sifre)
            if basarili:
                from dess import DESCipher
                oyun_client.des_cipher = DESCipher(anahtar_hazirligi)

                chat = ChatScreen()
                widget.addWidget(chat)
                # Düzeltilmiş geçiş
                widget.setCurrentWidget(chat)
            else:
                print("Sunucuya bağlanılamadı!")
        else:
            print("Alanlar boş olamaz")

    def kayitEkraninaGit(self):
        kayit = CreateAcc()
        widget.addWidget(kayit)
        widget.setCurrentWidget(kayit)  # Düzeltilmiş geçiş


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
        dosya, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Resim Sec", "", "Resimler (*.png);;Tum Dosyalar (*.*)")
        if dosya:
            self.resimYolu = dosya
            self.photobtn.setText(os.path.basename(dosya))

    def kayitOl(self):
        kadi = self.username.text()
        sifre = self.password.text()
        sifre_tekrar = self.confirmp.text()

        if sifre != sifre_tekrar: return
        if self.resimYolu == "": return

        try:
            sonuc = oyun_client.register(kadi, sifre, self.resimYolu)
            if sonuc == "KAYIT_OK":
                widget.setCurrentIndex(0)
            else:
                print("Kayıt hatası:", sonuc)
        except Exception as hata:
            print("Hata:", hata)

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    giris_ekrani = Login()
    widget.addWidget(giris_ekrani)
    widget.setFixedWidth(1100)
    widget.setFixedHeight(650)
    widget.setWindowTitle("Guvenli Mesajlasma")
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Cikis yapildi")

