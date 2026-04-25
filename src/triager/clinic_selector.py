# triager/clinic_selector.py
# 诊室选择智能体 - 根据结构化症状数据选择合适的诊室
#
# @author n1ghts4kura
# @date 2026-04-18
#
# 重构自 EOR-Team/ufc-2026/src/smart_triager/triager/clinic_selector.py

import dspy


class ClinicSelectorSignature(dspy.Signature):
    """根据患者症状选择合适的诊室"""

    body_parts: str = dspy.InputField(
        desc = "the body parts affected by the symptoms"
    )

    duration: str = dspy.InputField(
        desc = "how long the symptoms have been experienced"
    )

    severity: str = dspy.InputField(
        desc = "the severity level of the symptoms (轻微/中等/严重 or 轻/中/重)"
    )

    description: str = dspy.InputField(
        desc = "detailed description of the symptoms"
    )

    other_relevant_info: list[str] = dspy.InputField(
        desc = "other relevant information such as medical history, age, etc."
    )

    clinic_selection: str = dspy.OutputField(
        desc = '''the selected clinic ID. Must be one of: "emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic". Decision priority: 1. Pediatric (if patient is child under 14) > 2. Emergency (if severe symptoms) > 3. Surgery (if surgical intervention needed) > 4. Internal (default for mild/unclear symptoms)'''
    )


collector = dspy.ChainOfThought(
    ClinicSelectorSignature
)


def select_clinic(
    body_parts: str,
    duration: str,
    severity: str,
    description: str,
    other_relevant_info: list[str]
) -> tuple[str, object]:
    """
    根据患者症状选择合适的诊室。

    Args:
        body_parts: 受影响的身体部位
        duration: 症状持续时间
        severity: 症状严重程度（轻微/中等/严重）
        description: 症状详细描述
        other_relevant_info: 其他相关信息（如年龄、病史等）

    Returns:
        tuple: (clinic_selection, reasoning)
        - clinic_selection: 选择的诊室 ID
        - reasoning: ChainOfThought 推理过程
    """
    result = collector(
        # [STEP 3] 极限压缩
        instructions="Clinic selector in a Chinese hospital. Select: pediatric_clinic (child under 14), emergency_clinic (severe), surgery_clinic (needs operation), internal_clinic (default/mild).",
        body_parts=body_parts,
        duration=duration,
        severity=severity,
        description=description,
        other_relevant_info=other_relevant_info
    )

    return result.clinic_selection, result


__all__ = [
    "select_clinic",
    "ClinicSelectorSignature"
]
