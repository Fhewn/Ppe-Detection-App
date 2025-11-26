import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:path/path.dart' as p;

class SimpleCheckScreen extends StatefulWidget {
  const SimpleCheckScreen({super.key});

  @override
  State<SimpleCheckScreen> createState() => _SimpleCheckScreenState();
}

class _SimpleCheckScreenState extends State<SimpleCheckScreen> {
  
  // -----------------------------------------------------------------
  // Backend API (port 5001) - Yeni eğitilmiş model
  final String serverUrl = "http://172.20.10.14:5001/validate_image";
  // -----------------------------------------------------------------

  File? _imageFile;
  bool _isLoading = false;
  String _statusMessage = "Fotoğraf çekin veya seçin";
  Map<String, dynamic>? _analysisResult;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    try {
      // Kamera için daha yüksek kalite, galeri için optimize
      final XFile? pickedFile = await _picker.pickImage(
        source: source,
        maxWidth: source == ImageSource.camera ? 2400 : 1920,
        maxHeight: source == ImageSource.camera ? 3200 : 1080,
        imageQuality: source == ImageSource.camera ? 95 : 85,
        preferredCameraDevice: CameraDevice.rear, // Arka kamera (daha iyi)
      );

      if (pickedFile != null) {
        setState(() {
          _imageFile = File(pickedFile.path);
          if (source == ImageSource.camera) {
            _statusMessage = "📸 Kamera fotoğrafı alındı. Analiz Et butonuna basın.\n💡 İpucu: Kişi tam karşıdan, yakın mesafeden çekilmeli.";
          } else {
            _statusMessage = "🖼️ Galeri fotoğrafı seçildi. Analiz Et butonuna basın.";
          }
          _analysisResult = null;
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = "Hata: ${e.toString()}";
      });
    }
  }

  Future<void> _uploadAndAnalyze() async {
    if (_imageFile == null) {
      setState(() {
        _statusMessage = "Lütfen önce bir fotoğraf çekin.";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = "Görüntü analiz ediliyor...";
      _analysisResult = null;
    });

    try {
      var uri = Uri.parse(serverUrl);
      var request = http.MultipartRequest('POST', uri);

      request.files.add(
        await http.MultipartFile.fromPath(
          'image',
          _imageFile!.path,
          filename: p.basename(_imageFile!.path),
        ),
      );

      var streamedResponse = await request.send().timeout(
        const Duration(seconds: 60),
        onTimeout: () {
          throw Exception('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
        },
      );
      var response = await http.Response.fromStream(streamedResponse);

      setState(() {
        _isLoading = false;
      });

      if (response.statusCode == 200) {
        final Map<String, dynamic> result = json.decode(response.body);
        
        setState(() {
          _analysisResult = result;
          _statusMessage = result['success'] 
            ? "✅ Tüm ekipmanlar mevcut!" 
            : "⚠️ Eksik ekipman tespit edildi!";
        });
      } else {
        setState(() {
          _statusMessage = "Sunucu Hatası (Kod ${response.statusCode})";
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _statusMessage = "Yükleme Hatası: ${e.toString()}";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("KKE Kontrol Sistemi"),
        centerTitle: true,
        backgroundColor: Colors.blue,
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                // Görüntü Önizleme
                Container(
                  height: 300,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: _imageFile != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.file(
                            _imageFile!,
                            fit: BoxFit.contain,
                          ),
                        )
                      : const Center(
                          child: Icon(
                            Icons.image,
                            size: 100,
                            color: Colors.grey,
                          ),
                        ),
                ),
                const SizedBox(height: 20),

                // Butonlar
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text("Kamera"),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library),
                      label: const Text("Galeri"),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // Analiz Et Butonu
                ElevatedButton(
                  onPressed: _isLoading ? null : _uploadAndAnalyze,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          "Analiz Et",
                          style: TextStyle(fontSize: 18, color: Colors.white),
                        ),
                ),
                const SizedBox(height: 20),

                // Durum Mesajı
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue.shade200),
                  ),
                  child: Column(
                    children: [
                      Text(
                        _statusMessage,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: _analysisResult != null && _analysisResult!['success']
                              ? Colors.green
                              : Colors.orange,
                        ),
                      ),
                      if (_imageFile == null) ...[
                        const SizedBox(height: 8),
                        const Text(
                          "📋 Fotoğraf Çekim İpuçları:\n"
                          "• Kişi tam karşıdan görünsün\n"
                          "• Kask ve yelek net görünsün\n"
                          "• İyi ışıklandırma olsun\n"
                          "• 1-2 metre mesafeden çekin",
                          textAlign: TextAlign.left,
                          style: TextStyle(fontSize: 12, color: Colors.black54),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Sonuçlar
                if (_analysisResult != null) ...[
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            "Tespit Sonuçları:",
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 10),
                          _buildResultItem(
                            "Kask",
                            _analysisResult!['detected_items']['Kask'] ?? false,
                          ),
                          _buildResultItem(
                            "Yelek",
                            _analysisResult!['detected_items']['Yelek'] ?? false,
                          ),
                          if (_analysisResult!['missing_items'] != null &&
                              (_analysisResult!['missing_items'] as List).isNotEmpty) ...[
                            const SizedBox(height: 10),
                            const Divider(),
                            const Text(
                              "Eksik Ekipmanlar:",
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.red,
                              ),
                            ),
                            const SizedBox(height: 5),
                            ...(_analysisResult!['missing_items'] as List)
                                .map((item) => Text(
                                      "• $item",
                                      style: const TextStyle(color: Colors.red),
                                    ))
                                .toList(),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildResultItem(String label, bool detected) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(
            detected ? Icons.check_circle : Icons.cancel,
            color: detected ? Colors.green : Colors.red,
          ),
          const SizedBox(width: 10),
          Text(
            "$label: ${detected ? 'Var' : 'Yok'}",
            style: const TextStyle(fontSize: 16),
          ),
        ],
      ),
    );
  }
}
