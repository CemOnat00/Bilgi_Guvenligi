import socket
import json
import time

HOST = '127.0.0.1'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print("Sunucuya bağlanıldı.")

    # 1. ADIM: KENDİMİZİ TANITALIM (KİMLİK KARTI GÖNDERME)
    # Burada ismi değiştirebilirsin
    my_name = input("Kullanıcı Adını Gir: ") 
    
    login_paket = {
        "tip": "GIRIS",
        "isim": my_name
    }
    
    # JSON verisini stringe çevirip yolluyoruz (dumps)
    client.send(json.dumps(login_paket).encode('utf-8'))

    # 2. ADIM: SUNUCUDAN CEVAP BEKLE
    response = client.recv(1024).decode('utf-8')
    response_json = json.loads(response)
    print(f"SUNUCUDAN MESAJ: {response_json['msg']}")

    # Bağlantıyı açık tutmak için bekleme
    while True:
        msg = input("Mesaj yaz (Çıkmak için 'q'): ")
        if msg == 'q':
            break
        client.send(msg.encode('utf-8'))

except Exception as e:
    print(f"Hata: {e}")
finally:
    client.close()