from time import sleep
import cv2

class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            # It's good to provide more specific error messages
            raise Exception("Could not open camera. Please ensure it is connected and not in use by another application.")

    def get_frame(self):
        """
        Reads a frame from the camera, encodes it as JPEG, and returns the bytes.
        """
        ret, frame = self.capture.read()
        if not ret:
            raise Exception("Could not read frame from camera.")
        
        # Flip the frame horizontally (mirror effect)
        frame = cv2.flip(frame, 1)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            raise Exception("Could not encode frame to JPEG.")
        return buffer.tobytes()

    def capture_image(self, delay=0): # Changed default delay to 0
        """
        Captures a single raw image frame after an optional delay.
        """
        if delay > 0:
            sleep(delay)
        ret, frame = self.capture.read()
        if not ret:
            raise Exception("Could not read frame from camera.")
        
        # Flip the frame horizontally (mirror effect)
        frame = cv2.flip(frame, 1)
        return frame

    def release(self): # Renamed for consistency with app.py
        """
        Releases the camera resource.
        """
        if self.capture and self.capture.isOpened():
            self.capture.release()
        # cv2.destroyAllWindows() is generally not needed for web applications
        # as there's no GUI window opened by OpenCV directly.