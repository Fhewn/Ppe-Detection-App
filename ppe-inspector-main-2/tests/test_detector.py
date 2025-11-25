from src.detector import Detector

def test_detector_initialization():
    detector = Detector("src/models/ppe.pt")
    assert detector is not None

def test_detect_ppe():
    detector = Detector("src/models/ppe.pt")
    test_image_path = "tests/test_image.jpg"  # Path to a test image with PPE
    results = detector.detect(test_image_path)
    
    assert "hard_hat" in results
    assert "vest" in results
    assert "mask" in results

def test_detect_no_ppe():
    detector = Detector("src/models/ppe.pt")
    test_image_path = "tests/test_image_no_ppe.jpg"  # Path to a test image without PPE
    results = detector.detect(test_image_path)
    
    assert "hard_hat" not in results
    assert "vest" not in results
    assert "mask" not in results