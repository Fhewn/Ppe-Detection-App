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
        
    def validate_ppe(self, image):
        # Very low confidence threshold to catch all detections
        results = self.model(image, conf=0.05, imgsz=640, verbose=False)
        
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
        
        # Use smart logic: prioritize positive detections if confidence is close
        detected_items = {
            "helmet": False,
            "vest": False
        }
        
        if helmet_detections:
            # Check if there's a positive detection with reasonable confidence
            positive = [d for d in helmet_detections if d[0] == True]
            negative = [d for d in helmet_detections if d[0] == False]
            
            if positive and positive[0][1] >= 0.2:  # Positive with conf >= 0.2
                detected_items['helmet'] = True
                print(f"  🎯 KASK Sonuç: VAR (conf: {positive[0][1]:.2f})")
            elif negative:
                detected_items['helmet'] = False
                print(f"  🎯 KASK Sonuç: YOK (conf: {negative[0][1]:.2f})")
        
        if vest_detections:
            # Check if there's a positive detection with reasonable confidence
            positive = [d for d in vest_detections if d[0] == True]
            negative = [d for d in vest_detections if d[0] == False]
            
            if positive and positive[0][1] >= 0.2:  # Positive with conf >= 0.2
                detected_items['vest'] = True
                print(f"  🎯 YELEK Sonuç: VAR (conf: {positive[0][1]:.2f})")
            elif negative:
                detected_items['vest'] = False
                print(f"  🎯 YELEK Sonuç: YOK (conf: {negative[0][1]:.2f})")
        
        missing_items = [item for item, detected in detected_items.items() if not detected]
        
        print(f"✓ Final Sonuç: {detected_items}, Eksik: {missing_items}")

        return {
            "success": len(missing_items) == 0,
            "detected_items": detected_items,
            "missing_items": missing_items
        }