"""
vision/routes.py
FastAPI router for vision-based line-following navigation.
"""

import threading
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.logger import info
from src.vision.navigator import Navigator
from src.map import get_commands


router = APIRouter(prefix="/vision", tags=["vision"])

# Global navigator instance
_navigator: Optional[Navigator] = None
_navigator_thread: Optional[threading.Thread] = None


class NavigateRequest(BaseModel):
    start: str
    destination: str
    camera_id: int = 0


class NavigateResponse(BaseModel):
    success: bool
    message: str
    path: list[str] = []


@router.post("/start_navigate", response_model=NavigateResponse)
def start_navigate(request: NavigateRequest) -> NavigateResponse:
    """
    Start line-following navigation from start to destination.

    Computes path using map module, then starts the navigator in a background thread.
    """
    global _navigator, _navigator_thread

    if _navigator is not None and _navigator_thread and _navigator_thread.is_alive():
        return NavigateResponse(
            success=False,
            message="Navigation already in progress. Stop first."
        )

    # Compute path from map
    map_commands = get_commands(request.start, request.destination)
    if not map_commands:
        return NavigateResponse(
            success=False,
            message=f"No path found from {request.start} to {request.destination}"
        )

    # Convert commands to node path
    # get_commands returns [{action, param}], but we need the node sequence
    # Use map.dijkstra directly for the node path
    from src.map import get_map
    map_data = get_map()
    path = map_data.dijkstra(request.start, request.destination)
    if not path:
        return NavigateResponse(
            success=False,
            message=f"No path found from {request.start} to {request.destination}"
        )

    _navigator = Navigator(camera_id=request.camera_id)
    _navigator.set_path(path)

    # Run in background thread
    _navigator_thread = threading.Thread(target=_navigator.run, daemon=True)
    _navigator_thread.start()

    info(f"[Vision] Navigation started: {request.start} → {request.destination}")
    return NavigateResponse(
        success=True,
        message=f"Navigation started: {request.start} → {request.destination}",
        path=path,
    )


@router.post("/stop")
def stop_navigation() -> dict:
    """Emergency stop navigation."""
    global _navigator
    if _navigator is not None:
        _navigator.stop()
        _navigator = None
        return {"success": True, "message": "Navigation stopped"}
    return {"success": True, "message": "No navigation in progress"}


@router.get("/status")
def navigation_status() -> dict:
    """Get current navigation status."""
    if _navigator is not None and _navigator_thread and _navigator_thread.is_alive():
        return {
            "active": True,
            "state": _navigator._state.name,
            "current_step": _navigator._current_step,
            "total_steps": len(_navigator._path),
        }
    return {"active": False}
