from flask import Flask, render_template, Response, jsonify
from camera import Camera
from detector import Detector
import time
import cv2
import os

app = Flask(__name__)

# --- Singleton Camera Management ---
# Instead of using the global camera object directly,
# we will use a function that controls access to it.
_camera_instance = None

def get_camera():
    """
    Creates and returns a single camera object throughout the application (Singleton Pattern).
    """
    global _camera_instance
    if _camera_instance is None or not _camera_instance.capture.isOpened():
        try:
            _camera_instance = Camera()
        except Exception as e:
            # print(f"ERROR: Could not initialize camera: {e}") # Removed for debugging
            _camera_instance = None # Leave as None on failure
    return _camera_instance

detector = Detector()

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames():
    """Generator function that yields frames for the video stream."""
    camera_obj = get_camera()
    if not camera_obj:
        # print("Camera not found for video stream.") # Removed for debugging
        return

    try:
        while True:
            frame = camera_obj.get_frame()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        # print(f"Error during video stream: {e}") # Removed for debugging
        pass

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    try:
        camera_obj = get_camera()
        if not camera_obj:
            return jsonify({"error": "Could not initialize or find the camera."}), 500

        # print("Waiting for 3 seconds...") # Removed for debugging
        time.sleep(3)  # Wait for 3 seconds
        
        # Capture image from camera (it's in BGR format)
        image_bgr = camera_obj.capture_image()
        if image_bgr is None:
            return jsonify({"error": "Could not capture image."}), 400

        # --- Debug: Save Original Image to Disk ---
        save_path = os.path.join(os.path.dirname(__file__), "captured_image.jpg")
        cv2.imwrite(save_path, image_bgr)
        print(f"Original image saved to: {save_path}")
        
        # Convert the image from BGR (OpenCV default) to RGB (model expected format)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        results = detector.validate_ppe(image_rgb)
        return jsonify(results)
        
    except Exception as e:
        print(f"Critical error during capture: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stop')
def stop_camera():
    # --- VERY IMPORTANT: Check this section to solve SyntaxError ---
    # Inside this function, before the 'global _camera_instance' line,
    # DO NOT make any assignment to the '_camera_instance' variable (e.g., _camera_instance = None).
    # If it exists, delete that line. The 'global' declaration must be the FIRST reference to this variable.
    global _camera_instance
    if _camera_instance:
        _camera_instance.release()
        _camera_instance = None
        # print("Camera released.") # Removed for debugging
    return jsonify({"message": "Camera closed"})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # Ensure the camera is released when the application shuts down
        if _camera_instance:
            _camera_instance.release()
            # print("Camera released on application shutdown.")