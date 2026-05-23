"""
vision_calib_utils.py
Shared utilities for vision calibration scripts.

Provides:
- ensure_calib_dir()  — create data/vision_calib/{scene}/
- JsonlWriter         — line-buffered JSONL output
- log_console_10hz()  — rate-limited console logging helper
- draw_scene_overlay() — common OpenCV display overlay for scene mode
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALIB_DIR = ROOT / "data" / "vision_calib"


def ensure_calib_dir(scene: str) -> Path:
    """Create and return data/vision_calib/{scene}/ directory."""
    path = CALIB_DIR / scene
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitkeep").touch(exist_ok=True)
    return path


class JsonlWriter:
    """Line-buffered JSON line writer."""

    def __init__(self, path: Path):
        self._f = open(path, "w", encoding="utf-8")

    def write(self, record: dict) -> None:
        self._f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._f.flush()

    def close(self) -> None:
        self._f.close()


def log_console_10hz(last_time: float, now: float, msg: str) -> tuple[float, bool]:
    """
    Rate-limited console log at ~10Hz.

    Args:
        last_time: timestamp of last logged message
        now: current time
        msg: message to print if interval elapsed

    Returns:
        (new_last_time, was_printed)
    """
    if now - last_time >= 0.1:
        print(msg)
        return now, True
    return last_time, False
