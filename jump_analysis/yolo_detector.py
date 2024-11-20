from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_keypoints(self, frame):
        results = self.model(frame)
        keypoints = []
        for result in results.xyxy:
            keypoints = result.keypoints.cpu().numpy() if result.keypoints else []
        return keypoints
