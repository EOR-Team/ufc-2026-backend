"""
vision/__init__.py
Vision-based line-following navigation module.

Usage:
    from src.vision import LineDetector, PIDController, IntersectionDetector, Navigator

    # Quick start
    navigator = Navigator(destination="surgery_clinic")
    navigator.run()
"""

from src.vision.line_detector import LineDetector
from src.vision.pid_controller import PIDController
from src.vision.intersection_detector import IntersectionDetector
from src.vision.navigator import Navigator

__all__ = [
    "LineDetector",
    "PIDController",
    "IntersectionDetector",
    "Navigator",
]
