import socket
import os
import steg

HOST = '127.0.0.1'
PORT = 5555
def register_user(username, password, image_path):
    resimciktisi = f"encoded_{username}.png"
    basari = steg.encode(image_path, password, resimciktisi)
    if not basari:
        print("Resim oluşturma hatası")
        return
    filesize = os.path.getsize(resimciktisi)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        header = f"REGISTER|{username}|{filesize}"
        client.send(header.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        if response == "READY":
            print("Sunucu hazır, gönderiliyor...")
            with open(resimciktisi, "rb") as f:
                while True:
                    bytes_read = f.read(4096)
                    if not bytes_read:
                        break
                    client.sendall(bytes_read)
            final_response = client.recv(1024).decode('utf-8')
            if final_response == "REG_SUCCESS":
                print("Kayıt Başarılı")
            else:
                print("Kayıt Başarısız")
        client.close()
    except Exception as e:
        print(f"Hata: {e}")
if __name__ == "__main__":
    u_name = input("Kullanıcı Adı: ")
    passw = input("Şifre: ")
    img_p = "test.jpg"
    if os.path.exists(img_p):
        register_user(u_name, passw, img_p)
    else:
        print("test.jpg bulunamadı")