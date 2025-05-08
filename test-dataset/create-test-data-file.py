import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Test veri seti oluştur
np.random.seed(42)  # Tekrarlanabilirlik için

# 15000 satır için veri oluşturacağız
n_samples = 15000

# Normal dağılım (yaş verileri) - float olarak oluştur
ages = np.random.normal(loc=35, scale=12, size=n_samples).astype(float)
ages = np.clip(ages, 18, 80)  # Gerçekçi yaş sınırları

# Logaritmik dağılım (ücret verileri)
salaries = np.exp(np.random.normal(loc=10, scale=1, size=n_samples))
salaries = np.round(salaries / 100) * 100  # Para birimini yuvarla

# Çarpık dağılım (müşteri puanları)
scores = np.random.exponential(scale=2, size=n_samples)
scores = np.clip(scores, 0, 10)  # 0-10 arası puanlama

# Negatif çarpık dağılım (öğrenci notları)
grades = 100 - np.random.power(2, size=n_samples) * 40
grades = np.round(grades)  # Notları yuvarla

# Bimodal dağılım (harcama davranışı)
spending = np.concatenate([
    np.random.normal(loc=200, scale=50, size=n_samples//2),
    np.random.normal(loc=800, scale=150, size=n_samples//2)
])
np.random.shuffle(spending)
spending = np.round(spending)

# Uniform dağılım (rastgele değerler)
random_vals = np.random.uniform(low=0, high=100, size=n_samples)

# YENİ - Poisson dağılımı (haftada sipariş sayısı) - float olarak oluşturalım
order_count = np.random.poisson(lam=3, size=n_samples).astype(float)

# YENİ - Gamma dağılımı (bekleme süreleri)
wait_times = np.random.gamma(shape=2, scale=10, size=n_samples)
wait_times = np.round(wait_times, 1)  # Ondalık kısmı sınırla

# YENİ - Beta dağılımı (0-1 arası oranlar için - müşteri memnuniyet skoru)
satisfaction = np.random.beta(a=8, b=2, size=n_samples)
satisfaction = np.round(satisfaction * 100, 1)  # 0-100 arasına çevir

# Eksik değerler ekleme
for data in [ages, salaries, scores, grades, spending, random_vals, order_count, wait_times, satisfaction]:
    mask = np.random.choice([True, False], size=n_samples, p=[0.1, 0.9])  # %10 eksik veri
    data[mask] = np.nan

# Kategorik veriler - Daha fazla çeşitlilik için genişletilmiş listeler
departments = np.random.choice(
    ['Pazarlama', 'Mühendislik', 'İnsan Kaynakları', 'Satış', 'Finans', 
     'Üretim', 'Ar-Ge', 'Hukuk', 'Lojistik', 'Müşteri Hizmetleri'], 
    size=n_samples
)

cities = np.random.choice(
    ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 
     'Konya', 'Gaziantep', 'Kayseri', 'Eskişehir', 'Trabzon', 'Diyarbakır'],
    size=n_samples
)

is_active = np.random.choice(['Evet', 'Hayır'], size=n_samples, p=[0.8, 0.2])

product_categories = np.random.choice(
    ['Elektronik', 'Giyim', 'Kozmetik', 'Kitap', 'Spor', 'Gıda', 
     'Mobilya', 'Oyuncak', 'Bahçe', 'Otomotiv', 'Kırtasiye', 'Ev Aletleri'],
    size=n_samples
)

# YENİ - Ödeme yöntemleri
payment_methods = np.random.choice(
    ['Kredi Kartı', 'Nakit', 'Havale/EFT', 'Kapıda Ödeme', 'Dijital Cüzdan', 'Taksit'], 
    size=n_samples
)

# YENİ - Eğitim düzeyi
education_levels = np.random.choice(
    ['İlköğretim', 'Lise', 'Önlisans', 'Lisans', 'Yüksek Lisans', 'Doktora'], 
    size=n_samples
)

# YENİ - Medeni durum
marital_status = np.random.choice(
    ['Bekar', 'Evli', 'Boşanmış', 'Dul'], 
    size=n_samples,
    p=[0.45, 0.40, 0.10, 0.05]  # Gerçekçi dağılım oranları
)

# Tablo sınıfları
customer_class = np.where(scores > 7, 'Premium', np.where(scores > 4, 'Normal', 'Basic'))
performance_class = np.where(grades > 85, 'Yüksek', np.where(grades > 70, 'Orta', 'Düşük'))

# Aykırı değerler ekleme - Daha fazla aykırı değer ekleyelim (15000 satır için)
# Yaş için aykırı değerler
outlier_indices = np.random.choice(range(n_samples), size=30, replace=False)
ages[outlier_indices] = np.random.choice([90, 95, 99, 100], size=30)

# Maaş için aykırı değerler
outlier_indices = np.random.choice(range(n_samples), size=30, replace=False)
salaries[outlier_indices] = np.random.choice([500000, 650000, 700000, 800000, 1000000], size=30)

# Sütun isimleri ile DataFrame oluştur
df = pd.DataFrame({
    'Yaş': ages,
    'Maaş': salaries,
    'Müşteri_Puanı': scores,
    'Not': grades,
    'Aylık_Harcama': spending,
    'Rastgele_Değer': random_vals,
    'Haftalık_Sipariş': order_count,           # YENİ
    'Bekleme_Süresi': wait_times,              # YENİ
    'Memnuniyet_Skoru': satisfaction,          # YENİ
    'Departman': departments,
    'Şehir': cities,
    'Aktif_Mi': is_active,
    'Ürün_Kategorisi': product_categories,
    'Ödeme_Yöntemi': payment_methods,          # YENİ
    'Eğitim_Düzeyi': education_levels,         # YENİ
    'Medeni_Durum': marital_status,            # YENİ
    'Müşteri_Sınıfı': customer_class,
    'Performans_Sınıfı': performance_class
})

# Ek string veriler (normalizasyon algoritması tarafından işlenmeyecek)
# İsimler için Türkçe isimler kullanalım
isimler = ['Ali', 'Ayşe', 'Mehmet', 'Fatma', 'Ahmet', 'Zeynep', 'Mustafa', 'Emine', 
           'Hüseyin', 'Hatice', 'İbrahim', 'Havva', 'Ömer', 'Elif', 'Yusuf', 'Hacer',
           'İsmail', 'Meryem', 'Ramazan', 'Zeliha']
           
soyadlar = ['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Yıldırım', 'Öztürk',
            'Aydın', 'Özdemir', 'Arslan', 'Doğan', 'Kılıç', 'Aslan', 'Çetin', 'Şimşek',
            'Eren', 'Güneş', 'Koç', 'Kurt']

# Rastgele isim ve soyad kombinasyonları oluştur
df['Ad_Soyad'] = [f"{np.random.choice(isimler)} {np.random.choice(soyadlar)}" for _ in range(n_samples)]

# E-posta adresleri - daha gerçekçi
domainler = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'yandex.com']
df['Email'] = [f"{ad.lower().replace(' ', '')}_{i}@{np.random.choice(domainler)}" 
              for i, ad in enumerate(df['Ad_Soyad'])]

# Telefon numaraları - Türkiye formatında
df['Telefon'] = [f"+90-5{np.random.randint(10, 60)}{np.random.randint(1000000, 10000000)}" 
                for _ in range(n_samples)]

# Tarih verisi ekleyelim
baslangic_tarihi = pd.Timestamp('2020-01-01')
bitis_tarihi = pd.Timestamp('2025-05-01')
tarih_araligi = (bitis_tarihi - baslangic_tarihi).days
df['Kayıt_Tarihi'] = [baslangic_tarihi + pd.Timedelta(days=np.random.randint(tarih_araligi)) 
                     for _ in range(n_samples)]

# Boolean veri ekleyelim
df['Premium_Üyelik'] = np.random.choice([True, False], size=n_samples, p=[0.3, 0.7])

# YENİ - Son İşlem Tarihi (kayıt tarihinden sonraki bir tarih)
def random_later_date(start_date):
    max_days = (pd.Timestamp('2025-05-01') - start_date).days
    if max_days <= 0:
        return pd.Timestamp('2025-05-01')
    return start_date + pd.Timedelta(days=np.random.randint(0, max_days))

df['Son_İşlem_Tarihi'] = df['Kayıt_Tarihi'].apply(random_later_date)

# CSV olarak kaydet
df.to_csv('data_test_25cols-new.csv', index=False)

# Excel olarak kaydet
df.to_excel('data_test_25cols-new.xlsx', index=False)

print("Test veri seti 'data_test_25cols-new.csv' ve 'data_test_25cols-new.xlsx' olarak oluşturuldu.")
print(f"Toplam satır sayısı: {len(df)}")
print(f"Toplam sütun sayısı: {len(df.columns)}")
print("\nSütunlar:")
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

print("\nDataFrame başlık:")
print(df.head())

# Özet istatistikler (sayısal veriler için)
print("\nSayısal verilerin özet istatistikleri:")
print(df.describe())

# Her sütun için çarpıklık (skewness) değerleri
print("\nHer sayısal sütun için çarpıklık (skewness) değerleri:")
for col in df.select_dtypes(include=[np.number]).columns:
    print(f"{col}: {df[col].skew()}")