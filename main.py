import pandas as pd
import numpy as np
import os

# Test veri seti oluştur
np.random.seed(42)  # Tekrarlanabilirlik için

# Farklı dağılımlara sahip rastgele veri setleri oluştur
n_samples = 100

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

# Eksik değerler ekleme
for data in [ages, salaries, scores, grades, spending, random_vals]:
    mask = np.random.choice([True, False], size=n_samples, p=[0.1, 0.9])  # %10 eksik veri
    data[mask] = np.nan

# Kategorik veriler
departments = np.random.choice(['Pazarlama', 'Mühendislik', 'İnsan Kaynakları', 'Satış', 'Finans'], size=n_samples)
cities = np.random.choice(['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya'], size=n_samples)
is_active = np.random.choice(['Evet', 'Hayır'], size=n_samples, p=[0.8, 0.2])
product_categories = np.random.choice(['Elektronik', 'Giyim', 'Kozmetik', 'Kitap', 'Spor'], size=n_samples)

# Tablo sınıfları
customer_class = np.where(scores > 7, 'Premium', np.where(scores > 4, 'Normal', 'Basic'))
performance_class = np.where(grades > 85, 'Yüksek', np.where(grades > 70, 'Orta', 'Düşük'))

# Aykırı değerler ekleme
# Yaş için bir kaç aykırı değer ekle
outlier_indices = np.random.choice(range(n_samples), size=3, replace=False)
ages[outlier_indices] = [95, 99, 100]

# Maaş için bir kaç aykırı değer ekle
outlier_indices = np.random.choice(range(n_samples), size=3, replace=False)
salaries[outlier_indices] = [500000, 650000, 700000]

# Sütun isimleri ile DataFrame oluştur
df = pd.DataFrame({
    'Yaş': ages,
    'Maaş': salaries,
    'Müşteri_Puanı': scores,
    'Not': grades,
    'Aylık_Harcama': spending,
    'Rastgele_Değer': random_vals,
    'Departman': departments,
    'Şehir': cities,
    'Aktif_Mi': is_active,
    'Ürün_Kategorisi': product_categories,
    'Müşteri_Sınıfı': customer_class,
    'Performans_Sınıfı': performance_class
})

# Ek string veriler (normalizasyon algoritması tarafından işlenmeyecek)
df['Ad_Soyad'] = [f"Kişi-{i}" for i in range(n_samples)]
df['Email'] = [f"kisi{i}@ornek.com" for i in range(n_samples)]
df['Telefon'] = [f"555-{np.random.randint(1000, 10000)}" for _ in range(n_samples)]

# CSV olarak kaydet
df.to_csv('test_veri_seti.csv', index=False)

# Excel olarak kaydet
df.to_excel('test_veri_seti.xlsx', index=False)

print("Test veri seti 'test_veri_seti.csv' ve 'test_veri_seti.xlsx' olarak oluşturuldu.")
print("DataFrame başlık:")
print(df.head())

# Özet istatistikler (sayısal veriler için)
print("\nSayısal verilerin özet istatistikleri:")
print(df.describe())

# Her sütun için çarpıklık (skewness) değerleri
print("\nHer sayısal sütun için çarpıklık (skewness) değerleri:")
for col in df.select_dtypes(include=[np.number]).columns:
    print(f"{col}: {df[col].skew()}")