"""
test/test_vision_api.py
模拟前端调用 Vision API — 启动导航、查询状态、停止导航。

运行方式:
    python -m test.test_vision_api

注意: 需要后端服务器已启动 (python -m src.main)
"""

import requests
import sys
import time


BASE_URL = "http://localhost:8000"


def _print_commands(commands: list[dict]) -> None:
    """将指令序列格式化为可读形式。"""
    if not commands:
        print("  (无指令)")
        return
    parts = []
    for cmd in commands:
        if cmd["action"] == "forward":
            parts.append(f"直行 {cmd['param']}")
        elif cmd["action"] == "turn":
            direction = "右转" if cmd["param"] > 0 else "左转"
            parts.append(f"{direction} {abs(cmd['param'])}°")
    print(f"  路线: {' → '.join(parts)}")


def test_get_commands_preview():
    """预览不同路线的 get_commands 输出"""
    print("=== 测试: 路线预览 ===")
    routes = [
        ("entrance", "pharmacy"),
        ("entrance", "surgery_clinic"),
        ("entrance", "emergency_clinic"),
        ("registration_center", "quit"),
    ]
    for start, dest in routes:
        resp = requests.post(f"{BASE_URL}/vision/start_navigate", json={
            "start": start, "destination": dest
        })
        data = resp.json()
        # 立即停止，只是预览指令
        requests.post(f"{BASE_URL}/vision/stop")

        print(f"  {start} → {dest}:")
        if data["success"]:
            _print_commands(data["commands"])
        else:
            print(f"  失败: {data['message']}")
    print()


def test_start_navigate():
    """模拟前端发起导航请求"""
    print("=== 测试: 启动导航 ===")

    payload = {
        "start": "entrance",
        "destination": "pharmacy",
        "camera_id": 0,
    }

    resp = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload)
    data = resp.json()

    print(f"  状态码: {resp.status_code}")
    print(f"  响应: {data}")

    assert resp.status_code == 200, f"请求失败: {resp.status_code}"
    assert data["success"] is True, f"导航启动失败: {data['message']}"
    assert len(data["commands"]) > 0, "指令为空"

    _print_commands(data["commands"])
    print()

    # 清理
    requests.post(f"{BASE_URL}/vision/stop")
    return data


def test_status_fields():
    """查询状态并验证字段"""
    print("=== 测试: 状态字段 ===")

    resp = requests.get(f"{BASE_URL}/vision/status")
    data = resp.json()

    print(f"  响应: {data}")
    assert "active" in data, "缺少 active 字段"
    if data["active"]:
        assert "state" in data, "缺少 state 字段"
        assert "current_command" in data, "缺少 current_command 字段"
        assert "total_commands" in data, "缺少 total_commands 字段"
        assert "intersections_passed" in data, "缺少 intersections_passed 字段"
        assert "intersections_target" in data, "缺少 intersections_target 字段"
    print()


def test_invalid_destination():
    """测试无效目的地"""
    print("=== 测试: 无效目的地 ===")

    payload = {
        "start": "entrance",
        "destination": "nonexistent_place",
    }

    resp = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload)
    data = resp.json()

    print(f"  状态码: {resp.status_code}")
    print(f"  响应: {data}")
    assert data["success"] is False, "无效目的地应返回失败"
    assert data["commands"] == [], "失败时指令应为空"
    print()


def test_same_start_and_dest():
    """测试起点等于终点"""
    print("=== 测试: 起点=终点 ===")

    payload = {
        "start": "entrance",
        "destination": "entrance",
    }

    resp = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload)
    data = resp.json()

    print(f"  响应: {data}")
    assert data["success"] is False, "起点=终点应返回失败"
    print()


def test_start_while_running():
    """测试导航中重复启动"""
    print("=== 测试: 导航中重复启动 ===")

    # 先启动一个导航
    payload = {
        "start": "entrance",
        "destination": "surgery_clinic",
    }
    resp1 = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload)
    print(f"  第一次启动: {resp1.json()['success']}")

    # 再次启动（应被拒绝）
    payload2 = {
        "start": "entrance",
        "destination": "pharmacy",
    }
    resp2 = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload2)
    data2 = resp2.json()
    print(f"  重复启动: {data2['success']}, {data2['message']}")
    assert data2["success"] is False, "重复启动应被拒绝"

    # 清理
    requests.post(f"{BASE_URL}/vision/stop")
    print()


def test_full_flow():
    """完整流程: 启动 → 查询状态 → 停止"""
    print("=== 测试: 完整流程 ===")

    # 1. 启动导航
    payload = {
        "start": "entrance",
        "destination": "pharmacy",
    }
    resp = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload)
    data = resp.json()
    assert data["success"] is True
    print(f"  1. 启动导航: {data['message']}")
    _print_commands(data["commands"])

    # 2. 查询状态（导航应已启动）
    time.sleep(0.5)
    status = requests.get(f"{BASE_URL}/vision/status").json()
    print(f"  2. 状态: active={status['active']}, state={status.get('state', 'N/A')}, "
          f"cmd={status.get('current_command', '?')}/{status.get('total_commands', '?')}")

    # 3. 停止
    stop_resp = requests.post(f"{BASE_URL}/vision/stop").json()
    print(f"  3. 停止: {stop_resp['message']}")

    # 4. 再次查询状态
    time.sleep(0.5)
    status2 = requests.get(f"{BASE_URL}/vision/status").json()
    print(f"  4. 停止后状态: active={status2['active']}")
    print()


def main():
    print(f"目标服务器: {BASE_URL}")
    print()

    # 检查服务器是否在线
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"服务器在线: {resp.json()}")
    except requests.ConnectionError:
        print(f"无法连接到 {BASE_URL}，请先启动后端服务器:")
        print("  python -m src.main")
        sys.exit(1)
    print()

    # 运行测试
    test_get_commands_preview()
    test_invalid_destination()
    test_same_start_and_dest()
    test_full_flow()
    test_start_while_running()
    test_status_fields()

    print("所有测试完成")


if __name__ == "__main__":
    main()
