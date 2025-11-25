# Real-Time PPE (Personal Protective Equipment) Inspector

This project is a web-based, real-time Personal Protective Equipment (PPE) detection application built with Flask and YOLOv8. It uses a live webcam feed to detect whether a person is wearing essential safety gear such as a helmet, safety vest, and mask.

 


---

## Features

- **Live Video Stream:** Provides a real-time video feed directly in the web browser.
- **Real-Time Detection:** Utilizes a custom-trained YOLOv8 model to detect PPE items.
- **Instant Feedback:** Captures an image from the stream and provides immediate feedback on detected and missing PPE.
- **Web Interface:** A clean and responsive user interface built with Flask and Bootstrap.
- **Debugging Support:** Automatically saves the original captured image and the annotated image with detection results for easy verification.

## Tech Stack

- **Backend:** Python, Flask
- **Computer Vision:** OpenCV, Ultralytics (YOLOv8)
- **Frontend:** HTML, Bootstrap 5, JavaScript

## Project Structure

```
ppe-inspector/
├── src/
│   ├── templates/
│   │   └── index.html      # Frontend HTML template
│   ├── models/
│   │   └── ppe.pt          # Trained YOLOv8 model
│   ├── app.py              # Main Flask application
│   ├── camera.py           # Camera handling logic
│   └── detector.py         # YOLOv8 detection logic
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

- Python 3.8+
- A webcam connected to your computer.

### 2. Clone the Repository

```bash
git clone https://github.com/yadowop/ppe-inspector.git
cd ppe-inspector
```

### 3. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Navigate to the `src` directory and run the Flask application.

```bash
cd src
python app.py
```

The application will be available at `http://127.0.0.1:5000`. Open this URL in your web browser.

## How to Use

1.  Open the web application in your browser. You should see the live feed from your webcam.
2.  Position yourself in front of the camera wearing the PPE you want to check.
3.  Click the **"Check PPE"** button.
4.  The application will wait for 3 seconds, capture an image, and analyze it.
5.  The results will be displayed on the right, indicating which items were detected and which were missing.
6.  For debugging, the `captured_image.jpg` (original) and `detected_image.jpg` (with bounding boxes) will be saved in the `src` folder.

## License

This project is open-source. Feel free to use and modify it.