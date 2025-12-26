# 🦺 PPE Detection App - Kişisel Koruyucu Ekipman Tespit Sistemi

Flutter tabanlı mobil uygulama ve Python Flask backend ile geliştirilmiş **Kişisel Koruyucu Ekipman (KKE)** tespit sistemi.

## 🎯 Özellikler

### 📱 Mobil Uygulama (Flutter)
- **Yüz Tanıma ile Kayıt/Giriş** - Gerçek face_recognition kütüphanesi
- **PPE Kontrolü** - Kask ve yelek tespiti
- **Kamera Entegrasyonu** - Anlık fotoğraf çekme
- **Sonuç Görüntüleme** - Detaylı tespit sonuçları

### 🖥️ Backend (Python Flask)
- **AI Tabanlı Tespit** - YOLOv8 modeli ile PPE tespiti
- **Yüz Tanıma** - face_recognition kütüphanesi
- **Veritabanı** - SQLite ile veri saklama
- **Dashboard** - Web tabanlı yönetim paneli
- **API** - RESTful API servisleri

### 📊 Dashboard Özellikleri
- **Gerçek Zamanlı İstatistikler** - Toplam kontrol, uygunluk oranları
- **Detaylı Raporlar** - PDF/Excel export
- **Kullanıcı Yönetimi** - Kayıtlı kullanıcıları görüntüleme
- **Grafik Analizi** - Chart.js ile görselleştirme
- **Türkiye Saat Dilimi** - Doğru tarih/saat gösterimi

## 🚀 Kurulum

### 📋 Gereksinimler
- **Flutter SDK** (3.0+)
- **Python** (3.8+)
- **Android Studio** / **Xcode**
- **Git**

### 🔧 Backend Kurulumu
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python app_simple.py
```

### 📱 Mobil Uygulama Kurulumu
```bash
flutter pub get
flutter run
```

### 🏗️ APK Build
```bash
flutter build apk --release
```

## 🌐 VPS Kurulumu

Detaylı VPS kurulum rehberi için: [VPS_KURULUM_REHBERI.md](VPS_KURULUM_REHBERI.md)

```bash
# Hızlı kurulum
chmod +x arch_kurulum_script.sh
./arch_kurulum_script.sh
```

## 📖 Dokümantasyon

- **[VPS Kurulum Rehberi](VPS_KURULUM_REHBERI.md)** - Sunucu kurulumu
- **[Mobil Build Rehberi](MOBILE_BUILD_REHBERI.md)** - APK/IPA oluşturma
- **[Arkadaş Entegrasyon Rehberi](ARKADAS_ENTEGRASYON_REHBERI.md)** - Dış sistem entegrasyonu
- **[Hızlı Başlangıç](HIZLI_BASLANGIC.md)** - Temel kullanım

## 🔗 API Endpoints

### Mobil API
- `POST /api/register_user` - Kullanıcı kaydı
- `POST /api/login_user` - Yüz tanıma ile giriş
- `POST /validate_image` - PPE kontrolü

### Dashboard API
- `GET /api/stats` - İstatistikler
- `GET /api/inspections` - Kontrol kayıtları
- `GET /api/users` - Kullanıcı listesi
- `GET /dashboard` - Web dashboard

### Dış Sistem API
- `POST /api/veri-al` - Arkadaş sisteminden veri alma

## 🎨 Teknolojiler

### Frontend
- **Flutter** - Mobil uygulama framework
- **Dart** - Programlama dili
- **Camera Plugin** - Kamera erişimi
- **HTTP** - API iletişimi

### Backend
- **Python Flask** - Web framework
- **YOLOv8** - AI model (Ultralytics)
- **face_recognition** - Yüz tanıma
- **SQLite** - Veritabanı
- **OpenCV** - Görüntü işleme
- **Pillow** - Resim manipülasyonu

### Dashboard
- **HTML/CSS/JavaScript** - Web arayüzü
- **Chart.js** - Grafik kütüphanesi
- **jsPDF** - PDF export
- **SheetJS** - Excel export

## 📊 Sistem Mimarisi

```
📱 Flutter App
    ↓ HTTP API
🖥️ Flask Backend
    ↓ SQLite
💾 Database
    ↓ Web Interface
🌐 Dashboard
```

## 🔒 Güvenlik

- **Yüz Tanıma** - Gerçek biometric authentication
- **HTTPS** - SSL sertifikası ile güvenli iletişim
- **Input Validation** - Tüm girişler doğrulanır
- **Error Handling** - Güvenli hata yönetimi

## 📈 Performans

- **Optimized Models** - Hızlı AI inference
- **Image Compression** - Bandwidth tasarrufu
- **Caching** - Hızlı veri erişimi
- **Responsive Design** - Tüm cihazlarda uyumlu

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Ekip

- **Backend Development** - Python Flask, AI Integration
- **Mobile Development** - Flutter, Dart
- **DevOps** - VPS Setup, Deployment
- **UI/UX** - Dashboard Design

## 📞 İletişim

- **GitHub Issues** - Bug reports ve feature requests
- **Documentation** - Detaylı rehberler mevcut
- **Support** - Kurulum ve kullanım desteği

## 🎉 Demo

**Live Demo:** http://72.62.60.125:5002/dashboard

**APK Download:** [Releases](https://github.com/your-username/ppe-detection-app/releases)

---

⭐ **Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**