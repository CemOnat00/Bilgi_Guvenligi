import cv2
from matplotlib import pyplot as plt
from PIL import Image
import os
import numpy as np
#ilk işlem metin ve binary dönüşümleri
def binary_to_metin(binary_str):
    def decode_binary_string(s):
        return ''.join(chr(int(s[i * 8:i * 8 + 8], 2)) for i in range(len(s) // 8))
    return decode_binary_string(binary_str)
def metin_to_binary(veri):
    if isinstance(veri, str):
        binary_str = ""
        for char in veri:
            binary_str += format(ord(char), "08b")
        return binary_str
    elif isinstance(veri, int) or isinstance(veri, np.uint8):
        return format(veri, "08b")
    else:
        raise TypeError("Giriş verisi desteklenmiyor (Sadece yazı veya sayı olmalı).")
def resize(img,max_size=800):
    height,width=img.shape[:2]
    if max(height,width)<=max_size:
        return img
    oran=max_size/max(height,width)
    new_height=int(height*oran)
    new_width=int(width*oran)
    return cv2.resize(img,(new_width,new_height),interpolation=cv2.INTER_AREA)
def encode(img_path,secret_data,output_path):
    img=cv2.imread(img_path)
    if(img is None):
        print("Resim yüklenemedi")
        return False
   #Kücültme işlemi işlem hızı adına
    img=resize(img,max_size=800)
    data_sonu="$$$"
    full_msg=secret_data+data_sonu
    data_ind=0
    binary_data=metin_to_binary(full_msg)
    data_len=len(binary_data)
    max_bytes=img.shape[0]*img.shape[1]*3//8
    if data_len>max_bytes:
        print("Hata: Gizli veri çok büyük")
        return
    print("Gizli veri uzunluğu (bit):",data_len)
    print("Gizleniyor...")
    array_img=img.flatten()
    #listeleştirdikl flattenla
    #gizli veriyi bit bit yerleştir
    for i in range(data_len):
        if data_ind<len(array_img):
            pixels=format(array_img[i],'08b')
            new_pixels=pixels[:-1]+binary_data[data_ind]
            array_img[i]=int(new_pixels,2)
            data_ind+=1
    #gizli veriyi sona ekle
        else:
            break
    img_encoded=array_img.reshape(img.shape)
    if not output_path.endswith(".png"):
        output_path+=".png"
    cv2.imwrite(output_path,img_encoded)
    print("Gizli veri başarıyla gizlendi ve kaydedildi:",output_path)
    return True
def decode(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print("Resim yüklenemedi")
        return ""
    print("Veri Çıkarma İşlemi Başladı...")
    array_img = img.flatten()
    binary_data = ""
    secret_data = ""
    for i in range(len(array_img)):
        bit = str(array_img[i] & 1)
        binary_data += bit
        if len(binary_data) == 8:
            byte = binary_data
            char = chr(int(byte, 2))
            secret_data += char
            binary_data = ""
            if secret_data.endswith("$$$"):
                return secret_data[:-3]
#Binarye çevirme hazır
#gönderieln resmi sınırlayacağız
#ALTTAKİ RESİM KISMINDA SUNUCUDA VE CLİENTTA AYNI İSİM OLMASIN DİYE İSİMLERİ eşsiz yapmak lazım
#yoksa hepsia gizli_Resim.png olur çakışır







