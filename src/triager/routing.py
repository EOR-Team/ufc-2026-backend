# triager/routing.py
# triager 路由
#
# @author n1ghts4kura
# @date 2026-04-25
#

from fastapi import APIRouter
from pydantic import BaseModel

from src.triager.clinic_selector import select_clinic
from src.triager.condition_collector import collect_condition
from src.triager.requirement_collector import collect_requirement
from src.triager.route_patcher import patch_route


triager_router = APIRouter(prefix="/triager")


class SelectClinicRequest(BaseModel):
    body_parts: str
    duration: str
    severity: str
    description: str
    other_relevant_info: list[str] = []


class CollectConditionRequest(BaseModel):
    description_from_user: str


class CollectRequirementRequest(BaseModel):
    description_from_user: str


class PatchRouteRequest(BaseModel):
    destination_clinic_id: str
    requirement_summary: list[dict] = []
    origin_route: list[str] | None = None


@triager_router.post("/select_clinic")
def route_select_clinic(request: SelectClinicRequest):
    resp = select_clinic(
        body_parts=request.body_parts,
        duration=request.duration,
        severity=request.severity,
        description=request.description,
        other_relevant_info=request.other_relevant_info
    )

    return resp


@triager_router.post("/collect_condition")
def route_collect_condition(request: CollectConditionRequest):
    resp = collect_condition(
        description_from_user=request.description_from_user
    )

    return resp


@triager_router.post("/collect_requirement")
def route_collect_requirement(request: CollectRequirementRequest):
    resp = collect_requirement(
        requirement_from_user=request.description_from_user
    )

    return resp


@triager_router.post("/patch_route")
def route_patch_route(request: PatchRouteRequest):
    resp = patch_route(
        destination_clinic_id=request.destination_clinic_id,
        requirement_summary=request.requirement_summary,
        origin_route=request.origin_route
    )

    return resp