# test/test_car.py
# 小车运动测试 — 覆盖全部控制 API
#
# 约束:
#   - PWM 占比: FORWARD_SPEED=30, ROTATE_SPEED=30（均 ≤ 30）
#   - 运动时间: 每步 ≤ 2.5s
#     forward:  distance / V_FORWARD ≤ 2.5s → distance ≤ 0.5375m → 上限 0.5m
#     turn:     degree  / V_ROTATE  ≤ 2.5s → degree  ≤ 240°     → 上限 240°

import pytest

from src.car import (
    forward,
    backward,
    turn,
    stop,
    is_hardware_available,
    Robot,
)
from src.car.adapter import path_to_commands
from src.car.control import forward as _forward_raw


# ============================================================================
# 约束常量
# ============================================================================

FORWARD_SPEED = Robot.FORWARD_SPEED   # 30
ROTATE_SPEED  = Robot.ROTATE_SPEED     # 30
V_FORWARD     = Robot.V_FORWARD        # 0.215 m/s
V_ROTATE      = Robot.V_ROTATE         # 96.0 deg/s
MAX_DURATION  = 2.5                    # s


def _forward_duration(distance: float) -> float:
    return distance / V_FORWARD


def _turn_duration(degree: float) -> float:
    return degree / V_ROTATE


# ============================================================================
# Test Cases
# ============================================================================


class TestHardwareAvailability:
    """硬件可用性检查"""

    def test_is_hardware_available_exists(self):
        """is_hardware_available 应为 bool"""
        assert isinstance(is_hardware_available, bool)

    def test_robot_instance_exists(self):
        """Robot 单例存在"""
        assert Robot is not None

    def test_robot_speed_constants_within_limit(self):
        """FORWARD_SPEED 和 ROTATE_SPEED 不超过 30"""
        assert FORWARD_SPEED <= 30
        assert ROTATE_SPEED <= 30

    def test_calibration_constants_positive(self):
        """V_FORWARD 和 V_ROTATE 为正数"""
        assert V_FORWARD > 0
        assert V_ROTATE > 0


class TestForward:
    """前进 API"""

    def test_forward_within_limit(self):
        """前进 0.5m（约 2.33s，在 2.5s 内）"""
        distance = 0.5
        assert _forward_duration(distance) <= MAX_DURATION
        forward(distance)

    def test_forward_short_distance(self):
        """前进 0.1m"""
        forward(0.1)

    def test_forward_at_duration_boundary(self):
        """前进 0.537m（约 2.498s，逼近上限）"""
        distance = 0.537
        duration = _forward_duration(distance)
        assert duration <= MAX_DURATION, f"{duration}s exceeds {MAX_DURATION}s"
        forward(distance)


class TestBackward:
    """后退 API"""

    def test_backward_within_limit(self):
        """后退 0.5m（约 2.33s）"""
        distance = 0.5
        assert _forward_duration(distance) <= MAX_DURATION
        backward(distance)

    def test_backward_short_distance(self):
        """后退 0.2m"""
        backward(0.2)


class TestTurn:
    """旋转 API"""

    def test_turn_right_within_limit(self):
        """右转 90°（约 0.94s）"""
        degree = 90
        assert _turn_duration(degree) <= MAX_DURATION
        turn(degree)

    def test_turn_left_within_limit(self):
        """左转 90°（约 0.94s）"""
        degree = -90
        assert _turn_duration(abs(degree)) <= MAX_DURATION
        turn(degree)

    def test_turn_180_right(self):
        """右转 180°（约 1.875s）"""
        degree = 180
        assert _turn_duration(degree) <= MAX_DURATION
        turn(degree)

    def test_turn_180_left(self):
        """左转 180°（约 1.875s）"""
        degree = -180
        assert _turn_duration(abs(degree)) <= MAX_DURATION
        turn(degree)

    def test_turn_at_boundary(self):
        """旋转 240°（2.5s，恰好在上限）"""
        degree = 240
        assert _turn_duration(degree) == pytest.approx(MAX_DURATION, rel=0.01)
        turn(degree)

    def test_turn_zero_noop(self):
        """turn(0) 应为空操作"""
        turn(0)


class TestStop:
    """停止 API"""

    def test_stop(self):
        """调用 stop() 不抛异常"""
        stop()

    def test_stop_after_movement(self):
        """前进后立即停止"""
        forward(0.3)
        stop()


class TestCombinedMovements:
    """组合运动序列"""

    def test_simple_route(self):
        """模拟简单导航: 前进 → 右转 → 前进 → 停止"""
        forward(0.4)
        turn(90)
        forward(0.4)
        stop()

    def test_full_command_sequence(self):
        """使用全部基本指令"""
        forward(0.2)
        turn(-90)
        forward(0.3)
        turn(180)
        backward(0.2)
        turn(90)
        forward(0.1)
        stop()

    def test_duration_all_within_limit(self):
        """确保所有运动步长都在 2.5s 内"""
        steps: list[tuple[str, float]] = [
            ("forward", 0.5),
            ("turn", 90),
            ("forward", 0.3),
            ("turn", -90),
            ("backward", 0.4),
            ("turn", 180),
            ("forward", 0.2),
        ]
        for action, param in steps:
            if action in ("forward", "backward"):
                dur = _forward_duration(param)
            else:
                dur = _turn_duration(abs(param))
            assert dur <= MAX_DURATION, f"{action}({param}) takes {dur:.2f}s > {MAX_DURATION}s"


class TestAdapterIntegration:
    """路径→指令适配器集成测试"""

    def test_path_to_commands_simple(self):
        """entrance → toilet 生成有效指令序列"""
        commands = path_to_commands(["entrance", "toilet"])
        assert isinstance(commands, list)
        assert len(commands) > 0
        for action, param in commands:
            assert action in ("forward", "turn", "stop")

    def test_path_to_commands_single_node(self):
        """单节点路径返回空列表"""
        commands = path_to_commands(["entrance"])
        assert commands == []

    def test_path_to_commands_unknown_nodes(self):
        """未知节点路径返回空列表"""
        commands = path_to_commands(["mars", "jupiter"])
        assert commands == []

    def test_execute_adapter_commands(self):
        """执行 path_to_commands 输出的指令序列"""
        commands = path_to_commands(["entrance", "registration_center", "pharmacy", "quit"])
        assert len(commands) > 0
        for action, param in commands:
            if action == "forward":
                forward(param)
            elif action == "turn":
                turn(int(param))
            elif action == "stop":
                stop()

    def test_path_to_commands_all_main_nodes(self):
        """完整路线: 入口 → 挂号 → 诊室 → 缴费 → 药房 → 出口"""
        route = [
            "entrance",
            "registration_center",
            "surgery_clinic",
            "payment_center",
            "pharmacy",
            "quit",
        ]
        commands = path_to_commands(route)
        for action, param in commands:
            if action == "forward":
                forward(param)
            elif action == "turn":
                turn(int(param))
        stop()


class TestRobotAsyncApi:
    """Robot 异步 API 直调"""

    @pytest.mark.asyncio
    async def test_robot_forward_async(self):
        """异步 forward: 0.4m（约 1.86s）"""
        distance = 0.4
        assert _forward_duration(distance) <= MAX_DURATION
        await Robot.forward(distance)

    @pytest.mark.asyncio
    async def test_robot_turn_left_async(self):
        """异步 turn_left: 120°（1.25s）"""
        degree = 120
        assert _turn_duration(degree) <= MAX_DURATION
        await Robot.turn_left(degree)

    @pytest.mark.asyncio
    async def test_robot_turn_right_async(self):
        """异步 turn_right: 60°（0.625s）"""
        degree = 60
        assert _turn_duration(degree) <= MAX_DURATION
        await Robot.turn_right(degree)

    @pytest.mark.asyncio
    async def test_robot_backward_async(self):
        """异步 backward: 0.2m（约 0.93s）"""
        distance = 0.2
        assert _forward_duration(distance) <= MAX_DURATION
        await Robot.backward(distance)

    def test_robot_stop_sync(self):
        """Robot.stop() 同步调用"""
        Robot.stop()


class TestEdgeCases:
    """边界情况"""

    def test_turn_beyond_limit_rejected(self):
        """超过 2.5s 上限的角度应在测试中标记"""
        degree = 360
        duration = _turn_duration(degree)
        assert duration > MAX_DURATION, (
            f"360° turn should exceed limit ({duration:.2f}s > {MAX_DURATION}s)"
        )

    def test_forward_beyond_limit_rejected(self):
        """超过 2.5s 上限的距离应在测试中标记"""
        distance = 1.0
        duration = _forward_duration(distance)
        assert duration > MAX_DURATION, (
            f"1.0m forward should exceed limit ({duration:.2f}s > {MAX_DURATION}s)"
        )

    def test_multiple_stops(self):
        """连续多次 stop() 不应出错"""
        stop()
        stop()
        stop()

    def test_stop_without_movement(self):
        """未运动前 stop()"""
        stop()
