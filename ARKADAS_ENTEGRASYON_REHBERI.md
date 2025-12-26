# Arkadaş Sistemi Entegrasyon Rehberi

## 🎯 Amaç
Arkadaşınızın sisteminden sizin dashboard'ınıza veri göndermek için gerekli entegrasyon bilgileri.
Gönderilen veriler otomatik olarak:
- **Kontroller** sekmesinde kontrol kaydı olarak görünecek
- **Kayıtlar** sekmesinde kullanıcı kaydı olarak görünecek

## 📡 API Endpoint Bilgileri

**URL:** `http://72.62.60.125/api/veri-al`
**Method:** POST
**Content-Type:** application/json

## 📋 Gönderilecek Veri Formatı

```json
{
  "isim": "Ahmet",
  "soyisim": "Yılmaz",
  "departman": "Üretim",
  "durum": "Gecti",
  "tarih": "24.05.2024",
  "saat": "14:30:05"
}
```

### Önemli Notlar:
- `durum` alanı sadece **"Gecti"** veya **"Kaldi"** değerlerini alabilir
- `tarih` formatı: DD.MM.YYYY
- `saat` formatı: HH:MM:SS
- Tüm alanlar zorunludur

### Veri İşleme Mantığı:
- **"Gecti"** → Kask:✅ Yelek:✅ Durum:Uygun
- **"Kaldi"** → Kask:❌ Yelek:❌ Durum:Uygun Değil
- Kullanıcı otomatik olarak **Kayıtlar** sekmesine eklenir (EXT prefix ile sicil no)
- Kontrol sonucu **Kontroller** sekmesinde görünür

## 💻 Örnek Kodlar

### 1. JavaScript (Node.js/Browser)

```javascript
async function veriGonder(personelBilgisi) {
    const veri = {
        isim: personelBilgisi.isim,
        soyisim: personelBilgisi.soyisim,
        departman: personelBilgisi.departman,
        durum: personelBilgisi.durum, // "Gecti" veya "Kaldi"
        tarih: new Date().toLocaleDateString('tr-TR'),
        saat: new Date().toLocaleTimeString('tr-TR')
    };

    try {
        const response = await fetch('http://72.62.60.125/api/veri-al', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(veri)
        });

        const sonuc = await response.json();
        
        if (sonuc.success) {
            console.log('✅ Veri başarıyla gönderildi:', sonuc.message);
        } else {
            console.error('❌ Hata:', sonuc.error);
        }
    } catch (error) {
        console.error('❌ Bağlantı hatası:', error);
    }
}

// Kullanım örneği
veriGonder({
    isim: "Mehmet",
    soyisim: "Demir", 
    departman: "Kalite Kontrol",
    durum: "Gecti"
});
```

### 2. Python

```python
import requests
import json
from datetime import datetime

def veri_gonder(personel_bilgisi):
    url = "http://72.62.60.125/api/veri-al"
    
    veri = {
        "isim": personel_bilgisi["isim"],
        "soyisim": personel_bilgisi["soyisim"],
        "departman": personel_bilgisi["departman"],
        "durum": personel_bilgisi["durum"],  # "Gecti" veya "Kaldi"
        "tarih": datetime.now().strftime("%d.%m.%Y"),
        "saat": datetime.now().strftime("%H:%M:%S")
    }
    
    try:
        response = requests.post(
            url, 
            json=veri,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            sonuc = response.json()
            if sonuc['success']:
                print(f"✅ Veri başarıyla gönderildi: {sonuc['message']}")
            else:
                print(f"❌ Hata: {sonuc['error']}")
        else:
            print(f"❌ HTTP Hatası: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

# Kullanım örneği
veri_gonder({
    "isim": "Ayşe",
    "soyisim": "Kaya",
    "departman": "İnsan Kaynakları", 
    "durum": "Kaldi"
})
```

### 3. PHP

```php
<?php
function veriGonder($personelBilgisi) {
    $url = "http://72.62.60.125/api/veri-al";
    
    $veri = array(
        "isim" => $personelBilgisi["isim"],
        "soyisim" => $personelBilgisi["soyisim"],
        "departman" => $personelBilgisi["departman"],
        "durum" => $personelBilgisi["durum"], // "Gecti" veya "Kaldi"
        "tarih" => date("d.m.Y"),
        "saat" => date("H:i:s")
    );
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($veri)
        )
    );
    
    $context = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    if ($result !== FALSE) {
        $sonuc = json_decode($result, true);
        if ($sonuc['success']) {
            echo "✅ Veri başarıyla gönderildi: " . $sonuc['message'];
        } else {
            echo "❌ Hata: " . $sonuc['error'];
        }
    } else {
        echo "❌ Bağlantı hatası";
    }
}

// Kullanım örneği
veriGonder(array(
    "isim" => "Ali",
    "soyisim" => "Veli",
    "departman" => "Muhasebe",
    "durum" => "Gecti"
));
?>
```

### 4. Flutter/Dart

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<void> veriGonder(Map<String, String> personelBilgisi) async {
  final url = Uri.parse('http://72.62.60.125/api/veri-al');
  
  final veri = {
    'isim': personelBilgisi['isim'],
    'soyisim': personelBilgisi['soyisim'],
    'departman': personelBilgisi['departman'],
    'durum': personelBilgisi['durum'], // "Gecti" veya "Kaldi"
    'tarih': DateTime.now().toLocal().toString().split(' ')[0].split('-').reversed.join('.'),
    'saat': TimeOfDay.now().format(context),
  };

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode(veri),
    );

    if (response.statusCode == 200) {
      final sonuc = json.decode(response.body);
      if (sonuc['success']) {
        print('✅ Veri başarıyla gönderildi: ${sonuc['message']}');
      } else {
        print('❌ Hata: ${sonuc['error']}');
      }
    } else {
      print('❌ HTTP Hatası: ${response.statusCode}');
    }
  } catch (e) {
    print('❌ Bağlantı hatası: $e');
  }
}

// Kullanım örneği
veriGonder({
  'isim': 'Fatma',
  'soyisim': 'Şahin',
  'departman': 'Satış',
  'durum': 'Gecti'
});
```

## 🔧 Test Etme

### Postman ile Test:
1. Method: POST
2. URL: `http://72.62.60.125/api/veri-al`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "isim": "Test",
  "soyisim": "Kullanıcı",
  "departman": "Test Departmanı",
  "durum": "Gecti",
  "tarih": "17.12.2024",
  "saat": "15:30:00"
}
```

### cURL ile Test:
```bash
curl -X POST http://72.62.60.125/api/veri-al \
  -H "Content-Type: application/json" \
  -d '{
    "isim": "Test",
    "soyisim": "Kullanıcı", 
    "departman": "Test Departmanı",
    "durum": "Gecti",
    "tarih": "17.12.2024",
    "saat": "15:30:00"
  }'
```

## 📊 Dashboard'da Görüntüleme

Gönderilen veriler dashboard'da mevcut sekmelerde görüntülenecek:
- **URL:** http://72.62.60.125/dashboard
- **Kontroller Sekmesi:** Gönderilen her veri bir kontrol kaydı olarak görünür
- **Kayıtlar Sekmesi:** Gönderilen kişiler kullanıcı olarak kaydedilir
- **Dashboard:** Genel istatistiklerde dahil edilir
- **Raporlar:** Grafiklerde ve raporlarda görünür

## 🚨 Önemli Notlar

1. **Güvenlik:** Şu an API açık, production'da authentication eklenebilir
2. **Rate Limiting:** Çok fazla istek gönderilirse sunucu yavaşlayabilir
3. **Veri Formatı:** JSON formatına kesinlikle uyulmalı
4. **Durum Değerleri:** Sadece "Gecti" ve "Kaldi" kabul edilir
5. **Tarih/Saat:** Türkçe format kullanılmalı

## 🔄 Entegrasyon Adımları

1. **API Test Et:** Önce Postman/cURL ile test edin
2. **Kod Entegrasyonu:** Yukarıdaki örneklerden uygun olanı kullanın
3. **Hata Yönetimi:** try-catch blokları ekleyin
4. **Log Tutma:** Gönderilen verileri loglamayı unutmayın
5. **Dashboard Kontrol:** Verilerin dashboard'da göründüğünü kontrol edin

## 📞 Destek

Herhangi bir sorun yaşarsanız:
- Dashboard loglarını kontrol edin
- API response'larını inceleyin
- Veri formatının doğru olduğundan emin olun