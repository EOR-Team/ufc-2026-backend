"""
test/test_map_refactor.py
临时测试：验证运行时连边算法 + Dijkstra 在新地图上的连通性。

规则：|dx| + |dy| == 1 即连边（Manhattan 相邻）
"""

import json
import heapq
from pathlib import Path
from collections import defaultdict


def load_map():
    path = Path(__file__).parent.parent / "src" / "map" / "map.json"
    with open(path) as f:
        return json.load(f)


def rename_nav_nodes(nodes: list[dict]) -> list[dict]:
    """给 nav 节点赋予唯一 id: road_{x}_{y}"""
    renamed = []
    road_counter = defaultdict(int)
    for n in nodes:
        if n["type"] == "nav":
            new_id = f"road_{n['x']}_{n['y']}"
            n = {**n, "original_id": n["id"], "id": new_id}
            road_counter[new_id] += 1
        renamed.append(n)
    # 检查唯一性
    ids = [n["id"] for n in renamed]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"
    print(f"重命名 {sum(1 for n in nodes if n['type']=='nav')} 个 nav 节点 (无重复)")
    return renamed


def build_edges(nodes: list[dict]) -> list[dict]:
    """运行时构建 edges: |dx| + |dy| == 1 即连边"""
    edges = []
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if i >= j:
                continue
            dx = abs(u["x"] - v["x"])
            dy = abs(u["y"] - v["y"])
            if dx + dy == 1:
                cost = int(dx + dy)
                edges.append({"u": u["id"], "v": v["id"], "cost": cost, "name": ""})
    return edges


def dijkstra(nodes: list[dict], edges: list[dict], start: str, end: str) -> list[str] | None:
    """标准 Dijkstra"""
    node_ids = {n["id"] for n in nodes}
    if start not in node_ids or end not in node_ids:
        return None

    adj = defaultdict(list)
    for e in edges:
        adj[e["u"]].append((e["v"], e["cost"]))
        adj[e["v"]].append((e["u"], e["cost"]))

    distances = {n["id"]: float("inf") for n in nodes}
    distances[start] = 0.0
    previous = {n["id"]: None for n in nodes}
    heap = [(0.0, start)]

    while heap:
        dist, current = heapq.heappop(heap)
        if current == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            return path[::-1]
        if dist > distances[current]:
            continue
        for neighbor, cost in adj.get(current, []):
            new_dist = dist + cost
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))
    return None


def visualize_connectivity(nodes, edges):
    """打印每个节点的邻居数量"""
    adj = defaultdict(list)
    for e in edges:
        adj[e["u"]].append(e["v"])
        adj[e["v"]].append(e["u"])

    print("\n=== 节点连通性 ===")
    for n in nodes:
        neighbors = adj[n["id"]]
        main_flag = "★" if n["type"] == "main" else " "
        print(f"  [{main_flag}] {n['id']:25s} ({n['x']},{n['y']}) → {len(neighbors)} neighbors: {neighbors}")


def visualize_map_ascii(nodes):
    """ASCII 地图可视化"""
    max_x = max(n["x"] for n in nodes)
    max_y = max(n["y"] for n in nodes)
    grid = [["   " for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    for n in nodes:
        x, y = n["x"], n["y"]
        if n["type"] == "main":
            label = n["id"][:3].upper()
        else:
            label = " · "
        grid[y][x] = label

    print("\n=== 地图拓扑 (ASCII) ===")
    print("    " + "".join(f"{x:^3}" for x in range(max_x + 1)))
    for y in range(max_y + 1):
        print(f"y={y:<2} " + "".join(grid[y]))


def main():
    data = load_map()
    nodes = rename_nav_nodes(data["nodes"])

    visualize_map_ascii(nodes)

    edges = build_edges(nodes)
    print(f"\n构建 {len(edges)} 条边 (|dx|+|dy|=1)")

    visualize_connectivity(nodes, edges)

    # Dijkstra: 所有 main-main 配对
    main_ids = [n["id"] for n in nodes if n["type"] == "main"]
    print(f"\n=== Dijkstra 全配对 ({len(main_ids)} main nodes) ===")

    all_ok = True
    for i, start in enumerate(main_ids):
        for end in main_ids[i + 1 :]:
            path = dijkstra(nodes, edges, start, end)
            if path is None:
                print(f"  ✗ {start} → {end}: 不可达!")
                all_ok = False
            else:
                dist = len(path) - 1  # 边数 = 节点数-1
                # 简化路径：只显示 main + 拐点
                simplified = [path[0]]
                for k in range(1, len(path) - 1):
                    prev = next(n for n in nodes if n["id"] == path[k - 1])
                    curr = next(n for n in nodes if n["id"] == path[k])
                    next_n = next(n for n in nodes if n["id"] == path[k + 1])
                    # 方向变化即为拐点
                    if (prev["x"] - curr["x"], prev["y"] - curr["y"]) != (curr["x"] - next_n["x"], curr["y"] - next_n["y"]):
                        simplified.append(path[k])
                simplified.append(path[-1])
                print(f"  ✓ {start:25s} → {end:25s}  cost={dist:2d}  {simplified}")

    print(f"\n{'全部可达' if all_ok else '存在不可达!'}")


if __name__ == "__main__":
    main()
