# Bilgi_Guvenligi
Bilgi Güvenligi ve Güvenli Veri Iletisim Protokolü Analizi

Bu çalışma, bilgisayar ağları üzerinde gerçekleşen veri iletim süreçlerinde bilginin gizliliği, bütünlüğü ve erişilebilirliği prensiplerini uygulamalı olarak incelemek amacıyla geliştirilmiştir. Proje, istemci ve sunucu mimarisi arasındaki veri akışının güvenlik katmanlarını ve ağ protokollerini simüle eden bir altyapıya sahiptir.
Projenin Amacı ve Kapsamı

Projenin temel odak noktası, ağ üzerinden taşınan verilerin yetkisiz müdahalelere karşı korunması ve güvenli bir iletişim kanalının tesis edilmesidir. Bu kapsamda aşağıdaki hedeflere odaklanılmıştır:

    İstemci-Sunucu (Client-Server) mimarisinde güvenli veri alışverişi süreçlerinin analizi.

    Ağ soketleri (sockets) üzerinden düşük seviyeli veri iletişimi ve hata yönetimi mekanizmalarının kurulması.

    Veri bütünlüğünün korunması amacıyla iletişim protokollerinin geliştirilmesi ve test edilmesi.

Teknik Mimari ve Fonksiyonel Bileşenler

Sistem, Python programlama dili kullanılarak modüler bir yapıda inşa edilmiştir. İletişim döngüsü iki temel katmandan oluşmaktadır:

    Merkezi Sunucu Katmanı: İstemcilerden gelen bağlantı taleplerini karşılayan, veriyi doğrulayan ve sistemsel yanıtları yöneten ana kontrol ünitesidir.

    İstemci Test Birimi: Sunucu ile veri alışverişini başlatan, güvenlik senaryolarının uygulanmasını sağlayan ve uç nokta iletişimini simüle eden modüldür.

Geliştirme Süreci ve İş Birliği

Proje, siber güvenlik ve ağ yönetimi prensiplerine uygun olarak kolektif bir çalışma düzeni ile yürütülmektedir. Geliştirme sürecinde versiyon kontrol sistemi olarak GitHub kullanılmakta olup, değişiklikler eş zamanlı olarak takip edilmektedir.
Katkıda Bulunanlar

    Cem Onat Satır (github.com/CemOnat00) -

    Yakup Eren Arabul (github.com/ErenSbr) 

Yasal Bildirim

Bu proje yalnızca eğitim ve araştırma amaçlı geliştirilmiştir. Yazılımın içerisinde yer alan yöntemler ve kod blokları, bilgi güvenliği teorilerinin pratiğe dökülmesi amacını taşımaktadır.
