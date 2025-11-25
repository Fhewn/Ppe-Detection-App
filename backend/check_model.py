from ultralytics import YOLO
import os

model_path = os.path.join(os.path.dirname(__file__), "models", "ppe.pt")
model = YOLO(model_path)

print("=" * 50)
print("MODEL CLASS İSİMLERİ:")
print("=" * 50)
print(model.names)
print("=" * 50)
