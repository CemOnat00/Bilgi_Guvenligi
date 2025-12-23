from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
#Sürekli şifrrelem yeinden mi olucak onu konusmamız gerekiyor sistem çok yavaş.
#AES daha iyi ancak DES
#Çok yavaş olursa Keyi 1 kez çıakrtıp o şekilde yapıcam

import base64
class DESCipher:
    def __init__(self, key):
        if len(key) != 8:
            raise ValueError("DES anahtarı tam olarak 8 karakter (byte) olmalıdır.")
        self.key = key.encode('utf-8')
        self.cipher = DES.new(self.key, DES.MODE_ECB)
    def encrypt(self, text):
       cipher=DES.new(self.key, DES.MODE_ECB)
       padding=pad(text.encode('utf-8'),DES.block_size)
       ciphertxt=cipher.encrypt(padding)
       return base64.b64encode(ciphertxt)
    def decrypt(self, ciphertxt):
        cipher_text_bytes=base64.b64decode(ciphertxt)
        cipher=DES.new(self.key, DES.MODE_ECB)
        decrypted_padded=cipher.decrypt(cipher_text_bytes)
        return unpad(decrypted_padded,DES.block_size).decode('utf-8')


