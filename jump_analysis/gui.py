import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from video_processor import process_jump_video
from config import MODEL_PATH
from yolo_detector import YOLODetector
import threading

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

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

        self.result_label = tk.Label(
            self.root, text="", font=("Arial bold", 16), fg="white"
        )
        self.result_label.pack(pady=10)

    def open_file_dialog(self, event=None):
        """
        Opens file dialog to select a video file.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        print(file_path)
        if file_path:
            self.analyze_video(file_path)

    def analyze_video(self, file_path):
        """
        Processes the video and displays the results.
        """
        try:
            #user_height = float(
                #simpledialog.askstring(
                #"User Height", "Enter the user's height in meters:"
                    #)
                #)
            #if user_height <= 0:
                #raise ValueError("Height must be a positive number.")
            user_height = 1.75

            # Run the analysis in a separate thread to prevent UI freezing
            thread = threading.Thread(
                target=self.run_analysis,
                args=(file_path, user_height),
                daemon=True
            )
            print(thread)
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def run_analysis(self, file_path, user_height):
        """
        Executes the video processing and updates the progress bar.
        """
        try:
            self.progress_bar["value"] = 0
            self.progress_bar["maximum"] = 100

            def update_progress(current_frame, total_frames):
                progress = (current_frame / total_frames) * 100
                self.progress_bar["value"] = progress

            # Process the video
            print("start processing")
            print(file_path)

            jumps = process_jump_video(
                file_path, self.yolo_detector, user_height, progress_callback=update_progress)
            
            print("end processing")
            # Display the results
            if jumps:
                result_text = f"Total Jumps Detected: {len(jumps)}\n"
                for i, jump in enumerate(jumps, start=1):
                    result_text += f"Jump {i}: Flight Time = {jump['flight_time']:.3f}s, Height = {jump['jump_height']:.3f}m\n"
            else:
                result_text = "No valid jumps detected."

            self.result_label.config(text=result_text)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress_bar["value"] = 100  # Set progress bar to full when done

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.mainloop()

