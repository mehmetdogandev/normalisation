from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, session, redirect, flash
import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import shutil
import uuid
import json
import sqlite3
import hashlib
from functools import wraps
from waitress import serve

app = Flask(__name__)
app.secret_key = "normalizer_app_secret_key"  # Session için gerekli

# Klasörlerin oluşturulması
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
NEW_CSV_FOLDER = os.path.join(BASE_DIR, 'static', 'new_csv')
DATA_FILE = os.path.join(BASE_DIR, 'data', 'file_history.json')
DATABASE = os.path.join(BASE_DIR, 'database.db')

# Klasörleri oluştur
for folder in [UPLOAD_FOLDER, NEW_CSV_FOLDER, os.path.join(BASE_DIR, 'data')]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Veritabanı bağlantısı
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Şifre hashleme fonksiyonu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
# Veritabanını oluştur
def init_db():
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Var olan tabloda role sütunu olup olmadığını kontrol et
        try:
            # Tablodan bir satır al ve sütunları kontrol et
            user_info = cursor.execute("PRAGMA table_info(users)").fetchall()
            column_names = [column[1] for column in user_info]
            
            # Role sütunu yoksa ekle
            if 'role' not in column_names:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
                print("'role' sütunu users tablosuna eklendi.")
        except Exception as e:
            print(f"Sütun kontrolü sırasında hata: {e}")
        
        # Kullanıcı işlemleri tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_file TEXT NOT NULL,
            normalized_file TEXT NOT NULL,
            operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # İlk admin kullanıcısını ekle (eğer yoksa)
        admin = cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
        if not admin:
            cursor.execute('INSERT INTO users (username, password, email, full_name, role) VALUES (?, ?, ?, ?, ?)',
                          ('admin', hash_password('admin123'), 'admin@example.com', 'Admin User', 'admin'))
            print("Admin kullanıcısı oluşturuldu.")
        elif admin and 'role' in column_names and admin['role'] != 'admin':
            # Admin kullanıcısı varsa ve rolü admin değilse, rolünü güncelle
            cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('admin', 'admin'))
            print("Admin kullanıcısının rolü güncellendi.")
        
        conn.commit()
        conn.close()
# Uygulamayı başlatırken veritabanını oluştur
init_db()


# Login gerektiren sayfalar için dekoratör
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# İlerleme durumunu saklamak için global değişken
normalization_progress = {}

# Dosya geçmişini yükle
def load_file_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('uploaded_files', []), data.get('normalized_files', [])
        except Exception as e:
            print(f"Dosya geçmişi yüklenirken hata: {e}")
    return [], []

# Dosya geçmişini kaydet
def save_file_history(uploaded_files, normalized_files):
    try:
        data = {
            'uploaded_files': uploaded_files,
            'normalized_files': normalized_files
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Dosya geçmişi kaydedilirken hata: {e}")

# Normalizasyon sınıfı
class Normalizer:
    def __init__(self, file_path, process_id):
        self.file_path = file_path
        self.process_id = process_id
        
    def normalize(self):
        try:
            # CSV dosyasını oku
            df = pd.read_csv(self.file_path)
            
            # İlerleme durumunu başlat
            normalization_progress[self.process_id] = {
                "progress": 0,
                "status": "Dosya okuma işlemi tamamlandı."
            }
            
            # Adım 1: Veri analizi (%20)
            time.sleep(0.5)
            normalization_progress[self.process_id] = {
                "progress": 20,
                "status": "Veri yapısı analiz ediliyor..."
            }
            
            # Adım 2: Sayısal sütunları tespit et ve string sütunları filtrele (%40)
            time.sleep(0.5)
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # String sütunlarını bul
            string_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            # Sınıf isimlerini belirten sütunları koruyarak diğer string sütunları filtrele
            filtered_columns = []
            class_columns = []
            
            for col in string_columns:
                # Sütun adında "sınıf", "class", "kategori" gibi anahtar kelimeler varsa koru
                if any(keyword in col.lower() for keyword in ["class", "sınıf", "kategori", "category", "type", "tip"]):
                    class_columns.append(col)
                else:
                    filtered_columns.append(col)
            
            normalization_progress[self.process_id] = {
                "progress": 40,
                "status": f"{len(numeric_columns)} sayısal ve {len(class_columns)} sınıf sütunu işlenecek. {len(filtered_columns)} string sütunu işlenmeyecek."
            }
            
            # Adım 3: Eksik veri analizi ve önişleme (%60)
            time.sleep(0.5)
            
            # Sayısal sütunlardaki eksik değerleri Winsorization ile doldur
            for col in numeric_columns:
                if df[col].isnull().sum() > 0:
                    # Aykırı değerler için alt ve üst sınırlar
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    # Uç değerleri kırp
                    df[col] = df[col].clip(lower_bound, upper_bound)
                    
                    # Eksik değerleri medyan ile doldur
                    df[col] = df[col].fillna(df[col].median())
            
            normalization_progress[self.process_id] = {
                "progress": 60,
                "status": "Eksik ve aykırı değerler işlendi."
            }
            
            # Adım 4: Özgün normalizasyon algoritmamız (%80)
            time.sleep(0.5)
            
            # Her sayısal sütun için uygun normalizasyon tekniğini seç ve uygula
            for col in numeric_columns:
                if len(df[col]) > 0:
                    # Veri özellikleri analizi
                    data = df[col].dropna()
                    min_val = data.min()
                    max_val = data.max()
                    range_val = max_val - min_val
                    skewness = data.skew()  # Çarpıklık
                    
                    # Ölçekleme için boş dizi oluştur
                    normalized_values = np.zeros_like(df[col])
                    
                    # Veri dağılımına göre uygun normalizasyon tekniğini seç
                    if skewness > 1.0:  # Pozitif çarpık veriler için logaritmik dönüşüm
                        # Negatif ve sıfır değerler için ofset ekle
                        offset = abs(min_val) + 1 if min_val <= 0 else 0
                        
                        for i, val in enumerate(df[col]):
                            if not pd.isna(val):
                                # Logaritmik normalizasyon
                                log_val = np.log1p(val + offset)
                                # Sigmoid fonksiyonu (0-1 aralığına getir)
                                norm_val = 1 / (1 + np.exp(-log_val))
                                normalized_values[i] = norm_val
                                
                        # Min-max tekrar ölçekleme (0-1 aralığına garanti etmek için)
                        norm_min, norm_max = np.min(normalized_values), np.max(normalized_values)
                        if norm_max > norm_min:
                            normalized_values = (normalized_values - norm_min) / (norm_max - norm_min)
                            
                        df[col] = normalized_values
                        
                    elif skewness < -1.0:  # Negatif çarpık veriler için üstel dönüşüm
                        for i, val in enumerate(df[col]):
                            if not pd.isna(val):
                                # Min-max ölçekleme önce
                                scaled_val = (val - min_val) / range_val if range_val > 0 else 0
                                # Trigonometrik normalizasyon - sinüs fonksiyonu (0-1 aralığına)
                                norm_val = np.sin(scaled_val * np.pi/2)
                                normalized_values[i] = norm_val
                                
                        df[col] = normalized_values
                        
                    else:  # Normal dağılıma yakın veriler için hibrit yaklaşım
                        for i, val in enumerate(df[col]):
                            if not pd.isna(val):
                                # Min-max ölçekleme
                                scaled_val = (val - min_val) / range_val if range_val > 0 else 0
                                # Hibrit normalizasyon (arctan fonksiyonu)
                                norm_val = (np.arctan(scaled_val * 5 - 2.5) / np.pi) + 0.5
                                normalized_values[i] = norm_val
                                
                        df[col] = normalized_values

            normalization_progress[process_id] = {
                "progress": 80,
                "status": "Özgün normalizasyon algoritması uygulandı."
            }
            
            # Adım 5: Özgünlük doğrulaması ve son işlemler (%90)
            time.sleep(0.5)
            
            # Veriyi 0-1 aralığında olduğundan emin olmak için son kontrol
            for col in numeric_columns:
                if len(df[col].dropna()) > 0:
                    cur_min = df[col].min()
                    cur_max = df[col].max()
                    
                    # Eğer 0-1 aralığında değilse, son bir ölçekleme yap
                    if cur_min < 0 or cur_max > 1:
                        df[col] = (df[col] - cur_min) / (cur_max - cur_min) if cur_max > cur_min else 0
            
            normalization_progress[self.process_id] = {
                "progress": 90,
                "status": "Veriler 0-1 aralığına normalize edildi."
            }
            
            # Adım 6: Kalite kontrol ve tamamlama (%100)
            time.sleep(0.5)
            
            # Normalizasyon doğruluk metriği hesapla
            accuracy_scores = []
            for col in numeric_columns:
                data = df[col].dropna()
                if len(data) > 0:
                    # 0-1 aralığında olup olmadığını kontrol et
                    in_range = ((data >= 0) & (data <= 1)).mean()
                    accuracy_scores.append(in_range)
            
            avg_accuracy = np.mean(accuracy_scores) if accuracy_scores else 1.0
            
            normalization_progress[self.process_id] = {
                "progress": 100,
                "status": f"Normalizasyon tamamlandı. Doğruluk: {avg_accuracy:.2%}"
            }
            
            return df
            
        except Exception as e:
            print(f"Normalizasyon hatası: {e}")
            normalization_progress[self.process_id] = {
                "progress": -1,
                "status": f"Hata: {str(e)}"
            }
            return None
# Kullanıcının işlemlerini getir
def get_user_operations(user_id):
    conn = get_db_connection()
    operations = conn.execute('SELECT * FROM user_operations WHERE user_id = ? ORDER BY operation_date DESC', (user_id,)).fetchall()
    conn.close()
    return operations

# Kullanıcının yaptığı işlemi kaydet
def save_user_operation(user_id, original_file, normalized_file):
    conn = get_db_connection()
    conn.execute('INSERT INTO user_operations (user_id, original_file, normalized_file) VALUES (?, ?, ?)',
                 (user_id, original_file, normalized_file))
    conn.commit()
    conn.close()
# Flask app.py dosyasına aşağıdaki kodu ekleyin

# Önce, statik video dosyalarını servis etmek için yeni bir rota ekleyin 
# (mevcut kodunuzun sonuna, en alta ekleyin)

@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    """Video dosyalarını servis etmek için özel bir rota"""
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'videos'), filename)

# NOT: Bu kodu app.py dosyasına ekledikten sonra aşağıdaki klasör yapısını oluşturun:
# - /static/videos/ 
# Bu klasöre {{ url_for('static', filename='videos/arkaplan.mp4') }} dosyanızı koyun
# Kayıt sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        
        conn = get_db_connection()
        
        # Kullanıcı adı veya email mevcut mu kontrol et
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                           (username, email)).fetchone()
        
        if user:
            conn.close()
            flash('Bu kullanıcı adı veya e-posta adresi zaten kayıtlı!', 'error')
            return redirect(url_for('register'))
        
        # Yeni kullanıcıyı ekle
        conn.execute('INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)',
                    (username, hash_password(password), email, full_name))
        conn.commit()
        conn.close()
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login sayfası
# index route fonksiyonunu güncelleyelim
@app.route('/')
@login_required
def index():
    # Sadece giriş yapmış kullanıcının dosyalarını getir
    user_id = session['user_id']
    username = session.get('username', '')
    
    # Kullanıcının işlemlerini getir
    conn = get_db_connection()
    user_operations = conn.execute('SELECT * FROM user_operations WHERE user_id = ? ORDER BY operation_date DESC', (user_id,)).fetchall()
    conn.close()
    
    # Kullanıcının yüklediği dosyaları getir
    user_uploaded_files = []
    user_normalized_files = []
    
    if os.path.exists(UPLOAD_FOLDER) and os.path.exists(NEW_CSV_FOLDER):
        # Kişisel uploaded dosyaları
        for filename in os.listdir(UPLOAD_FOLDER):
            if username in filename:  # Sadece kullanıcının adını içeren dosyaları getir
                try:
                    parts = filename.split('-')
                    extension = filename.split('.')[-1].lower() if '.' in filename else ''
                    
                    if len(parts) >= 4:
                        first_name = parts[0]
                        last_name = parts[1]
                        file_name = parts[2]
                        
                        # Dosya adındaki tarih kısmını ayıkla
                        date_parts = filename.split('_')
                        if len(date_parts) >= 2:
                            date_str = date_parts[-2]
                            time_str = date_parts[-1].split('.')[0]
                            
                            # Tarih formatını düzenle
                            try:
                                year = date_str[:4]
                                month = date_str[4:6]
                                day = date_str[6:8]
                                
                                hours = time_str[:2]
                                minutes = time_str[2:4]
                                
                                formatted_date = f"{day}.{month}.{year} {hours}:{minutes}"
                            except:
                                formatted_date = datetime.now().strftime("%d.%m.%Y %H:%M")
                        
                        file_info = {
                            "user_name": f"{first_name} {last_name}",
                            "file_name": filename,
                            "date": formatted_date,
                            "path": f"uploads/{filename}",
                            "download_url": url_for('download_file', file_path=f"uploads/{filename}"),
                            "format": "excel" if extension in ['xls', 'xlsx'] else "csv"
                        }
                        user_uploaded_files.append(file_info)
                except Exception as e:
                    print(f"Dosya bilgisi çıkarılırken hata: {e}")
        
        # Kişisel normalized dosyaları
        for filename in os.listdir(NEW_CSV_FOLDER):
            if username in filename and "normalized" in filename:  # Sadece kullanıcının adını içeren dosyaları getir
                try:
                    parts = filename.split('-')
                    extension = filename.split('.')[-1].lower() if '.' in filename else ''
                    
                    if len(parts) >= 5:
                        first_name = parts[0]
                        last_name = parts[1]
                        
                        # Dosya adındaki tarih kısmını ayıkla
                        date_parts = filename.split('_')
                        if len(date_parts) >= 2:
                            date_str = date_parts[-2]
                            time_str = date_parts[-1].split('.')[0]
                            
                            # Tarih formatını düzenle
                            try:
                                year = date_str[:4]
                                month = date_str[4:6]
                                day = date_str[6:8]
                                
                                hours = time_str[:2]
                                minutes = time_str[2:4]
                                
                                formatted_date = f"{day}.{month}.{year} {hours}:{minutes}"
                            except:
                                formatted_date = datetime.now().strftime("%d.%m.%Y %H:%M")
                        
                        file_info = {
                            "user_name": f"{first_name} {last_name}",
                            "file_name": filename,
                            "date": formatted_date,
                            "path": f"new_csv/{filename}",
                            "download_url": url_for('download_file', file_path=f"new_csv/{filename}"),
                            "format": "excel" if extension in ['xls', 'xlsx'] else "csv"
                        }
                        user_normalized_files.append(file_info)
                except Exception as e:
                    print(f"Dosya bilgisi çıkarılırken hata: {e}")
    
    # Tarih sırasına göre sırala
    user_uploaded_files.sort(key=lambda x: x.get('date', ''), reverse=True)
    user_normalized_files.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('index.html', 
                          user_operations=user_operations,
                          uploaded_files=user_uploaded_files,
                          normalized_files=user_normalized_files)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# Normalize endpoint'ini güncelle
@app.route('/normalize', methods=['POST'])
@login_required
def normalize():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Dosya bulunamadı"})
    
    file = request.files['file']
    first_name = request.form.get('firstName', '')
    last_name = request.form.get('lastName', '')
    file_format = request.form.get('fileFormat', 'csv')  # Seçilen dosya formatı
    
    if file.filename == '':
        return jsonify({"success": False, "message": "Dosya seçilmedi"})
    
    try:
        # Yüklenen dosyayı kaydetme
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        original_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        filename_base = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        
        # Kullanıcı bilgilerini dosya adına ekle
        username = session.get('username', 'unknown')
        new_filename = f"{first_name}-{last_name}-{filename_base}-{username}-{timestamp}.{original_extension}"
        
        upload_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(upload_path)
        
        # Benzersiz işlem ID'si oluştur
        process_id = str(uuid.uuid4())
        
        # Session'a process_id'yi kaydet
        session['process_id'] = process_id
        
        # İlerleme durumunu başlat
        normalization_progress[process_id] = {
            "progress": 0,
            "status": "Dosya yüklendi, işleme hazırlanıyor..."
        }
        
        # Dosyayı oku ve DataFrame'e çevir
        try:
            if original_extension.lower() in ['xls', 'xlsx']:
                # Excel dosyası
                df = pd.read_excel(upload_path)
                file_type = "excel"
                normalization_progress[process_id] = {
                    "progress": 10,
                    "status": "Excel dosyası başarıyla okundu."
                }
            elif original_extension.lower() == 'csv':
                # CSV dosyası
                df = pd.read_csv(upload_path)
                file_type = "csv"
                normalization_progress[process_id] = {
                    "progress": 10,
                    "status": "CSV dosyası başarıyla okundu."
                }
            else:
                return jsonify({"success": False, "message": "Desteklenmeyen dosya formatı"})
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            return jsonify({"success": False, "message": f"Dosya okunamadı: {str(e)}"})
        
        # Normalizasyon işlemini gerçekleştir
        try:
            # Adım 2: Sayısal sütunları tespit et (%30)
            time.sleep(0.5)  # Simule edilen işlem zamanı
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            normalization_progress[process_id] = {
                "progress": 30,
                "status": f"{len(numeric_columns)} sayısal sütun tespit edildi."
            }
            
            # Adım 3: Eksik verileri kontrol et ve doldur (%50)
            time.sleep(0.5)  # Simule edilen işlem zamanı
            for col in numeric_columns:
                if df[col].isnull().sum() > 0:
                    df[col] = df[col].fillna(df[col].median())
            
            normalization_progress[process_id] = {
                "progress": 50,
                "status": "Eksik değerler dolduruldu."
            }
            
            # Adım 4: Normalizasyon işlemini uygula (%80)
            time.sleep(0.5)  # Simule edilen işlem zamanı
            for col in numeric_columns:
                if len(df[col]) > 0:  # Sütun boş değilse
                    min_val = df[col].min()
                    max_val = df[col].max()
                    if max_val > min_val:  # Bölme hatası olmaması için kontrol
                        df[col] = (df[col] - min_val) / (max_val - min_val)
            
            normalization_progress[process_id] = {
                "progress": 80,
                "status": "Normalizasyon işlemi uygulandı."
            }
            
            # Adım 5: Normalize edilmiş dosyayı kaydet (%100)
            time.sleep(0.5)  # Simule edilen işlem zamanı
            
            # Burada kullanıcının tercih ettiği formatta dosyayı oluşturuyoruz
            output_extension = "xlsx" if file_format == "excel" else "csv"
            
            # Ancak orijinal dosya formatını da koruyoruz
            if file_type == "excel" and original_extension.lower() in ['xls', 'xlsx']:
                output_extension = original_extension
            
            normalized_filename = f"{first_name}-{last_name}-{filename_base}-normalized-{username}-{timestamp}.{output_extension}"
            normalized_path = os.path.join(NEW_CSV_FOLDER, normalized_filename)
            
            # DataFrame'i seçilen formatta kaydet
            if output_extension.lower() in ['xls', 'xlsx']:
                # Excel olarak kaydet
                df.to_excel(normalized_path, index=False, engine='openpyxl')
                output_format = "Excel"
            else:
                # CSV olarak kaydet
                df.to_csv(normalized_path, index=False)
                output_format = "CSV"
            
            normalization_progress[process_id] = {
                "progress": 100,
                "status": f"İşlem tamamlandı. Dosya {output_format} formatında kaydedildi."
            }
            
            # İşlem geçmişini kullanıcı için veritabanında sakla
            save_user_operation(session['user_id'], new_filename, normalized_filename)
            
            # İşlem geçmişini güncelle
            formatted_date = now.strftime("%d.%m.%Y %H:%M")
            
            uploaded_file_info = {
                "user_name": f"{first_name} {last_name}",
                "file_name": original_filename,
                "date": formatted_date,
                "path": f"uploads/{new_filename}",
                "download_url": url_for('download_file', file_path=f"uploads/{new_filename}")
            }
            
            normalized_file_info = {
                "user_name": f"{first_name} {last_name}",
                "file_name": f"{filename_base}-normalized.{output_extension}",
                "date": formatted_date,
                "path": f"new_csv/{normalized_filename}",
                "download_url": url_for('download_file', file_path=f"new_csv/{normalized_filename}"),
                "file_format": output_format.lower()
            }
            
            # İşlem tamamlandı
            return jsonify({
                "success": True,
                "message": f"Dosya başarıyla normalize edildi ve {output_format} formatında kaydedildi",
                "download_url": url_for('download_file', file_path=f"new_csv/{normalized_filename}"),
                "uploaded_file": uploaded_file_info,
                "normalized_file": normalized_file_info,
                "process_id": process_id,
                "file_format": output_format.lower()
            })
            
        except Exception as e:
            print(f"Normalizasyon işlemi hatası: {e}")
            normalization_progress[process_id] = {
                "progress": -1,
                "status": f"Hata: {str(e)}"
            }
            return jsonify({"success": False, "message": f"Normalizasyon işlemi başarısız oldu: {str(e)}"})
            
    except Exception as e:
        print(f"Genel hata: {e}")
        return jsonify({"success": False, "message": f"Hata oluştu: {str(e)}"})
# Excel dosyaları için normalizasyon sınıfı
class ExcelNormalizer:
    def __init__(self, file_path, process_id):
        self.file_path = file_path
        self.process_id = process_id
        
    def normalize(self):
        try:
            # Excel dosyasını oku
            df = pd.read_excel(self.file_path)
            
            # İlerleme durumunu başlat
            normalization_progress[self.process_id] = {
                "progress": 0,
                "status": "Excel dosyası okuma işlemi tamamlandı."
            }
            
            # Adım 1: Veri analizi (%20)
            time.sleep(0.5)
            normalization_progress[self.process_id] = {
                "progress": 20,
                "status": "Excel verisi analiz ediliyor..."
            }
            
            # Adım 2: Sayısal sütunları tespit et ve string sütunları filtrele (%40)
            time.sleep(0.5)
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # String sütunlarını bul
            string_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            # Sınıf isimlerini belirten sütunları koruyarak diğer string sütunları filtrele
            filtered_columns = []
            class_columns = []
            
            for col in string_columns:
                # Sütun adında "sınıf", "class", "kategori" gibi anahtar kelimeler varsa koru
                if any(keyword in col.lower() for keyword in ["class", "sınıf", "kategori", "category", "type", "tip"]):
                    class_columns.append(col)
                else:
                    filtered_columns.append(col)
            
            normalization_progress[self.process_id] = {
                "progress": 40,
                "status": f"{len(numeric_columns)} sayısal ve {len(class_columns)} sınıf sütunu işlenecek. {len(filtered_columns)} string sütunu işlenmeyecek."
            }
            
            # Adım 3: Eksik veri analizi ve önişleme (%60)
            time.sleep(0.5)
            
            # Sayısal sütunlardaki eksik değerleri Winsorization ile doldur
            for col in numeric_columns:
                if df[col].isnull().sum() > 0:
                    # Aykırı değerler için alt ve üst sınırlar
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    # Uç değerleri kırp
                    df[col] = df[col].clip(lower_bound, upper_bound)
                    
                    # Eksik değerleri medyan ile doldur
                    df[col] = df[col].fillna(df[col].median())
            
            normalization_progress[self.process_id] = {
                "progress": 60,
                "status": "Eksik ve aykırı değerler işlendi."
            }
            
            # Adım 4: Özgün normalizasyon algoritmamız (%80)
            time.sleep(0.5)
            
            # Her sayısal sütun için uygun normalizasyon tekniğini seç ve uygula
            for col in numeric_columns:
                if len(df[col]) > 0:
                    # Veri özellikleri analizi
                    data = df[col].dropna()
                    min_val = data.min()
                    max_val = data.max()
                    range_val = max_val - min_val
                    skewness = data.skew()  # Çarpıklık
                    
                    # Ölçekleme için boş dizi oluştur
                    normalized_values = np.zeros_like(df[col])
                    
                    # Veri dağılımına göre uygun normalizasyon tekniğini seç
                    if skewness > 1.0:  # Pozitif çarpık veriler için logaritmik dönüşüm
                        # Negatif ve sıfır değerler için ofset ekle
                        offset = abs(min_val) + 1 if min_val <= 0 else 0
                        
                        for i, val in enumerate(df[col]):
                            if not pd.isna(val):
                                # Logaritmik normalizasyon
                                log_val = np.log1p(val + offset)
                                # Sigmoid fonksiyonu (0-1 aralığına getir)
                                norm_val = 1 / (1 + np.exp(-log_val))
                                normalized_values[i] = norm_val
                                
                        # Min-max tekrar ölçekleme (0-1 aralığına garanti etmek için)
                        norm_min, norm_max = np.min(normalized_values), np.max(normalized_values)
                        if norm_max > norm_min:
                            normalized_values = (normalized_values - norm_min) / (norm_max - norm_min)
                            
                        df[col] = normalized_values
                        
                    elif skewness < -1.0:  # Negatif çarpık veriler için üstel dönüşüm
                        for i, val in enumerate(df[col]):
                            if not pd.isna(val):
                                # Min-max ölçekleme önce
                                scaled_val = (val - min_val) / range_val if range_val > 0 else 0
                                # Trigonometrik normalizasyon - sinüs fonksiyonu (0-1 aralığına)
                                norm_val = np.sin(scaled_val * np.pi/2)
                                normalized_values[i] = norm_val
                                
                        df[col] = normalized_values
                        
                    else:  # Normal dağılıma yakın veriler için hibrit yaklaşım
                        for i, val in enumerate(df[col]):
                            if not pd.isna(val):
                                # Min-max ölçekleme
                                scaled_val = (val - min_val) / range_val if range_val > 0 else 0
                                # Hibrit normalizasyon (arctan fonksiyonu)
                                norm_val = (np.arctan(scaled_val * 5 - 2.5) / np.pi) + 0.5
                                normalized_values[i] = norm_val
                                
                        df[col] = normalized_values
            
            normalization_progress[self.process_id] = {
                "progress": 80,
                "status": "Özgün normalizasyon algoritması uygulandı."
            }
            
            # Adım 5: Özgünlük doğrulaması ve son işlemler (%90)
            time.sleep(0.5)
            
            # Veriyi 0-1 aralığında olduğundan emin olmak için son kontrol
            for col in numeric_columns:
                if len(df[col].dropna()) > 0:
                    cur_min = df[col].min()
                    cur_max = df[col].max()
                    
                    # Eğer 0-1 aralığında değilse, son bir ölçekleme yap
                    if cur_min < 0 or cur_max > 1:
                        df[col] = (df[col] - cur_min) / (cur_max - cur_min) if cur_max > cur_min else 0
            
            normalization_progress[self.process_id] = {
                "progress": 90,
                "status": "Excel verileri 0-1 aralığına normalize edildi."
            }
            
            # Adım 6: Kalite kontrol ve tamamlama (%100)
            time.sleep(0.5)
            
            # Normalizasyon doğruluk metriği hesapla
            accuracy_scores = []
            for col in numeric_columns:
                data = df[col].dropna()
                if len(data) > 0:
                    # 0-1 aralığında olup olmadığını kontrol et
                    in_range = ((data >= 0) & (data <= 1)).mean()
                    accuracy_scores.append(in_range)
            
            avg_accuracy = np.mean(accuracy_scores) if accuracy_scores else 1.0
            
            normalization_progress[self.process_id] = {
                "progress": 100,
                "status": f"Excel normalizasyonu tamamlandı. Doğruluk: {avg_accuracy:.2%}"
            }
            
            return df
            
        except Exception as e:
            print(f"Excel Normalizasyon hatası: {e}")
            normalization_progress[self.process_id] = {
                "progress": -1,
                "status": f"Hata: {str(e)}"
            }
            return None
          
@app.route('/progress/<process_id>')
@login_required
def get_progress(process_id):
    """İşlem ilerlemesini döndüren endpoint"""
    if process_id in normalization_progress:
        return jsonify(normalization_progress[process_id])
    return jsonify({"progress": 0, "status": "İşlem başlatılıyor..."})
# Login sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            
            flash('Başarıyla giriş yaptınız!', 'success')
            
            # Yönetici ise admin paneline yönlendir
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')
    
    return render_template('login.html')
# Yönetici gerektiren sayfalar için dekoratör
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız!', 'error')
            return redirect(url_for('login'))
        elif session.get('role') != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok!', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Tüm kullanıcıları getir
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY registration_date DESC').fetchall()
    conn.close()
    return users

# Belirli bir kullanıcının işlemlerini getir
def get_user_operations_by_admin(user_id):
    conn = get_db_connection()
    operations = conn.execute('SELECT * FROM user_operations WHERE user_id = ? ORDER BY operation_date DESC', (user_id,)).fetchall()
    conn.close()
    return operations

# Kullanıcı sil
def delete_user(user_id):
    conn = get_db_connection()
    # Önce kullanıcının işlemlerini sil
    conn.execute('DELETE FROM user_operations WHERE user_id = ?', (user_id,))
    # Sonra kullanıcıyı sil
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

# Yönetici paneli
@app.route('/admin')
@admin_required
def admin_dashboard():
    users = get_all_users()
    return render_template('admin_dashboard.html', users=users)

# Kullanıcı detaylarını görüntüle
@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_view_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if not user:
        flash('Kullanıcı bulunamadı!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    operations = get_user_operations_by_admin(user_id)
    
    # Kullanıcının dosyalarını bul
    user_files = []
    
    if os.path.exists(UPLOAD_FOLDER) and os.path.exists(NEW_CSV_FOLDER):
        # Kullanıcı adını al
        username = user['username']
        
        # Yüklenen dosyaları getir
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.csv') and username in filename:
                file_info = {
                    "type": "uploaded",
                    "file_name": filename,
                    "path": f"uploads/{filename}",
                    "date": get_date_from_filename(filename),
                    "download_url": url_for('download_file', file_path=f"uploads/{filename}")
                }
                user_files.append(file_info)
        
        # Normalize edilmiş dosyaları getir
        for filename in os.listdir(NEW_CSV_FOLDER):
            if filename.endswith('.csv') and username in filename:
                file_info = {
                    "type": "normalized",
                    "file_name": filename,
                    "path": f"new_csv/{filename}",
                    "date": get_date_from_filename(filename),
                    "download_url": url_for('download_file', file_path=f"new_csv/{filename}")
                }
                user_files.append(file_info)
    
    # Dosyaları tarihe göre sırala
    user_files.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('admin_view_user.html', user=user, operations=operations, files=user_files)

# Kullanıcı silme
@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # Admin kendini silemesin
    if user_id == session['user_id']:
        flash('Kendinizi silemezsiniz!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Kullanıcıyı sil
    delete_user(user_id)
    
    flash('Kullanıcı başarıyla silindi!', 'success')
    return redirect(url_for('admin_dashboard'))

# Dosya adından tarih bilgisini çıkar
# Dosya adından tarih bilgisini çıkar (düzeltilmiş)
def get_date_from_filename(filename):
    try:
        date_parts = filename.split('_')
        if len(date_parts) >= 2:
            date_str = date_parts[-2]
            time_str = date_parts[-1].split('.')[0]
            
            # Tarih formatını düzenle
            try:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                
                # Saat ve dakika için düzeltme
                if len(time_str) >= 4:
                    hours = time_str[:2]
                    minutes = time_str[2:4]
                    formatted_date = f"{day}.{month}.{year} {hours}:{minutes}"
                else:
                    formatted_date = f"{day}.{month}.{year} 00:00"
                    
                return formatted_date
            except:
                pass
    except:
        pass
    
    return datetime.now().strftime("%d.%m.%Y %H:%M")

# Yönetici için güvenlik kontrolü olmayan dosya indirme
@app.route('/admin/download/<path:file_path>')
@admin_required
def admin_download_file(file_path):
    directory, filename = file_path.split('/', 1)
    return send_from_directory(os.path.join('static', directory), filename, as_attachment=True)
# Çıkış yap
@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız!', 'success')
    return redirect(url_for('login'))

@app.route('/download/<path:file_path>')
@login_required
def download_file(file_path):
    directory, filename = file_path.split('/', 1)
    
    # Güvenlik kontrolü: Kullanıcı sadece kendi dosyalarını indirebilmeli
    username = session.get('username', '')
    
    # Admin kullanıcıları için erişim kısıtlamasını kaldır
    if session.get('role') == 'admin':
        pass  # Admin kullanıcıları tüm dosyalara erişebilir
    elif username not in filename:
        flash('Bu dosyaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('index'))
    
    # Dosya uzantısını kontrol et
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    # MIME türünü ayarla
    mime_type = None
    if file_extension == 'csv':
        mime_type = 'text/csv'
    elif file_extension == 'xlsx':
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file_extension == 'xls':
        mime_type = 'application/vnd.ms-excel'
    
    # Dosyayı indir
    if mime_type:
        return send_from_directory(
            os.path.join('static', directory), 
            filename, 
            as_attachment=True,
            mimetype=mime_type
        )
    else:
        return send_from_directory(os.path.join('static', directory), filename, as_attachment=True)

@app.route('/my-operations')
@login_required
def my_operations():
    """Kullanıcının kendi işlemlerini görüntüleme sayfası"""
    operations = get_user_operations(session['user_id'])
    return render_template('my_operations.html', operations=operations)

def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = socket.gethostbyname(socket.gethostname())
    return ip

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"📡 Uygulama yerel ağda şu adresten erişilebilir: http://{local_ip}:5000\n")
    serve(app, host='0.0.0.0', port=5000)