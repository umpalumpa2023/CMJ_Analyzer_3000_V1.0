import cv2
import numpy as np
import json
from config import MODEL_PATH
from jump_metrics import calculate_jump_height
from detection_logic import JumpAnalyzer
from yolo_detector import YOLODetector

# Counter movement auswertung + Dysbalane wenn Frontansicht
def save_keypoints_to_json(data, file_name="keypoints_data.json"):
    """
    Save the complete keypoints data, including all fields, to a JSON file.
    
    Parameters:
        data (list or object): Keypoints data, potentially containing custom objects, NumPy arrays, etc.
        file_name (str): The name of the JSON file to save the data.
    """
    def convert_to_serializable(obj):
        """Recursively convert objects to JSON-compatible types."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert NumPy arrays to lists
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)  # Convert NumPy floats to Python floats
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)  # Convert NumPy integers to Python integers
        elif hasattr(obj, "__dict__"):  # For objects like Keypoints with attributes
            return {key: convert_to_serializable(value) for key, value in vars(obj).items()}
        elif isinstance(obj, list):  # Recursively process lists
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):  # Recursively process dictionaries
            return {key: convert_to_serializable(value) for key, value in obj.items()}
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):  # Handle other iterable objects
            return list(map(convert_to_serializable, obj))
        return obj  # Return as-is for serializable types

    # Convert the entire data structure to a JSON-compatible format
    serializable_data = convert_to_serializable(data)
    
    # Write the JSON-compatible data to a file
    with open(file_name, "w") as json_file:
        json.dump(serializable_data, json_file, indent=4)

    print(f"Complete keypoints data saved to {file_name}")

def load_keypoints(filename="keypoints.json"):
    """
    Loads YOLO keypoints from a JSON file.

    Parameters:
    - filename: Name of the file to load the keypoints from

    Returns:
    - keypoints_array: List of keypoints (as NumPy arrays or original format)
    """
    with open(filename, "r") as f:
        data = json.load(f)

    # Convert lists back to NumPy arrays
    keypoints_array = [np.array(keypoints) for keypoints in data]
    
    print(f"Keypoints loaded from {filename}")
    return keypoints_array

def process_jump_video(video_path, user_height, progress_callback=None):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    jump_analyzer = JumpAnalyzer()
    yolo_detector = YOLODetector(MODEL_PATH)

    jumps = []  # List to store data for all detected jumps

    jump_detected = False
    takeoff_frame, landing_frame = None, None


    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # Update progress
        if progress_callback:
            progress_callback(current_frame, frame_count)            

        # Run YOLO detection
        keypoints = yolo_detector.detect_keypoints(frame)

        baseline = jump_analyzer.baseline_hip_y

        if not jump_detected and jump_analyzer.check_takeoff_condition(keypoints):
            jump_detected = True
            takeoff_frame = current_frame
            keypoints_takeoff = keypoints
            #print(f"Takeoff detected at frame {current_frame}, time {timestamp:.2f}s")

        if jump_detected and jump_analyzer.check_landing_condition(keypoints):
            landing_frame = current_frame
            flight_time = (landing_frame - takeoff_frame) / fps
            jump_height = calculate_jump_height(flight_time)
            keypoints_landing = keypoints

            #print(f"Landing detected at frame {landing_frame}, time {timestamp:.2f}s")
            #print(f"Jump detected: Flight Time = {flight_time:.2f}s, Height = {jump_height:.2f}m")

            # Save jump metrics
            jumps.append({
                "takeoff_frame": takeoff_frame,
                "landing_frame": landing_frame,
                "flight_time": flight_time,
                "jump_height": jump_height,
                "keypoints_takeoff": keypoints_takeoff,
                "keypoints_landing": keypoints_landing,
                "baseline": baseline
            })

            # Reset for the next jump
            jump_detected = False
            takeoff_frame, landing_frame = None, None

    keypoints_array = yolo_detector.keypoints_array
    cap.release()
    return jumps, keypoints_array