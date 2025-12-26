# 🎯 VDS Kurulum Özeti

## 📦 Hazırlanan Dosyalar

✅ **VDS_KURULUM_REHBERI.md** - Detaylı adım adım kurulum rehberi
✅ **HIZLI_BASLANGIC.md** - 15 dakikada kurulum
✅ **backend/install-vds.sh** - Otomatik kurulum scripti
✅ **backend/requirements.txt** - Python bağımlılıkları
✅ **backend/.env.example** - Environment variables şablonu
✅ **README.md** - Proje dokümantasyonu

## 🚀 Kurulum Adımları (Özet)

### 1️⃣ VDS Satın Alın
- **Önerilen:** DigitalOcean, Linode, Vultr
- **Fiyat:** 5-6$/ay
- **Özellikler:** 2GB RAM, 2 CPU, 20GB SSD
- **OS:** Ubuntu 22.04 LTS

### 2️⃣ Domain Ayarları (Opsiyonel)
```
A Kaydı: @ → VDS_IP_ADRESI
A Kaydı: www → VDS_IP_ADRESI
```

### 3️⃣ VDS'e Bağlanın
```bash
ssh root@VDS_IP_ADRESI
```

### 4️⃣ Dosyaları Yükleyin
```bash
# Yöntem 1: Git (önerilen)
git clone https://github.com/KULLANICI/ppe-detection.git /var/www/ppe-detection

# Yöntem 2: SFTP (FileZilla, WinSCP)
# backend/ klasörünü /var/www/ppe-detection/backend/ konumuna yükle
```

### 5️⃣ Otomatik Kurulum
```bash
cd /var/www/ppe-detection/backend
chmod +x install-vds.sh
sudo bash install-vds.sh
```

Script şunları yapar:
- ✅ Sistem güncellemesi
- ✅ Gerekli paketleri yükler
- ✅ Python virtual environment
- ✅ Backend'i systemd servisi olarak kurar
- ✅ Nginx reverse proxy
- ✅ Güvenlik duvarı
- ✅ Otomatik yedekleme
- ✅ SSL sertifikası (opsiyonel)

### 6️⃣ Mobil Uygulamayı Güncelleyin

**3 dosyada URL değiştirin:**

1. `lib/screens/register_screen.dart`
2. `lib/screens/login_screen.dart`
3. `lib/screens/simple_check_screen.dart`

```dart
// Eski
final String serverUrl = "https://untransposed-unawarely-keri.ngrok-free.dev/api/...";

// Yeni
final String serverUrl = "https://DOMAIN_ADINIZ.com/api/...";
// veya
final String serverUrl = "http://VDS_IP:5001/api/...";
```

### 7️⃣ APK Build
```bash
flutter clean
flutter pub get
flutter build apk --release
```

### 8️⃣ Test Edin
```bash
# Backend durumu
systemctl status ppe-backend.service

# API test
curl http://localhost:5001/api

# Dashboard
# Tarayıcı: http://VDS_IP/dashboard
```

## 🎉 Tamamlandı!

Projeniz artık 7/24 çalışıyor!

## 📊 Erişim Bilgileri

### Web Dashboard
```
http://DOMAIN_ADINIZ.com/dashboard
veya
http://VDS_IP:5001/dashboard
```

### API Endpoints
```
http://DOMAIN_ADINIZ.com/api
http://DOMAIN_ADINIZ.com/api/users
http://DOMAIN_ADINIZ.com/api/stats
```

### Mobil Uygulama
```
https://DOMAIN_ADINIZ.com/api/register_user
https://DOMAIN_ADINIZ.com/api/login_user
https://DOMAIN_ADINIZ.com/validate_image
```

## 🔧 Yönetim Komutları

### Servis Yönetimi
```bash
sudo systemctl start ppe-backend.service    # Başlat
sudo systemctl stop ppe-backend.service     # Durdur
sudo systemctl restart ppe-backend.service  # Yeniden başlat
sudo systemctl status ppe-backend.service   # Durum
```

### Log Görüntüleme
```bash
sudo tail -f /var/log/ppe-detection/backend.log
sudo journalctl -u ppe-backend.service -f
```

### Yedekleme
```bash
sudo /usr/local/bin/backup-ppe-db.sh  # Manuel yedek
ls /var/backups/ppe-detection/        # Yedekleri listele
```

## 🚨 Sorun Giderme

### Backend çalışmıyor?
```bash
sudo systemctl status ppe-backend.service
sudo journalctl -u ppe-backend.service -n 50
```

### Port çakışması?
```bash
sudo lsof -i :5001
sudo kill -9 PID
sudo systemctl restart ppe-backend.service
```

### Nginx hatası?
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 📚 Detaylı Dokümantasyon

- **Hızlı Başlangıç:** `HIZLI_BASLANGIC.md`
- **Detaylı Rehber:** `VDS_KURULUM_REHBERI.md`
- **Proje Dokümantasyonu:** `README.md`

## ✅ Kontrol Listesi

- [ ] VDS satın alındı
- [ ] Domain ayarlandı (opsiyonel)
- [ ] VDS'e bağlanıldı
- [ ] Dosyalar yüklendi
- [ ] Kurulum scripti çalıştırıldı
- [ ] Backend servisi çalışıyor
- [ ] Nginx çalışıyor
- [ ] SSL kuruldu (opsiyonel)
- [ ] Mobil uygulama URL'leri güncellendi
- [ ] APK build edildi
- [ ] Test edildi ✅

## 💡 İpuçları

1. **SSL Kullanın:** Let's Encrypt ücretsiz
2. **Yedek Alın:** Otomatik yedekleme aktif
3. **Logları İzleyin:** Düzenli kontrol edin
4. **Güncelleme Yapın:** Sistem ve paketleri güncel tutun
5. **Monitoring:** Prometheus/Grafana ekleyin (opsiyonel)

## 🎯 Sonraki Adımlar

1. ✅ Projeyi VDS'de çalıştırın
2. ✅ SSL sertifikası kurun
3. ✅ Mobil uygulamayı test edin
4. ✅ Dashboard'u kontrol edin
5. ⭐ Monitoring sistemi kurun (opsiyonel)
6. ⭐ CDN kullanın (Cloudflare) (opsiyonel)
7. ⭐ Rate limiting ekleyin (opsiyonel)

## 📞 Yardım

Sorun yaşarsanız:
1. Logları kontrol edin
2. Servis durumunu kontrol edin
3. Detaylı rehberlere bakın
4. GitHub Issues açın

---

**Başarılar! 🚀**
