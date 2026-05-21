"""
map/tools.py
Map management functions, utilities, and path-to-command conversion.
"""

import json
from pathlib import Path
from typing import Literal

from src.logger import info, error, debug
from src.utils import ROOT_DIR
from src.map.typedef import Map, Node, Edge

AbsoluteDir = Literal["east", "west", "south", "north", "stay"]


def _rename_nav_nodes(nodes: list[dict]) -> list[dict]:
    """Assign unique IDs to nav nodes: road_{x}_{y}."""
    for n in nodes:
        if n.get("type") == "nav" and n.get("id") == "road":
            n["id"] = f"road_{n['x']}_{n['y']}"
    return nodes


def _load_map_from_json(json_path: Path | str | None = None) -> Map | None:
    """Load map from JSON file and return Map object."""
    if json_path is None:
        json_path = ROOT_DIR / "src" / "map" / "map.json"
    else:
        json_path = Path(json_path)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["nodes"] = _rename_nav_nodes(data.get("nodes", []))
        return Map(**data)
    except Exception as e:
        error(f"[Map] Failed to load map: {e}")
        return None


def _compute_all_costs(map_obj: Map) -> None:
    """Deprecated: costs are now set during edge building. Kept as no-op for compatibility."""
    pass


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
        _cached_map = map_obj
        info(f"[Map] Loaded map with {len(map_obj.nodes)} nodes, {len(map_obj.edges)} edges")

    return _cached_map


# ========== Path to Commands ==========


def _get_absolute_direction(dx: float, dy: float) -> AbsoluteDir:
    """Convert coordinate delta to cardinal direction."""
    if dx > 0:
        return "east"
    elif dx < 0:
        return "west"
    elif dy > 0:
        return "south"
    elif dy < 0:
        return "north"
    return "stay"


def _direction_to_degrees(direction: AbsoluteDir) -> int:
    """Map cardinal direction to degrees (clockwise from east)."""
    mapping = {"east": 0, "north": 90, "west": 180, "south": 270, "stay": 0}
    return mapping[direction]


def _get_relative_turn(current_dir: AbsoluteDir, target_dir: AbsoluteDir) -> int:
    """
    Calculate the relative turn angle between two directions.
    Returns angle in degrees: positive = clockwise (right), negative = counter-clockwise (left).
    """
    current_deg = _direction_to_degrees(current_dir)
    target_deg = _direction_to_degrees(target_dir)
    diff = (target_deg - current_deg) % 360

    if diff == 0:
        return 0
    elif diff == 180:
        return 180
    elif diff == 90:
        return 90
    elif diff == 270:
        return -90
    return 0


def _merge_consecutive_straights(actions: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Merge consecutive forward moves into a single action."""
    if not actions:
        return []

    merged: list[tuple[str, float]] = []
    for action_type, param in actions:
        if action_type == "forward" and merged and merged[-1][0] == "forward":
            merged[-1] = ("forward", merged[-1][1] + param)
        else:
            merged.append((action_type, param))

    return merged


def get_commands(start: str, end: str) -> list[dict[str, str | float]]:
    """
    Convert a single-segment route between two nodes into car control commands.

    Args:
        start: Starting node ID
        end: Ending node ID

    Returns:
        List of {action, param} dicts, e.g.:
            [{"action": "forward", "param": 3.0}, {"action": "turn", "param": -90}]
    """
    map_data = get_map()
    path = map_data.dijkstra(start, end)
    if path is None or len(path) < 2:
        return []

    node_dict = {n.id: n for n in map_data.nodes}

    actions: list[tuple[str, float]] = []
    current_dir: AbsoluteDir | None = None

    for i in range(len(path) - 1):
        current_id = path[i]
        next_id = path[i + 1]

        current_node = node_dict.get(current_id)
        next_node = node_dict.get(next_id)

        if not current_node or not next_node:
            continue

        dx = next_node.x - current_node.x
        dy = next_node.y - current_node.y
        distance = abs(dx) + abs(dy)

        target_dir = _get_absolute_direction(dx, dy)

        if current_dir is None:
            if distance > 0:
                actions.append(("forward", distance))
            current_dir = target_dir
            continue

        turn_angle = _get_relative_turn(current_dir, target_dir)

        if turn_angle == 180:
            if distance > 0:
                actions.append(("forward", distance))
            actions.append(("turn", 180))
        elif turn_angle != 0:
            actions.append(("turn", turn_angle))
            if distance > 0:
                actions.append(("forward", distance))
        else:
            if distance > 0:
                actions.append(("forward", distance))

        current_dir = target_dir

    actions = _merge_consecutive_straights(actions)

    debug(f"[Map] Commands {start} → {end}: {len(actions)} actions")
    return [{"action": a, "param": p} for a, p in actions]


def get_cost(start: str, end: str) -> int | None:
    """
    Get the shortest-path cost (Manhattan distance) between two nodes.

    Args:
        start: Starting node ID
        end: Ending node ID

    Returns:
        Total cost in meters, or None if unreachable.
    """
    map_data = get_map()
    path = map_data.dijkstra(start, end)
    if path is None or len(path) < 2:
        return None
    return len(path) - 1
