from ultralytics import YOLO
import numpy as np

class YOLODetector:
    def __init__(self, model_path):
        # Load the YOLO model
        self.model = YOLO(model_path)

    def detect_keypoints(self, frame):
        # Run the YOLO model on the frame
        results = self.model(frame)

        keypoints = []  # List to store all keypoints for detected people

        # Loop through detections in the results
        for result in results:
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                # Convert keypoints to numpy array
                keypoints_array = result.keypoints.cpu().numpy()
                
                # Optional: Restructure the keypoints array for easier access
                # Format: [[x1, y1, confidence1], [x2, y2, confidence2], ...]
                for keypoint_set in keypoints_array:
                    keypoints.append(keypoint_set)

        # Debugging: Print the structure of extracted keypoints
        if not keypoints:
            print("No keypoints detected.")
        else:
            print(f"Extracted {len(keypoints)} keypoints sets:")
            for i, person_keypoints in enumerate(keypoints):
                print(f"Person {i+1}: {person_keypoints}")

        return keypoints
