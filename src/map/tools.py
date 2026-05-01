"""
map/tools.py
Map management functions and Map extensions.
"""

import json
import heapq
from pathlib import Path

from src.logger import debug, info, error
from src.utils import ROOT_DIR, Result
from src.map.typedef import Map, Node, Edge


def _load_map_from_json(json_path: Path | str | None = None) -> Map | None:
    """Load map from JSON file and return Map object."""
    if json_path is None:
        json_path = ROOT_DIR / "src" / "map" / "map.json"
    else:
        json_path = Path(json_path)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Map(**data)
    except Exception as e:
        error(f"[Map] Failed to load map: {e}")
        return None


def _compute_all_costs(map_obj: Map) -> None:
    """Compute Manhattan distance costs for all edges in-place."""
    node_dict = {n.id: n for n in map_obj.nodes}

    for edge in map_obj.edges:
        u_node = node_dict.get(edge.u)
        v_node = node_dict.get(edge.v)
        if u_node and v_node:
            edge.cost = int(abs(u_node.x - v_node.x) + abs(u_node.y - v_node.y))


# ========== Map Instance Methods ==========

def _get_main_node_ids(self: Map) -> list[str]:
    """Get IDs of all main (non-nav) nodes."""
    return [node.id for node in self.nodes if node.type == "main"]


def _get_main_node_info(self: Map) -> dict[str, dict[str, str]]:
    """Get name and description for all main nodes."""
    return {
        node.id: {"name": node.name or "", "description": node.description or ""}
        for node in self.nodes
        if node.type == "main"
    }


def _dijkstra(self: Map, start_id: str, end_id: str) -> list[str] | None:
    """Find shortest path between two nodes using Dijkstra's algorithm."""
    # Build adjacency list
    adj: dict[str, list[tuple[str, int]]] = {}
    for edge in self.edges:
        cost = edge.cost if edge.cost is not None else 1
        adj.setdefault(edge.u, []).append((edge.v, cost))
        adj.setdefault(edge.v, []).append((edge.u, cost))

    # Check nodes exist
    node_ids = {n.id for n in self.nodes}
    if start_id not in node_ids or end_id not in node_ids:
        return None

    # Dijkstra
    distances: dict[str, float] = {n.id: float("inf") for n in self.nodes}
    distances[start_id] = 0.0
    previous: dict[str, str | None] = {n.id: None for n in self.nodes}
    heap: list[tuple[float, str]] = [(0.0, start_id)]

    while heap:
        dist, current = heapq.heappop(heap)

        if current == end_id:
            path = []
            node = end_id
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


# Attach methods to Map class
Map.get_main_node_ids = _get_main_node_ids
Map.get_main_node_info = _get_main_node_info
Map.dijkstra = _dijkstra


# ========== Module-level Cache ==========

_cached_map: Map | None = None


def get_map() -> Map:
    """
    Get the pre-loaded and pre-computed Map object.
    Uses lazy loading - loads and computes costs on first call.
    """
    global _cached_map

    if _cached_map is None:
        map_obj = _load_map_from_json()
        if map_obj is None:
            raise RuntimeError("Failed to load map from map.json")
        _compute_all_costs(map_obj)
        _cached_map = map_obj
        info(f"[Map] Loaded map with {len(map_obj.nodes)} nodes, {len(map_obj.edges)} edges")

    return _cached_map
