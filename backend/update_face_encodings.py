#!/usr/bin/env python3
"""
Mevcut kullanıcıların fotoğraflarından face encoding oluşturur
"""

import sqlite3
import os
import json
from PIL import Image
import numpy as np

DATABASE = 'ppe_inspections.db'

def update_face_encodings():
    """Mevcut kullanıcılar için face encoding oluştur"""
    
    try:
        import face_recognition
        print("✅ face_recognition modülü yüklü")
    except ImportError:
        print("❌ face_recognition modülü yüklü değil!")
        print("Yüklemek için: pip install face_recognition")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Face encoding'i olmayan kullanıcıları bul
    cursor.execute('''
        SELECT id, sicil_no, name, surname, photo_filename
        FROM users_db
        WHERE face_encoding IS NULL OR face_encoding = ''
    ''')
    
    users = cursor.fetchall()
    
    if not users:
        print("✅ Tüm kullanıcıların face encoding'i mevcut")
        conn.close()
        return
    
    print(f"📋 {len(users)} kullanıcı için face encoding oluşturulacak...")
    
    updated = 0
    failed = 0
    
    for user_id, sicil_no, name, surname, photo_filename in users:
        print(f"\n🔄 İşleniyor: {name} {surname} ({sicil_no})")
        
        if not photo_filename:
            print(f"  ⚠️ Fotoğraf dosyası yok")
            failed += 1
            continue
        
        photo_path = os.path.join('users', photo_filename)
        
        if not os.path.exists(photo_path):
            print(f"  ⚠️ Fotoğraf bulunamadı: {photo_path}")
            failed += 1
            continue
        
        try:
            # Fotoğrafı yükle
            image = Image.open(photo_path)
            image = image.convert('RGB')
            image_np = np.array(image)
            
            # Yüz tespiti
            face_locations = face_recognition.face_locations(image_np)
            
            if not face_locations:
                print(f"  ❌ Yüz bulunamadı")
                failed += 1
                continue
            
            if len(face_locations) > 1:
                print(f"  ⚠️ Birden fazla yüz tespit edildi, ilki kullanılacak")
            
            # Face encoding oluştur
            face_encodings = face_recognition.face_encodings(image_np, face_locations)
            
            if not face_encodings:
                print(f"  ❌ Face encoding oluşturulamadı")
                failed += 1
                continue
            
            face_encoding = face_encodings[0].tolist()
            face_encoding_str = json.dumps(face_encoding)
            
            # Veritabanını güncelle
            cursor.execute('''
                UPDATE users_db
                SET face_encoding = ?
                WHERE id = ?
            ''', (face_encoding_str, user_id))
            
            conn.commit()
            
            print(f"  ✅ Face encoding oluşturuldu ve kaydedildi")
            updated += 1
            
        except Exception as e:
            print(f"  ❌ Hata: {e}")
            failed += 1
    
    conn.close()
    
    print("\n" + "="*50)
    print(f"✅ Başarılı: {updated}")
    print(f"❌ Başarısız: {failed}")
    print(f"📊 Toplam: {len(users)}")
    print("="*50)

if __name__ == '__main__':
    print("🚀 Face Encoding Güncelleme Scripti")
    print("="*50)
    update_face_encodings()
