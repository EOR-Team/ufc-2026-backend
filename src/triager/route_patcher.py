# triager/route_patcher.py
# 路线修改器 - 使用 ChainOfThought 模式根据用户需求生成修改方案
#
# @author n1ghts4kura
# @date 2026-04-19
#
# 重构自 EOR-Team/ufc-2026/src/smart_triager/triager/route_patcher.py

import dspy
from typing import Optional

# 可用的位置节点定义
AVAILABLE_LOCATIONS = {
    "entrance": "医院入口",
    "registration_center": "挂号中心",
    "emergency_clinic": "急诊室 - 24小时开放，专门用于抢救与处理突发、危重的伤病员",
    "surgery_clinic": "外科诊室 - 处理需手术或操作的外伤、感染、肿瘤等体表及内部疾病",
    "internal_clinic": "内科诊室 - 通过问诊、查体及非手术方式诊疗人体内部各系统疾病",
    "pediatric_clinic": "儿科诊室 - 专门为14周岁以下儿童及青少年提供疾病诊疗",
    "payment_center": "缴费中心",
    "pharmacy": "药房",
    "toilet": "洗手间/厕所",
    "restroom": "洗手间/厕所",  # 别名
    "print_shop": "打印店",
    "quit": "出口",
}


def _format_locations() -> str:
    """格式化可用位置列表供 instructions 使用"""
    lines = []
    for loc_id, desc in AVAILABLE_LOCATIONS.items():
        lines.append(f"- {loc_id}: {desc}")
    return "\n".join(lines)


class RoutePatcherSignature(dspy.Signature):
    """Generate route modification patches for hospital navigation (generation task).

    Optimization notes (2026-04-19):
    - Generation task: timing keywords are essential (现在, 给医生看病前, 拿完药之后, 最后)
    - Output format (type/previous/this/next) must be clear but can be concise
    - Minimal desc compression while preserving generation quality
    """

    destination_clinic_id: str = dspy.InputField(
        desc="target clinic ID"
    )

    requirement_summary: list[dict] = dspy.InputField(
        desc="list of {when: timing, what: action} requirements"
    )

    current_route: list[str] = dspy.InputField(
        desc="path as location IDs, e.g. ['entrance', 'registration_center', 'surgery_clinic']"
    )

    patches: list[dict] = dspy.OutputField(
        desc='''list of patches: {type: "insert"|"delete", previous: loc, this: loc, next: loc}.
Example: [{"type": "insert", "previous": "entrance", "this": "toilet", "next": "registration_center"}].
Output [] if no modifications needed.'''
    )


class RoutePatcherCot(dspy.ChainOfThought):
    """路线修改器的 CoT 模块"""
    pass


def apply_patches(route: list[str], patches: list[dict]) -> list[str]:
    """
    应用 patches 到路线上。

    Args:
        route: 原路线
        patches: 修改方案列表

    Returns:
        修改后的路线
    """
    if not patches:
        return route.copy()

    # 深拷贝路线
    result = route.copy()

    # 先应用所有 delete 操作
    for patch in patches:
        if patch.get("type") == "delete":
            previous = patch.get("previous")
            this = patch.get("this")

            if previous in result:
                idx = result.index(previous)
                # 删除 previous 后的第一个 this
                if idx + 1 < len(result) and result[idx + 1] == this:
                    result.pop(idx + 1)

    # 再应用所有 insert 操作
    for patch in patches:
        if patch.get("type") == "insert":
            previous = patch.get("previous")
            this = patch.get("this")
            next_loc = patch.get("next")

            if previous in result:
                idx = result.index(previous)
                if next_loc and next_loc in result:
                    next_idx = result.index(next_loc)
                    if next_idx == idx + 1:
                        result.insert(idx + 1, this)
                    else:
                        # 如果 next 不在紧邻位置，调整插入逻辑
                        result.insert(idx + 1, this)
                else:
                    # 追加到 previous 之后
                    result.insert(idx + 1, this)

    return result


def patch_route(
    destination_clinic_id: str,
    requirement_summary: list[dict],
    origin_route: Optional[list[str]] = None
) -> tuple[list[str], list[dict]]:
    """
    根据用户需求生成路线修改方案并应用。

    Args:
        destination_clinic_id: 目标诊室 ID
        requirement_summary: 用户需求列表，每个需求包含 'when'（时机）和 'what'（动作）
        origin_route: 原路线，默认为基于 surgery_clinic 的标准路线

    Returns:
        tuple: (final_route, patches)
        - final_route: 修改后的最终路线
        - patches: 生成的修改方案列表
    """
    if origin_route is None:
        origin_route = [
            "entrance",
            "registration_center",
            "surgery_clinic",
            "payment_center",
            "pharmacy",
            "quit"
        ]

    locations_info = _format_locations()

    # 创建 CoT 模块
    cot = RoutePatcherCot(RoutePatcherSignature)

    result = cot(
        instructions=f"""Route patcher in a Chinese hospital. Insert locations based on: "现在"(after entrance), "给医生看病前"(before clinic), "拿完药之后"(after pharmacy), "最后"(before quit). Output JSON: {{"patches": [{{"type": "insert"|"delete", "previous": loc, "this": loc, "next": loc}}]}}.""",
        destination_clinic_id=destination_clinic_id,
        requirement_summary=requirement_summary,
        current_route=origin_route
    )

    # 提取 patches
    patches = result.patches if hasattr(result, 'patches') else []

    # 应用 patches 到路线
    final_route = apply_patches(origin_route, patches)

    return final_route, patches


__all__ = [
    "patch_route",
    "RoutePatcherSignature",
    "apply_patches",
    "AVAILABLE_LOCATIONS",
]
