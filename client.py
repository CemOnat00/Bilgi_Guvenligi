import socket
import os
import json
import steg
import time
import base64
HOST = '127.0.0.1'
PORT = 12345
class GameClient:
    def __init__(self):
        self.client_socket = None
        self.username = None
        self.connected = False
        self.des_cipher = None
    def baglan(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.connected = True
            return True
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False
        #kayıt olma islemi
    def register(self, username, password, image_path):
        password_padded = password.ljust(8)[:8]
        resimciktisi = f"encoded_{username}.png"
        basari = steg.encode(image_path, password_padded, resimciktisi)
        if not basari: return "Resim oluşturulamadı"
        if not self.connected:
            if not self.baglan(): return "Bağlantı yok"
        try:
            with open(resimciktisi, "rb") as f:
                img_data = f.read()
            img_str = base64.b64encode(img_data).decode('utf-8')
            paket = {"tip": "REGISTER", "isim": username, "resim_data": img_str}
            self.client_socket.send(json.dumps(paket).encode('utf-8'))
            cevap = json.loads(self.client_socket.recv(1024).decode('utf-8'))
            if cevap.get("durum") == "REG_SUCCESS":
                self.client_socket.close()
                self.connected = False
                return "KAYIT_OK"
            else:
                return cevap.get("msg", "Kayit Basarisiz")
        except Exception as e:
            self.client_socket.close()
            self.connected = False
            return f"Hata: {e}"
    def giris_yap(self, username, password):
        if not self.connected:
            if not self.baglan(): return False
        self.username = username
        #des için 8 e tamamladıknolrsa olsun paddledik
        password_padded = password.ljust(8)[:8]
        try:
            paket = {"tip": "GIRIS", "isim": username, "sifre": password_padded}
            self.client_socket.send(json.dumps(paket).encode('utf-8'))
            cevap_raw = self.client_socket.recv(1024).decode('utf-8')
            cevap = json.loads(cevap_raw)
            if cevap.get("durum") == "LOGIN_SUCCESS":
                return True
            else:
                print("Giriş Başarısız:", cevap.get("msg"))
                return False
        except Exception as e:
            print("Giriş Hatası:", e)
            return False
    def mesaj_yolla(self, alici, mesaj):
        if self.des_cipher:
            try:
                sifreli = self.des_cipher.encrypt(mesaj).decode('utf-8')
                paket = {
                    "tip": "MESAJ",
                    "alici": alici,
                    "mesaj": sifreli,
                    "gonderen": self.username
                }
                self.client_socket.send(json.dumps(paket).encode('utf-8'))
            except Exception as e:
                print(f"Mesaj gönderme hatası: {e}")
    def dinle(self, mesaj_geldi_callback, liste_geldi_callback):
        while self.connected:
            try:
                veri = self.client_socket.recv(1024000).decode('utf-8')
                if not veri: break
                try:
                    paket = json.loads(veri)
                except:
                    continue
                if paket["tip"] == "USER_LIST":
                    liste_geldi_callback(paket["users"])
                elif paket["tip"] == "YENI_MESAJ":
                    if self.des_cipher:
                        cozulmus = self.des_cipher.decrypt(paket["mesaj"])
                        mesaj_geldi_callback(paket["gonderen"], cozulmus)
            except:
                break
