"""
test/test_vision_scene.py
Scene calibration — line detection + intersection data capture.

Records detection fields at 20Hz to JSONL and logs summaries at 10Hz to console.
Optional --display shows an OpenCV window with real-time overlay.

Usage:
    python -m test.test_vision_scene --tag on_line                         # record only
    python -m test.test_vision_scene --tag near_junction --display         # with OpenCV window
    python -m test.test_vision_scene --tag my_test --display --camera 1    # specify camera

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
from src.vision.intersection_detector import IntersectionDetector
from test.vision_calib_utils import (
    ensure_calib_dir,
    JsonlWriter,
    log_console_10hz,
)
from test.vision_calib_display import draw_scene_overlay

RECORD_INTERVAL = 0.05   # 20Hz
SCENE = "line_scene"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Vision scene calibration — line + intersection data capture")
    p.add_argument("--tag", required=True, help="Test label (used as output filename)")
    p.add_argument("--display", action="store_true", help="Show OpenCV overlay window")
    p.add_argument("--camera", type=int, default=0, help="Camera device ID")
    return p.parse_args()


def main():
    args = parse_args()
    tag = args.tag
    camera_id = args.camera
    show_display = args.display

    # Setup
    out_dir = ensure_calib_dir(SCENE)
    jsonl_path = out_dir / f"{tag}.jsonl"
    screenshot_dir = out_dir / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)

    detector = LineDetector(camera_id=camera_id)
    inter_detector = IntersectionDetector()

    if not detector.open():
        print(f"ERROR: Cannot open camera {camera_id}")
        sys.exit(1)

    writer = JsonlWriter(jsonl_path)
    print(f"Scene capture started: tag={tag}, camera={camera_id}")
    print(f"Recording to {jsonl_path} (20Hz JSONL, 10Hz console)")

    if show_display:
        print("Display ON. Keys: [s]screenshot [d]toggle display [q]quit")
        cv2.namedWindow("Scene Calibration", cv2.WINDOW_NORMAL)

    total_frames = 0
    total_recorded = 0
    last_record_time = 0.0
    last_log_time = 0.0
    start_time = time.time()
    display_on = show_display

    try:
        while True:
            now = time.time()

            # Read & detect
            frame = detector.read_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            total_frames += 1
            deviation, line_detected, binary = detector.detect(frame)
            if binary is None:
                continue

            # Intersection classification stats (always computed)
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            vertical_count = 0
            horizontal_count = 0
            total_area = 0.0
            for c in contours:
                total_area += cv2.contourArea(c)
                xb, yb, wb, hb = cv2.boundingRect(c)
                if hb > 0 and wb > 0:
                    if hb / wb > 2.0:
                        vertical_count += 1
                    if wb / hb > 2.0:
                        horizontal_count += 1

            roi_h, roi_w = binary.shape[:2]
            area_ratio = total_area / (roi_w * roi_h) if roi_w * roi_h > 0 else 0.0
            at_intersection = inter_detector.detect(binary, deviation, line_detected)

            # Record at 20Hz
            if now - last_record_time >= RECORD_INTERVAL:
                writer.write({
                    "t": round(now - start_time, 3),
                    "area": round(total_area, 1),
                    "vertical": vertical_count,
                    "horizontal": horizontal_count,
                    "ratio": round(area_ratio, 4),
                    "deviation": round(deviation, 4),
                    "line_detected": line_detected,
                    "at_intersection": at_intersection,
                })
                last_record_time = now
                total_recorded += 1

            # Console log at 10Hz
            last_log_time, _ = log_console_10hz(last_log_time, now,
                f"[{now - start_time:.1f}s] dev={deviation:+.3f} area={total_area:.0f} "
                f"ratio={area_ratio:.3f} V={vertical_count} H={horizontal_count} "
                f"isect={'YES' if at_intersection else 'NO'} "
                f"rec={total_recorded}")

            # Display
            if display_on and total_frames % 2 == 0:  # update display at ~half framerate
                elapsed = now - start_time
                fps = total_frames / elapsed if elapsed > 0 else 0
                overlay = draw_scene_overlay(
                    frame, binary, deviation, line_detected, at_intersection,
                    total_area, area_ratio, vertical_count, horizontal_count, fps,
                )
                cv2.imshow("Scene Calibration", overlay)

            # Keyboard handling
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
                    cv2.destroyWindow("Scene Calibration")
                else:
                    cv2.namedWindow("Scene Calibration", cv2.WINDOW_NORMAL)
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
