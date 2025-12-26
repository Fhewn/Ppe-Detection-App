# PPE Detection Sistemi - Arch Linux VPS Kurulum Rehberi

## 🎯 Hedef
fhewn.com domaininde PPE Detection sisteminin dashboard.html'ini çalıştırmak

## 📋 Gereksinimler
- Arch Linux VPS (IP: 72.62.60.125)
- Domain: fhewn.com
- Python 3.8+
- Nginx (Web Server)
- SSL Sertifikası

## 🚀 Kurulum Adımları

### 1. VPS'e Bağlanma
```bash
ssh root@72.62.60.125
```

### 2. Sistem Güncellemesi (Arch Linux)
```bash
pacman -Syu --noconfirm
```

### 3. Gerekli Paketleri Kurma (Arch Linux)
```bash
# Python ve pip
pacman -S python python-pip python-virtualenv --noconfirm

# Nginx
pacman -S nginx --noconfirm

# Git
pacman -S git --noconfirm

# SSL için Certbot
pacman -S certbot certbot-nginx --noconfirm

# Sistem araçları
pacman -S htop curl wget unzip base-devel --noconfirm

# OpenCV için gerekli kütüphaneler
pacman -S opencv python-opencv --noconfirm
```

### 4. Proje Dosyalarını Yükleme
```bash
# Proje klasörü oluştur
mkdir -p /var/www/fhewn.com
cd /var/www/fhewn.com

# Projeyi klonla veya dosyaları yükle
# (Bu adımda backend klasörünü yükleyeceğiz)
```

### 5. Python Sanal Ortamı
```bash
cd /var/www/fhewn.com
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 6. Python Bağımlılıklarını Kurma
```bash
# requirements.txt'den kurulum
pip install Flask==3.0.0
pip install Flask-CORS==4.0.0
pip install Pillow==10.1.0
pip install numpy==1.26.2
pip install opencv-python==4.8.1.78
pip install gunicorn==21.2.0
pip install python-dotenv==1.0.0

# Face recognition (opsiyonel - uzun sürer)
# pip install cmake dlib face_recognition
```

### 7. Nginx Konfigürasyonu
```bash
# Nginx config dosyası oluştur
nano /etc/nginx/sites-available/fhewn.com
```

**Nginx Config İçeriği:**
```nginx
server {
    listen 80;
    server_name fhewn.com www.fhewn.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # File upload için
        client_max_body_size 50M;
    }

    # Static files
    location /static/ {
        alias /var/www/fhewn.com/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # User photos
    location /users/ {
        alias /var/www/fhewn.com/backend/users/;
        expires 1y;
    }

    # Inspection images
    location /inspections/ {
        alias /var/www/fhewn.com/backend/inspections/;
        expires 1y;
    }
}
```

### 8. Nginx'i Aktifleştirme
```bash
# Site'ı aktifleştir
ln -s /etc/nginx/sites-available/fhewn.com /etc/nginx/sites-enabled/

# Default site'ı kaldır
rm /etc/nginx/sites-enabled/default

# Nginx'i test et
nginx -t

# Nginx'i yeniden başlat
systemctl restart nginx
systemctl enable nginx
```

### 9. SSL Sertifikası (Let's Encrypt)
```bash
certbot --nginx -d fhewn.com -d www.fhewn.com
```

### 10. HTTP Kullanıcısı Oluşturma (Arch Linux)
```bash
# Arch Linux'ta nginx http kullanıcısı ile çalışır
useradd -r -s /bin/false http 2>/dev/null || true
```

### 11. Systemd Service Oluşturma
```bash
nano /etc/systemd/system/ppe-detection.service
```

**Service İçeriği (Arch Linux için):**
```ini
[Unit]
Description=PPE Detection Flask App
After=network.target

[Service]
User=http
Group=http
WorkingDirectory=/var/www/fhewn.com/backend
Environment=PATH=/var/www/fhewn.com/venv/bin
ExecStart=/var/www/fhewn.com/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 12. Service'i Başlatma
```bash
systemctl daemon-reload
systemctl start ppe-detection
systemctl enable ppe-detection
systemctl status ppe-detection
```

### 13. Firewall Ayarları (Arch Linux - iptables)
```bash
# Arch Linux'ta ufw yerine iptables kullanılır
pacman -S iptables --noconfirm

# Temel firewall kuralları
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -j DROP

# Kuralları kaydet
iptables-save > /etc/iptables/iptables.rules
systemctl enable iptables
systemctl start iptables
```

### 14. Dosya İzinleri (Arch Linux)
```bash
chown -R http:http /var/www/fhewn.com
chmod -R 755 /var/www/fhewn.com
```

## 🔧 Önemli Dosyalar

### Production App.py Değişiklikleri
```python
# app.py'nin son satırını değiştir:
if __name__ == '__main__':
    print("🚀 KKE Detection API başlatılıyor...")
    print("📡 URL: http://0.0.0.0:5001")
    print("📊 Dashboard: http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)  # Production'da debug=False
```

### Environment Variables (.env)
```bash
# /var/www/fhewn.com/backend/.env
FLASK_ENV=production
DATABASE_PATH=/var/www/fhewn.com/backend/ppe_inspections.db
UPLOAD_FOLDER=/var/www/fhewn.com/backend/uploads
```

## 📊 Monitoring ve Loglar

### Logları İzleme
```bash
# Flask app logları
journalctl -u ppe-detection -f

# Nginx logları
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Sistem Durumu
```bash
systemctl status ppe-detection
systemctl status nginx
```

## 🔄 Güncelleme ve Bakım

### Uygulamayı Yeniden Başlatma
```bash
systemctl restart ppe-detection
systemctl restart nginx
```

### Veritabanı Yedekleme
```bash
# Otomatik yedekleme scripti
nano /var/www/fhewn.com/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /var/www/fhewn.com/backend/ppe_inspections.db /var/www/fhewn.com/backups/db_backup_$DATE.db
find /var/www/fhewn.com/backups/ -name "*.db" -mtime +7 -delete
```

## 🌐 Domain Ayarları

Hostinger DNS panelinde:
- A Record: fhewn.com → VPS IP
- A Record: www.fhewn.com → VPS IP

## ✅ Test Etme

1. http://fhewn.com → Dashboard açılmalı
2. https://fhewn.com → SSL ile güvenli erişim
3. API endpoints test edilmeli

## 🚨 Güvenlik

1. SSH key-based authentication
2. Fail2ban kurulumu
3. Regular security updates
4. Database backup strategy
5. Monitoring setup

## 📱 Mobile App Bağlantısı

Flutter uygulamasında API URL'ini güncelle:
```dart
const String API_BASE_URL = 'https://fhewn.com';
```