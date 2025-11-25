def load_image(image_path):
    import cv2
    image = cv2.imread(image_path)
    return image

def preprocess_image(image):
    # Resize the image to the input size required by the model
    import cv2
    resized_image = cv2.resize(image, (640, 640))  # Assuming the model expects 640x640 input
    return resized_image

def draw_results(image, results):
    import cv2
    for result in results:
        # Assuming result contains bounding box coordinates and label
        x1, y1, x2, y2, label = result
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

def check_ppe_presence(results):
    required_equipment = {'hard_hat': False, 'vest': False, 'mask': False}
    for result in results:
        label = result[-1]  # Assuming the label is the last element
        if label in required_equipment:
            required_equipment[label] = True
    return required_equipment