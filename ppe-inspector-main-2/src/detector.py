from ultralytics import YOLO
import cv2
import numpy as np
import os

class Detector:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "models", "ppe.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
        self.model = YOLO(model_path)
        
    def validate_ppe(self, image):
        # 'image' is already a NumPy array in RGB format here.
        # Let's manually lower the confidence threshold to catch weaker detections.
        # This is important for debugging.
        # Normally, this value could be around 0.25.
        results = self.model(image, conf=0.1)
        
        # Check for detected objects
        # We are simplifying the logic: let's focus on detecting the presence of all equipment.
        # Initially, all are considered 'not detected', and will be set to 'detected' if found.
        detected_items = {
            "helmet": False,
            "vest": False,
            "mask": False
        }
        
        print(f"Initial detected_items: {detected_items}")
        print("\n--- Model Detection Start ---")
        for r in results:
            # --- Debugging: Visualize Results ---
            # Let's draw the detections using ultralytics' own plot() method.
            # This method returns an image even if there are no detections.
            # The returned image is in BGR format and can be saved directly with cv2.imwrite.
            # We will always save this image for debugging.
            annotated_image = r.plot()
            # Print all class names recognized by the model (very important for debugging)
            if hasattr(r, 'names') and r.names:
                print(f"Classes recognized by model (r.names): {r.names}")
            else:
                print("Model class names (r.names) not found or empty.")

            boxes = r.boxes
            if not boxes:
                print("No bounding boxes detected in this result object.")
                continue

            for box in boxes:
                c = box.cls[0]
                conf = box.conf[0]
                try:
                    class_name = r.names[int(c)]
                except (KeyError, IndexError):
                    print(f"ERROR: No name found in the model for class ID {int(c)}.")
                    continue

                print(f"Detected Object: '{class_name}', Confidence: {conf:.2f}, Class ID: {int(c)}")

                # Let's normalize the class name by converting to lowercase and removing spaces.
                # This can resolve issues with case sensitivity or spacing.
                normalized_class_name = class_name.lower().replace(' ', '') # remove spaces, convert to lowercase
                print(f"Normalized Class Name: '{normalized_class_name}'") # Debug print: Normalized class name
                
                # Apply the new detection logic
                if normalized_class_name == 'hardhat':
                    detected_items['helmet'] = True
                    print("Detection: Wearing Helmet.")
                elif normalized_class_name == 'mask':
                    detected_items['mask'] = True
                    print("Detection: Wearing Mask.")
                elif normalized_class_name == 'safetyvest':
                    detected_items['vest'] = True
                    print("Detection: Wearing Vest.")
                elif normalized_class_name == 'no-mask':
                    detected_items['mask'] = False # If 'no-mask' is detected, it means no mask.
                    print("Detection: NOT Wearing Mask.")
                elif normalized_class_name == 'no-safetyvest':
                    detected_items['vest'] = False # If 'no-safetyvest' is detected, it means no vest.
                    print("Detection: NOT Wearing Vest.")
                elif normalized_class_name not in ['person']: # Ignore irrelevant classes like 'person'
                    print(f"WARNING: Unexpected class detected: '{class_name}'")
        
        print(f"detected_items after loop: {detected_items}") # Debug print: state of detected_items after the loop
        # Determine missing items
        missing_items = [item for item, detected in detected_items.items() if not detected]
        
        # Save the image with detections (for debugging)
        save_path_annotated = os.path.join(os.path.dirname(__file__), "detected_image.jpg")
        cv2.imwrite(save_path_annotated, annotated_image)
        print(f"Image with detections saved to: {save_path_annotated}")
        
        print(f"Detection Summary: {detected_items}")
        print("--- Model Detection End ---\n")

        return {
            "success": len(missing_items) == 0,
            "detected_items": detected_items,
            "missing_items": missing_items
        }