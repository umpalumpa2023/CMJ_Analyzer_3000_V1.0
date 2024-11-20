from config import GRAVITY

def calculate_jump_height(flight_time):
    """
    Calculate jump height using flight time and kinematic equations.
    """
    return 0.5 * GRAVITY * (flight_time / 2) ** 2
