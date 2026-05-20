"""
test/test_vision_display.py
可视化调试工具 — 实时显示摄像头画面、黑线检测、路口检测、PID 输出。

运行方式:
    python -m test.test_vision_display

按 q 退出。
"""

import cv2
import numpy as np
import sys

from src.vision.line_detector import LineDetector
from src.vision.pid_controller import PIDController
from src.vision.intersection_detector import IntersectionDetector


def draw_overlay(
    frame: np.ndarray,
    roi: np.ndarray,
    binary: np.ndarray,
    deviation: float,
    line_detected: bool,
    at_intersection: bool,
    left_speed: int,
    right_speed: int,
) -> np.ndarray:
    """在画面上绘制检测信息叠加层。"""
    h, w = frame.shape[:2]
    display = frame.copy()

    # 画 ROI 区域边界
    roi_top = int(h * 0.5)
    cv2.rectangle(display, (0, roi_top), (w, h), (0, 255, 0), 2)

    # 偏差指示条
    bar_y = 30
    bar_w = 200
    bar_x = (w - bar_w) // 2
    cv2.rectangle(display, (bar_x, bar_y - 5), (bar_x + bar_w, bar_y + 5), (100, 100, 100), -1)
    center_x = bar_x + bar_w // 2
    indicator_x = int(center_x + deviation * (bar_w // 2))
    color = (0, 255, 0) if line_detected else (0, 0, 255)
    cv2.circle(display, (indicator_x, bar_y), 8, color, -1)
    cv2.line(display, (center_x, bar_y - 10), (center_x, bar_y + 10), (255, 255, 255), 1)

    # 文字信息
    info_y = 60
    cv2.putText(display, f"Deviation: {deviation:+.3f}", (10, info_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(display, f"Line: {'YES' if line_detected else 'NO'}", (10, info_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if line_detected else (0, 0, 255), 2)
    cv2.putText(display, f"Intersection: {'YES' if at_intersection else 'NO'}", (10, info_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255) if at_intersection else (255, 255, 255), 2)
    cv2.putText(display, f"Motor L:{left_speed} R:{right_speed}", (10, info_y + 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # 右侧小窗：二值化结果
    small_h, small_w = 80, 120
    binary_resized = cv2.resize(binary, (small_w, small_h))
    binary_bgr = cv2.cvtColor(binary_resized, cv2.COLOR_GRAY2BGR)
    display[h - small_h - 10:h - 10, w - small_w - 10:w - 10] = binary_bgr
    cv2.putText(display, "Binary", (w - small_w - 10, h - small_h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return display


def main():
    print("=== Vision Display Test ===")
    print("按 q 退出")
    print()

    # 解析命令行参数
    camera_id = 0
    if len(sys.argv) > 1:
        try:
            camera_id = int(sys.argv[1])
        except ValueError:
            print(f"用法: python -m test.test_vision_display [camera_id]")
            sys.exit(1)

    detector = LineDetector(camera_id=camera_id)
    pid = PIDController()
    inter_detector = IntersectionDetector()

    if not detector.open():
        print(f"无法打开摄像头 {camera_id}")
        sys.exit(1)

    print(f"摄像头 {camera_id} 已打开")

    try:
        while True:
            frame = detector.read_frame()
            if frame is None:
                print("无法读取画面")
                continue

            # 黑线检测
            roi = detector._crop_roi(frame)
            binary = detector._preprocess(roi)
            deviation, line_detected = detector._find_line_center(binary)

            # 路口检测
            at_intersection = inter_detector.detect(binary, deviation, line_detected)

            # PID 计算
            left_speed, right_speed = pid.compute(deviation) if line_detected else (0, 0)

            # 绘制叠加层
            display = draw_overlay(
                frame, roi, binary,
                deviation, line_detected, at_intersection,
                left_speed, right_speed,
            )

            cv2.imshow("Vision Debug", display)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        detector.close()
        cv2.destroyAllWindows()
        print("已退出")


if __name__ == "__main__":
    main()
