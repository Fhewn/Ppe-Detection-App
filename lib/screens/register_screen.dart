import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  CameraController? _controller;
  Future<void>? _initializeControllerFuture;
  bool _isProcessing = false;
  String _statusMessage = "";
  bool _photoTaken = false;
  String? _capturedImagePath;
  
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _surnameController = TextEditingController();

  // Backend URL - VPS
  final String serverUrl = "http://72.62.60.125:5002/api/register_user";

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    final firstCamera = cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.front,
      orElse: () => cameras.first,
    );

    _controller = CameraController(
      firstCamera,
      ResolutionPreset.medium,
    );

    _initializeControllerFuture = _controller!.initialize();
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _controller?.dispose();
    _nameController.dispose();
    _surnameController.dispose();
    super.dispose();
  }

  Future<void> _takeFacePhoto() async {
    if (_controller == null || !_controller!.value.isInitialized) return;

    setState(() {
      _isProcessing = true;
      _statusMessage = "Fotoğraf çekiliyor...";
    });

    try {
      final image = await _controller!.takePicture();
      setState(() {
        _photoTaken = true;
        _capturedImagePath = image.path;
        _statusMessage = "✅ Fotoğraf çekildi! Şimdi bilgilerinizi girin.";
        _isProcessing = false;
      });
    } catch (e) {
      setState(() {
        _statusMessage = "Hata: $e";
        _isProcessing = false;
      });
    }
  }

  Future<void> _retakePhoto() async {
    setState(() {
      _photoTaken = false;
      _capturedImagePath = null;
      _statusMessage = "";
    });
    await _initializeCamera();
  }

  Future<void> _register() async {
    if (_capturedImagePath == null) {
      setState(() {
        _statusMessage = "Lütfen önce fotoğraf çekin";
      });
      return;
    }
    
    if (_nameController.text.isEmpty || _surnameController.text.isEmpty) {
      setState(() {
        _statusMessage = "Lütfen ad ve soyad giriniz";
      });
      return;
    }

    setState(() {
      _isProcessing = true;
      _statusMessage = "Yüz analiz ediliyor ve sicil no oluşturuluyor...";
    });

    try {
      var uri = Uri.parse(serverUrl);
      var request = http.MultipartRequest('POST', uri);
      
      request.fields['name'] = _nameController.text;
      request.fields['surname'] = _surnameController.text;
      
      request.files.add(
        await http.MultipartFile.fromPath(
          'image',
          _capturedImagePath!,
          filename: 'register_face.jpg',
        ),
      );

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success']) {
          final user = data['user'];
          if (mounted) {
            showDialog(
              context: context,
              barrierDismissible: false,
              builder: (context) => AlertDialog(
                title: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green, size: 32),
                    SizedBox(width: 10),
                    Text("Kayıt Başarılı"),
                  ],
                ),
                content: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Hoşgeldiniz!",
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 10),
                    Text("Ad Soyad: ${user['name']} ${user['surname']}"),
                    SizedBox(height: 5),
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.blue.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.badge, color: Colors.blue),
                          SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "Sicil Numaranız",
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                              ),
                              Text(
                                "${user['sicil_no']}",
                                style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue.shade900,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: 10),
                    Text(
                      "⚠️ Bu numarayı not ediniz!",
                      style: TextStyle(
                        color: Colors.orange.shade700,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 5),
                    Text(
                      "Giriş yaparken yüzünüz otomatik olarak tanınacaktır.",
                      style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                    ),
                  ],
                ),
                actions: [
                  TextButton(
                    onPressed: () async {
                      Navigator.of(context).pop(); // Close dialog
                      
                      // Kamera controller'ı dispose et
                      if (_controller != null) {
                        await _controller!.dispose();
                        _controller = null;
                      }
                      
                      Navigator.of(context).pop(); // Go back to login
                    },
                    child: Text("Giriş Ekranına Dön", style: TextStyle(fontSize: 16)),
                  ),
                ],
              ),
            );
          }
        } else {
          setState(() {
            _statusMessage = "❌ Kayıt başarısız: ${data['message']}";
          });
        }
      } else {
        setState(() {
          _statusMessage = "❌ Sunucu hatası: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = "❌ Hata: $e";
      });
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF667eea),
              Color(0xFF764ba2),
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            child: Column(
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Row(
                    children: [
                      IconButton(
                        icon: Icon(Icons.arrow_back, color: Colors.white),
                        onPressed: () async {
                          // Kamera controller'ı dispose et
                          if (_controller != null) {
                            await _controller!.dispose();
                            _controller = null;
                          }
                          Navigator.pop(context);
                        },
                      ),
                      SizedBox(width: 10),
                      Text(
                        "Yeni Kayıt",
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Camera Preview
                Container(
                  margin: EdgeInsets.symmetric(horizontal: 20),
                  height: 400,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 10,
                        offset: Offset(0, 5),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: _photoTaken && _capturedImagePath != null
                        ? Stack(
                            fit: StackFit.expand,
                            children: [
                              Image.file(
                                File(_capturedImagePath!),
                                fit: BoxFit.cover,
                              ),
                              Positioned(
                                top: 10,
                                right: 10,
                                child: Container(
                                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: Colors.green,
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.check, color: Colors.white, size: 16),
                                      SizedBox(width: 5),
                                      Text(
                                        "Fotoğraf Çekildi",
                                        style: TextStyle(color: Colors.white, fontSize: 12),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          )
                        : FutureBuilder<void>(
                            future: _initializeControllerFuture,
                            builder: (context, snapshot) {
                              if (snapshot.connectionState == ConnectionState.done) {
                                return Stack(
                                  alignment: Alignment.center,
                                  children: [
                                    CameraPreview(_controller!),
                                    Container(
                                      width: 250,
                                      height: 250,
                                      decoration: BoxDecoration(
                                        border: Border.all(color: Colors.white, width: 3),
                                        borderRadius: BorderRadius.circular(125),
                                      ),
                                    ),
                                    Positioned(
                                      bottom: 20,
                                      child: Container(
                                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                        decoration: BoxDecoration(
                                          color: Colors.black54,
                                          borderRadius: BorderRadius.circular(20),
                                        ),
                                        child: Text(
                                          "Yüzünüzü çerçeveye yerleştirin",
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 14,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                );
                              } else {
                                return Center(child: CircularProgressIndicator(color: Colors.white));
                              }
                            },
                          ),
                  ),
                ),
                
                SizedBox(height: 20),
                
                // Take Photo Button - Always visible
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : (_photoTaken ? _retakePhoto : _takeFacePhoto),
                    icon: Icon(_photoTaken ? Icons.refresh : Icons.camera_alt, size: 28),
                    label: Text(
                      _photoTaken ? "Yeniden Çek" : "Fotoğraf Çek",
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                      backgroundColor: Colors.white,
                      foregroundColor: Color(0xFF667eea),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                  ),
                ),
                
                SizedBox(height: 20),
                
                // Form Fields - Always visible after photo
                if (_photoTaken)
                  Container(
                    margin: EdgeInsets.all(20),
                    padding: EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black26,
                          blurRadius: 10,
                          offset: Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        // Info text
                        Container(
                          padding: EdgeInsets.all(12),
                          margin: EdgeInsets.only(bottom: 15),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade50,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.blue.shade200),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.info_outline, color: Colors.blue.shade700),
                              SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  "Bilgilerinizi girin, sicil numaranız otomatik oluşturulacak",
                                  style: TextStyle(
                                    color: Colors.blue.shade900,
                                    fontSize: 13,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        
                        TextField(
                          controller: _nameController,
                          decoration: InputDecoration(
                            labelText: "Ad",
                            prefixIcon: Icon(Icons.person),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            filled: true,
                            fillColor: Colors.grey.shade50,
                          ),
                        ),
                        SizedBox(height: 15),
                        TextField(
                          controller: _surnameController,
                          decoration: InputDecoration(
                            labelText: "Soyad",
                            prefixIcon: Icon(Icons.person_outline),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            filled: true,
                            fillColor: Colors.grey.shade50,
                          ),
                        ),
                        SizedBox(height: 20),
                        
                        if (_statusMessage.isNotEmpty)
                          Container(
                            padding: EdgeInsets.all(12),
                            margin: EdgeInsets.only(bottom: 15),
                            decoration: BoxDecoration(
                              color: _statusMessage.contains("❌") 
                                  ? Colors.red.shade50 
                                  : Colors.blue.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: _statusMessage.contains("❌") 
                                    ? Colors.red.shade200 
                                    : Colors.blue.shade200,
                              ),
                            ),
                            child: Text(
                              _statusMessage,
                              style: TextStyle(
                                color: _statusMessage.contains("❌") 
                                    ? Colors.red.shade900 
                                    : Colors.blue.shade900,
                                fontWeight: FontWeight.w500,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        
                        // Register Button
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _isProcessing ? null : _register,
                            icon: _isProcessing 
                                ? SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      color: Colors.white,
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Icon(Icons.check_circle, size: 24),
                            label: Text(
                              _isProcessing ? "Sicil No Oluşturuluyor..." : "Kayıt Ol",
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              padding: EdgeInsets.symmetric(vertical: 16),
                              backgroundColor: Color(0xFF667eea),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                
                SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
