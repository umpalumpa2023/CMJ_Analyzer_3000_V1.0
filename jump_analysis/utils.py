
baseline_hip_y = None  # Global variable to store the baseline hip position

def check_takeoff_condition(keypoints):
    """
    Check if takeoff condition is met using keypoints.
    Takeoff occurs when the hip keypoint is higher than the baseline position.
    """
    global baseline_hip_y
    if keypoints and 'hip' in keypoints:
        hip_y = keypoints['hip'][1]  # Assuming keypoints['hip'] = (x, y)
        if baseline_hip_y is None:
            baseline_hip_y = hip_y  # Initialize baseline on first frame
        return hip_y < baseline_hip_y  # True if hip is higher than baseline
    return False

def check_landing_condition(keypoints):
    """
    Check if landing condition is met using keypoints.
    Landing occurs when the hip keypoint returns to the baseline position.
    """
    global baseline_hip_y
    if keypoints and 'hip' in keypoints:
        hip_y = keypoints['hip'][1]  # Assuming keypoints['hip'] = (x, y)
        return hip_y >= baseline_hip_y  # True if hip is back at or below baseline
    return False
