"""
map/routes.py
FastAPI router for map-related endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

from src.car.adapter import path_to_commands

router = APIRouter(prefix="/map", tags=["map"])


class TranslateRequest(BaseModel):
    path: list[str]


class TranslateItem(BaseModel):
    action: Literal["forward", "turn", "stop"]
    param: float


@router.post("/translate")
def translate_path(body: TranslateRequest) -> list[TranslateItem]:
    """
    Convert a map node path to car control command sequence.

    Body:
        path: List of node IDs, e.g. ["entrance", "toilet"]

    Returns:
        List of {action, param} dicts, e.g. [{"action": "forward", "param": 4.0}, ...]
    """
    commands = path_to_commands(body.path)
    return [TranslateItem(action=a, param=p) for a, p in commands]