"""
vision/navigator.py
Line-following navigation controller.

Consumes get_commands() output directly: [{action: "forward"|"turn", param: float}].
- "forward" param = Manhattan distance → number of intersections to pass
- "turn" param = angle → execute fixed turn at intersection

State machine:
    FOLLOW_LINE → 检测到路口 → CROSSING（过路口）→ TURNING（转向）→ FOLLOW_LINE → ... → DONE
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
TURN_SPEED: Final[int] = 30                      # motor speed for turning (0-100)


class NavState(Enum):
    """Navigation state machine states."""
    IDLE = auto()
    FOLLOW_LINE = auto()
    CROSSING = auto()
    TURNING = auto()
    DONE = auto()
    STOPPED = auto()


class Navigator:
    """
    Line-following navigator that directly executes get_commands() output.

    Usage:
        from src.map import get_commands

        nav = Navigator()
        commands = get_commands("entrance", "pharmacy")
        nav.set_commands(commands)
        nav.run()
    """

    def __init__(self, camera_id: int = 0):
        self._line_detector = LineDetector(camera_id=camera_id)
        self._pid = PIDController()
        self._intersection_detector = IntersectionDetector()

        self._commands: list[dict] = []         # [{action, param}]
        self._cmd_idx: int = 0                  # current command index
        self._intersections_passed: int = 0     # intersections passed in current forward segment
        self._intersections_target: int = 0     # how many to pass before next turn
        self._state = NavState.IDLE
        self._last_intersection_time: float = 0.0

    def set_commands(self, commands: list[dict]) -> None:
        """
        Set commands from get_commands() output.

        Args:
            commands: [{action: "forward"|"turn", param: float}]
                      forward param = Manhattan distance (1.0 = one edge = one intersection)
                      turn param = angle in degrees (positive = right, negative = left)
        """
        self._commands = commands
        self._cmd_idx = 0
        self._state = NavState.IDLE
        info(f"[Navigator] Commands set: {commands}")

    def _prepare_next_forward(self) -> bool:
        """
        Set up the next forward segment by counting intersections to pass.

        Returns:
            True if there's a forward segment to execute, False if no more commands.
        """
        self._intersections_passed = 0
        self._intersections_target = 0

        # Count intersections from consecutive forward commands
        while self._cmd_idx < len(self._commands):
            cmd = self._commands[self._cmd_idx]
            if cmd["action"] == "forward":
                # Each 1.0 Manhattan distance = one edge = one intersection to pass
                self._intersections_target += int(round(cmd["param"]))
                self._cmd_idx += 1
            else:
                break

        return self._intersections_target > 0

    def stop(self) -> None:
        """Emergency stop."""
        self._state = NavState.STOPPED
        Robot.stop()
        self._line_detector.close()
        info("[Navigator] Stopped")

    def run(self) -> None:
        """
        Main navigation loop. Blocks until all commands are executed or stopped.

        Executes get_commands() sequence:
            forward N → 巡线经过 N 个路口
            turn ±90 → 路口固定转向
        """
        if not self._commands:
            warning("[Navigator] No commands set")
            return

        if not self._line_detector.open():
            error("[Navigator] Failed to open camera")
            return

        # Prepare first forward segment
        if not self._prepare_next_forward():
            warning("[Navigator] No forward commands at start")
            self._line_detector.close()
            return

        self._state = NavState.FOLLOW_LINE
        self._pid.reset()
        self._intersection_detector.reset()
        self._last_intersection_time = 0.0

        info(f"[Navigator] Starting: {len(self._commands)} commands, "
             f"first segment: {self._intersections_target} intersections")

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
                self._state = NavState.CROSSING
                self._intersections_passed += 1
                info(f"[Navigator] Intersection {self._intersections_passed}/{self._intersections_target}")
                return

        # PID line following
        left_speed, right_speed = self._pid.compute(deviation)
        self._set_differential_speed(left_speed, right_speed)

    def _tick_crossing(self) -> None:
        """
        Cross through intersection with fixed forward movement.
        Then decide: more intersections in this segment → continue,
        or next command is a turn → execute turn, or done.
        """
        # Move forward to cross intersection center
        Robot.t_up(LINE_FOLLOW_BASE_SPEED)
        time.sleep(INTERSECTION_FORWARD_TIME)
        Robot.stop()
        self._last_intersection_time = time.time()

        # Check if we've passed enough intersections for current forward segment
        if self._intersections_passed < self._intersections_target:
            # More intersections to pass in this segment
            self._intersection_detector.reset()
            self._pid.reset()
            self._state = NavState.FOLLOW_LINE
            return

        # Forward segment complete — look for next turn command
        turn_angle = self._get_next_turn()

        if turn_angle is None:
            # No more commands — done
            self._state = NavState.DONE
            info("[Navigator] All commands executed, destination reached!")
            return

        # Execute turn
        self._pending_turn_angle = turn_angle
        self._state = NavState.TURNING

    def _get_next_turn(self) -> float | None:
        """
        Consume the next turn command from the command list.

        Returns:
            Turn angle (positive = right, negative = left), or None if no more turns.
        """
        while self._cmd_idx < len(self._commands):
            cmd = self._commands[self._cmd_idx]
            if cmd["action"] == "turn":
                self._cmd_idx += 1
                return cmd["param"]
            elif cmd["action"] == "forward":
                # Next forward segment — prepare it and return None (no turn needed yet)
                self._prepare_next_forward()
                return None
        return None

    def _tick_turning(self) -> None:
        """Execute a fixed-angle turn at intersection."""
        angle = self._pending_turn_angle

        if angle > 0:
            Robot.turnRight(TURN_SPEED)
            direction = "right"
        elif angle < 0:
            Robot.turnLeft(TURN_SPEED)
            direction = "left"
        else:
            direction = "forward"

        # Turn for duration proportional to angle
        duration = abs(angle) / 90.0 * TURN_DURATION_90
        time.sleep(duration)
        Robot.stop()
        self._last_intersection_time = time.time()

        # After turn, prepare next forward segment
        has_next = self._prepare_next_forward()
        self._intersection_detector.reset()
        self._pid.reset()

        if has_next:
            self._state = NavState.FOLLOW_LINE
            info(f"[Navigator] Turned {direction} {abs(angle)}°, next: {self._intersections_target} intersections")
        else:
            self._state = NavState.DONE
            info(f"[Navigator] Turned {direction} {abs(angle)}°, all commands done")

    def _set_differential_speed(self, left: int, right: int) -> None:
        """Set left/right motor speeds for differential steering."""
        Robot._bot.MotorRun(0, 'forward', left)
        Robot._bot.MotorRun(1, 'forward', left)
        Robot._bot.MotorRun(2, 'forward', right)
        Robot._bot.MotorRun(3, 'forward', right)
