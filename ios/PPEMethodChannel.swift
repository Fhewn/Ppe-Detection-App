import Flutter
import UIKit

class PPEMethodChannel {
    
    static func register(with registrar: FlutterPluginRegistrar) {
        let channel = FlutterMethodChannel(
            name: "com.example.ppe_detection/coreml",
            binaryMessenger: registrar.messenger()
        )
        
        channel.setMethodCallHandler { call, result in
            switch call.method {
            case "detectPPE":
                handleDetectPPE(call: call, result: result)
            default:
                result(FlutterMethodNotImplemented)
            }
        }
    }
    
    private static func handleDetectPPE(call: FlutterMethodCall, result: @escaping FlutterResult) {
        guard let args = call.arguments as? [String: Any],
              let imageData = args["imageBytes"] as? FlutterStandardTypedData else {
            result(FlutterError(code: "INVALID_ARGUMENT",
                              message: "Image bytes required",
                              details: nil))
            return
        }
        
        guard let image = UIImage(data: imageData.data) else {
            result(FlutterError(code: "INVALID_IMAGE",
                              message: "Could not decode image",
                              details: nil))
            return
        }
        
        PPEDetector.shared.detectPPE(image: image) { detections in
            result(detections)
        }
    }
}
