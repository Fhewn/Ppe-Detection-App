import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'register_screen.dart';
import 'simple_check_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  CameraController? _controller;
  Future<void>? _initializeControllerFuture;
  bool _isProcessing = false;
  String _statusMessage = "";
  Map<String, dynamic>? _loggedInUser;

  // Backend URL - VPS
  final String serverUrl = "http://72.62.60.125:5002/api/login_user"; 

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
    super.dispose();
  }

  Future<void> _captureAndLogin() async {
    if (_controller == null || !_controller!.value.isInitialized) return;

    setState(() {
      _isProcessing = true;
      _statusMessage = "Yüzünüz taranıyor...";
      _loggedInUser = null;
    });

    try {
      final image = await _controller!.takePicture();
      
      var uri = Uri.parse(serverUrl);
      var request = http.MultipartRequest('POST', uri);
      
      request.files.add(
        await http.MultipartFile.fromPath(
          'image',
          image.path,
          filename: 'login_face.jpg',
        ),
      );

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success']) {
          final user = data['user'];
          setState(() {
            _loggedInUser = user;
            _statusMessage = "✅ Giriş başarılı!";
          });
          
          // 2 saniye bekle ve sonra ana ekrana geç
          await Future.delayed(Duration(seconds: 2));
          
          if (mounted) {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(
                builder: (context) => SimpleCheckScreen(
                  userName: "${user['name']} ${user['surname']}",
                  sicilNo: user['sicil_no'],
                ),
              ),
            );
          }
        } else {
          setState(() {
            _statusMessage = "❌ ${data['message']}";
          });
        }
      } else if (response.statusCode == 401) {
        setState(() {
          _statusMessage = "❌ Kullanıcı tanınamadı. Lütfen kayıt olun.";
        });
      } else {
        setState(() {
          _statusMessage = "❌ Sunucu hatası: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = "❌ Bağlantı hatası: $e";
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
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                    SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "Yüz Tanıma Girişi",
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          "Yüzünüzü kameraya gösterin",
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.white70,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              // Camera Preview
              Expanded(
                child: Container(
                  margin: EdgeInsets.symmetric(horizontal: 20),
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
                    child: FutureBuilder<void>(
                      future: _initializeControllerFuture,
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.done) {
                          return Stack(
                            alignment: Alignment.center,
                            children: [
                              CameraPreview(_controller!),
                              // Face oval guide
                              Container(
                                width: 280,
                                height: 350,
                                decoration: BoxDecoration(
                                  border: Border.all(
                                    color: _loggedInUser != null 
                                        ? Colors.green 
                                        : Colors.white,
                                    width: 3,
                                  ),
                                  borderRadius: BorderRadius.circular(140),
                                ),
                              ),
                              // Instructions
                              if (_loggedInUser == null)
                                Positioned(
                                  bottom: 30,
                                  child: Container(
                                    padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                                    decoration: BoxDecoration(
                                      color: Colors.black54,
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                    child: Text(
                                      "Yüzünüzü çerçeveye yerleştirin",
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 16,
                                      ),
                                    ),
                                  ),
                                ),
                              // Success overlay
                              if (_loggedInUser != null)
                                Container(
                                  color: Colors.black54,
                                  child: Center(
                                    child: Column(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Icon(
                                          Icons.check_circle,
                                          color: Colors.green,
                                          size: 80,
                                        ),
                                        SizedBox(height: 20),
                                        Text(
                                          "Hoşgeldiniz!",
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 28,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        SizedBox(height: 10),
                                        Text(
                                          "${_loggedInUser!['name']} ${_loggedInUser!['surname']}",
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 22,
                                          ),
                                        ),
                                        SizedBox(height: 5),
                                        Container(
                                          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                          decoration: BoxDecoration(
                                            color: Colors.white24,
                                            borderRadius: BorderRadius.circular(20),
                                          ),
                                          child: Text(
                                            "Sicil No: ${_loggedInUser!['sicil_no']}",
                                            style: TextStyle(
                                              color: Colors.white,
                                              fontSize: 16,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                            ],
                          );
                        } else {
                          return Center(
                            child: CircularProgressIndicator(color: Colors.white),
                          );
                        }
                      },
                    ),
                  ),
                ),
              ),
              
              // Bottom Section
              Container(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    // Status Message
                    if (_statusMessage.isNotEmpty)
                      Container(
                        padding: EdgeInsets.all(12),
                        margin: EdgeInsets.only(bottom: 15),
                        decoration: BoxDecoration(
                          color: _statusMessage.contains("❌") 
                              ? Colors.red.shade50 
                              : _statusMessage.contains("✅")
                                  ? Colors.green.shade50
                                  : Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _statusMessage.contains("❌") 
                                ? Colors.red.shade200 
                                : _statusMessage.contains("✅")
                                    ? Colors.green.shade200
                                    : Colors.blue.shade200,
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _statusMessage.contains("❌") 
                                  ? Icons.error_outline 
                                  : _statusMessage.contains("✅")
                                      ? Icons.check_circle_outline
                                      : Icons.info_outline,
                              color: _statusMessage.contains("❌") 
                                  ? Colors.red.shade700 
                                  : _statusMessage.contains("✅")
                                      ? Colors.green.shade700
                                      : Colors.blue.shade700,
                            ),
                            SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                _statusMessage,
                                style: TextStyle(
                                  color: _statusMessage.contains("❌") 
                                      ? Colors.red.shade900 
                                      : _statusMessage.contains("✅")
                                          ? Colors.green.shade900
                                          : Colors.blue.shade900,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    
                    // Buttons
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _isProcessing ? null : _captureAndLogin,
                            icon: _isProcessing 
                                ? SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      color: Color(0xFF667eea),
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Icon(Icons.face_retouching_natural, size: 28),
                            label: Text(
                              _isProcessing ? "Taranıyor..." : "Giriş Yap",
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              padding: EdgeInsets.symmetric(vertical: 16),
                              backgroundColor: Colors.white,
                              foregroundColor: Color(0xFF667eea),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(30),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    SizedBox(height: 15),
                    
                    // Register Button
                    TextButton.icon(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (context) => const RegisterScreen()),
                        );
                      },
                      icon: Icon(Icons.person_add, color: Colors.white),
                      label: Text(
                        "Hesabınız yok mu? Kayıt Olun",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
