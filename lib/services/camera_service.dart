import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';

class CameraService {
  CameraController? _controller;
  bool _isInitialized = false;

  CameraController? get controller => _controller;
  bool get isInitialized => _isInitialized;

  Future<void> initializeCamera() async {
    try {
      final cameras = await availableCameras();
      
      if (cameras.isEmpty) {
        throw Exception('Kamera bulunamadı');
      }
      
      final camera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      _controller = CameraController(
        camera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _controller?.initialize();
      _isInitialized = true;
    } catch (e) {
      _isInitialized = false;
      rethrow;
    }
  }

  Future<void> startCamera() async {
    // Kamera kullanıma hazır
  }

  Future<void> stopCamera() async {
    try {
      await _controller?.stopImageStream();
    } catch (e) {
      // Durdurma hatalarını yoksay
    }
  }

  Future<void> dispose() async {
    try {
      await _controller?.dispose();
      _isInitialized = false;
    } catch (e) {
      // Temizleme hatalarını yoksay
    }
  }
}