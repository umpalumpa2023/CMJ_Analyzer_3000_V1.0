import cv2
from jump_metrics import calculate_jump_height
from detection_logic import JumpAnalyzer


# Counter movement auswertung + Dysbalane wenn Frontansicht

def process_jump_video(video_path, yolo_detector, user_height, progress_callback=None):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    jump_analyzer = JumpAnalyzer()

    jumps = []  # List to store data for all detected jumps

    jump_detected = False
    takeoff_frame, landing_frame = None, None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        timestamp = current_frame / fps

        # Update progress
        if progress_callback:
            progress_callback(current_frame, frame_count)            

        # Run YOLO detection
        keypoints = yolo_detector.detect_keypoints(frame)

        if not jump_detected and jump_analyzer.check_takeoff_condition(keypoints):
            jump_detected = True
            takeoff_frame = current_frame
            #print(f"Takeoff detected at frame {current_frame}, time {timestamp:.2f}s")

        if jump_detected and jump_analyzer.check_landing_condition(keypoints):
            landing_frame = current_frame
            flight_time = (landing_frame - takeoff_frame) / fps
            jump_height = calculate_jump_height(flight_time)

            #print(f"Landing detected at frame {landing_frame}, time {timestamp:.2f}s")
            #print(f"Jump detected: Flight Time = {flight_time:.2f}s, Height = {jump_height:.2f}m")

            # Save jump metrics
            jumps.append({
                "takeoff_frame": takeoff_frame,
                "landing_frame": landing_frame,
                "flight_time": flight_time,
                "jump_height": jump_height
            })

            # Reset for the next jump
            jump_detected = False
            takeoff_frame, landing_frame = None, None

    cap.release()
    return jumps, keypoints