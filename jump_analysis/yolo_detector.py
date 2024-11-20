from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_keypoints(self, frame):
        # Run YOLO detection on the frame
        results = self.model(frame)
        keypoints = []

        # Iterate through the results to extract keypoints
        for result in results:
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                keypoints.append(result.keypoints.cpu().numpy())
        
        return keypoints  # Return all keypoints as a list
