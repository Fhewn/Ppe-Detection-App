from tkinter import Tk, Button, Label
import cv2
import time
from camera import Camera
from detector import Detector

class PPEInspectorUI:
    def __init__(self, master):
        self.master = master
        master.title("PPE Inspector")

        self.label = Label(master, text="Press the button to capture an image and validate PPE.")
        self.label.pack()

        self.capture_button = Button(master, text="Capture Image", command=self.capture_and_validate)
        self.capture_button.pack()

        self.result_label = Label(master, text="")
        self.result_label.pack()

        self.camera = Camera()
        self.detector = Detector()

    def capture_and_validate(self):
        self.label.config(text="Capturing image...")
        self.master.update()
        time.sleep(3)  # Wait for 3 seconds before capturing

        image = self.camera.capture_image()
        result = self.detector.validate_ppe(image)

        self.result_label.config(text=result)

if __name__ == "__main__":
    root = Tk()
    ppe_inspector_ui = PPEInspectorUI(root)
    root.mainloop()