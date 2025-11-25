from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from detector import Detector
from PIL import Image
import numpy as np
import sqlite3
from datetime import datetime
import os

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

@app.route('/validate_image', methods=['POST'])
def validate_image():
    """Flutter uygulaması için PPE doğrulama"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        image_pil = Image.open(file.stream).convert('RGB')
        image_rgb = np.array(image_pil)
        
        print(f"📸 Image received: {image_rgb.shape}")
        
        # Debug: Save image for inspection
        import cv2
        cv2.imwrite('backend/last_test_image.jpg', cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
        print("💾 Test görüntüsü kaydedildi: backend/last_test_image.jpg")
        
        results = detector.validate_ppe(image_rgb)
        
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
            INSERT INTO inspections (timestamp, kask, yelek, gozluk, uygunluk)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            1 if detected_items['Kask'] else 0,
            1 if detected_items['Yelek'] else 0,
            0,  # gozluk - artık kullanılmıyor
            1 if success else 0
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
            SELECT timestamp, kask, yelek, gozluk, uygunluk
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
                'uygunluk': row[4]
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
    """ID'li kayıtları getir"""
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

if __name__ == '__main__':
    print("🚀 KKE Detection API başlatılıyor...")
    print("📡 URL: http://localhost:5001")
    print("📊 Dashboard: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
