# triager/condition_collector.py
# User physical condition collector
#
# @author n1ghts4kura
# @date 2026-04-18
#
# Refactored from EOR-Team/ufc-2026/src/smart_triager/triager/condition_collector.py

import dspy

from src import logger


class ConditionCollectorSignature(dspy.Signature):
    """Collect user physical condition info (information extraction task).

    Optimization notes (2026-04-19):
    - Based on Signature optimization experiments, minimal desc works better
    - Information extraction tasks don't need detailed extraction rules
    """

    previous_conclusions: str = dspy.InputField(
        desc = "之前的病情分析结论（如果有的话）"
    )

    description_from_user: str = dspy.InputField(
        desc="用户的症状描述"
    )

    duration: str = dspy.OutputField(
        desc="症状持续时间（中文）"
    )

    severity: str = dspy.OutputField(
        desc="症状严重程度（中文）"
    )

    body_parts: str = dspy.OutputField(
        desc="受影响的身体部位（中文）"
    )

    description: str = dspy.OutputField(
        desc="症状描述（中文）"
    )

    other_relevant_info: list[str] = dspy.OutputField(
        desc="其他相关信息（中文）"
    )


collector = dspy.ChainOfThought(
    ConditionCollectorSignature
)


DEFAULT_CONDITION = {
    "duration": "未填写",
    "severity": "未填写",
    "body_parts": "未填写",
    "description": "未填写",
    "other_relevant_info": [],
}


def _normalize_condition_value(value: object) -> str:
    if value in (None, "", "unknown"):
        return "未填写"
    return str(value)


def collect_condition(description_from_user: str, previous_conclusions: list[str] = []) -> dict:
    """Collect user physical condition information.

    Args:
        description_from_user: 用户的症状描述（中文）
        previous_conclusions: 之前的病情分析结论（如果有的话）

    Returns:
        dict: 包含症状信息的字典，包括 duration, severity, body_parts, description, other_relevant_info 字段
    """

    previous_conclusions_str = ""

    if previous_conclusions:
        for i in range(len(previous_conclusions)):
            previous_conclusions_str += f"[{ i + 1 }] { previous_conclusions[i] };"

    try:
        resp = collector(
            instructions="从用户的描述中提取信息：症状持续时间、严重程度、受影响的身体部位、症状描述、其他相关信息。如果存在之前的分析，将其作为基础，并在此基础上进行补充和修正。",
            description_from_user = description_from_user,
            previous_conclusions = previous_conclusions_str
        )

        duration = _normalize_condition_value(getattr(resp, "duration", None))
        severity = _normalize_condition_value(getattr(resp, "severity", None))
        body_parts = _normalize_condition_value(getattr(resp, "body_parts", None))
        description = _normalize_condition_value(getattr(resp, "description", None))
        other_relevant_info = getattr(resp, "other_relevant_info", [])

        logger.info(f"[ConditionCollector] Receive user description: {description_from_user}; previous conclusions: {previous_conclusions_str}")
        logger.info(f"[ConditionCollector] Reasoning: {resp.reasoning}")
        logger.info(f"[ConditionCollector] Extracted condition: duration={duration}, severity={severity}, body_parts={body_parts}, description={description}, other_info={other_relevant_info}")

        return {
            "duration": duration,
            "severity": severity,
            "body_parts": body_parts,
            "description": description,
            "other_relevant_info": other_relevant_info
        }
    except Exception as e:
        logger.error(f"[ConditionCollector] Fallback to default condition due to error: {e}", exc_info=True)
        return DEFAULT_CONDITION.copy()


__all__ = [
    "collect_condition"
]
