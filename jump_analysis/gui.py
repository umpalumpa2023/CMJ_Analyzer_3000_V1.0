import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Canvas
from video_processor import process_jump_video
from config import MODEL_PATH
from yolo_detector import YOLODetector
import threading
import cv2
from PIL import Image, ImageTk
from functools import partial

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

        # Placeholder for Clear Button
        self.clear_button = None

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


    def reset_gui(self):
        """
        Resets the GUI to its original state.
        """
        # Clear result label
        self.result_label.config(text="")

        # Reset the progress bar
        self.progress_bar["value"] = 0

        # Destroy any dynamically created widgets
        for widget in self.root.pack_slaves():
            if widget not in (self.label, self.progress_bar, self.result_label):
                widget.destroy()

        # Hide and delete the Clear button
        if self.clear_button:
            self.clear_button.destroy()
            self.clear_button = None

        # Reset the instruction label
        self.label.config(text="Click to Browse a Video File")


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
            jumps = process_jump_video(
                file_path, self.yolo_detector, user_height, progress_callback=update_progress
            )

            if jumps:
                # Update the result label
                result_text = f"Total Jumps Detected: {len(jumps)}\n"
                self.result_label.config(text=result_text)

                for i, jump in enumerate(jumps, start=1):
                    # Extract frames for takeoff and landing
                    cap.set(cv2.CAP_PROP_POS_FRAMES, jump["takeoff_frame"])
                    ret_takeoff, frame_takeoff = cap.read()

                    cap.set(cv2.CAP_PROP_POS_FRAMES, jump["landing_frame"])
                    ret_landing, frame_landing = cap.read()

                    if ret_takeoff and ret_landing:
                        # Annotate frames with keypoints and baseline
                        keypoints_takeoff = jump["keypoints_takeoff"][-1].xy
                        keypoints_landing = jump["keypoints_landing"][-1].xy

                        # Left and right hips
                        left_hip_takeoff = keypoints_takeoff[0][11]
                        right_hip_takeoff = keypoints_takeoff[0][12]
                        left_hip_landing = keypoints_landing[0][11]
                        right_hip_landing = keypoints_landing[0][12]

                        # Draw the baseline and keypoints on frames
                        height, width = frame_takeoff.shape[:2]
                        frame_takeoff = cv2.line(
                            frame_takeoff, (0, int(jump["baseline"])),
                            (width, int(jump["baseline"])), color=(0, 255, 0), thickness=3
                        )
                        frame_landing = cv2.line(
                            frame_landing, (0, int(jump["baseline"])),
                            (width, int(jump["baseline"])), color=(0, 255, 0), thickness=3
                        )
                        cv2.circle(frame_takeoff, tuple(map(int, left_hip_takeoff)), 10, (255, 0, 0), 5)
                        cv2.circle(frame_takeoff, tuple(map(int, right_hip_takeoff)), 10, (0, 0, 255), 5)
                        cv2.circle(frame_landing, tuple(map(int, left_hip_landing)), 10, (255, 0, 0), 5)
                        cv2.circle(frame_landing, tuple(map(int, right_hip_landing)), 10, (0, 0, 255), 5)

                        # Add a button for visualizing this jump
                        self.create_result_entry(jump, frame_takeoff, frame_landing, i)

                cap.release()
            else:
                self.result_label.config(text="No valid jumps detected.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress_bar["value"] = 100  # Set progress bar to full when done

                # Show the Clear button once progress is complete
            if self.clear_button is None:
                self.clear_button = tk.Button(
                    self.root,
                    text="Clear",
                    font=("Arial", 14),
                    command=self.reset_gui,
                )
                self.clear_button.place(x=10, y=10)  # Position at the top-left corner


    def create_result_entry(self, jump, frame_takeoff, frame_landing, jump_index):
        """
        Create a result entry with a visualization button for a specific jump.
        """
        # Frame to hold result text and button
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=5, anchor="w")

        # Display result text
        result_text = (
            f"Jump {jump_index}: Flight Time = {jump['flight_time']:.3f}s, "
            f"Height = {jump['jump_height']:.3f}m"
        )
        tk.Label(result_frame, text=result_text, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        # Button to display frames
        view_button = tk.Button(
            result_frame,
            text="View Takeoff and Landing Frames",
            command=lambda: self.display_in_new_window(frame_takeoff, frame_landing, jump_index)
        )
        view_button.pack(side=tk.LEFT, padx=5)
        result_frame.pack(anchor="center") # Center the result entry

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.title("CMJ_Analyzer_3000")
        self.root.mainloop()