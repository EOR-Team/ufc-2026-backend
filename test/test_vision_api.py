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
    print(f"  指令: {data['commands']}")
    print()
    return data


def test_status():
    """查询导航状态"""
    print("=== 测试: 查询状态 ===")

    resp = requests.get(f"{BASE_URL}/vision/status")
    data = resp.json()

    print(f"  状态码: {resp.status_code}")
    print(f"  响应: {data}")
    print()
    return data


def test_stop():
    """停止导航"""
    print("=== 测试: 停止导航 ===")

    resp = requests.post(f"{BASE_URL}/vision/stop")
    data = resp.json()

    print(f"  状态码: {resp.status_code}")
    print(f"  响应: {data}")
    print()
    return data


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
    print(f"  第一次启动: {resp1.json()}")

    # 再次启动（应被拒绝）
    payload2 = {
        "start": "entrance",
        "destination": "pharmacy",
    }
    resp2 = requests.post(f"{BASE_URL}/vision/start_navigate", json=payload2)
    data2 = resp2.json()
    print(f"  重复启动: {data2}")
    assert data2["success"] is False, "重复启动应被拒绝"

    # 清理
    requests.post(f"{BASE_URL}/vision/stop")
    print()


def test_full_flow():
    """完整流程: 启动 → 等待 → 查询状态 → 停止"""
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

    # 2. 查询状态
    time.sleep(1)
    status = requests.get(f"{BASE_URL}/vision/status").json()
    print(f"  2. 状态: active={status['active']}, state={status.get('state', 'N/A')}")

    # 3. 停止
    stop_resp = requests.post(f"{BASE_URL}/vision/stop").json()
    print(f"  3. 停止: {stop_resp}")

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
    test_invalid_destination()
    test_full_flow()
    test_start_while_running()

    print("所有测试完成")


if __name__ == "__main__":
    main()
