# 📱 Flutter APK Build Rehberi

## ✅ API URL Güncellendi
VPS IP adresi ile API URL'leri güncellendi:
- Login: `http://72.62.60.125/api/login_user`
- Register: `http://72.62.60.125/api/register_user`  
- PPE Check: `http://72.62.60.125/validate_image`

## 🔧 APK Build Adımları

### 1. Flutter Kurulumunu Kontrol Et
```bash
flutter doctor
```

### 2. Dependencies'leri Güncelle
```bash
flutter pub get
flutter pub upgrade
```

### 3. Android Build Ayarları

#### app/build.gradle Kontrol Et
```bash
# Android minimum SDK version
android/app/build.gradle
minSdkVersion 21
targetSdkVersion 34
```

#### Internet Permission Kontrol Et
```bash
# android/app/src/main/AndroidManifest.xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
```

### 4. Release APK Build

#### Debug APK (Test için)
```bash
flutter build apk --debug
```

#### Release APK (Production)
```bash
flutter build apk --release
```

#### Split APK (Daha küçük boyut)
```bash
flutter build apk --split-per-abi --release
```

### 5. APK Dosya Konumları

Build sonrası APK dosyaları:
```
build/app/outputs/flutter-apk/
├── app-release.apk (Universal)
├── app-arm64-v8a-release.apk (64-bit ARM)
├── app-armeabi-v7a-release.apk (32-bit ARM)
└── app-x86_64-release.apk (x86 64-bit)
```

## 📋 Önerilen Build Komutu

```bash
# Temizlik
flutter clean
flutter pub get

# Release build
flutter build apk --release --split-per-abi

# Dosya boyutları kontrol
ls -lh build/app/outputs/flutter-apk/
```

## 📱 Test Etme

### 1. Debug APK ile Test
```bash
# Debug APK yükle ve test et
flutter build apk --debug
adb install build/app/outputs/flutter-apk/app-debug.apk
```

### 2. Release APK Test
```bash
# Release APK yükle
adb install build/app/outputs/flutter-apk/app-release.apk
```

## 🔒 APK İmzalama (Opsiyonel)

### 1. Keystore Oluştur
```bash
keytool -genkey -v -keystore ~/ppe-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias ppe-key
```

### 2. key.properties Oluştur
```bash
# android/key.properties
storePassword=<password>
keyPassword=<password>
keyAlias=ppe-key
storeFile=<path-to-keystore>
```

### 3. build.gradle Güncelle
```gradle
// android/app/build.gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

## 🚀 Hızlı Build Scripti

```bash
#!/bin/bash
echo "🧹 Temizlik yapılıyor..."
flutter clean
flutter pub get

echo "🔨 APK build alınıyor..."
flutter build apk --release --split-per-abi

echo "📱 APK dosyaları:"
ls -lh build/app/outputs/flutter-apk/

echo "✅ Build tamamlandı!"
echo "📍 APK konumu: build/app/outputs/flutter-apk/"
```

## 📊 APK Boyut Optimizasyonu

### 1. Obfuscation Aktif Et
```bash
flutter build apk --release --obfuscate --split-debug-info=build/debug-info
```

### 2. Tree Shaking
```bash
flutter build apk --release --tree-shake-icons
```

### 3. Compression
```bash
flutter build apk --release --shrink
```

## 🔧 Sorun Giderme

### Gradle Build Hatası
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
```

### Network Security Config
```xml
<!-- android/app/src/main/res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">72.62.60.125</domain>
    </domain-config>
</network-security-config>
```

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
```

## 📱 Final APK

Önerilen APK:
- **Universal**: `app-release.apk` (Tüm cihazlar)
- **ARM64**: `app-arm64-v8a-release.apk` (Modern telefonlar)

## 🎯 Test Checklist

- [ ] APK başarıyla build alındı
- [ ] Uygulama açılıyor
- [ ] Kamera çalışıyor
- [ ] API bağlantısı çalışıyor
- [ ] PPE kontrolü çalışıyor
- [ ] Kullanıcı kayıt/giriş çalışıyor

**🎉 APK hazır! Artık mobil cihazlarda test edebilirsiniz.**