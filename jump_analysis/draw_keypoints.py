import cv2

def draw_keypoints(frame, keypoints):
    """
    Draws keypoints on the frame.
    :param frame: The current video frame.
    :param keypoints: The detected keypoints for the current frame.
    :return: Frame with keypoints drawn.
    """
    if keypoints is not None:
        for point in keypoints:
            # Each keypoint is assumed to have (x, y) coordinates
            x, y = int(point[0]), int(point[1])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Draw green circles
    return frame