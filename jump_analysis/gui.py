import tkinter as tk
import matplotlib.pyplot as plt
import threading
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox, ttk, Canvas
from video_processor import process_jump_video, save_keypoints_to_json
from PIL import Image, ImageTk

class JumpAnalysisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jump Analysis")
        self.root.geometry("1000x800")

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
        self.label.bind("<Button-1>", self.open_file_dialog)

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

        self.result_label = tk.Label(
            self.root, text="", font=("Arial bold", 16), fg="white"
        )
        self.result_label.pack(pady=10)

        # Initialize an empty plot
        self.fig, self.ax1 = plt.subplots(figsize=(9, 4))
        self.ax1.set_xlabel('Frame Number')
        self.ax1.set_ylabel('Normalized Hand Y Position', color='k')
        self.ax1.tick_params(axis='y', labelcolor='k')
        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel('Confidence', color='k')
        self.ax2.tick_params(axis='y', labelcolor='k')
        self.fig.tight_layout()

        self.position_plot = FigureCanvasTkAgg(self.fig, self.root)
        self.position_plot.get_tk_widget().pack(padx = 10, pady=10)

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
            user_height = 1.75
            thread = threading.Thread(
                target=self.run_analysis, args=(file_path, user_height), daemon=True
            )
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

            jumps, keypoints_array = process_jump_video(
                file_path, user_height, progress_callback=update_progress
            )
            #print(keypoints_array)
            # Save keypoints
            save_keypoints_to_json(data=keypoints_array, file_name="keypoints_data.json")
            
            if jumps:
                result_text = f"Total Jumps Detected: {len(jumps)}\n"
                y_positions_left_hip, y_positions_right_hip = [], []
                confidences_left_hip, confidences_right_hip = [], []

                for i, jump in enumerate(jumps, start=1):
                    result_text += f"Jump {i}: Flight Time = {jump['flight_time']:.3f}s, Height = {jump['jump_height']:.3f}m\n"

                    # Get the takeoff and landing frames for display
                    cap.set(cv2.CAP_PROP_POS_FRAMES, jump["takeoff_frame"])
                    ret_takeoff, frame_takeoff = cap.read()

                    cap.set(cv2.CAP_PROP_POS_FRAMES, jump["landing_frame"])
                    ret_landing, frame_landing = cap.read()

                    # Assuming keypoints is a list and the hip is at index 11
                    keypoints_data_takeoff = jump["keypoints_takeoff"][-1].xy # (1, 17, 2) shape for 17 keypoints
                    keypoints_data_landing = jump["keypoints_landing"][-1].xy

                    # Access left and right hip keypoints
                    left_hip_takeoff = keypoints_data_takeoff[0][11]  # Left hip (x, y)
                    right_hip_takeoff = keypoints_data_takeoff[0][12]  # Right hip (x, y)
                    left_hip_landing = keypoints_data_landing[0][11]  # Left hip (x, y)
                    right_hip_landing = keypoints_data_landing[0][12] # Right hip (x, y)

                    if ret_takeoff and ret_landing:
                        height, width = frame_takeoff.shape[:2]

                        # Draw the baseline
                        frame_takeoff = cv2.line(frame_takeoff, (0, int(jump["baseline"])), (width, int(jump["baseline"])), color=(0, 255, 0), thickness=3)
                        frame_landing = cv2.line(frame_landing, (0, int(jump["baseline"])), (width, int(jump["baseline"])), color=(0, 255, 0), thickness=3)

                        # Draw keypoints on the takeoff frame
                        cv2.circle(frame_takeoff, tuple(map(int, left_hip_takeoff)), radius=10, color=(255, 0, 0), thickness=5)  # Left hip (blue)
                        cv2.circle(frame_takeoff, tuple(map(int, right_hip_takeoff)), radius=10, color=(0, 0, 255), thickness=5)  # Right hip (red)

                        # Draw keypoints on the landing frame
                        cv2.circle(frame_landing, tuple(map(int, left_hip_landing)), radius=10, color=(255, 0, 0), thickness=5)  # Left hip (blue)
                        cv2.circle(frame_landing, tuple(map(int, right_hip_landing)), radius=10, color=(0, 0, 255), thickness=5)  # Right hip (red)
                        self.root.after(0, lambda: self.display_in_new_window(frame_takeoff, frame_landing, i))

                # Extract keypoint data
                for keypoints in keypoints_array:
                        keypoints_xyn = keypoints[-1].xyn
                        keypoints_conf = keypoints[-1].conf

                        left_hip_y_position = keypoints_xyn[0][11][1]
                        right_hip_y_position = keypoints_xyn[0][12][1]
                        left_hip_confidence = keypoints_conf[0][11]
                        right_hip_confidence = keypoints_conf[0][12]

                        y_positions_left_hip.append(left_hip_y_position)
                        y_positions_right_hip.append(right_hip_y_position)
                        confidences_left_hip.append(left_hip_confidence)
                        confidences_right_hip.append(right_hip_confidence)    

                self.root.after(0, lambda: self.update_plot(
                    y_positions_right_hip,
                    confidences_right_hip,
                    y_positions_left_hip,
                    confidences_left_hip
                ))
                self.root.after(0, lambda: self.result_label.config(text=result_text))
            else:
                self.root.after(0, lambda: self.result_label.config(text="No valid jumps detected."))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            cap.release()
            self.progress_bar["value"] = 100

    def update_plot(self, y_positions_right, confidences_right, y_positions_left, confidences_left):
        """
        Updates the plot with new data.
        """
        self.ax1.clear()
        self.ax2.clear()

        # Update primary axis (Left Y-axis)
        self.ax1.plot(range(len(y_positions_right)), y_positions_right, color='b', label='Right Hand Y Position', linewidth=0.5)
        self.ax1.plot(range(len(y_positions_left)), y_positions_left, color='g', label='Left Hand Y Position', linewidth=0.5)
        self.ax1.set_xlabel('Frame Number')
        self.ax1.set_ylabel('Normalized Hand Y Position', color='k')
        self.ax1.tick_params(axis='y', labelcolor='k')

        # Update secondary axis (Right Y-axis)
        self.ax2.plot(range(len(confidences_right)), confidences_right, color='r', label='Right Hand Confidence', linestyle='--', linewidth=0.5)
        self.ax2.plot(range(len(confidences_left)), confidences_left, color='orange', label='Left Hand Confidence', linestyle='--', linewidth=0.5)
        self.ax2.set_ylabel('Confidence', color='k')
        self.ax2.tick_params(axis='y', labelcolor='k')

        # Move the secondary axis label to the right side
        self.ax2.yaxis.set_label_position("right")
        self.ax2.yaxis.tick_right()

        # Add legends outside the plot
        self.ax1.legend(loc='lower left')
        self.ax2.legend(loc='lower right')

        self.fig.tight_layout()

        self.position_plot.draw()

    def display_in_new_window(self, frame_takeoff, frame_landing, i):
        """
        Displays the takeoff and landing frames in a new window.
        """
        new_window = tk.Toplevel(self.root)
        new_window.title(f"Takeoff and Landing Frames for Jump {i}")
        new_window.geometry("960x720")

        canvas_width = 480
        canvas_height = 640

        # Convert frames to ImageTk format
        frame_takeoff_resized = self.resize_frame_to_canvas(frame_takeoff, canvas_width, canvas_height)
        frame_takeoff_rgb = cv2.cvtColor(frame_takeoff_resized, cv2.COLOR_BGR2RGB)
        img_takeoff = ImageTk.PhotoImage(Image.fromarray(frame_takeoff_rgb))

        frame_landing_resized = self.resize_frame_to_canvas(frame_landing, canvas_width, canvas_height)
        frame_landing_rgb = cv2.cvtColor(frame_landing_resized, cv2.COLOR_BGR2RGB)
        img_landing = ImageTk.PhotoImage(Image.fromarray(frame_landing_rgb))

        # Display takeoff frame
        tk.Label(new_window, text="Takeoff Frame").grid(row=0, column=0)
        takeoff_canvas = Canvas(new_window, width=canvas_width, height=canvas_height)
        takeoff_canvas.grid(row=1, column=0)
        takeoff_canvas.create_image(0, 0, anchor=tk.NW, image=img_takeoff)
        takeoff_canvas.image = img_takeoff

        # Display landing frame
        tk.Label(new_window, text="Landing Frame").grid(row=0, column=1)
        landing_canvas = Canvas(new_window, width=canvas_width, height=canvas_height)
        landing_canvas.grid(row=1, column=1)
        landing_canvas.create_image(0, 0, anchor=tk.NW, image=img_landing)
        landing_canvas.image = img_landing

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

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.mainloop()
