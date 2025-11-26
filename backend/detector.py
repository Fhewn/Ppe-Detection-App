from ultralytics import YOLO
import cv2
import numpy as np
import os

class Detector:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "models", "ppe.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
        # Optimize model for faster inference
        self.model = YOLO(model_path)
        self.model.fuse()  # Fuse layers for faster inference
    
    def check_image_quality(self, image):
        """Görüntü kalitesini kontrol et (bulanıklık tespiti)"""
        # Laplacian variance ile bulanıklık tespiti
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Parlaklık kontrolü
        brightness = np.mean(gray)
        
        print(f"📊 Görüntü Kalitesi:")
        print(f"  - Netlik skoru: {laplacian_var:.2f} (>100 iyi, <50 bulanık)")
        print(f"  - Parlaklık: {brightness:.2f} (50-200 arası ideal)")
        
        quality_issues = []
        
        if laplacian_var < 50:
            quality_issues.append("Görüntü çok bulanık")
        elif laplacian_var < 100:
            quality_issues.append("Görüntü biraz bulanık")
            
        if brightness < 50:
            quality_issues.append("Görüntü çok karanlık")
        elif brightness > 200:
            quality_issues.append("Görüntü çok parlak")
        
        return {
            'is_good': len(quality_issues) == 0,
            'sharpness': laplacian_var,
            'brightness': brightness,
            'issues': quality_issues
        }
    
    def enhance_image(self, image):
        """Görüntüyü iyileştir"""
        # Kontrast ve parlaklık ayarı (CLAHE)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        # Hafif keskinleştirme
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Orijinal ile karıştır (çok keskin olmasın)
        result = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)
        
        return result
        
    def validate_ppe(self, image):
        # Görüntü kalitesini kontrol et
        quality = self.check_image_quality(image)
        
        # Eğer görüntü kalitesi düşükse, iyileştir
        if not quality['is_good']:
            print("⚠️ Görüntü kalitesi düşük, iyileştiriliyor...")
            for issue in quality['issues']:
                print(f"  - {issue}")
            image = self.enhance_image(image)
            print("✨ Görüntü iyileştirildi!")
        else:
            print("✅ Görüntü kalitesi iyi!")
        
        # Low confidence threshold for better detection
        results = self.model(image, conf=0.01, imgsz=640, verbose=False)
        
        # Track best confidence for each item
        helmet_detections = []  # (has_helmet, confidence)
        vest_detections = []    # (has_vest, confidence)
        
        print("\n🔍 Tespit edilen tüm nesneler:")
        for r in results:
            boxes = r.boxes
            if not boxes:
                print("  ❌ Hiç nesne tespit edilmedi")
                continue

            for box in boxes:
                c = box.cls[0]
                conf = float(box.conf[0])
                try:
                    class_name = r.names[int(c)]
                except (KeyError, IndexError):
                    continue

                normalized_class_name = class_name.lower().replace(' ', '')
                print(f"  📦 {class_name} (confidence: {conf:.2f})")
                
                # Collect all detections with confidence
                if normalized_class_name == 'hardhat':
                    helmet_detections.append((True, conf))
                    print(f"    ✅ KASK VAR!")
                elif normalized_class_name == 'no-hardhat':
                    helmet_detections.append((False, conf))
                    print(f"    ❌ KASK YOK!")
                elif normalized_class_name == 'safetyvest':
                    vest_detections.append((True, conf))
                    print(f"    ✅ YELEK VAR!")
                elif normalized_class_name == 'no-safetyvest':
                    vest_detections.append((False, conf))
                    print(f"    ❌ YELEK YOK!")
        
        # Use smart logic: require minimum 0.60 confidence for positive detections
        detected_items = {
            "helmet": False,
            "vest": False
        }
        
        MIN_CONFIDENCE = 0.40  # Minimum confidence for positive detection
        
        if helmet_detections:
            # Sort by confidence
            positive = sorted([d for d in helmet_detections if d[0] == True], key=lambda x: x[1], reverse=True)
            negative = sorted([d for d in helmet_detections if d[0] == False], key=lambda x: x[1], reverse=True)
            
            if positive and positive[0][1] >= MIN_CONFIDENCE:
                detected_items['helmet'] = True
                print(f"  🎯 KASK Sonuç: VAR (conf: {positive[0][1]:.2f}) ✓")
            else:
                detected_items['helmet'] = False
                if positive:
                    print(f"  🎯 KASK Sonuç: YOK (pozitif tespit yetersiz: {positive[0][1]:.2f} < {MIN_CONFIDENCE})")
                elif negative:
                    print(f"  🎯 KASK Sonuç: YOK (negatif tespit: {negative[0][1]:.2f})")
                else:
                    print(f"  🎯 KASK Sonuç: YOK (tespit yok)")
        
        if vest_detections:
            # Sort by confidence
            positive = sorted([d for d in vest_detections if d[0] == True], key=lambda x: x[1], reverse=True)
            negative = sorted([d for d in vest_detections if d[0] == False], key=lambda x: x[1], reverse=True)
            
            if positive and positive[0][1] >= MIN_CONFIDENCE:
                detected_items['vest'] = True
                print(f"  🎯 YELEK Sonuç: VAR (conf: {positive[0][1]:.2f}) ✓")
            else:
                detected_items['vest'] = False
                if positive:
                    print(f"  🎯 YELEK Sonuç: YOK (pozitif tespit yetersiz: {positive[0][1]:.2f} < {MIN_CONFIDENCE})")
                elif negative:
                    print(f"  🎯 YELEK Sonuç: YOK (negatif tespit: {negative[0][1]:.2f})")
                else:
                    print(f"  🎯 YELEK Sonuç: YOK (tespit yok)")
        
        missing_items = [item for item, detected in detected_items.items() if not detected]
        
        print(f"✓ Final Sonuç: {detected_items}, Eksik: {missing_items}")

        return {
            "success": len(missing_items) == 0,
            "detected_items": detected_items,
            "missing_items": missing_items,
            "image_quality": quality
        }