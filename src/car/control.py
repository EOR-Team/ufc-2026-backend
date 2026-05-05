"""
car/control.py
Car control functions - mock/logging implementation.
"""

from src.logger import info, debug


def forward(distance: float) -> None:
    """
    Move forward a specified distance (simulation/logging mode).

    Args:
        distance: Distance in meters
    """
    info(f"[Car] Forward: {distance}m")


def backward(distance: float) -> None:
    """
    Move backward a specified distance (simulation/logging mode).

    Args:
        distance: Distance in meters
    """
    info(f"[Car] Backward: {distance}m")


def turn(angle: int) -> None:
    """
    Rotate the car by a specified angle (simulation/logging mode).

    Args:
        angle: Rotation angle in degrees
            - positive = clockwise (right turn)
            - negative = counter-clockwise (left turn)
    """
    direction = "right" if angle > 0 else "left"
    info(f"[Car] Turn: {direction} {abs(angle)}°")


def stop() -> None:
    """
    Stop the car immediately (simulation/logging mode).
    """
    info("[Car] Stop")
