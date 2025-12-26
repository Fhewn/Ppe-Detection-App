from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from detector import Detector
from PIL import Image
import numpy as np
import sqlite3
from datetime import datetime
import os
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ Face recognition modülü bulunamadı. Kullanıcı kayıt/giriş özellikleri devre dışı.")
import json

app = Flask(__name__)
CORS(app)

# Veritabanı
DATABASE = 'ppe_inspections.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            sicil_no TEXT UNIQUE NOT NULL,
            face_encoding TEXT NOT NULL,
            photo_filename TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Veritabanı hazır")

init_db()
detector = Detector()

@app.route('/')
def dashboard():
    """Admin Dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/inspections/<filename>')
def get_inspection_image(filename):
    """Kontrol görüntüsünü getir"""
    try:
        return send_from_directory('inspections', filename)
    except:
        return '', 404

@app.route('/validate_image', methods=['POST'])
def validate_image():
    """Flutter uygulaması için PPE doğrulama"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        image_pil = Image.open(file.stream)
        
        # iPhone EXIF orientation düzeltmesi
        try:
            from PIL import ImageOps
            image_pil = ImageOps.exif_transpose(image_pil)
            print("📱 EXIF orientation düzeltildi")
        except Exception as e:
            print(f"⚠️ EXIF düzeltme hatası (normal): {e}")
        
        image_pil = image_pil.convert('RGB')
        image_rgb = np.array(image_pil)
        
        height, width = image_rgb.shape[:2]
        print(f"📸 Image received: {width}x{height}")
        
        # Görüntü çok küçükse uyar
        if width < 640 or height < 640:
            print(f"⚠️ UYARI: Görüntü çok küçük! Tespit kalitesi düşük olabilir.")
        
        results = detector.validate_ppe(image_rgb)
        
        # Görüntüyü kaydet (timestamp ile)
        import cv2
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f'inspection_{timestamp}.jpg'
        image_path = os.path.join('backend', 'inspections', image_filename)
        
        # inspections klasörünü oluştur
        os.makedirs(os.path.join('backend', 'inspections'), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
        print(f"💾 Görüntü kaydedildi: {image_path}")
        
        # Flutter için response'u düzenle - Sadece Kask ve Yelek
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
        
        response = {
            'success': success,
            'detected_items': detected_items,
            'missing_items': missing_items,
            'message': '✅ Ekipman Tam' if success else f'⚠️ Eksik: {", ".join(missing_items)}'
        }
        
        # Veritabanına kaydet
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inspections (timestamp, kask, yelek, gozluk, uygunluk, image_filename)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            1 if detected_items['Kask'] else 0,
            1 if detected_items['Yelek'] else 0,
            0,  # gozluk - artık kullanılmıyor
            1 if success else 0,
            image_filename
        ))
        conn.commit()
        conn.close()
        
        print(f"✅ Response: {response}")
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """Tüm kayıtları getir"""
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

@app.route('/api/delete_inspection/<int:id>', methods=['DELETE'])
def delete_inspection(id):
    """Tek bir kaydı sil"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inspections WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Kayıt silindi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_all', methods=['DELETE'])
def clear_all():
    """Tüm kayıtları sil"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inspections')
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Tüm kayıtlar silindi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inspections_with_id', methods=['GET'])
def get_inspections_with_id():
    """ID'li kayıtları getir - Tarih/saat'e göre azalan sıralı"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, kask, yelek, gozluk, uygunluk
            FROM inspections
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        inspections = []
        for row in rows:
            inspections.append({
                'id': row[0],
                'timestamp': row[1],
                'kask': row[2],
                'yelek': row[3],
                'gozluk': row[4],
                'uygunluk': row[5]
            })
        
        return jsonify(inspections), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_inspection', methods=['POST'])
def add_inspection():
    """Yeni kayıt ekle"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inspections (timestamp, kask, yelek, gozluk, uygunluk, image_filename)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['kask'],
            data['yelek'],
            0,  # gozluk
            data['uygunluk'],
            'manual_entry.jpg'
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Kayıt eklendi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_inspection/<int:id>', methods=['PUT'])
def update_inspection(id):
    """Kaydı güncelle"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inspections 
            SET timestamp = ?, kask = ?, yelek = ?, uygunluk = ?
            WHERE id = ?
        ''', (
            data['timestamp'],
            data['kask'],
            data['yelek'],
            data['uygunluk'],
            id
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Kayıt güncellendi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_test_data', methods=['POST'])
def add_test_data():
    """Test verileri ekle"""
    try:
        import random
        from datetime import timedelta
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 10 adet test verisi ekle
        for i in range(10):
            # Rastgele tarih (son 30 gün)
            random_date = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            # Rastgele ekipman durumu
            kask = random.choice([0, 1])
            yelek = random.choice([0, 1])
            uygunluk = 1 if (kask and yelek) else 0
            
            cursor.execute('''
                INSERT INTO inspections (timestamp, kask, yelek, gozluk, uygunluk, image_filename)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                random_date.isoformat(),
                kask, yelek, 0, uygunluk,
                f'test_image_{i+1}.jpg'
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '10 test verisi eklendi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup', methods=['GET'])
def backup_database():
    """Veritabanını JSON olarak yedekle"""
    try:
        import json
        from flask import Response
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inspections ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        # Kolon isimleri
        columns = ['id', 'timestamp', 'kask', 'yelek', 'gozluk', 'uygunluk', 'image_filename', 'created_at']
        
        # JSON formatına çevir
        backup_data = []
        for row in rows:
            record = {}
            for i, col in enumerate(columns):
                if i < len(row):
                    record[col] = row[i]
            backup_data.append(record)
        
        backup = {
            'export_date': datetime.now().isoformat(),
            'total_records': len(backup_data),
            'data': backup_data
        }
        
        response = Response(
            json.dumps(backup, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=ppe_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        )
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/register_user', methods=['POST'])
def register_user():
    """Kullanıcı Kayıt"""
    if not FACE_RECOGNITION_AVAILABLE:
        return jsonify({'error': 'Face recognition modülü mevcut değil'}), 500
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        name = request.form.get('name')
        surname = request.form.get('surname')
        
        if not name or not surname:
            return jsonify({'error': 'Name and surname required'}), 400

        file = request.files['image']
        image_pil = Image.open(file.stream)
        
        # EXIF düzeltme
        try:
            from PIL import ImageOps
            image_pil = ImageOps.exif_transpose(image_pil)
        except:
            pass
            
        image_pil = image_pil.convert('RGB')
        image_np = np.array(image_pil)
        
        # Yüz tespiti ve encoding
        face_locations = face_recognition.face_locations(image_np)
        if not face_locations:
            return jsonify({'error': 'Yüz bulunamadı'}), 400
            
        if len(face_locations) > 1:
            return jsonify({'error': 'Birden fazla yüz tespit edildi'}), 400
            
        face_encodings = face_recognition.face_encodings(image_np, face_locations)
        if not face_encodings:
            return jsonify({'error': 'Yüz kodlanamadı'}), 400
            
        face_encoding = face_encodings[0].tolist()
        
        # Sicil No oluştur (Yıl + Random 4 hane)
        import random
        sicil_no = f"{datetime.now().year}{random.randint(1000, 9999)}"
        
        # Fotoğrafı kaydet
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        photo_filename = f'user_{sicil_no}_{timestamp}.jpg'
        os.makedirs(os.path.join('backend', 'users'), exist_ok=True)
        image_pil.save(os.path.join('backend', 'users', photo_filename))
        
        # Veritabanına kaydet
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (name, surname, sicil_no, face_encoding, photo_filename)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, surname, sicil_no, json.dumps(face_encoding), photo_filename))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Sicil no çakışması, tekrar deneyin'}), 500
        finally:
            conn.close()
            
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
        print(f"Register Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login_user', methods=['POST'])
def login_user():
    """Yüz ile Giriş"""
    if not FACE_RECOGNITION_AVAILABLE:
        return jsonify({'error': 'Face recognition modülü mevcut değil'}), 500
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        image_pil = Image.open(file.stream)
        
        # EXIF düzeltme
        try:
            from PIL import ImageOps
            image_pil = ImageOps.exif_transpose(image_pil)
        except:
            pass
            
        image_pil = image_pil.convert('RGB')
        image_np = np.array(image_pil)
        
        # Gelen görüntüdeki yüzü bul
        face_locations = face_recognition.face_locations(image_np)
        if not face_locations:
            return jsonify({'error': 'Yüz bulunamadı'}), 400
            
        unknown_face_encoding = face_recognition.face_encodings(image_np, face_locations)[0]
        
        # Veritabanındaki kullanıcıları çek
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, surname, sicil_no, face_encoding FROM users')
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            user_id, name, surname, sicil_no, encoding_json = user
            known_face_encoding = np.array(json.loads(encoding_json))
            
            # Karşılaştır
            results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding, tolerance=0.6)
            
            if results[0]:
                return jsonify({
                    'success': True,
                    'message': 'Giriş başarılı',
                    'user': {
                        'name': name,
                        'surname': surname,
                        'sicil_no': sicil_no
                    }
                }), 200
                
        return jsonify({'success': False, 'message': 'Kullanıcı tanınamadı'}), 401
        
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 KKE Detection API başlatılıyor...")
    print("📡 URL: http://0.0.0.0:5001")
    print("📊 Dashboard: http://0.0.0.0:5001")
    # Production için debug=False
    import os
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)
