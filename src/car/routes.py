"""
car/routes.py
FastAPI router for robot car control endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.car.control import forward, backward, turn, stop

router = APIRouter(prefix="/car", tags=["car"])


class CommandResponse(BaseModel):
    status: str = "ok"


@router.post("/forward", response_model=CommandResponse)
def car_forward(length: float):
    """Move forward a specified distance (blocking)."""
    forward(length)
    return CommandResponse()


@router.post("/backward", response_model=CommandResponse)
def car_backward(length: float):
    """Move backward a specified distance (blocking)."""
    backward(length)
    return CommandResponse()


@router.post("/turn", response_model=CommandResponse)
def car_turn(angle: int):
    """Rotate the car by a specified angle (blocking)."""
    turn(angle)
    return CommandResponse()


@router.post("/stop", response_model=CommandResponse)
def car_stop():
    """Stop the car immediately (blocking)."""
    stop()
    return CommandResponse()