import socket
import threading
import json
import os
import steg  # Steganografi işlemleri için
from dess import DESCipher  # DES şifreleme sınıfı için
from PIL import Image

HOST = '127.0.0.1'
PORT = 12345

# KULLANICI REHBERİ (DATABASE)
# Yapı şöyle olacak:
# users = {
#    "Cem": { "socket": <baglanti_objesi>, "status": "online" },
# }
users = {} 

def extract_msg(image_path):
    """
    Sunucuya gelen resim dosyasının yolunu (path) alır,
    içine gizlenmiş metni (parolayı) okur ve geri döndürür.
    """
    img = Image.open(image_path)
    
    # Resimdeki pikselleri tek tek gezen bir iteratör oluştur
    img_data = iter(img.getdata())

    data = ""
    
    while True:
        # Pikselleri 3'er 3'er oku (R, G, B değerleri)
        pixels = [value for value in next(img_data)[:3] +
                                next(img_data)[:3] +
                                next(img_data)[:3]]

        # Piksellerin son bitlerini birleştirip harfe çevir
        binstr = ''
        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))

        # Eğer okunan verinin son 3 karakteri '$$$' ise mesaj bitmiş demektir.
        # (B Kişisi mesajın sonuna işaret olarak $$$ koymalı)
        if data[-3:] == "$$$":
            return data[:-3] # İşaret kısmını at ve şifreyi dön
        
def broadcast(message, sender_name="Sistem"):
    """Herkese mesaj yayar"""
    for user_name, user_info in users.items():
        try:
            # Mesajı gönderirken de JSON kullanıyoruz ki client ne olduğunu anlasın
            paket = json.dumps({"sender": sender_name, "msg": message})
            user_info["socket"].send(paket.encode('utf-8'))
        except:
            pass

def handle_client(client_socket, client_address):
    print(f"[BAĞLANTI] {client_address} bağlandı. İstek bekleniyor...")
    user_name = None
    
    try:
        while True:
            # İstemciden JSON formatında gelen veriyi oku
            msg_raw = client_socket.recv(4096).decode('utf-8')
            if not msg_raw:
                break
            
            request = json.loads(msg_raw)
            tip = request.get("tip")

            # --- GÖREV 3: KAYIT VE STEGANOGRAFİ ENTEGRASYONU ---
            if tip == "REGISTER":
                user_name = request["isim"]
                file_size = request["boyut"]
                
                # Dosya alımı için onay gönder
                client_socket.send(json.dumps({"durum": "READY"}).encode('utf-8'))
                
                # Resim verisini al
                received_data = b""
                while len(received_data) < file_size:
                    chunk = client_socket.recv(4096)
                    if not chunk: break
                    received_data += chunk
                
                # Resmi kaydet ve anahtarı çıkar
                if not os.path.exists("gelen_resimler"):
                    os.makedirs("gelen_resimler")
                
                save_path = f"gelen_resimler/{user_name}.png"
                with open(save_path, "wb") as f:
                    f.write(received_data)
                
                # Steganografi ile şifreyi (anahtarı) çıkartıyoruz
                extracted_key = steg.decode(save_path)
                
                if extracted_key:
                    users[user_name] = {
                        "socket": client_socket,""
                        "key": extracted_key,
                        "status": "online",
                        "mailbox": [] # Çevrimdışı mesaj deposu
                    }
                    print(f"[KAYIT BAŞARILI] {user_name} anahtarı: {extracted_key}")
                    client_socket.send(json.dumps({"durum": "REG_SUCCESS"}).encode('utf-8'))
                else:
                    client_socket.send(json.dumps({"durum": "REG_FAIL"}).encode('utf-8'))

            # --- GÖREV 4: ŞİFRELEMELİ MESAJ YÖNLENDİRME (ROUTING) ---
            elif tip == "MESAJ":
                sender = request["gonderen"]
                target = request["alici"]
                encrypted_content = request["mesaj"]
                
                if target in users:
                    # 1. Gönderenin anahtarıyla deşifre et (Sunucu mesajı okur)
                    cipher_sender = DESCipher(users[sender]["key"])
                    plain_text = cipher_sender.decrypt(encrypted_content)
                    
                    # 2. Alıcının anahtarıyla tekrar şifrele
                    cipher_target = DESCipher(users[target]["key"])
                    re_encrypted_msg = cipher_target.encrypt(plain_text)
                    
                    paket = json.dumps({
                        "tip": "YENI_MESAJ",
                        "gonderen": sender,
                        "mesaj": re_encrypted_msg.decode('utf-8')
                    })
                    
                    # Alıcı online ise hemen gönder, değilse kutusuna at
                    if users[target].get("status") == "online":
                        users[target]["socket"].send(paket.encode('utf-8'))
                    else:
                        users[target]["mailbox"].append(paket)
                else:
                    client_socket.send(json.dumps({"durum": "HATA", "msg": "Alici bulunamadi"}).encode('utf-8'))

    except Exception as e:
        print(f"[HATA] {client_address} - {e}")
    
    # Bağlantı koptuğunda temizlik yap
    if user_name and user_name in users:
        users[user_name]["status"] = "offline"
        print(f"[ÇIKIŞ] {user_name} çevrimdışı.")
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[DİNLİYOR] Sunucu {HOST}:{PORT} açık...")

    try:
        while True:
            client_socket, client_address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
    except KeyboardInterrupt:
        print("\n[KAPANIYOR] Sunucu kapatılıyor...")
        server.close()

if __name__ == "__main__":
    start_server()