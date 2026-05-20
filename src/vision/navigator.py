"""
vision/navigator.py
Line-following navigation controller.

Integrates LineDetector, PIDController, and IntersectionDetector to
navigate a black-line course. At intersections, uses pre-planned path
to decide turn direction.
"""

import time
from enum import Enum, auto
from typing import Final

from src.logger import info, warning, error
from src.vision.line_detector import LineDetector
from src.vision.pid_controller import PIDController
from src.vision.intersection_detector import IntersectionDetector
from src.car.LOBOROBOT import Robot


# Calibration constants (measure on real hardware)
INTERSECTION_FORWARD_TIME: Final[float] = 1.5   # seconds to cross intersection center
TURN_DURATION_90: Final[float] = 1.0             # seconds for 90-degree turn
LINE_FOLLOW_BASE_SPEED: Final[int] = 20          # base motor speed (0-100)
INTERSECTION_COOLDOWN: Final[float] = 2.0        # seconds to ignore after handling intersection


class NavState(Enum):
    """Navigation state machine states."""
    IDLE = auto()
    FOLLOW_LINE = auto()
    AT_INTERSECTION = auto()
    CROSSING = auto()
    TURNING = auto()
    DONE = auto()
    STOPPED = auto()


class Navigator:
    """
    Line-following navigator with pre-planned path execution.

    Usage:
        nav = Navigator()
        nav.set_path(["entrance", "road_2_9", "road_2_7", "pharmacy"])
        nav.run()
    """

    def __init__(self, camera_id: int = 0):
        self._line_detector = LineDetector(camera_id=camera_id)
        self._pid = PIDController()
        self._intersection_detector = IntersectionDetector()

        self._path: list[str] = []
        self._current_step: int = 0  # index of next intersection to handle
        self._state = NavState.IDLE
        self._last_intersection_time: float = 0.0

    def set_path(self, path: list[str]) -> None:
        """
        Set the navigation path as a list of node IDs.

        Args:
            path: Ordered list of node IDs, e.g. ["entrance", "road_2_9", "road_2_7", "pharmacy"]
                  The car follows the line and turns at each intermediate node.
        """
        self._path = path
        self._current_step = 0
        self._state = NavState.IDLE
        info(f"[Navigator] Path set: {path}")

    def _get_turn_direction(self) -> str:
        """
        Determine turn direction at current intersection based on path.

        Compares positions of previous, current, and next nodes to decide.
        Returns: "left", "right", or "forward"
        """
        if self._current_step < 1 or self._current_step >= len(self._path) - 1:
            return "forward"

        from src.map import get_map
        map_data = get_map()
        node_dict = {n.id: n for n in map_data.nodes}

        prev_id = self._path[self._current_step - 1]
        curr_id = self._path[self._current_step]
        next_id = self._path[self._current_step + 1]

        prev = node_dict.get(prev_id)
        curr = node_dict.get(curr_id)
        next_node = node_dict.get(next_id)

        if not all([prev, curr, next_node]):
            return "forward"

        # Direction vectors
        dx_in = curr.x - prev.x
        dy_in = curr.y - prev.y
        dx_out = next_node.x - curr.x
        dy_out = next_node.y - curr.y

        # Cross product to determine turn direction
        # In coordinate system: x=right, y=down
        cross = dx_in * dy_out - dy_in * dx_out

        if cross > 0:
            return "right"
        elif cross < 0:
            return "left"
        else:
            return "forward"

    def stop(self) -> None:
        """Emergency stop."""
        self._state = NavState.STOPPED
        Robot.stop()
        self._line_detector.close()
        info("[Navigator] Stopped")

    def run(self) -> None:
        """
        Main navigation loop. Blocks until path is complete or stopped.

        State machine:
            IDLE → FOLLOW_LINE → AT_INTERSECTION → CROSSING → TURNING → FOLLOW_LINE → ... → DONE
        """
        if not self._path or len(self._path) < 2:
            warning("[Navigator] No valid path set")
            return

        if not self._line_detector.open():
            error("[Navigator] Failed to open camera")
            return

        self._state = NavState.FOLLOW_LINE
        self._pid.reset()
        self._intersection_detector.reset()
        self._last_intersection_time = 0.0

        info(f"[Navigator] Starting navigation: {self._path[0]} → {self._path[-1]}")

        try:
            while self._state not in (NavState.DONE, NavState.STOPPED):
                self._tick()
        except KeyboardInterrupt:
            info("[Navigator] Interrupted by user")
        finally:
            Robot.stop()
            self._line_detector.close()

    def _tick(self) -> None:
        """Single iteration of the navigation loop."""

        if self._state == NavState.FOLLOW_LINE:
            self._tick_follow_line()

        elif self._state == NavState.AT_INTERSECTION:
            self._tick_at_intersection()

        elif self._state == NavState.CROSSING:
            self._tick_crossing()

        elif self._state == NavState.TURNING:
            self._tick_turning()

    def _tick_follow_line(self) -> None:
        """Follow the black line, check for intersections."""
        frame = self._line_detector.read_frame()
        if frame is None:
            return

        deviation, line_detected = self._line_detector.detect(frame)

        # Preprocess for intersection detector
        roi = self._line_detector._crop_roi(frame)
        binary = self._line_detector._preprocess(roi)

        # Check for intersection (with cooldown)
        now = time.time()
        if now - self._last_intersection_time > INTERSECTION_COOLDOWN:
            at_intersection = self._intersection_detector.detect(
                binary, deviation, line_detected
            )
            if at_intersection:
                Robot.stop()
                self._state = NavState.AT_INTERSECTION
                info(f"[Navigator] At intersection, step {self._current_step}/{len(self._path) - 1}")
                return

        # PID line following
        left_speed, right_speed = self._pid.compute(deviation)
        self._set_differential_speed(left_speed, right_speed)

    def _tick_at_intersection(self) -> None:
        """Handle intersection: cross it with fixed forward movement."""
        self._current_step += 1

        if self._current_step >= len(self._path) - 1:
            # Reached destination
            Robot.stop()
            self._state = NavState.DONE
            info("[Navigator] Destination reached!")
            return

        turn_dir = self._get_turn_direction()
        info(f"[Navigator] Intersection {self._current_step}: turning {turn_dir}")

        # Move forward to cross intersection center
        Robot.t_up(LINE_FOLLOW_BASE_SPEED)
        time.sleep(INTERSECTION_FORWARD_TIME)
        Robot.stop()
        self._last_intersection_time = time.time()

        if turn_dir == "forward":
            # No turn needed, go straight through
            self._state = NavState.FOLLOW_LINE
            self._intersection_detector.reset()
            self._pid.reset()
        else:
            self._state = NavState.TURNING
            self._pending_turn = turn_dir

    def _tick_crossing(self) -> None:
        """Cross through intersection (currently handled in _tick_at_intersection)."""
        self._state = NavState.FOLLOW_LINE

    def _tick_turning(self) -> None:
        """Execute a fixed-angle turn at intersection."""
        turn_dir = self._pending_turn

        if turn_dir == "left":
            Robot.turnLeft(30)
        elif turn_dir == "right":
            Robot.turnRight(30)

        time.sleep(TURN_DURATION_90)
        Robot.stop()
        self._last_intersection_time = time.time()

        # Reset detectors and resume line following
        self._intersection_detector.reset()
        self._pid.reset()
        self._state = NavState.FOLLOW_LINE

        info(f"[Navigator] Turned {turn_dir}, resuming line follow")

    def _set_differential_speed(self, left: int, right: int) -> None:
        """Set left/right motor speeds for differential steering."""
        # Motors 0,1 = left side; motors 2,3 = right side
        # (adjust based on actual wiring)
        Robot._bot.MotorRun(0, 'forward', left)
        Robot._bot.MotorRun(1, 'forward', left)
        Robot._bot.MotorRun(2, 'forward', right)
        Robot._bot.MotorRun(3, 'forward', right)
