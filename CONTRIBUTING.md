# Katkıda Bulunma Rehberi

KKE Denetim Sistemi projesine katkıda bulunmak istediğiniz için teşekkür ederiz! 🎉

## 🚀 Başlarken

1. Repository'yi fork edin
2. Yerel makinenize klonlayın
3. Yeni bir branch oluşturun
4. Değişikliklerinizi yapın
5. Test edin
6. Pull Request açın

## 📋 Geliştirme Ortamı

### Backend Geliştirme
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

### Flutter Geliştirme
```bash
flutter pub get
flutter run
```

## 🎯 Katkı Alanları

### Öncelikli İyileştirmeler
- [ ] Daha fazla ekipman tipi desteği (eldiven, gözlük, vb.)
- [ ] Çoklu dil desteği
- [ ] Offline mod
- [ ] Kullanıcı yönetimi
- [ ] Bildirim sistemi
- [ ] Model performans iyileştirmeleri

### Bug Raporları
- GitHub Issues kullanın
- Detaylı açıklama yapın
- Ekran görüntüsü ekleyin
- Adımları belirtin

### Özellik İstekleri
- GitHub Issues'da "enhancement" etiketi kullanın
- Kullanım senaryosu açıklayın
- Mockup/tasarım ekleyin (opsiyonel)

## 📝 Kod Standartları

### Python (Backend)
- PEP 8 standartlarına uyun
- Docstring kullanın
- Type hints ekleyin
- Unit test yazın

### Dart (Flutter)
- Dart style guide'a uyun
- Widget'ları küçük tutun
- State management best practices
- Yorum satırları ekleyin

### Commit Mesajları
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: Yeni özellik
- `fix`: Bug düzeltme
- `docs`: Dokümantasyon
- `style`: Kod formatı
- `refactor`: Kod yeniden yapılandırma
- `test`: Test ekleme
- `chore`: Genel bakım

**Örnek:**
```
feat: Add multi-language support

- Added Turkish and English translations
- Created language selector in settings
- Updated all UI strings

Closes #123
```

## 🧪 Test

### Backend Testleri
```bash
cd backend
python -m pytest tests/
```

### Flutter Testleri
```bash
flutter test
```

## 📚 Dokümantasyon

- README.md güncelleyin
- API değişikliklerini belgeleyin
- Kod yorumları ekleyin
- Örnek kullanım gösterin

## ✅ Pull Request Checklist

- [ ] Kod çalışıyor
- [ ] Testler geçiyor
- [ ] Dokümantasyon güncellendi
- [ ] Commit mesajları anlamlı
- [ ] Conflict yok
- [ ] Kod review yapıldı

## 🤝 Davranış Kuralları

- Saygılı olun
- Yapıcı eleştiri yapın
- Yardımcı olun
- Kapsayıcı olun

## 📞 İletişim

- GitHub Issues
- Email: your.email@example.com
- Discord: [Link]

## 🙏 Teşekkürler

Her katkı değerlidir! Projeyi geliştirmeye yardımcı olduğunuz için teşekkürler.
