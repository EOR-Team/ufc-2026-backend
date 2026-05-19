"""
car/__init__.py
Car control module — direct control and path-to-commands adapter.

Usage:
    # Direct control (sync functions, works on both Pi and dev machines)
    from src.car import forward, backward, turn, stop

    forward(3.0)
    turn(90)
    forward(5.0)
    stop()

    # Check hardware availability
    from src.car import is_hardware_available
    print(is_hardware_available)  # True on Pi, False on dev

    # Advanced: async direct access to the hardware singleton
    from src.car import Robot
    await Robot.forward(3.0)
    await Robot.turn_left(90)

    # Path to commands conversion
    from src.car.adapter import path_to_commands

    commands = path_to_commands(["entrance", "toilet"])
    for action, param in commands:
        if action == "forward":
            forward(param)
        elif action == "turn":
            turn(int(param))
        elif action == "stop":
            stop()
"""

from src.car.control import forward, backward, turn, stop
from src.car.LOBOROBOT import Robot

is_hardware_available: bool = Robot.is_available

__all__ = [
    "forward",
    "backward",
    "turn",
    "stop",
    "is_hardware_available",
    "Robot",
]
