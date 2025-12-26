# 🚀 VDS Kurulum Rehberi - PPE Detection App

Bu rehber, PPE Detection uygulamanızı bir VDS (Virtual Dedicated Server) üzerinde sürekli çalışır hale getirmeniz için hazırlanmıştır.

## 📋 İçindekiler
1. [VDS Gereksinimleri](#vds-gereksinimleri)
2. [Sunucu Kurulumu](#sunucu-kurulumu)
3. [Backend Kurulumu](#backend-kurulumu)
4. [Systemd Servisi Oluşturma](#systemd-servisi-oluşturma)
5. [Nginx Reverse Proxy](#nginx-reverse-proxy)
6. [SSL Sertifikası](#ssl-sertifikası)
7. [Mobil Uygulama Güncelleme](#mobil-uygulama-güncelleme)

---

## 🖥️ VDS Gereksinimleri

### Minimum Özellikler:
- **İşletim Sistemi:** Ubuntu 22.04 LTS (önerilen)
- **RAM:** 2 GB (4 GB önerilen)
- **CPU:** 2 Core
- **Disk:** 20 GB SSD
- **Bant Genişliği:** Sınırsız veya yüksek

### Önerilen VDS Sağlayıcılar (Türkiye):
- DigitalOcean (5$/ay)
- Linode (5$/ay)
- Vultr (6$/ay)
- Turhost
- Natro
- Hostinger

---

## 🔧 Sunucu Kurulumu

### 1. VDS'e Bağlanma
```bash
ssh root@SUNUCU_IP_ADRESI
```

### 2. Sistem Güncellemesi
```bash
apt update && apt upgrade -y
```

### 3. Gerekli Paketleri Yükleme
```bash
# Python ve pip
apt install -y python3 python3-pip python3-venv

# Sistem kütüphaneleri
apt install -y build-essential cmake pkg-config
apt install -y libopencv-dev python3-opencv
apt install -y libboost-all-dev

# Git
apt install -y git

# Nginx (web sunucusu)
apt install -y nginx

# Certbot (SSL için)
apt install -y certbot python3-certbot-nginx

# Supervisor (process manager)
apt install -y supervisor
```

---

## 📦 Backend Kurulumu

### 1. Proje Klasörü Oluşturma
```bash
mkdir -p /var/www/ppe-detection
cd /var/www/ppe-detection
```

### 2. Projeyi Yükleme
```bash
# GitHub'dan (eğer repo varsa)
git clone https://github.com/KULLANICI_ADI/ppe-detection.git .

# Veya manuel olarak dosyaları yükleyin (SFTP ile)
```

### 3. Python Virtual Environment
```bash
cd /var/www/ppe-detection/backend
python3 -m venv venv
source venv/bin/activate
```

### 4. Python Paketlerini Yükleme
```bash
pip install --upgrade pip
pip install flask flask-cors pillow numpy

# Face recognition (opsiyonel - dlib derlemesi uzun sürebilir)
pip install face_recognition

# Eğer face_recognition yüklenemezse:
# pip install cmake
# pip install dlib
# pip install face_recognition
```

### 5. Veritabanı ve Klasörleri Oluşturma
```bash
mkdir -p /var/www/ppe-detection/backend/users
touch /var/www/ppe-detection/backend/ppe_inspections.db
chmod 755 /var/www/ppe-detection/backend/users
```

---

## ⚙️ Systemd Servisi Oluşturma

### 1. Servis Dosyası Oluşturma
```bash
nano /etc/systemd/system/ppe-backend.service
```

### 2. Servis İçeriği:
```ini
[Unit]
Description=PPE Detection Backend Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/ppe-detection/backend
Environment="PATH=/var/www/ppe-detection/backend/venv/bin"
ExecStart=/var/www/ppe-detection/backend/venv/bin/python3 app_simple.py

Restart=always
RestartSec=10

StandardOutput=append:/var/log/ppe-backend.log
StandardError=append:/var/log/ppe-backend-error.log

[Install]
WantedBy=multi-user.target
```

### 3. Servisi Başlatma
```bash
# Servisi etkinleştir
systemctl daemon-reload
systemctl enable ppe-backend.service
systemctl start ppe-backend.service

# Durumu kontrol et
systemctl status ppe-backend.service

# Logları görüntüle
journalctl -u ppe-backend.service -f
```

### 4. Servis Komutları
```bash
# Başlat
systemctl start ppe-backend.service

# Durdur
systemctl stop ppe-backend.service

# Yeniden başlat
systemctl restart ppe-backend.service

# Durum kontrolü
systemctl status ppe-backend.service

# Loglar
tail -f /var/log/ppe-backend.log
```

---

## 🌐 Nginx Reverse Proxy

### 1. Nginx Konfigürasyonu
```bash
nano /etc/nginx/sites-available/ppe-detection
```

### 2. Konfigürasyon İçeriği:
```nginx
server {
    listen 80;
    server_name DOMAIN_ADINIZ.com www.DOMAIN_ADINIZ.com;

    # Maksimum upload boyutu (fotoğraflar için)
    client_max_body_size 10M;

    # Backend API
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeout ayarları
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Kullanıcı fotoğrafları
    location /users/ {
        alias /var/www/ppe-detection/backend/users/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Dashboard static files
    location /dashboard {
        proxy_pass http://127.0.0.1:5001/dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Nginx'i Aktifleştirme
```bash
# Sembolik link oluştur
ln -s /etc/nginx/sites-available/ppe-detection /etc/nginx/sites-enabled/

# Default site'ı kaldır (opsiyonel)
rm /etc/nginx/sites-enabled/default

# Konfigürasyonu test et
nginx -t

# Nginx'i yeniden başlat
systemctl restart nginx
```

---

## 🔒 SSL Sertifikası (HTTPS)

### 1. Domain Ayarları
- Domain sağlayıcınızdan (GoDaddy, Namecheap, vb.) A kaydı ekleyin
- A kaydı: `@` → `SUNUCU_IP_ADRESI`
- A kaydı: `www` → `SUNUCU_IP_ADRESI`

### 2. Let's Encrypt SSL Kurulumu
```bash
# SSL sertifikası al
certbot --nginx -d DOMAIN_ADINIZ.com -d www.DOMAIN_ADINIZ.com

# Otomatik yenileme testi
certbot renew --dry-run
```

### 3. SSL Sonrası Nginx Konfigürasyonu
Certbot otomatik olarak güncelleyecek, ancak manuel kontrol:
```bash
nano /etc/nginx/sites-available/ppe-detection
```

---

## 📱 Mobil Uygulama Güncelleme

### 1. Backend URL'ini Güncelleme

**lib/screens/register_screen.dart:**
```dart
// Eski (Ngrok)
final String serverUrl = "https://untransposed-unawarely-keri.ngrok-free.dev/api/register_user";

// Yeni (VDS)
final String serverUrl = "https://DOMAIN_ADINIZ.com/api/register_user";
```

**lib/screens/login_screen.dart:**
```dart
// Eski
final String serverUrl = "https://untransposed-unawarely-keri.ngrok-free.dev/api/login_user";

// Yeni
final String serverUrl = "https://DOMAIN_ADINIZ.com/api/login_user";
```

**lib/screens/simple_check_screen.dart:**
```dart
// Eski
final String serverUrl = "https://untransposed-unawarely-keri.ngrok-free.dev/validate_image";

// Yeni
final String serverUrl = "https://DOMAIN_ADINIZ.com/validate_image";
```

### 2. APK Yeniden Build
```bash
flutter clean
flutter pub get
flutter build apk --release
```

---

## 🔥 Güvenlik Duvarı (UFW)

```bash
# UFW'yi etkinleştir
ufw enable

# SSH
ufw allow 22/tcp

# HTTP
ufw allow 80/tcp

# HTTPS
ufw allow 443/tcp

# Durumu kontrol et
ufw status
```

---

## 📊 İzleme ve Bakım

### 1. Log Dosyaları
```bash
# Backend logları
tail -f /var/log/ppe-backend.log
tail -f /var/log/ppe-backend-error.log

# Nginx logları
tail -f /var/nginx/access.log
tail -f /var/nginx/error.log

# Sistem logları
journalctl -u ppe-backend.service -f
```

### 2. Veritabanı Yedekleme
```bash
# Otomatik yedekleme scripti
nano /usr/local/bin/backup-ppe-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ppe-detection"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Veritabanı yedeği
cp /var/www/ppe-detection/backend/ppe_inspections.db $BACKUP_DIR/db_$DATE.db

# Kullanıcı fotoğrafları yedeği
tar -czf $BACKUP_DIR/users_$DATE.tar.gz /var/www/ppe-detection/backend/users/

# 30 günden eski yedekleri sil
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Yedekleme tamamlandı: $DATE"
```

```bash
# Scripti çalıştırılabilir yap
chmod +x /usr/local/bin/backup-ppe-db.sh

# Cron job ekle (her gün saat 02:00)
crontab -e
```

Cron içeriği:
```
0 2 * * * /usr/local/bin/backup-ppe-db.sh >> /var/log/ppe-backup.log 2>&1
```

### 3. Disk Kullanımı İzleme
```bash
# Disk durumu
df -h

# Klasör boyutları
du -sh /var/www/ppe-detection/*
```

---

## 🚨 Sorun Giderme

### Backend Çalışmıyor
```bash
# Servis durumu
systemctl status ppe-backend.service

# Logları kontrol et
journalctl -u ppe-backend.service -n 50

# Manuel başlatma testi
cd /var/www/ppe-detection/backend
source venv/bin/activate
python3 app_simple.py
```

### Nginx Hatası
```bash
# Konfigürasyon testi
nginx -t

# Logları kontrol et
tail -f /var/log/nginx/error.log

# Nginx'i yeniden başlat
systemctl restart nginx
```

### Port Kontrolü
```bash
# 5001 portunu dinleyen process
netstat -tulpn | grep 5001

# Veya
lsof -i :5001
```

### Dosya İzinleri
```bash
# Backend klasörü
chown -R www-data:www-data /var/www/ppe-detection
chmod -R 755 /var/www/ppe-detection

# Users klasörü (yazılabilir)
chmod 775 /var/www/ppe-detection/backend/users
```

---

## 📈 Performans Optimizasyonu

### 1. Gunicorn ile Production Server
```bash
pip install gunicorn

# Gunicorn ile başlat
gunicorn -w 4 -b 127.0.0.1:5001 app_simple:app
```

Systemd servisini güncelle:
```ini
ExecStart=/var/www/ppe-detection/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app_simple:app
```

### 2. Nginx Cache
```nginx
# Nginx konfigürasyonuna ekle
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=ppe_cache:10m max_size=100m;

location / {
    proxy_cache ppe_cache;
    proxy_cache_valid 200 5m;
    # ... diğer ayarlar
}
```

---

## ✅ Kontrol Listesi

- [ ] VDS satın alındı ve erişim sağlandı
- [ ] Sistem güncellemeleri yapıldı
- [ ] Gerekli paketler yüklendi
- [ ] Backend dosyaları yüklendi
- [ ] Python virtual environment oluşturuldu
- [ ] Python paketleri yüklendi
- [ ] Systemd servisi oluşturuldu ve başlatıldı
- [ ] Nginx kuruldu ve yapılandırıldı
- [ ] Domain A kaydı eklendi
- [ ] SSL sertifikası kuruldu
- [ ] Güvenlik duvarı yapılandırıldı
- [ ] Mobil uygulama URL'leri güncellendi
- [ ] Yeni APK build edildi
- [ ] Yedekleme sistemi kuruldu
- [ ] Test edildi ve çalışıyor ✅

---

## 🎯 Hızlı Başlangıç Komutları

```bash
# Tek komutla kurulum (Ubuntu 22.04)
curl -sSL https://raw.githubusercontent.com/KULLANICI_ADI/ppe-detection/main/install.sh | bash

# Veya manuel kurulum için yukarıdaki adımları takip edin
```

---

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Logları kontrol edin
2. Servis durumunu kontrol edin
3. Port ve firewall ayarlarını kontrol edin
4. GitHub Issues'da sorun bildirin

---

**Not:** Bu rehber Ubuntu 22.04 LTS için hazırlanmıştır. Farklı işletim sistemleri için komutlar değişebilir.
