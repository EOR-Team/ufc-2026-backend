"""
car/__init__.py
Car control module - direct control and path-to-commands adapter.

Usage:
    # Direct control
    from src.car import forward, backward, turn, stop

    forward(3.0)
    turn(90)
    forward(5.0)
    stop()

    # Path to commands conversion
    from src.car.adapter import path_to_commands
    from src.car import forward, turn

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


__all__ = [
    "forward",
    "backward",
    "turn",
    "stop",
]
