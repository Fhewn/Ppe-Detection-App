import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    let controller = window?.rootViewController as! FlutterViewController
    
    // Core ML Method Channel'ı kaydet
    let channel = FlutterMethodChannel(
      name: "com.example.ppe_detection/coreml",
      binaryMessenger: controller.binaryMessenger
    )
    
    channel.setMethodCallHandler { call, result in
      if call.method == "detectPPE" {
        guard let args = call.arguments as? [String: Any],
              let imageData = args["imageBytes"] as? FlutterStandardTypedData else {
          result(FlutterError(code: "INVALID_ARGUMENT", message: "Görüntü baytları gerekli", details: nil))
          return
        }
        
        guard let image = UIImage(data: imageData.data) else {
          result(FlutterError(code: "INVALID_IMAGE", message: "Görüntü decode edilemedi", details: nil))
          return
        }
        
        PPEDetector.shared.detectPPE(image: image) { detections in
          result(detections)
        }
      } else {
        result(FlutterMethodNotImplemented)
      }
    }
    
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
