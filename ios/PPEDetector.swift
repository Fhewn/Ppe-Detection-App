import Foundation
import CoreML
import Vision
import UIKit

@objc class PPEDetector: NSObject {
    
    private var model: VNCoreMLModel?
    
    @objc static let shared = PPEDetector()
    
    private override init() {
        super.init()
        loadModel()
    }
    
    private func loadModel() {
        // Load PPE Detection Core ML model
        do {
            // Try to load compiled model first
            if let modelURL = Bundle.main.url(forResource: "PPEDetection", withExtension: "mlmodelc") {
                let mlModel = try MLModel(contentsOf: modelURL)
                model = try VNCoreMLModel(for: mlModel)
                print("✅ Core ML model loaded successfully from compiled model")
            } else {
                print("❌ Model file not found in bundle")
                print("Make sure PPEDetection.mlmodel is added to Xcode project")
            }
        } catch {
            print("❌ Failed to load model: \(error)")
        }
    }
    
    @objc func detectPPE(image: UIImage, completion: @escaping ([String: Any]) -> Void) {
        guard let model = model else {
            completion(["error": "Model not loaded"])
            return
        }
        
        guard let ciImage = CIImage(image: image) else {
            completion(["error": "Invalid image"])
            return
        }
        
        let request = VNCoreMLRequest(model: model) { request, error in
            if let error = error {
                completion(["error": error.localizedDescription])
                return
            }
            
            guard let results = request.results as? [VNRecognizedObjectObservation] else {
                completion(["detections": []])
                return
            }
            
            // Parse detections
            var detections: [[String: Any]] = []
            
            for observation in results {
                guard let topLabel = observation.labels.first else { continue }
                
                let boundingBox = observation.boundingBox
                
                // Convert normalized coordinates to pixel coordinates
                let imageWidth = ciImage.extent.width
                let imageHeight = ciImage.extent.height
                
                let detection: [String: Any] = [
                    "label": topLabel.identifier,
                    "confidence": topLabel.confidence,
                    "x": boundingBox.origin.x * imageWidth,
                    "y": (1 - boundingBox.origin.y - boundingBox.height) * imageHeight,
                    "width": boundingBox.width * imageWidth,
                    "height": boundingBox.height * imageHeight
                ]
                
                detections.append(detection)
            }
            
            completion(["detections": detections])
        }
        
        request.imageCropAndScaleOption = .scaleFill
        
        let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])
        
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                try handler.perform([request])
            } catch {
                completion(["error": error.localizedDescription])
            }
        }
    }
}
