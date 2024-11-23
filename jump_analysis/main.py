from video_processor import process_jump_video
from yolo_detector import YOLODetector
from gui import JumpAnalysisApp
from config import MODEL_PATH

if __name__ == "__main__":
    # Start the GUI application
    app = JumpAnalysisApp()
    app.run()
