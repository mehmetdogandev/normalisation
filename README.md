# Veri Normalizasyon Aracı

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![Pandas](https://img.shields.io/badge/pandas-1.3+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

CSV ve Excel dosyalarınızdaki verileri akıllı bir şekilde normalize eden web tabanlı bir araç.

## 📹 Tanıtım Videosu

Bu projenin tanıtım videosunu izlemek için aşağıdaki bağlantıya tıklayabilirsiniz:

[📺 Veri Normalizasyon Aracı Tanıtım Videosu](https://youtu.be/NuyVgOtisrU)

## 📋 Proje Hakkında

Bu proje, veri bilimi ve makine öğrenmesi projelerinde sıkça kullanılan normalizasyon işlemini otomatikleştiren bir web uygulamasıdır. Algoritma, veri setinizin dağılımını analiz ederek en uygun normalizasyon tekniğini seçer ve uygular.

## 🖼️ Ekran Görüntüleri

### Giriş Ekranı
![Giriş Ekranı](/api/placeholder/400/320)

### Kullanıcı Detayları Sayfası
![Kullanıcı Detayları](/api/placeholder/400/320)

### İşlem Geçmişi Sayfası
![İşlem Geçmişi](/api/placeholder/400/320)

### Giriş Sayfası
![Giriş Sayfası](/api/placeholder/400/320)

### Kayıt Ol Sayfası
![Kayıt Ol Sayfası](/api/placeholder/400/320)

### Dosya Yükleme ve Normalizasyon Arayüzü
![Dosya Normalizasyon Aracı](/api/placeholder/400/320)

### Normalizasyon Algoritması Bilgi Sayfası
![Veri Normalizasyon Algoritması](/api/placeholder/400/320)

### Yönetici Paneli - Kullanıcı Listesi
![Yönetici Paneli](/api/placeholder/400/320)

### ✨ Özellikler

- **Akıllı Normalizasyon Algoritması**: Veri dağılımına göre optimize edilmiş normalizasyon tekniği seçimi
- **Çoklu Format Desteği**: CSV ve Excel dosyaları (.csv, .xls, .xlsx)
- **Otomatik Veri Analizi**: Sayısal sütunların otomatik tespiti
- **Eksik ve Aykırı Değer İşleme**: Winsorization ve medyan doldurma teknikleri
- **Kullanıcı Yönetimi**: Çoklu kullanıcı desteği ve oturum yönetimi
- **İşlem Geçmişi**: Tüm normalizasyon işlemlerinin kaydı
- **Responsive Arayüz**: Mobil cihazlarda da sorunsuz çalışan modern arayüz

### 🧠 Algoritma Özellikleri

- **Pozitif Çarpık Veriler**: Logaritmik dönüşüm + Sigmoid fonksiyonu
- **Negatif Çarpık Veriler**: Min-Max ölçekleme + Trigonometrik normalizasyon
- **Normal Dağılıma Yakın Veriler**: Hibrit ArcTan yaklaşımı
- **Aykırı Değer Tespiti**: IQR (Interquartile Range) yöntemi
- **Doğruluk Kontrolü**: Normalize edilmiş verilerin 0-1 aralığı garantisi

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- Flask
- Pandas
- NumPy
- Waitress (production deployment için)
- SQLite3 (veritabanı için)

### Adım Adım Kurulum

1. Repo'yu klonlayın:

```bash
git clone https://github.com/mehmetdogandev/normalisation.git
cd normalisation
```

2. Sanal ortam oluşturun ve aktifleştirin:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

4. Uygulamayı başlatın:

```bash
python app.py
```

5. Tarayıcınızı açın ve şu adrese gidin:

```
http://127.0.0.1:5000
```

### Docker ile Kurulum

```bash
docker build -t normalisation-app .
docker run -p 5000:5000 normalisation-app
```

## 📊 Kullanım

1. Hesap oluşturun veya giriş yapın
2. Ana sayfada "Dosya Seç" butonuna tıklayın veya dosyanızı sürükleyip bırakın
3. Ad ve soyad bilgilerinizi girin
4. Çıktı formatını seçin (CSV veya Excel)
5. "Normalize Et" butonuna tıklayın
6. İlerleme çubuğu tamamlandığında, normalize edilmiş dosyayı indirebilirsiniz

## 🔧 Normalizasyon Adımları

1. **Dosya Okuma ve Analiz (%20)**: Yüklenen dosya okunur ve veri yapısı analiz edilir
2. **Sayısal Sütun Tespiti (%40)**: Normalize edilecek sütunlar belirlenir ve sınıf sütunları korunur
3. **Eksik ve Aykırı Değer İşleme (%60)**: Eksik değerler doldurulur ve aykırı değerler işlenir
4. **Akıllı Normalizasyon (%80)**: Veri dağılımına uygun normalizasyon tekniği uygulanır
5. **Doğrulama ve Kontrol (%90)**: Normalize edilmiş verilerin 0-1 aralığında olduğu doğrulanır
6. **Sonuç Dosyasının Oluşturulması (%100)**: İşlenmiş veriler seçilen formatta kaydedilir

## 📁 Proje Yapısı

```
normalisation/
├── app.py                  # Ana uygulama dosyası
├── database.db             # SQLite veritabanı
├── requirements.txt        # Gerekli kütüphaneler
├── static/                 # Statik dosyalar
│   ├── css/                # CSS stilleri
│   ├── js/                 # JavaScript dosyaları
│   ├── uploads/            # Yüklenen dosyalar
│   ├── new_csv/            # Normalize edilmiş dosyalar
│   └── videos/             # Video dosyaları
│   └── images/             # projeye ait arayüz görselleri
└── templates/              # HTML şablonları
    ├── index.html          # Ana sayfa
    ├── login.html          # Giriş sayfası
    ├── register.html       # Kayıt sayfası
    ├── about.html          # Algoritma hakkında bilgi
    ├── header.html         # Başlık şablonu
    └── footer.html         # Alt bilgi şablonu
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen bir pull request göndermeden önce şunları yapın:

1. Repo'yu forklayın
2. Yeni bir feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request açın

## 📞 İletişim

Mehmet DOĞAN - [mehmetdogan.dev@gmail.com](mailto:mehmetdogan.dev@gmail.com)

Proje Bağlantısı: [https://github.com/mehmetdogandev/imagecription](https://github.com/mehmetdogandev/imagecription)

### Sosyal Medya & Web

- **Website**: [memetdogan.com](https://memetdogan.com)
- **LinkedIn**: [linkedin.com/in/mehmetdogandev](https://www.linkedin.com/in/mehmetdogandev/)
- **YouTube**: [youtube.com/@md-kare](https://www.youtube.com/@md-kare)

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

---

⭐️ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐️