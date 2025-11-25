"""
YOLOv8 modelini CoreML formatına çevir
"""
from ultralytics import YOLO
import os

def convert_to_coreml():
    """
    backend/models/ppe_new.pt'yi CoreML'e çevir
    """
    model_path = 'backend/models/ppe_new.pt'
    
    if not os.path.exists(model_path):
        model_path = 'backend/models/ppe.pt'
    
    if not os.path.exists(model_path):
        print("❌ Model bulunamadı!")
        return
    
    print(f"🤖 Model yükleniyor: {model_path}")
    model = YOLO(model_path)
    
    print("🔄 CoreML formatına çevriliyor...")
    model.export(format='coreml', nms=True)
    
    print("✅ CoreML modeli oluşturuldu!")
    print("📁 Dosya: ppe_new.mlpackage veya ppe.mlpackage")
    print("\n📱 iOS'a eklemek için:")
    print("1. .mlpackage dosyasını Xcode'da ios/Runner/ klasörüne sürükle")
    print("2. 'Copy items if needed' seç")
    print("3. Target: Runner seç")

if __name__ == '__main__':
    convert_to_coreml()
