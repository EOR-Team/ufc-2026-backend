"""
car/__init__.py
Car control module — direct hardware control.

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

    # Path-to-commands conversion (moved to src.map)
    from src.map import get_commands

    commands = get_commands("entrance", "surgery_clinic")
    for cmd in commands:
        if cmd["action"] == "forward":
            forward(cmd["param"])
        elif cmd["action"] == "turn":
            turn(int(cmd["param"]))
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
