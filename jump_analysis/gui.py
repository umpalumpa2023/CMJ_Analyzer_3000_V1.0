import tkinter as tk
from tkinter import filedialog, messagebox
from jump_analysis.video_processor import process_jump_video
from config import MODEL_PATH
from jump_analysis.yolo_detector import YOLODetector

class JumpAnalysisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jump Analysis")
        self.root.geometry("600x400")
        
        self.yolo_detector = YOLODetector(MODEL_PATH)

        # UI Elements
        self.label = tk.Label(
            self.root,
            text="Click to Browse a Video File",
            font=("Arial", 16),
            bg="lightgray",
            relief="ridge",
            width=40,
            height=10
        )
        self.label.pack(pady=20)
        self.label.bind("<Button-1>", self.open_file_dialog)  # Bind left mouse click to file dialog

        self.result_label = tk.Label(
            self.root, text="", font=("Arial", 14), fg="green"
        )
        self.result_label.pack(pady=10)

    def open_file_dialog(self, event=None):
        """
        Opens file dialog to select a video file.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            self.analyze_video(file_path)

    def analyze_video(self, file_path):
        """
        Processes the video and displays the results.
        """
        try:
            user_height = float(
                messagebox.askstring(
                    "User Height", "Enter the user's height in meters:"
                )
            )
            if user_height <= 0:
                raise ValueError("Height must be a positive number.")

            # Analyze the video
            flight_time, jump_height = process_jump_video(file_path, self.yolo_detector, user_height)

            # Display the results
            if flight_time > 0:
                result_text = f"Flight Time: {flight_time:.2f} seconds\nJump Height: {jump_height:.2f} meters"
            else:
                result_text = "No valid jump detected."

            self.result_label.config(text=result_text)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.mainloop()

if __name__ == "__main__":
    app = JumpAnalysisApp()
    app.run()
