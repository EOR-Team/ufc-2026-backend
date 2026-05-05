"""
map/tools.py
Map management functions and utilities.
"""

import json
from pathlib import Path

from src.logger import info, error
from src.utils import ROOT_DIR
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
