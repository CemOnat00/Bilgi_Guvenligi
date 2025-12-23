import socket
import threading
import json  # YENİ: Veri paketleme kütüphanesi
from PIL import Image

HOST = '127.0.0.1'
PORT = 12345

# KULLANICI REHBERİ (DATABASE)
# Yapı şöyle olacak:
# users = {
#    "Cem": { "socket": <baglanti_objesi>, "status": "online" },
#    "Asude": { "socket": <baglanti_objesi>, "status": "online" }
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
        
        # Eğer okunan verinin son 5 karakteri '#####' ise mesaj bitmiş demektir.
        # (B Kişisi mesajın sonuna işaret olarak ##### koymalı)
        if data[-5:] == "#####":
            return data[:-5] # İşaret kısmını at ve şifreyi dön
        
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
    print(f"[BAĞLANTI] {client_address} bağlandı. Kimlik bekleniyor...")
    
    user_name = None
    
    try:
        # 1. ADIM: İLK GELEN VERİYİ OKU (GİRİŞ İSTEĞİ OLMALI)
        buffer = client_socket.recv(1024).decode('utf-8')
        request = json.loads(buffer) # Gelen yazıyı Sözlüğe çevir
        
        if request["tip"] == "GIRIS":
            user_name = request["isim"]
            
            # Kullanıcıyı hafızaya kaydet
            users[user_name] = {
                "socket": client_socket,
                "status": "online"
            }
            print(f"[GİRİŞ BAŞARILI] {user_name} listeye eklendi.")
            print(f"Aktif Kullanıcılar: {list(users.keys())}")
            
            # Kişiye özel hoşgeldin mesajı
            welcome_msg = json.dumps({"sender": "Sistem", "msg": f"Hosgeldin {user_name}!"})
            client_socket.send(welcome_msg.encode('utf-8'))
            
        else:
            print("[HATA] İlk paket GİRİŞ isteği değildi. Bağlantı reddediliyor.")
            client_socket.close()
            return

        # 2. ADIM: ARTIK SOHBET DÖNGÜSÜNE GİREBİLİRİZ
        connected = True
        while connected:
            msg_data = client_socket.recv(1024)
            if not msg_data:
                break
            
            # İleride şifreli mesajlar burada işlenecek
            # Şimdilik sadece sunucuda ekrana basıyoruz
            print(f"[{user_name}]: {msg_data.decode('utf-8')}")

    except Exception as e:
        print(f"[HATA] {e}")
    
    # ÇIKIŞ İŞLEMLERİ
    if user_name and user_name in users:
        del users[user_name] # Listeden sil
        print(f"[ÇIKIŞ] {user_name} listeden silindi.")
        print(f"Kalan Kullanıcılar: {list(users.keys())}")
    
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