"""
car/control.py
Car control functions — delegates to LOBOROBOT Robot on Raspberry Pi,
falls back to logging on machines without smbus/RPi.GPIO.
"""

import asyncio

from src.logger import info
from src.car.LOBOROBOT import Robot


def forward(distance: float) -> None:
    """
    Move forward a specified distance.

    On hardware: runs at fixed FORWARD_SPEED for calibrated duration.
    On dev machine: logs the action only.

    Args:
        distance: Distance in meters
    """
    if Robot.is_available:
        info(f"[Car] Forward: {distance}m")
        asyncio.run(Robot.forward(distance))
    else:
        info(f"[Car] Forward: {distance}m (mock)")


def backward(distance: float) -> None:
    """
    Move backward a specified distance.

    On hardware: runs at fixed FORWARD_SPEED for calibrated duration.
    On dev machine: logs the action only.

    Args:
        distance: Distance in meters
    """
    if Robot.is_available:
        info(f"[Car] Backward: {distance}m")
        asyncio.run(Robot.backward(distance))
    else:
        info(f"[Car] Backward: {distance}m (mock)")


def turn(angle: int) -> None:
    """
    Rotate the car by a specified angle.

    On hardware: delegates to Robot.turn_right or Robot.turn_left
    based on angle sign. Uses fixed ROTATE_SPEED for calibrated duration.
    On dev machine: logs the action only.

    Args:
        angle: Rotation angle in degrees
            - positive = clockwise (right turn)
            - negative = counter-clockwise (left turn)
            - zero = no-op
    """
    if Robot.is_available:
        if angle > 0:
            info(f"[Car] Turn right: {angle}°")
            asyncio.run(Robot.turn_right(angle))
        elif angle < 0:
            info(f"[Car] Turn left: {abs(angle)}°")
            asyncio.run(Robot.turn_left(abs(angle)))
    else:
        direction = "right" if angle > 0 else "left"
        info(f"[Car] Turn: {direction} {abs(angle)}° (mock)")


def stop() -> None:
    """
    Stop the car immediately.

    On hardware: calls Robot.stop() which directly halts all motors
    synchronously (no timing delay, for emergency stop).
    On dev machine: logs the action only.
    """
    if Robot.is_available:
        Robot.stop()
    info("[Car] Stop")
