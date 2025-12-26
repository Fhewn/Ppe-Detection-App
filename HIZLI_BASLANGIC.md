# 🚀 Hızlı Başlangıç - VDS Kurulumu

Bu rehber, projenizi VDS'de 15 dakikada çalışır hale getirmeniz için hazırlanmıştır.

## 📋 Ön Hazırlık

### 1. VDS Satın Alın
- **Önerilen:** DigitalOcean, Linode, Vultr (5-6$/ay)
- **Minimum:** 2GB RAM, 2 CPU Core, 20GB SSD
- **İşletim Sistemi:** Ubuntu 22.04 LTS

### 2. Domain Ayarları (Opsiyonel)
- Domain sağlayıcınızdan A kaydı ekleyin
- `@` → VDS IP Adresi
- `www` → VDS IP Adresi

---

## ⚡ Otomatik Kurulum (Önerilen)

### 1. VDS'e Bağlanın
```bash
ssh root@SUNUCU_IP_ADRESI
```

### 2. Proje Dosyalarını Yükleyin
```bash
# Yöntem 1: Git ile (eğer GitHub'da varsa)
git clone https://github.com/KULLANICI_ADI/ppe-detection.git /var/www/ppe-detection

# Yöntem 2: SFTP ile manuel yükleme
# FileZilla, WinSCP veya Cyberduck kullanarak
# backend/ klasörünü /var/www/ppe-detection/backend/ konumuna yükleyin
```

### 3. Kurulum Scriptini Çalıştırın
```bash
cd /var/www/ppe-detection/backend
chmod +x install-vds.sh
sudo bash install-vds.sh
```

Script otomatik olarak:
- ✅ Sistem güncellemelerini yapar
- ✅ Gerekli paketleri yükler
- ✅ Python virtual environment oluşturur
- ✅ Backend'i systemd servisi olarak kurar
- ✅ Nginx reverse proxy yapılandırır
- ✅ Güvenlik duvarını ayarlar
- ✅ Otomatik yedekleme sistemi kurar
- ✅ SSL sertifikası kurar (opsiyonel)

### 4. Test Edin
```bash
# Servis durumu
systemctl status ppe-backend.service

# API testi
curl http://localhost:5001/api

# Dashboard
# Tarayıcıda: http://SUNUCU_IP/dashboard
```

---

## 🔧 Manuel Kurulum

Eğer otomatik kurulum çalışmazsa, detaylı adımlar için `VDS_KURULUM_REHBERI.md` dosyasına bakın.

---

## 📱 Mobil Uygulamayı Güncelleme

### 1. URL'leri Değiştirin

**lib/screens/register_screen.dart:**
```dart
final String serverUrl = "https://DOMAIN_ADINIZ.com/api/register_user";
// veya
final String serverUrl = "http://SUNUCU_IP:5001/api/register_user";
```

**lib/screens/login_screen.dart:**
```dart
final String serverUrl = "https://DOMAIN_ADINIZ.com/api/login_user";
```

**lib/screens/simple_check_screen.dart:**
```dart
final String serverUrl = "https://DOMAIN_ADINIZ.com/validate_image";
```

### 2. APK Build
```bash
flutter clean
flutter pub get
flutter build apk --release
```

APK konumu: `build/app/outputs/flutter-apk/app-release.apk`

---

## 🔒 SSL Kurulumu (HTTPS)

### Domain ile SSL
```bash
sudo certbot --nginx -d DOMAIN_ADINIZ.com -d www.DOMAIN_ADINIZ.com
```

### Otomatik Yenileme
```bash
# Test
sudo certbot renew --dry-run

# Cron job (otomatik eklenir)
# Her gün saat 03:00'te kontrol eder
```

---

## 📊 Yönetim Komutları

### Servis Yönetimi
```bash
# Başlat
sudo systemctl start ppe-backend.service

# Durdur
sudo systemctl stop ppe-backend.service

# Yeniden başlat
sudo systemctl restart ppe-backend.service

# Durum
sudo systemctl status ppe-backend.service

# Otomatik başlatmayı etkinleştir
sudo systemctl enable ppe-backend.service
```

### Log Görüntüleme
```bash
# Backend logları
sudo tail -f /var/log/ppe-detection/backend.log

# Hata logları
sudo tail -f /var/log/ppe-detection/backend-error.log

# Systemd logları
sudo journalctl -u ppe-backend.service -f

# Nginx logları
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Yedekleme
```bash
# Manuel yedekleme
sudo /usr/local/bin/backup-ppe-db.sh

# Yedekleri görüntüle
ls -lh /var/backups/ppe-detection/

# Yedekten geri yükleme
sudo cp /var/backups/ppe-detection/db_TARIH.db /var/www/ppe-detection/backend/ppe_inspections.db
sudo systemctl restart ppe-backend.service
```

---

## 🚨 Sorun Giderme

### Backend Çalışmıyor
```bash
# 1. Servis durumunu kontrol et
sudo systemctl status ppe-backend.service

# 2. Logları kontrol et
sudo journalctl -u ppe-backend.service -n 50

# 3. Manuel başlatma testi
cd /var/www/ppe-detection/backend
source venv/bin/activate
python3 app_simple.py
```

### Port Zaten Kullanımda
```bash
# 5001 portunu kullanan process'i bul
sudo lsof -i :5001

# Process'i sonlandır
sudo kill -9 PID_NUMARASI

# Servisi yeniden başlat
sudo systemctl restart ppe-backend.service
```

### Nginx Hatası
```bash
# Konfigürasyon testi
sudo nginx -t

# Nginx'i yeniden başlat
sudo systemctl restart nginx
```

### Dosya İzin Hatası
```bash
# İzinleri düzelt
sudo chown -R www-data:www-data /var/www/ppe-detection
sudo chmod -R 755 /var/www/ppe-detection
sudo chmod 775 /var/www/ppe-detection/backend/users
```

### Veritabanı Hatası
```bash
# Veritabanını yeniden oluştur
cd /var/www/ppe-detection/backend
source venv/bin/activate
python3 -c "from app_simple import init_db; init_db()"
```

---

## 📈 Performans İyileştirme

### Gunicorn ile Production Server
```bash
# Gunicorn yükle
source /var/www/ppe-detection/backend/venv/bin/activate
pip install gunicorn

# Systemd servisini güncelle
sudo nano /etc/systemd/system/ppe-backend.service
```

ExecStart satırını değiştir:
```ini
ExecStart=/var/www/ppe-detection/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app_simple:app
```

```bash
# Servisi yeniden yükle
sudo systemctl daemon-reload
sudo systemctl restart ppe-backend.service
```

---

## ✅ Kurulum Sonrası Kontrol Listesi

- [ ] Backend servisi çalışıyor (`systemctl status ppe-backend.service`)
- [ ] API erişilebilir (`curl http://localhost:5001/api`)
- [ ] Dashboard açılıyor (tarayıcıda)
- [ ] Nginx çalışıyor (`systemctl status nginx`)
- [ ] Güvenlik duvarı aktif (`ufw status`)
- [ ] SSL kuruldu (opsiyonel)
- [ ] Mobil uygulama URL'leri güncellendi
- [ ] Yeni APK build edildi
- [ ] Mobil uygulamadan test edildi
- [ ] Otomatik yedekleme çalışıyor

---

## 🎯 Hızlı Test

### 1. API Test
```bash
# Sağlık kontrolü
curl http://SUNUCU_IP:5001/api

# Kullanıcıları listele
curl http://SUNUCU_IP:5001/api/users

# İstatistikler
curl http://SUNUCU_IP:5001/api/stats
```

### 2. Dashboard Test
Tarayıcıda: `http://SUNUCU_IP:5001/dashboard`

### 3. Mobil Uygulama Test
- Kayıt ol
- Giriş yap
- PPE kontrolü yap
- Dashboard'da kontrol et

---

## 📞 Yardım

Sorun yaşarsanız:

1. **Logları kontrol edin:**
   ```bash
   sudo journalctl -u ppe-backend.service -n 100
   ```

2. **Servis durumunu kontrol edin:**
   ```bash
   sudo systemctl status ppe-backend.service
   sudo systemctl status nginx
   ```

3. **Port ve firewall kontrol edin:**
   ```bash
   sudo ufw status
   sudo netstat -tulpn | grep 5001
   ```

4. **Detaylı rehbere bakın:**
   `VDS_KURULUM_REHBERI.md`

---

## 🎉 Tebrikler!

Projeniz artık VDS'de çalışıyor ve 7/24 erişilebilir durumda!

**Önemli Notlar:**
- Düzenli olarak yedek alın
- Logları kontrol edin
- Sistem güncellemelerini yapın
- SSL sertifikasını yenileyin (otomatik)

**Sonraki Adımlar:**
- Monitoring sistemi kurun (Prometheus, Grafana)
- Rate limiting ekleyin
- CDN kullanın (Cloudflare)
- Database optimizasyonu yapın
