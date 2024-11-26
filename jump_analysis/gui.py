import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Canvas
from video_processor import process_jump_video
from config import MODEL_PATH
from yolo_detector import YOLODetector
import threading
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class JumpAnalysisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jump Analysis")
        self.root.geometry("1000x800")

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

        # Canvas for video frames
        self.canvas = Canvas(self.root, width=480, height=640)
        self.canvas.pack(pady=10)

    def display_in_new_window(self, frame_takeoff, frame_landing, i):
        # Create a new window
        new_window = tk.Toplevel(self.root)
        new_window.title(f"Takeoff and Landing Frames for Jump {i}")
        new_window.geometry("960x720")  # Adjusted for space for titles

        canvas_width = 480
        canvas_height = 640

        # Convert frames to ImageTk format
        frame_takeoff_resized = self.resize_frame_to_canvas(frame_takeoff, canvas_width, canvas_height)
        frame_takeoff_rgb = cv2.cvtColor(frame_takeoff_resized, cv2.COLOR_BGR2RGB)
        img_takeoff = ImageTk.PhotoImage(Image.fromarray(frame_takeoff_rgb))

        frame_landing_resized = self.resize_frame_to_canvas(frame_landing, canvas_width, canvas_height)
        frame_landing_rgb = cv2.cvtColor(frame_landing_resized, cv2.COLOR_BGR2RGB)
        img_landing = ImageTk.PhotoImage(Image.fromarray(frame_landing_rgb))

        # Title for Takeoff frame
        label_takeoff = tk.Label(new_window, text="Takeoff Frame", font=("Arial", 14, "bold"))
        label_takeoff.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Create canvas for Takeoff frame
        canvas_takeoff = Canvas(new_window, width=canvas_width, height=canvas_height)
        canvas_takeoff.grid(row=1, column=0, padx=10, pady=5)
        canvas_takeoff.create_image(0, 0, anchor=tk.NW, image=img_takeoff)
        canvas_takeoff.image = img_takeoff  # Keep a reference

        # Title for Landing frame
        label_landing = tk.Label(new_window, text="Landing Frame", font=("Arial", 14, "bold"))
        label_landing.grid(row=0, column=1, padx=10, pady=(10, 5))

        # Create canvas for Landing frame
        canvas_landing = Canvas(new_window, width=canvas_width, height=canvas_height)
        canvas_landing.grid(row=1, column=1, padx=10, pady=5)
        canvas_landing.create_image(0, 0, anchor=tk.NW, image=img_landing)
        canvas_landing.image = img_landing  # Keep a reference


    def resize_frame_to_canvas(self, frame, canvas_width, canvas_height):
        """
        Resize the frame to fit within the Canvas dimensions while maintaining the aspect ratio.
        """
        original_height, original_width = frame.shape[:2]
        scale_width = canvas_width / original_width
        scale_height = canvas_height / original_height
        scale = min(scale_width, scale_height)

        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        return cv2.resize(frame, (new_width, new_height))


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
        cap = cv2.VideoCapture(file_path)

        try:
            self.progress_bar["value"] = 0
            self.progress_bar["maximum"] = 100

            def update_progress(current_frame, total_frames):
                progress = (current_frame / total_frames) * 100
                self.progress_bar["value"] = progress

            # Process the video
            print("start processing")
            print(file_path)

            jumps, keypoints = process_jump_video(
                file_path, self.yolo_detector, user_height, progress_callback=update_progress)
            
            print("end processing")
            # Display the results
            if jumps:
                result_text = f"Total Jumps Detected: {len(jumps)}\n"
                for i, jump in enumerate(jumps, start=1):
                    result_text += f"Jump {i}: Flight Time = {jump['flight_time']:.3f}s, Height = {jump['jump_height']:.3f}m\n"

                            # Get the frames
                    cap.set(cv2.CAP_PROP_POS_FRAMES, jump["takeoff_frame"])
                    ret, frame_takeoff = cap.read()
                    cap.set(cv2.CAP_PROP_POS_FRAMES, jump["landing_frame"])
                    ret, frame_landing = cap.read()

                    if ret:
                        # Display annotated frames
                        self.display_in_new_window(frame_takeoff, frame_landing, i)

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
        self.root.title("CMJ_Analyzer_3000")
        self.root.mainloop()