"""
map/routes.py
FastAPI router for map-related endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.map.tools import get_commands

router = APIRouter(prefix="/map", tags=["map"])


class CommandsRequest(BaseModel):
    start: str
    end: str


class CommandsItem(BaseModel):
    action: str
    param: float


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
