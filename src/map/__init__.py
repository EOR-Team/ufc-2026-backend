"""
map/__init__.py
Map module - structured hospital map data.

Usage:
    from src.map import get_map

    map_data = get_map()
    main_ids = map_data.get_main_node_ids()
    info = map_data.get_main_node_info()
    path = map_data.dijkstra("entrance", "surgery_clinic")
"""

from src.map.typedef import Node, Edge, Map
from src.map.tools import get_map


__all__ = ["Node", "Edge", "Map", "get_map"]
