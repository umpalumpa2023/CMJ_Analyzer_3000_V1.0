
baseline_hip_y = None

def check_takeoff_condition(keypoints):
    global baseline_hip_y
    if keypoints:
        # Assuming keypoints is a list and the hip is at index 11
        left_hip = keypoints.data[0][11]  # [x, y] of the left hip
        right_hip = keypoints.data[0][12]  # [x, y] of the right hip
        hip_y = right_hip[1]   # Extract y-coordinate
        if baseline_hip_y is None:
            baseline_hip_y = hip_y
            print(f"Baseline initialized to: {baseline_hip_y}")  # Debugging
        return hip_y < baseline_hip_y
    print("Keypoints missing or hip not detected")  # Debugging
    return False


def check_landing_condition(keypoints):
    """
    Check if landing condition is met using keypoints.
    Landing occurs when the hip keypoint returns to the baseline position.
    """
    global baseline_hip_y
    if keypoints and 'hip' in keypoints:
        left_hip = keypoints.data[0][11]  # [x, y] of the left hip
        right_hip = keypoints.data[0][12]  # [x, y] of the right hip
        hip_y = right_hip[1]  # Assuming keypoints['hip'] = (x, y)
        return hip_y >= baseline_hip_y  # True if hip is back at or below baseline
    return False
