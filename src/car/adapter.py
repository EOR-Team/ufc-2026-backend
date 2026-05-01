"""
car/adapter.py
Path to car commands conversion layer.
Converts map node paths into actionable car control sequences.
"""

from typing import Literal

from src.logger import debug
from src.map import get_map

# Cardinal directions
AbsoluteDir = Literal["east", "west", "south", "north", "stay"]

# Car action types
ActionType = Literal["forward", "turn", "stop"]


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
        # 180° turn - use原地旋转 turn(180)
        return 180
    elif diff == 90:
        return 90
    elif diff == 270:
        return -90
    return 0


def _expand_to_full_path(path: list[str]) -> list[str]:
    """
    Expand a path of main nodes to include nav nodes using Dijkstra.
    """
    if len(path) < 2:
        return path

    map_data = get_map()
    node_dict = {n.id: n for n in map_data.nodes}
    full_path = [path[0]]

    for i in range(len(path) - 1):
        start, end = path[i], path[i + 1]
        segment = map_data.dijkstra(start, end)
        if segment:
            # Skip first node of segment to avoid duplicate
            full_path.extend(segment[1:])
        else:
            debug(f"[Car] No path found from {start} to {end}")

    return full_path


def _merge_consecutive_straights(actions: list[tuple[ActionType, float]]) -> list[tuple[ActionType, float]]:
    """Merge consecutive forward moves into a single action."""
    if not actions:
        return []

    merged: list[tuple[ActionType, float]] = []
    for action_type, param in actions:
        if action_type == "forward" and merged and merged[-1][0] == "forward":
            # Accumulate distance
            merged[-1] = ("forward", merged[-1][1] + param)
        else:
            merged.append((action_type, param))

    return merged


def path_to_commands(path: list[str]) -> list[tuple[ActionType, float]]:
    """
    Convert a map node path to car control command sequence.

    Args:
        path: List of node IDs representing the route
              e.g., ["entrance", "toilet"] or ["entrance", "crossroad5", "toilet"]

    Returns:
        List of (action_type, parameter) tuples
        e.g., [("forward", 3.0), ("turn", -90), ("forward", 5.0)]

    Example:
        >>> commands = path_to_commands(["entrance", "toilet"])
        >>> for action, param in commands:
        ...     if action == "forward":
        ...         forward(param)
        ...     elif action == "turn":
        ...         turn(int(param))
    """
    # Expand path to include nav nodes
    full_path = _expand_to_full_path(path)
    if len(full_path) < 2:
        return []

    # Build node lookup
    map_data = get_map()
    node_dict = {n.id: n for n in map_data.nodes}

    actions: list[tuple[ActionType, float]] = []
    current_dir: AbsoluteDir | None = None

    for i in range(len(full_path) - 1):
        current_id = full_path[i]
        next_id = full_path[i + 1]

        current_node = node_dict.get(current_id)
        next_node = node_dict.get(next_id)

        if not current_node or not next_node:
            continue

        dx = next_node.x - current_node.x
        dy = next_node.y - current_node.y
        distance = abs(dx) + abs(dy)

        target_dir = _get_absolute_direction(dx, dy)

        # First segment - always forward
        if current_dir is None:
            if distance > 0:
                actions.append(("forward", distance))
            current_dir = target_dir
            continue

        # Calculate relative turn
        turn_angle = _get_relative_turn(current_dir, target_dir)

        if turn_angle == 180:
            # 180° turn - use原地旋转 turn(180)
            if distance > 0:
                actions.append(("forward", distance))
            actions.append(("turn", 180))
        elif turn_angle != 0:
            # Add turn action
            actions.append(("turn", turn_angle))
            # Add forward if there's distance
            if distance > 0:
                actions.append(("forward", distance))
        else:
            # Going straight - add forward
            if distance > 0:
                actions.append(("forward", distance))

        current_dir = target_dir

    # Merge consecutive straights
    actions = _merge_consecutive_straights(actions)

    debug(f"[Car] Path {path} → {len(actions)} commands")
    return actions
