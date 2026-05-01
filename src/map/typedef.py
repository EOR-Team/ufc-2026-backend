"""
map/typedef.py
Map data type definitions using Pydantic.
"""

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
    edges: list[Edge] = Field(..., description="List of all map edges")
