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


class RequirementCollectorSignature(dspy.Signature):
    """收集用户需求（when/what 结构）"""

    requirement_from_user: str = dspy.InputField(
        desc = "the user's requirement description in Chinese for hospital route planning"
    )

    requirements: str = dspy.OutputField(
        desc = '''a valid JSON string containing a "requirements" list. Each requirement has "when" (timing/sequence, e.g., "给医生看病前", "拿完药之后") and "what" (action, e.g., "去洗手间", "原路返回"). If no requirements, return "{\"requirements\": []}". Example: "{\"requirements\": [{\"when\": \"给医生看病前\", \"what\": \"去洗手间\"}]}"'''
    )


collector = dspy.ChainOfThought(
    RequirementCollectorSignature
)


def collect_requirement(requirement_from_user: str):
    """
    收集用户需求。

    Args:
        requirement_from_user: 用户的需求描述（中文）

    Returns:
        tuple: (requirements_list, reasoning)
        - requirements_list: list of dicts with 'when' and 'what' keys
        - reasoning: ChainOfThought 推理过程
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

    return requirements_list, result


__all__ = [
    "collect_requirement",
    "RequirementCollectorSignature"
]