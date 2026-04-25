# triager/requirement_collector.py
# 患者需求收集器
# 根据用户自述收集患者的具体需求（when/what 结构）
#
# @author n1ghts4kura
# @date 2026-04-18
#
# 重构自 EOR-Team/ufc-2026/src/smart_triager/triager/requirement_collector.py

import json
import dspy

from src import logger


class RequirementCollectorSignature(dspy.Signature):
    """Collect user requirements for hospital route planning (information extraction task).

    Optimization notes (2026-04-19):
    - Based on Signature optimization experiments, minimal desc works better
    - Information extraction tasks don't need detailed extraction rules
    - Field names are sufficient for the model to understand what to extract
    """

    requirement_from_user: str = dspy.InputField(
        desc="user requirement description"
    )

    requirements: str = dspy.OutputField(
        desc="requirements as JSON with when and what keys"
    )


collector = dspy.ChainOfThought(
    RequirementCollectorSignature
)


def collect_requirement(requirement_from_user: str) -> list[dict[str, str]]:
    """
    收集用户需求。

    Args:
        requirement_from_user: 用户的需求描述（中文）

    Returns:
        requirements_list: 解析后的需求列表，每个需求包含 when 和 what 字段
    """

    result = collector(
        instructions = "Extract requirements (when, what) from user text. Output JSON list.",
        requirement_from_user=requirement_from_user
    )

    # 解析 JSON 字符串（兼容单引号 Python repr 格式）
    requirements_list = []
    try:
        data = json.loads(result.requirements)
        # data 可以是 list 直接返回，或 dict 包含 "requirements" 键
        if isinstance(data, list):
            requirements_list = data
        else:
            requirements_list = data.get("requirements", [])
    except (json.JSONDecodeError, AttributeError):
        try:
            fixed = result.requirements.replace("'", '"')
            data = json.loads(fixed)
            if isinstance(data, list):
                requirements_list = data
            else:
                requirements_list = data.get("requirements", [])
        except (json.JSONDecodeError, AttributeError):
            requirements_list = []
        
    logger.info(f"[RequirementCollector] Receive user requirement: {requirement_from_user}")
    logger.info(f"[RequirementCollector] Extracted requirements: {requirements_list}")

    return requirements_list

__all__ = [
    "collect_requirement",
    "RequirementCollectorSignature"
]