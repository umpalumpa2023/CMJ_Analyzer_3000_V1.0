from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_keypoints(self, frame):
        results = self.model(frame)
        keypoints = []

        # Loop through detections in results
        for result in results:
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                keypoints.extend(result.keypoints.cpu().numpy())

        return keypoints
