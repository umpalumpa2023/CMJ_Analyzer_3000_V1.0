baseline_hip_y = None
tolerance = 0.075  # % tolerance

def check_takeoff_condition(keypoints):
    """
    Check if takeoff condition is met using keypoints.
    Takeoff occurs when the hip keypoint is higher than the baseline position with a tolerance.
    """
    global baseline_hip_y
    if keypoints:
        # Assuming keypoints is a list and the hip is at index 11
        keypoints_data = keypoints[-1].xy  # (1, 17, 2) shape for 17 keypoints

        # Access left and right hip keypoints
        left_hip = keypoints_data[0][11]  # Left hip (x, y)
        right_hip = keypoints_data[0][12]  # Right hip (x, y)

        # Print hip positions
        #print(f"Left Hip: {left_hip}")
        #print(f"Right Hip: {right_hip}")

        # Compute the average y-coordinate of the hips
        avg_hip_y = (left_hip + right_hip) / 2
        hip_y = avg_hip_y[1]  # Extract y-coordinate

        if baseline_hip_y is None:
            # Initialize baseline if not already set
            baseline_hip_y = hip_y
            #print(f"Baseline initialized to: {baseline_hip_y}")  # Debugging

        # Define upper and lower bounds for the baseline with tolerance
        lower_bound = baseline_hip_y * (1 - tolerance)
        upper_bound = baseline_hip_y * (1 + tolerance)

        #print(f"Baseline with Tolerance: {lower_bound:.2f} - {upper_bound:.2f}")
        return hip_y < lower_bound  # True if hip is significantly higher than the baseline
    print("Keypoints missing or hip not detected")  # Debugging
    return False


def check_landing_condition(keypoints):
    """
    Check if landing condition is met using keypoints.
    Landing occurs when the hip keypoint returns to the baseline position within a tolerance.
    """
    global baseline_hip_y
    if keypoints:
        keypoints_data = keypoints[-1].xy  # (1, 17, 2) shape for 17 keypoints

        # Access left and right hip keypoints
        left_hip = keypoints_data[0][11]  # Left hip (x, y)
        right_hip = keypoints_data[0][12]  # Right hip (x, y)

        # Print hip positions
        #print(f"Left Hip: {left_hip}")
        #print(f"Right Hip: {right_hip}")

        # Compute the average y-coordinate of the hips
        avg_hip_y = (left_hip + right_hip) / 2
        hip_y = avg_hip_y[1]  # Extract y-coordinate

        # Define upper and lower bounds for the baseline with tolerance
        lower_bound = baseline_hip_y * (1 - tolerance)
        upper_bound = baseline_hip_y * (1 + tolerance)

        #print(f"Baseline with Tolerance: {lower_bound:.2f} - {upper_bound:.2f}")
        return lower_bound <= hip_y <= upper_bound  # True if hip is within baseline range
    return False
