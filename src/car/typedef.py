"""
car/typedef.py
Car control type definitions.
"""

from pydantic import BaseModel, Field
from typing import Literal


class TurnType(Literal["left", "right"]):
    """Turn direction: left or right."""
    pass


class CarAction(BaseModel):
    """Single car action: turn first, then move."""
    turn: TurnType = Field(..., description="Turn direction")
    distance: float = Field(..., ge=0, description="Movement distance after turning")


class CarCommands(BaseModel):
    """Sequence of car movement commands."""
    actions: list[CarAction] = Field(default_factory=list, description="Ordered list of actions")
