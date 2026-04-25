# src/medical_care.py
# 医疗护理建议智能体 - 根据症状和诊断结果生成个性化医疗建议
#
# @author n1ghts4kura
# @date 2026-04-19
#
# 重构自 EOR-Team/ufc-2026/src/medical/agent.py

import dspy
from typing import Optional


class MedicalCareSignature(dspy.Signature):
    """根据患者症状和诊断结果生成个性化医疗建议"""

    symptoms: str = dspy.InputField(
        desc = "patient's symptoms description"
    )

    diagnosis: str = dspy.InputField(
        desc = "doctor's diagnosis result"
    )

    scenario: str = dspy.OutputField(
        desc = '''one of: "medication_consultation", "recovery_advice", "symptom_interpretation", "general_advice"'''
    )

    requires_doctor_consultation: bool = dspy.OutputField(
        desc = "whether the user needs to consult a doctor for safety reasons (e.g., medication dosage changes)"
    )

    response: str = dspy.OutputField(
        desc = "personalized medical advice in Chinese, 200 characters or less, practical and actionable"
    )


collector = dspy.ChainOfThought(
    MedicalCareSignature
)


def get_medical_care_advice(
    symptoms: str,
    diagnosis: str
) -> tuple[dict, object]:
    """
    根据患者症状和诊断结果生成个性化医疗建议。

    Args:
        symptoms: 患者描述的症状
        diagnosis: 医生的诊断结果

    Returns:
        tuple: (advice_dict, reasoning)
        - advice_dict: 包含 scenario, requires_doctor_consultation, response 的字典
        - reasoning: ChainOfThought 推理过程
    """
    result = collector(
        instructions="""Medical Care Advisor in a Chinese hospital. Output JSON with: scenario (medication_consultation/recovery_advice/symptom_interpretation/general_advice), requires_doctor (bool), response (Chinese, 200 chars).
""",
        symptoms=symptoms,
        diagnosis=diagnosis
    )

    advice_dict = {
        "scenario": result.scenario,
        "requires_doctor_consultation": result.requires_doctor_consultation,
        "response": result.response
    }

    return advice_dict, result


__all__ = [
    "get_medical_care_advice",
    "MedicalCareSignature"
]
