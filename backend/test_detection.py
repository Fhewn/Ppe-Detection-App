from ultralytics import YOLO
import cv2
import os

# Model yükle
model_path = os.path.join(os.path.dirname(__file__), "models", "ppe.pt")
model = YOLO(model_path)

print("=" * 60)
print("MODEL SINIF İSİMLERİ:")
print("=" * 60)
for idx, name in model.names.items():
    print(f"  {idx}: {name}")
print("=" * 60)
print("\nModel şu anda bu sınıfları tespit edebiliyor.")
print("Eğer 'Goggles' veya 'Gözlük' yoksa, model yeniden eğitilmeli.")
print("=" * 60)
