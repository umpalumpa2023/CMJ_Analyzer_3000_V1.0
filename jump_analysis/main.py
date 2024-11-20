from video_processor import process_jump_video
from yolo_detector import YOLODetector
from config import MODEL_PATH

if __name__ == "__main__":
    # Define the video file path
    video_path = "C:\Users\Sam\Desktop\CMJ_Analyzer_3000_V1.0\jump_analysis\CMJ_01_001_Seite.MP4"  # Replace with your actual video file name

    # Load YOLO model
    yolo_detector = YOLODetector(MODEL_PATH)

    # User-provided height
    user_height = float(input("Enter the user's height in meters: "))
    if user_height <= 0:
        raise ValueError("Height must be a positive number.")

    # Process the video
    jumps = process_jump_video(video_path, yolo_detector, user_height)

    # Display the results
    if jumps:
        print(f"Total Jumps Detected: {len(jumps)}")
        for i, jump in enumerate(jumps, start=1):
            print(f"Jump {i}: Flight Time = {jump['flight_time']:.2f}s, Height = {jump['jump_height']:.2f}m")
    else:
        print("No valid jumps detected.")
