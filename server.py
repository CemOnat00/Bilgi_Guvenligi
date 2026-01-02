import socket
import threading
import json
import os
import steg
from dess import DESCipher
from PIL import Image
import base64
import time
HOST = '127.0.0.1'
PORT = 12345
online_users = {}
DB_FILE = "users_db.json"
OFFLINE_FILE = "offline_messages.json"
def print_header(title):
    print("\n" + "=" * 50)
    print(f" {title}".center(50))
    print("=" * 50)
def print_step(step, msg):
    print(f"[*] {step}: {msg}")
def print_crypto(action, data):
    print(f"    >>> {action}: {data}")
def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}
def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f)
def load_offline_msgs():
    if not os.path.exists(OFFLINE_FILE): return {}
    try:
        with open(OFFLINE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}
def save_offline_msgs(msgs):
    with open(OFFLINE_FILE, 'w') as f: json.dump(msgs, f)
def broadcast_user_list():
    db = load_db()
    user_list_data = []
    for u_name in db.keys():
        durum = "Online" if u_name in online_users else "Offline"
        user_list_data.append({"username": u_name, "status": durum})
    paket = json.dumps({"tip": "USER_LIST", "users": user_list_data})
    for user in online_users.values():
        try:
            user["socket"].send(paket.encode('utf-8'))
        except:
            pass
def handle_client(client_socket, client_address):
    user_name = None
    buffer = ""
    try:
        while True:
            try:
                # Paqrça parça almazsak ubuntu kaldırmadı
                data = client_socket.recv(4096).decode('utf-8')
                if not data: break
                buffer += data
                try:
                    request = json.loads(buffer)
                    buffer = ""
                except json.JSONDecodeError:

                    continue

                tip = request.get("tip")
                # Kayıt islemi
                if tip == "REGISTER":
                    isim = request["isim"]
                    resim_base64 = request["resim_data"]
                    print_header(f"YENİ KAYIT İSTEĞİ: {isim}")
                    print_step("VERİ ALINDI", "İstemciden resim verisi alındı.")

                    db = load_db()
                    if isim in db:
                        print_step("HATA", "Kullanıcı zaten var.")
                        client_socket.send(
                            json.dumps({"durum": "REG_FAIL", "msg": "Kullanici zaten var"}).encode('utf-8'))
                        continue

                    if not os.path.exists("gelen_resimler"): os.makedirs("gelen_resimler")
                    # WİNdowsta çalıştı dümdüzde linuxda düzeltme
                    save_path = os.path.join("gelen_resimler", f"{isim}.png")
                    try:
                        with open(save_path, "wb") as f:
                            f.write(base64.b64decode(resim_base64))
                        print_step("DOSYA", f"Resim kaydedildi: {save_path}")
                        print_step("STEGANOGRAFİ", "Resim pikselleri taranıyor...")
                        # Steganografi işlemi
                        extracted_key = steg.decode(save_path)
                        if extracted_key:
                            final_key = extracted_key.ljust(8)[:8]
                            print_crypto("GİZLİ VERİ BULUNDU", extracted_key)
                            db[isim] = final_key
                            save_db(db)
                            print_step("BAŞARILI", f"{isim} veritabanına eklendi.")
                            client_socket.send(json.dumps({"durum": "REG_SUCCESS"}).encode('utf-8'))
                            broadcast_user_list()
                        else:
                            print_step("Hata", "Gizli veri yok/okunamadı.")
                            client_socket.send(
                                json.dumps({"durum": "REG_FAIL", "msg": "Sifre okunamadi"}).encode('utf-8'))
                    except Exception as e:
                        print(f"Kayıt işlem hatası: {e}")
                        client_socket.send(json.dumps({"durum": "REG_FAIL", "msg": str(e)}).encode('utf-8'))

                # Giris İşlemi
                elif tip == "GIRIS":
                    isim = request["isim"]
                    sifre = request["sifre"].ljust(8)[:8]
                    db = load_db()
                    if isim in db and db[isim] == sifre:
                        user_name = isim
                        online_users[isim] = {"socket": client_socket, "key": sifre}
                        print(f"\n[GİRİŞ] {isim} sisteme bağlandı. (Online)")
                        client_socket.send(json.dumps({"durum": "LOGIN_SUCCESS"}).encode('utf-8'))
                        broadcast_user_list()
                        print(f"[*] {isim} için offline mesajlar hazırlanıyor...")
                        time.sleep(1)
                        # Offline mesajlar
                        off_msgs = load_offline_msgs()
                        if isim in off_msgs:
                            messages = off_msgs[isim]
                            for msg_pkt in messages:
                                try:
                                    client_socket.send(json.dumps(msg_pkt).encode('utf-8'))
                                    time.sleep(0.1)
                                except:
                                    pass
                            del off_msgs[isim]
                            save_offline_msgs(off_msgs)
                    else:
                        print(f"\n[BAŞARISIZ GİRİŞ] {isim}")
                        client_socket.send(
                            json.dumps({"durum": "LOGIN_FAIL", "msg": "Hatali kullanici/sifre"}).encode('utf-8'))
                # Mesajlaşma
                elif tip == "MESAJ":
                    sender = request.get("gonderen", user_name)
                    target = request["alici"]
                    encrypted_content = request["mesaj"]

                    print_header(f"MESAJ: {sender} -> {target}")
                    print("\n" + "█" * 60)
                    print(f"📨  MESAJ TRAFİĞİ: {sender}  --->  {target}".center(60))
                    print("-" * 60)

                    db = load_db()
                    if sender in db and target in db:
                        try:

                            # 1. Gönderenin şifresiyle çöz
                            sender_key = db[sender]
                            cipher_sender = DESCipher(sender_key)
                            plain_text = cipher_sender.decrypt(encrypted_content)
                            print(f" *** [1. ADIM] Gelen Şifreli Paket (Client -> Server):")
                            print(f"     {encrypted_content[:40]}...")
                            print(f"\n ** [2. ADIM] SUNUCUDA ÇÖZÜLEN VERİ (AÇIK METİN):")
                            print(f"      MESAJ İÇERİĞİ:  {plain_text}")

                            # 2. Alıcının şifresiyle şifrele
                            target_key = db[target]
                            cipher_target = DESCipher(target_key)
                            re_encrypted_msg = cipher_target.encrypt(plain_text)
                            print(f"\n  [3. ADIM] Alıcı İçin Tekrar Şifrelendi (Server -> Target):")
                            print(f"      {re_encrypted_msg.decode('utf-8')[:40]}...")
                            paket_out = {
                                "tip": "YENI_MESAJ",
                                "gonderen": sender,
                                "mesaj": re_encrypted_msg.decode('utf-8')
                            }
                            if target in online_users:
                                online_users[target]["socket"].send(json.dumps(paket_out).encode('utf-8'))
                            else:
                                off_msgs = load_offline_msgs()
                                if target not in off_msgs: off_msgs[target] = []
                                off_msgs[target].append(paket_out)
                                save_offline_msgs(off_msgs)
                        except Exception as e:
                            print(f"Mesaj iletim hatası: {e}")

            except Exception as e:

                print(f"Bağlantı hatası: {e}")
                break
    except Exception as e:
        print(f"Handle client kritik hata: {e}")
    finally:
        if user_name and user_name in online_users:
            del online_users[user_name]
            print(f"[ÇIKIŞ] {user_name} ayrıldı.")
            broadcast_user_list()
        client_socket.close()
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("\n" + "*" * 50)
    print(f" GÜVENLİ MESAJLAŞMA SUNUCUSU BAŞLATILDI: {HOST}:{PORT}")
    print("*" * 50 + "\n")
    try:
        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr)).start()
    except:
        server.close()
if __name__ == "__main__":
    start_server()
