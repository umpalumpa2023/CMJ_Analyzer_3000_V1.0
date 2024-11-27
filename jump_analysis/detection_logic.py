class JumpAnalyzer:
    def __init__(self, tolerance=0.02, max_baseline_frames=10):
        """
        Initialize the JumpAnalyzer class with parameters for jump detection.
        """
        self.tolerance = tolerance  # Percentage tolerance for baseline comparison
        self.max_baseline_frames = max_baseline_frames  # Number of frames to calculate baseline
        self.baseline_frames = []  # Store y-coordinates of the hips for baseline calculation
        self.baseline_hip_y = None # Baseline y-coordinate of the hip
        self.lower_bound = None
        self.upper_bound = None  

    def update_baseline(self, hip_y):
        """
        Update the baseline using the first max_baseline_frames frames.
        """
        self.baseline_frames.append(hip_y)
        if len(self.baseline_frames) == self.max_baseline_frames:
            # Calculate the average y-coordinate for baseline
            self.baseline_hip_y = sum(self.baseline_frames) / len(self.baseline_frames)
            print(f"Baseline initialized to: {self.baseline_hip_y}")
            self.lower_bound = self.baseline_hip_y * (1 - self.tolerance)
            self.upper_bound = self.baseline_hip_y * (1 + self.tolerance)  # Debugging


    def check_takeoff_condition(self, keypoints):
        """
        Check if takeoff condition is met using keypoints.
        """
        if not keypoints:
            print("Keypoints missing or hip not detected")  # Debugging
            return False

        # Assuming keypoints is a list and the hip is at index 11
        keypoints_data = keypoints[-1].xy  # (1, 17, 2) shape for 17 keypoints

        # Access left and right hip keypoints
        left_hip = keypoints_data[0][11]  # Left hip (x, y)
        right_hip = keypoints_data[0][12]  # Right hip (x, y)

        # Compute the average y-coordinate of the hips
        avg_hip_y = (left_hip + right_hip) / 2
        hip_y = avg_hip_y[1]  # Extract y-coordinate

        if self.baseline_hip_y is None:
            # Update the baseline with the first few frames
            self.update_baseline(hip_y)
            return False  # Wait until baseline is initialized

        return hip_y < self.lower_bound  # True if hip is significantly higher than baseline

    def check_landing_condition(self, keypoints):
        """
        Check if landing condition is met using keypoints.
        """
        if not keypoints:
            print("Keypoints missing or hip not detected")  # Debugging
            return False

        # Assuming keypoints is a list and the hip is at index 11
        keypoints_data = keypoints[-1].xy  # (1, 17, 2) shape for 17 keypoints

        # Access left and right hip keypoints
        left_hip = keypoints_data[0][11]  # Left hip (x, y)
        right_hip = keypoints_data[0][12]  # Right hip (x, y)

        # Compute the average y-coordinate of the hips
        avg_hip_y = (left_hip + right_hip) / 2
        hip_y = avg_hip_y[1]  # Extract y-coordinate

        return self.lower_bound <= hip_y <= self.upper_bound  # True if hip is within baseline range
