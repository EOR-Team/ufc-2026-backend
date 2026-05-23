"""
test/test_vision_pid.py
PID dynamic data capture — records deviation, motor speeds, and PID parameters.

Captures line detection + PID output at 20Hz to JSONL and logs at 10Hz to console.
Optional --display shows an OpenCV window with motor-speed visual bars.

Usage:
    python -m test.test_vision_pid --tag pid_straight                         # record only
    python -m test.test_vision_pid --tag pid_straight --display               # with OpenCV window
    python -m test.test_vision_pid --tag my_test --display --camera 1         # specify camera

Keys (display mode):  s = screenshot,  d = toggle display on/off,  q = quit
"""

import argparse
import os
import sys
import time
from datetime import datetime

import cv2
import numpy as np

from src.vision.line_detector import LineDetector
from src.vision.pid_controller import PIDController
from test.vision_calib_utils import (
    ensure_calib_dir,
    JsonlWriter,
    log_console_10hz,
)
from test.vision_calib_display import draw_pid_overlay

RECORD_INTERVAL = 0.05   # 20Hz
SCENE = "pid_test"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Vision PID data capture — deviation + motor output recorder")
    p.add_argument("--tag", required=True, help="Test label (used as output filename)")
    p.add_argument("--display", action="store_true", help="Show OpenCV overlay window")
    p.add_argument("--camera", type=int, default=0, help="Camera device ID")
    return p.parse_args()


def main():
    args = parse_args()
    tag = args.tag
    camera_id = args.camera
    show_display = args.display

    out_dir = ensure_calib_dir(SCENE)
    jsonl_path = out_dir / f"{tag}.jsonl"
    screenshot_dir = out_dir / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)

    detector = LineDetector(camera_id=camera_id)
    pid = PIDController()

    if not detector.open():
        print(f"ERROR: Cannot open camera {camera_id}")
        sys.exit(1)

    writer = JsonlWriter(jsonl_path)
    print(f"PID capture started: tag={tag}, camera={camera_id}")
    print(f"PID gains: Kp={pid.kp:.1f} Ki={pid.ki:.1f} Kd={pid.kd:.1f}")
    print(f"Recording to {jsonl_path} (20Hz JSONL, 10Hz console)")

    if show_display:
        print("Display ON. Keys: [s]screenshot [d]toggle display [q]quit")
        cv2.namedWindow("PID Calibration", cv2.WINDOW_NORMAL)

    total_frames = 0
    total_recorded = 0
    last_record_time = 0.0
    last_log_time = 0.0
    start_time = time.time()
    display_on = show_display

    try:
        while True:
            now = time.time()

            frame = detector.read_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            total_frames += 1
            deviation, line_detected, binary = detector.detect(frame)
            if binary is None:
                continue

            left_speed, right_speed = pid.compute(deviation, line_detected)

            # Record at 20Hz
            if now - last_record_time >= RECORD_INTERVAL:
                writer.write({
                    "t": round(now - start_time, 3),
                    "deviation": round(deviation, 4),
                    "line_detected": line_detected,
                    "left_speed": left_speed,
                    "right_speed": right_speed,
                    "kp": pid.kp,
                    "ki": pid.ki,
                    "kd": pid.kd,
                })
                last_record_time = now
                total_recorded += 1

            # Console log at 10Hz
            last_log_time, _ = log_console_10hz(last_log_time, now,
                f"[{now - start_time:.1f}s] dev={deviation:+.3f} "
                f"line={'Y' if line_detected else 'N'} "
                f"L={left_speed} R={right_speed} "
                f"rec={total_recorded}")

            # Display at ~half framerate
            if display_on and total_frames % 2 == 0:
                elapsed = now - start_time
                fps = total_frames / elapsed if elapsed > 0 else 0
                overlay = draw_pid_overlay(
                    frame, binary, deviation, line_detected,
                    left_speed, right_speed, pid.kp, pid.ki, pid.kd, fps,
                )
                cv2.imshow("PID Calibration", overlay)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuit requested.")
                break
            elif key == ord('s'):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                shot_path = screenshot_dir / f"{tag}_{ts}.png"
                cv2.imwrite(str(shot_path), frame)
                print(f"\nScreenshot saved: {shot_path}")
            elif key == ord('d'):
                display_on = not display_on
                if not display_on:
                    cv2.destroyWindow("PID Calibration")
                else:
                    cv2.namedWindow("PID Calibration", cv2.WINDOW_NORMAL)
                print(f"\nDisplay {'ON' if display_on else 'OFF'}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        writer.close()
        detector.close()
        cv2.destroyAllWindows()
        elapsed = time.time() - start_time
        print(f"\nDone. {total_recorded} records in {elapsed:.1f}s "
              f"({total_recorded / elapsed:.1f} Hz effective)")
        print(f"Output: {jsonl_path}")


if __name__ == "__main__":
    main()
