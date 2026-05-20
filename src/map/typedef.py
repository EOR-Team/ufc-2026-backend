"""
map/typedef.py
Map data type definitions using Pydantic.
"""

import heapq

from pydantic import BaseModel, Field
from typing import Literal


class Node(BaseModel):
    """Map node representing a location."""
    id: str = Field(..., description="Unique node identifier")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    type: Literal["main", "nav"] = Field(..., description="Node type: main or nav")
    name: str | None = Field(default=None, description="Node name")
    description: str | None = Field(default=None, description="Node description")


class Edge(BaseModel):
    """Map edge representing a connection between two nodes."""
    u: str = Field(..., description="Source node ID")
    v: str = Field(..., description="Target node ID")
    name: str | None = Field(default=None, description="Edge name")
    cost: int | None = Field(default=None, description="Edge traversal cost (Manhattan distance)")


class Map(BaseModel):
    """Complete map structure with nodes and edges."""
    nodes: list[Node] = Field(..., description="List of all map nodes")
    edges: list[Edge] = Field(default_factory=list, description="List of all map edges")

    def model_post_init(self, __context) -> None:
        self._build_edges()

    def _build_edges(self) -> None:
        """Build edges from node adjacency: |dx|+|dy| == 1, cost = 1."""
        result: list[Edge] = []
        for i, u in enumerate(self.nodes):
            for j, v in enumerate(self.nodes):
                if i >= j:
                    continue
                if abs(u.x - v.x) + abs(u.y - v.y) == 1:
                    result.append(Edge(u=u.id, v=v.id, cost=1))
        self.edges = result

    def get_main_node_ids(self) -> list[str]:
        """Get IDs of all main (non-nav) nodes."""
        return [node.id for node in self.nodes if node.type == "main"]

    def get_main_node_info(self) -> dict[str, dict[str, str]]:
        """Get name and description for all main nodes."""
        return {
            node.id: {"name": node.name or "", "description": node.description or ""}
            for node in self.nodes
            if node.type == "main"
        }

    def dijkstra(self, start_id: str, end_id: str) -> list[str] | None:
        """Find shortest path between two nodes using Dijkstra's algorithm."""
        adj: dict[str, list[tuple[str, int]]] = {}
        for edge in self.edges:
            cost = edge.cost if edge.cost is not None else 1
            adj.setdefault(edge.u, []).append((edge.v, cost))
            adj.setdefault(edge.v, []).append((edge.u, cost))

        node_ids = {n.id for n in self.nodes}
        if start_id not in node_ids or end_id not in node_ids:
            return None

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
