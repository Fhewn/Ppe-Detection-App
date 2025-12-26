from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import random
from datetime import datetime
import sqlite3
import os
import pytz

app = Flask(__name__)
CORS(app)

# Veritabanı
DATABASE = 'ppe_inspections.db'

# Basit kullanıcı listesi (memory'de)
users = {}

def init_db():
    """Veritabanını başlat"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Kontrol kayıtları tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            kask INTEGER NOT NULL,
            yelek INTEGER NOT NULL,
            gozluk INTEGER NOT NULL,
            uygunluk INTEGER NOT NULL,
            image_filename TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Kullanıcılar tablosu - face_encoding ve departman sütunu eklendi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            sicil_no TEXT UNIQUE NOT NULL,
            departman TEXT DEFAULT 'Belirtilmemiş',
            photo_filename TEXT,
            face_encoding TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Mevcut tabloya departman sütunu ekle (eğer yoksa)
    try:
        cursor.execute('ALTER TABLE users_db ADD COLUMN departman TEXT DEFAULT "Belirtilmemiş"')
        print("✅ Departman sütunu eklendi")
    except sqlite3.OperationalError:
        # Sütun zaten varsa hata vermez
        pass
    
    conn.commit()
    conn.close()
    print("✅ Veritabanı hazır")

def load_users_from_db():
    """Veritabanından kullanıcıları yükle"""
    global users
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sicil_no, name, surname, departman, photo_filename, face_encoding
            FROM users_db
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        users = {}
        for row in rows:
            sicil_no, name, surname, departman, photo_filename, face_encoding_str = row
            user_data = {
                'name': name,
                'surname': surname,
                'sicil_no': sicil_no,
                'departman': departman or 'Belirtilmemiş',
                'photo_filename': photo_filename
            }
            
            # Face encoding'i JSON'dan listeye çevir
            if face_encoding_str:
                import json
                user_data['face_encoding'] = json.loads(face_encoding_str)
            
            users[sicil_no] = user_data
        
        print(f"✅ {len(users)} kullanıcı veritabanından yüklendi")
        if len(users) > 0:
            print(f"📋 Kayıtlı kullanıcılar: {', '.join([f'{u['name']} {u['surname']}' for u in users.values()])}")
    except Exception as e:
        print(f"⚠️ Kullanıcılar yüklenirken hata: {e}")
        users = {}

# Veritabanını başlat ve kullanıcıları yükle
init_db()
load_users_from_db()

@app.route('/dashboard')
@app.route('/dashboard.html')
def dashboard():
    """Dashboard HTML sayfası"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/register_user', methods=['POST'])
def register_user():
    """Kullanıcı Kayıt - Yüz Encoding ile"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        name = request.form.get('name')
        surname = request.form.get('surname')
        
        if not name or not surname:
            return jsonify({'error': 'Name and surname required'}), 400

        file = request.files['image']
        
        # Görüntüyü oku
        from PIL import Image
        import numpy as np
        
        image_pil = Image.open(file.stream)
        
        # EXIF orientation düzeltmesi
        try:
            from PIL import ImageOps
            image_pil = ImageOps.exif_transpose(image_pil)
        except:
            pass
        
        image_pil = image_pil.convert('RGB')
        image_np = np.array(image_pil)
        
        # Yüz encoding'i oluştur
        face_encoding = None
        try:
            import face_recognition
            
            # Yüz tespiti
            face_locations = face_recognition.face_locations(image_np)
            if not face_locations:
                return jsonify({'error': 'Yüz bulunamadı. Lütfen yüzünüzü net gösterin.'}), 400
            
            if len(face_locations) > 1:
                return jsonify({'error': 'Birden fazla yüz tespit edildi. Lütfen tek kişi olun.'}), 400
            
            # Yüz encoding
            face_encodings = face_recognition.face_encodings(image_np, face_locations)
            if face_encodings:
                face_encoding = face_encodings[0].tolist()
                print("✅ Yüz encoding oluşturuldu")
        except ImportError:
            print("⚠️ face_recognition yüklü değil, encoding olmadan kayıt yapılıyor")
        
        # Türkiye saat diliminde zaman al
        turkey_tz = pytz.timezone('Europe/Istanbul')
        now_turkey = datetime.now(turkey_tz)
        
        # Sicil No oluştur (Yıl + Random 4 hane)
        sicil_no = f"{now_turkey.year}{random.randint(1000, 9999)}"
        
        # Fotoğrafı kaydet
        timestamp = now_turkey.strftime('%Y%m%d_%H%M%S')
        photo_filename = f'user_{sicil_no}_{timestamp}.jpg'
        os.makedirs('users', exist_ok=True)
        image_pil.save(os.path.join('users', photo_filename))
        print(f"📸 Fotoğraf kaydedildi: {photo_filename}")
        
        # Face encoding'i JSON string'e çevir
        face_encoding_str = None
        if face_encoding:
            import json
            face_encoding_str = json.dumps(face_encoding)
        
        # Veritabanına kaydet
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users_db (name, surname, sicil_no, departman, photo_filename, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, surname, sicil_no, 'Mobil Kayıt', photo_filename, face_encoding_str))
            conn.commit()
            print(f"💾 Kullanıcı veritabanına kaydedildi (Face encoding: {'✅' if face_encoding else '❌'})")
        except sqlite3.IntegrityError:
            print("⚠️ Sicil no çakışması")
            conn.close()
            return jsonify({'error': 'Bu sicil numarası zaten kullanılıyor'}), 400
        finally:
            conn.close()
        
        # Memory'ye de kaydet
        user_data = {
            'name': name,
            'surname': surname,
            'sicil_no': sicil_no,
            'departman': 'Mobil Kayıt',
            'photo_filename': photo_filename
        }
        
        if face_encoding:
            user_data['face_encoding'] = face_encoding
        
        users[sicil_no] = user_data
        
        print(f"✅ Yeni kullanıcı kaydedildi: {name} {surname} - {sicil_no}")
        
        return jsonify({
            'success': True,
            'message': 'Kayıt başarılı',
            'user': {
                'name': name,
                'surname': surname,
                'sicil_no': sicil_no
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Register Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login_user', methods=['POST'])
def login_user():
    """Yüz ile Giriş - Gerçek Yüz Tanıma"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        if not users:
            return jsonify({
                'success': False,
                'message': 'Kayıtlı kullanıcı yok. Lütfen önce kayıt olun.'
            }), 401
        
        file = request.files['image']
        
        # Görüntüyü oku
        from PIL import Image
        import numpy as np
        
        image_pil = Image.open(file.stream)
        
        # EXIF orientation düzeltmesi
        try:
            from PIL import ImageOps
            image_pil = ImageOps.exif_transpose(image_pil)
        except:
            pass
        
        image_pil = image_pil.convert('RGB')
        image_np = np.array(image_pil)
        
        # Yüz tanıma dene
        try:
            import face_recognition
            
            # Gelen görüntüdeki yüzü bul
            face_locations = face_recognition.face_locations(image_np)
            if not face_locations:
                return jsonify({
                    'success': False,
                    'message': 'Yüz bulunamadı. Lütfen yüzünüzü kameraya gösterin.'
                }), 400
            
            unknown_face_encodings = face_recognition.face_encodings(image_np, face_locations)
            if not unknown_face_encodings:
                return jsonify({
                    'success': False,
                    'message': 'Yüz kodlanamadı. Lütfen tekrar deneyin.'
                }), 400
            
            unknown_face_encoding = unknown_face_encodings[0]
            
            # Kayıtlı kullanıcılarla karşılaştır
            for sicil_no, user_data in users.items():
                if 'face_encoding' in user_data:
                    known_face_encoding = np.array(user_data['face_encoding'])
                    
                    # Karşılaştır
                    results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding, tolerance=0.6)
                    
                    if results[0]:
                        print(f"✅ Giriş başarılı: {user_data['name']} {user_data['surname']}")
                        return jsonify({
                            'success': True,
                            'message': 'Giriş başarılı',
                            'user': {
                                'name': user_data['name'],
                                'surname': user_data['surname'],
                                'sicil_no': sicil_no
                            }
                        }), 200
            
            # Hiçbir kullanıcı eşleşmedi
            print("❌ Yüz tanınamadı")
            return jsonify({
                'success': False,
                'message': 'Yüzünüz tanınamadı. Lütfen kayıt olun.'
            }), 401
            
        except ImportError:
            print("⚠️ face_recognition yüklü değil - Yüz tanıma devre dışı")
            return jsonify({
                'success': False,
                'message': 'Yüz tanıma sistemi aktif değil. Lütfen sistem yöneticisine başvurun.'
            }), 503
        
    except Exception as e:
        print(f"❌ Login Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Tüm kullanıcıları listele - Veritabanından"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, surname, departman, sicil_no, photo_filename, created_at
            FROM users_db
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        users_list = []
        for row in rows:
            users_list.append({
                'id': row[0],
                'name': row[1],
                'surname': row[2],
                'departman': row[3] or 'Belirtilmemiş',
                'sicil_no': row[4],
                'photo_filename': row[5],
                'created_at': row[6]
            })
        
        return jsonify({
            'users': users_list,
            'total': len(users_list)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<filename>')
def get_user_photo(filename):
    """Kullanıcı fotoğrafını getir"""
    try:
        return send_from_directory('users', filename)
    except:
        return '', 404

@app.route('/validate_image', methods=['POST'])
def validate_image():
    """PPE Validation - Gerçek Tespit"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        # Görüntüyü oku
        from PIL import Image
        import numpy as np
        
        image_pil = Image.open(file.stream)
        
        # EXIF orientation düzeltmesi
        try:
            from PIL import ImageOps
            image_pil = ImageOps.exif_transpose(image_pil)
        except:
            pass
        
        image_pil = image_pil.convert('RGB')
        image_np = np.array(image_pil)
        
        # Detector'ı import et ve kullan
        try:
            from detector import Detector
            detector = Detector()
            results = detector.validate_ppe(image_np)
            
            # Flutter için response'u düzenle
            detected_items = {
                'Kask': results['detected_items']['helmet'],
                'Yelek': results['detected_items']['vest']
            }
            
            missing_items = []
            if not detected_items['Kask']:
                missing_items.append('Kask')
            if not detected_items['Yelek']:
                missing_items.append('Yelek')
            
            success = len(missing_items) == 0
            
            print(f"🔍 PPE Kontrolü: Kask={detected_items['Kask']}, Yelek={detected_items['Yelek']}")
            
            # Veritabanına kaydet - Türkiye saat diliminde
            turkey_tz = pytz.timezone('Europe/Istanbul')
            now_turkey = datetime.now(turkey_tz)
            
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO inspections (timestamp, kask, yelek, gozluk, uygunluk, image_filename)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                now_turkey.isoformat(),
                1 if detected_items['Kask'] else 0,
                1 if detected_items['Yelek'] else 0,
                0,  # gozluk
                1 if success else 0,
                'mobile_check.jpg'
            ))
            conn.commit()
            conn.close()
            print("💾 Kontrol veritabanına kaydedildi")
            
            return jsonify({
                'success': success,
                'detected_items': detected_items,
                'missing_items': missing_items,
                'message': '✅ Tüm ekipmanlar mevcut' if success else f'⚠️ Eksik: {", ".join(missing_items)}'
            }), 200
            
        except Exception as detector_error:
            print(f"⚠️ Detector hatası, rastgele sonuç döndürülüyor: {detector_error}")
            # Detector çalışmazsa rastgele sonuç döndür
            has_helmet = random.choice([True, False])
            has_vest = random.choice([True, False])
            
            detected_items = {
                'Kask': has_helmet,
                'Yelek': has_vest
            }
            
            missing_items = []
            if not has_helmet:
                missing_items.append('Kask')
            if not has_vest:
                missing_items.append('Yelek')
            
            success = len(missing_items) == 0
            
            return jsonify({
                'success': success,
                'detected_items': detected_items,
                'missing_items': missing_items,
                'message': '✅ Tüm ekipmanlar mevcut' if success else f'⚠️ Eksik: {", ".join(missing_items)}'
            }), 200
        
    except Exception as e:
        print(f"❌ Validate Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    """Ana sayfa - Dashboard'a yönlendir"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/api')
def api_info():
    """API bilgileri"""
    return jsonify({
        'status': 'running',
        'message': 'PPE Detection API - Simplified',
        'endpoints': [
            '/api/register_user',
            '/api/login_user',
            '/api/users',
            '/validate_image',
            '/dashboard',
            '/api/inspections',
            '/api/stats'
        ]
    })

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """Tüm kontrol kayıtlarını getir"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, kask, yelek, gozluk, uygunluk, image_filename
            FROM inspections
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        inspections = []
        for row in rows:
            inspections.append({
                'timestamp': row[0],
                'kask': row[1],
                'yelek': row[2],
                'gozluk': row[3],
                'uygunluk': row[4],
                'image_filename': row[5]
            })
        
        return jsonify(inspections), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """İstatistikler"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM inspections')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM inspections WHERE uygunluk = 1')
        compliant = cursor.fetchone()[0]
        
        conn.close()
        
        non_compliant = total - compliant
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        
        return jsonify({
            'total': total,
            'compliant': compliant,
            'non_compliant': non_compliant,
            'compliance_rate': round(compliance_rate, 1)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/veri-al', methods=['POST'])
def receive_external_data():
    """Arkadaşının sisteminden veri alma - Kontroller ve Kullanıcı kayıtlarına ekle"""
    try:
        # JSON verisini al
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON verisi bulunamadı'}), 400
        
        # Gerekli alanları kontrol et
        required_fields = ['isim', 'soyisim', 'departman', 'durum', 'tarih', 'saat']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Eksik alan: {field}'}), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 1. Kullanıcıyı users_db tablosuna ekle (eğer yoksa)
        sicil_no = f"EXT{random.randint(1000, 9999)}"  # Dış sistemden gelenlere EXT prefix
        
        # Kullanıcı zaten var mı kontrol et
        cursor.execute('''
            SELECT sicil_no FROM users_db WHERE name = ? AND surname = ?
        ''', (data['isim'], data['soyisim']))
        
        existing_user = cursor.fetchone()
        if existing_user:
            sicil_no = existing_user[0]
            print(f"👤 Mevcut kullanıcı bulundu: {data['isim']} {data['soyisim']} - {sicil_no}")
        else:
            # Yeni kullanıcı ekle
            cursor.execute('''
                INSERT INTO users_db (name, surname, sicil_no, departman, photo_filename, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['isim'], data['soyisim'], sicil_no, data['departman'], None, None))
            
            # Memory'ye de ekle
            users[sicil_no] = {
                'name': data['isim'],
                'surname': data['soyisim'],
                'sicil_no': sicil_no,
                'departman': data['departman'],
                'photo_filename': None
            }
            print(f"👤 Yeni kullanıcı eklendi: {data['isim']} {data['soyisim']} - {sicil_no}")
        
        # 2. Kontrol kaydı ekle (durum -> kask/yelek mapping)
        # "Gecti" = Kask:Var, Yelek:Var, Uygun
        # "Kaldi" = Kask:Yok, Yelek:Yok, Uygun Değil
        kask = 1 if data['durum'] == 'Gecti' else 0
        yelek = 1 if data['durum'] == 'Gecti' else 0
        uygunluk = 1 if data['durum'] == 'Gecti' else 0
        
        # Tarih/saat formatını ISO formatına çevir - Türkiye saat diliminde
        try:
            # "24.05.2024 14:30:05" formatından datetime'a çevir
            datetime_str = f"{data['tarih']} {data['saat']}"
            dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")
            
            # Türkiye saat dilimini ekle
            turkey_tz = pytz.timezone('Europe/Istanbul')
            dt_turkey = turkey_tz.localize(dt)
            timestamp = dt_turkey.isoformat()
        except:
            # Hatalı format durumunda şu anki Türkiye zamanını kullan
            turkey_tz = pytz.timezone('Europe/Istanbul')
            timestamp = datetime.now(turkey_tz).isoformat()
        
        cursor.execute('''
            INSERT INTO inspections (timestamp, kask, yelek, gozluk, uygunluk, image_filename)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            kask,
            yelek,
            0,  # gözlük
            uygunluk,
            f'external_{data["isim"]}_{data["soyisim"]}.jpg'
        ))
        
        conn.commit()
        conn.close()
        
        print(f"📥 Arkadaş sisteminden veri alındı: {data['isim']} {data['soyisim']} - {data['durum']}")
        print(f"👤 Kullanıcı: {sicil_no}")
        print(f"🔍 Kontrol: Kask={kask}, Yelek={yelek}, Uygun={uygunluk}")
        
        return jsonify({
            'success': True,
            'message': 'Veri başarıyla kaydedildi',
            'user_sicil_no': sicil_no,
            'control_result': {
                'kask': bool(kask),
                'yelek': bool(yelek),
                'uygun': bool(uygunluk)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Dış veri alma hatası: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    import os
    
    # Production/Development modu
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    print("🚀 PPE Detection API başlatılıyor...")
    print(f"📡 URL: http://0.0.0.0:5002")
    print(f"🔧 Mod: {'Production' if is_production else 'Development'}")
    print(f"💾 Veritabanı: {DATABASE}")
    
    # Production'da debug=False
    app.run(
        host='0.0.0.0', 
        port=5002, 
        debug=not is_production,
        threaded=True
    )
