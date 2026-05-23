"""
vision_calib_display.py
OpenCV overlay drawing functions for calibration scripts.

These require cv2 and numpy — only import on the Raspberry Pi where
OpenCV is installed. Separated from vision_calib_utils.py so that
test_chassis_calib.py can import the utilities without cv2.
"""

import cv2
import numpy as np


def draw_scene_overlay(
    frame: np.ndarray,
    binary: np.ndarray,
    deviation: float,
    line_detected: bool,
    at_intersection: bool,
    area: float,
    ratio: float,
    vertical: int,
    horizontal: int,
    fps: float,
) -> np.ndarray:
    """Draw detection debug overlay for scene capture mode."""
    h, w = frame.shape[:2]
    display = frame.copy()

    # ROI boundary line
    roi_top = int(h * 0.4)
    cv2.rectangle(display, (0, roi_top), (w, h), (0, 255, 0), 2)

    # Deviation bar (top center)
    bar_y = 30
    bar_w = 200
    bar_x = (w - bar_w) // 2
    cv2.rectangle(display, (bar_x, bar_y - 5), (bar_x + bar_w, bar_y + 5), (100, 100, 100), -1)
    center_x = bar_x + bar_w // 2
    indicator_x = int(center_x + deviation * (bar_w // 2))
    color = (0, 255, 0) if line_detected else (0, 0, 255)
    cv2.circle(display, (indicator_x, bar_y), 8, color, -1)
    cv2.line(display, (center_x, bar_y - 10), (center_x, bar_y + 10), (255, 255, 255), 1)

    # Text overlay (left column)
    info_lines = [
        f"Dev: {deviation:+.3f}  Line: {'Y' if line_detected else 'N'}",
        f"Intersection: {'YES' if at_intersection else 'NO'}",
        f"Area: {area:.0f}  Ratio: {ratio:.3f}",
        f"V:{vertical} H:{horizontal}",
        f"FPS: {fps:.1f}",
    ]
    for i, line in enumerate(info_lines):
        y = 60 + i * 22
        cv2.putText(display, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # Binary preview (bottom-right corner)
    bh, bw = 80, 120
    binary_small = cv2.resize(binary, (bw, bh))
    binary_bgr = cv2.cvtColor(binary_small, cv2.COLOR_GRAY2BGR)
    display[h - bh - 10:h - 10, w - bw - 10:w - 10] = binary_bgr
    cv2.putText(display, "Binary", (w - bw - 10, h - bh - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Key hints
    cv2.putText(display, "[s]save [d]display [q]quit",
                (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    return display


def draw_pid_overlay(
    frame: np.ndarray,
    binary: np.ndarray,
    deviation: float,
    line_detected: bool,
    left_speed: int,
    right_speed: int,
    kp: float,
    ki: float,
    kd: float,
    fps: float,
) -> np.ndarray:
    """Draw PID debug overlay for PID tuning mode."""
    h, w = frame.shape[:2]
    display = frame.copy()

    # ROI boundary line
    roi_top = int(h * 0.4)
    cv2.rectangle(display, (0, roi_top), (w, h), (0, 255, 0), 2)

    # Deviation bar
    bar_y = 30
    bar_w = 200
    bar_x = (w - bar_w) // 2
    cv2.rectangle(display, (bar_x, bar_y - 5), (bar_x + bar_w, bar_y + 5), (100, 100, 100), -1)
    center_x = bar_x + bar_w // 2
    indicator_x = int(center_x + deviation * (bar_w // 2))
    color = (0, 255, 0) if line_detected else (0, 0, 255)
    cv2.circle(display, (indicator_x, bar_y), 8, color, -1)
    cv2.line(display, (center_x, bar_y - 10), (center_x, bar_y + 10), (255, 255, 255), 1)

    # Motor speed visual bars
    motor_y = 55
    bar_h = 12
    max_bar_w = 150
    motor_x = 10

    # Left motor bar
    left_w = int(left_speed / 100.0 * max_bar_w)
    cv2.putText(display, f"L", (motor_x, motor_y + bar_h - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.rectangle(display, (motor_x + 15, motor_y), (motor_x + 15 + left_w, motor_y + bar_h), (0, 255, 255), -1)
    cv2.putText(display, str(left_speed), (motor_x + 15 + left_w + 5, motor_y + bar_h - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Right motor bar
    motor_y2 = motor_y + bar_h + 5
    right_w = int(right_speed / 100.0 * max_bar_w)
    cv2.putText(display, f"R", (motor_x, motor_y2 + bar_h - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.rectangle(display, (motor_x + 15, motor_y2), (motor_x + 15 + right_w, motor_y2 + bar_h), (255, 255, 0), -1)
    cv2.putText(display, str(right_speed), (motor_x + 15 + right_w + 5, motor_y2 + bar_h - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Text info
    info_lines = [
        f"Dev: {deviation:+.3f}  Line: {'Y' if line_detected else 'N'}",
        f"PID: Kp={kp:.1f} Ki={ki:.1f} Kd={kd:.1f}",
        f"FPS: {fps:.1f}",
    ]
    for i, line in enumerate(info_lines):
        y = motor_y2 + bar_h + 15 + i * 22
        cv2.putText(display, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # Binary preview
    bh, bw = 80, 120
    binary_small = cv2.resize(binary, (bw, bh))
    binary_bgr = cv2.cvtColor(binary_small, cv2.COLOR_GRAY2BGR)
    display[h - bh - 10:h - 10, w - bw - 10:w - 10] = binary_bgr

    # Key hints
    cv2.putText(display, "[s]save [d]display [q]quit",
                (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    return display
