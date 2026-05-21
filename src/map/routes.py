"""
map/routes.py
FastAPI router for map-related endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.map.tools import get_commands, get_cost, get_map

router = APIRouter(prefix="/map", tags=["map"])


class CommandsRequest(BaseModel):
    start: str
    end: str


class CommandsItem(BaseModel):
    action: str
    param: float


class NodeInfo(BaseModel):
    id: str
    name: str
    description: str


class CostResponse(BaseModel):
    cost: int | None


# ========== Nodes ==========


@router.get("/nodes")
def route_get_nodes() -> list[NodeInfo]:
    """
    Get all main node IDs, names, and descriptions.

    Returns:
        List of {id, name, description} for every main node.
    """
    info = get_map().get_main_node_info()
    return [NodeInfo(id=k, name=v["name"], description=v["description"]) for k, v in info.items()]


# ========== Commands ==========


@router.post("/commands")
def route_get_commands(body: CommandsRequest) -> list[CommandsItem]:
    """
    Get car control commands for a single-segment route between two nodes.

    Body:
        start: Starting node ID (e.g. "entrance")
        end: Ending node ID (e.g. "surgery_clinic")

    Returns:
        List of {action, param} dicts, e.g.:
            [{"action": "forward", "param": 3.0}, {"action": "turn", "param": -90}]
    """
    commands = get_commands(body.start, body.end)
    return [CommandsItem(**cmd) for cmd in commands]


# ========== Cost ==========


@router.post("/cost")
def route_get_cost(body: CommandsRequest) -> CostResponse:
    """
    Get the shortest-path cost (Manhattan distance) between two nodes.

    Body:
        start: Starting node ID (e.g. "entrance")
        end: Ending node ID (e.g. "surgery_clinic")

    Returns:
        {cost: int | null} — total distance in meters, or null if unreachable.
    """
    cost = get_cost(body.start, body.end)
    return CostResponse(cost=cost)
