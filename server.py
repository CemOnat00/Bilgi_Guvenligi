import socket
import threading
import os
import steg  # Kendi yazdığın modül

SUNUCU_IP = '127.0.0.1'
PORT_NO = 5555
RESIM_KLASORU = 'gelen_resimler'

aktif_baglantilar = []
kullanici_bilgileri = {}

# 🔹 YENİ: kullanıcı -> socket eşlemesi
kullanici_socketleri = {}

liste_kilidi = threading.Lock()


def satir_satir_oku(soket):
    tampon_veri = b""
    while not tampon_veri.endswith(b"\n"):
        tek_byte = soket.recv(1)
        if not tek_byte:
            break
        tampon_veri += tek_byte
    return tampon_veri.decode('utf-8').strip()

def herkese_yay(mesaj, gonderen_kim):
    with liste_kilidi:
        for kisi in aktif_baglantilar[:]:
            if kisi != gonderen_kim:
                try:
                    kisi.send(mesaj.encode('utf-8'))
                except:
                    kisi.close()
                    aktif_baglantilar.remove(kisi)


def istemciyle_ilgilen(istemci_soketi, adres):
    print(f"Yeni biri geldi: {adres}")
    while True:
        try:
            gelen_veri = satir_satir_oku(istemci_soketi)
            if not gelen_veri:
                break
            # 🔹 REGISTER
            if gelen_veri.startswith("REGISTER"):
                _, k_adi, dosya_boyutu = gelen_veri.split("|")
                dosya_boyutu = int(dosya_boyutu)
                print(f"{k_adi} kayıt olmak istiyor...")
                istemci_soketi.sendall("READY\n".encode('utf-8'))
                toplanan_veri = b""
                while len(toplanan_veri) < dosya_boyutu:
                    paket = istemci_soketi.recv(4096)
                    if not paket:
                        break
                    toplanan_veri += paket
                dosya_yolu = os.path.join(RESIM_KLASORU, f"{k_adi}.png")
                with open(dosya_yolu, "wb") as dosya:
                    dosya.write(toplanan_veri)
                gizli_sifre = steg.decode(dosya_yolu)
                if gizli_sifre:
                    kullanici_bilgileri[k_adi] = gizli_sifre
                    # 🔹 YENİ: kullanıcıyı socket ile eşle
                    with liste_kilidi:
                        kullanici_socketleri[k_adi] = istemci_soketi
                    print(f"Kayıt OK -> {k_adi}")
                    istemci_soketi.sendall("REG_SUCCESS\n".encode('utf-8'))
                else:
                    istemci_soketi.sendall("REG_FAIL\n".encode('utf-8'))
            elif gelen_veri.startswith("LOGIN"):
                parts = gelen_veri.split("|")
                # Eğer şifre boş gelirse hata vermesin diye kontrol
                if len(parts) >= 3:
                    _, k_adi, sifre = parts

                    with liste_kilidi:
                        kullanici_socketleri[k_adi] = istemci_soketi

                    print(f"{k_adi} sisteme giriş yaptı.")
                    istemci_soketi.sendall("LOGIN_SUCCESS\n".encode('utf-8'))
                else:
                    print("Hatalı LOGIN formatı")


            # 🔹 YENİ: BİREBİR MESAJ
            elif gelen_veri.startswith("MSG"):
                # MSG|gonderen|alici|mesaj
                _, gonderen, alici, mesaj = gelen_veri.split("|", 3)

                with liste_kilidi:
                    if alici in kullanici_socketleri:
                        try:
                            kullanici_socketleri[alici].send(
                                f"[Özel] {gonderen}: {mesaj}\n".encode('utf-8')
                            )
                        except:
                            pass
                    else:
                        istemci_soketi.send(
                            "Kullanıcı çevrimdışı.\n".encode('utf-8')
                        )

            # 🔹 Broadcast (ESKİ HALİYLE DURUYOR)
            else:
                print(f"{adres}: {gelen_veri}")
                herkese_yay(f"{adres} dedi ki: {gelen_veri}", istemci_soketi)

        except Exception as hata:
            print(f"Hata: {hata}")
            break

    print(f"{adres} ayrıldı.")
    istemci_soketi.close()

    with liste_kilidi:
        if istemci_soketi in aktif_baglantilar:
            aktif_baglantilar.remove(istemci_soketi)

        # 🔹 YENİ: socket düşerse kullanıcıyı da sil
        for k, s in list(kullanici_socketleri.items()):
            if s == istemci_soketi:
                del kullanici_socketleri[k]


def cikis_kontrolcusu(ana_soket):
    while True:
        giris = input()
        if giris == 'q':
            print("Sunucu kapatılıyor...")
            ana_soket.close()
            os._exit(0)


if __name__ == "__main__":
    if not os.path.exists(RESIM_KLASORU):
        os.makedirs(RESIM_KLASORU)

    sunucu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sunucu.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sunucu.bind((SUNUCU_IP, PORT_NO))
    except:
        sunucu.bind(('127.0.0.1', PORT_NO))

    sunucu.listen(5)
    print(f"Sunucu çalışıyor... {SUNUCU_IP}:{PORT_NO}")

    threading.Thread(
        target=cikis_kontrolcusu,
        args=(sunucu,),
        daemon=True
    ).start()
    while True:
        conn, adres = sunucu.accept()
        aktif_baglantilar.append(conn)
        t = threading.Thread(
            target=istemciyle_ilgilen,
            args=(conn, adres)
        )
        t.start()
