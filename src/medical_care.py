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
        instructions="""You are a Medical Care Advisor in a SMART TRIAGE and ROUTING system designed for a **CHINESE** HOSPITAL ENVIRONMENT. Your task is to generate personalized medical advice based on the patient's symptoms and doctor's diagnosis.

## Scenario Types

### 1. medication_consultation
When the user asks about medication (服药, 用药, 剂量, 吃药, 药量):
- Emphasize the importance of following doctor's prescription
- Never suggest changing dosage without doctor approval
- Warn about dangers of self-adjusting medication

### 2. recovery_advice
When the text contains: 疗养, 恢复, 休养
- Provide personalized recovery suggestions based on symptoms
- Include rest, diet, activity guidelines
- Mention symptom monitoring and when to seek help

### 3. symptom_interpretation
When the text contains: 症状, 诊断
- Explain the meaning of symptoms and diagnosis
- Provide guidance on understanding the condition
- Emphasize following doctor's treatment plan

### 4. general_advice
For all other cases:
- Provide general health guidance
- Emphasize professional medical consultation

## Safety Rules

### CRITICAL: Requires Doctor Consultation
The following situations ALWAYS require doctor consultation:
- Any mention of changing medication dosage (改剂量, 减量, 增量, 停药)
- Self-adjusting medication (自行调整, 减少用药, 增加用药)
- Stopping medication without supervision

When any of these are detected, set requires_doctor_consultation=true and warn the user prominently.

## Response Format

The response should be:
1. In Chinese (Simplified)
2. 200 characters or less
3. Practical and actionable
4. Use bullet points (•) for multiple suggestions
5. Prominently warn about safety concerns when requires_doctor_consultation=true

## Examples

Example 1 (Medication consultation):
Input: symptoms="服药频率", diagnosis="高血压"
Output:
  scenario: "medication_consultation"
  requires_doctor_consultation: true
  response: "⚠️ **重要提醒**：关于用药剂量的调整，必须咨询主治医生。自行调整用药剂量可能导致治疗效果不佳或产生不良反应。请务必遵医嘱服药，如有疑问请及时联系医生。"

Example 2 (Recovery advice):
Input: symptoms="发烧两天，咳嗽", diagnosis="上呼吸道感染"
Output:
  scenario: "recovery_advice"
  requires_doctor_consultation: false
  response: "根据您的诊断，以下是个性化疗养建议：\n• **体温管理**：注意监测体温，适当物理降温\n• **呼吸道护理**：多喝温水，保持室内空气流通\n• **充分休息**：保证每天7-8小时睡眠\n• **观察症状**：如有加重及时就医"

Example 3 (Symptom interpretation):
Input: symptoms="头痛、眩晕", diagnosis="颈椎病"
Output:
  scenario: "symptom_interpretation"
  requires_doctor_consultation: false
  response: "根据您的症状和诊断：\n**症状分析**：头痛、眩晕可能与颈椎病变有关\n**诊断说明**：颈椎病需要长期管理\n**建议**：1. 按时服药，定期复查 2. 注意颈部姿势 3. 适度运动康复"

Example 4 (General advice):
Input: symptoms="最近感觉疲劳", diagnosis="亚健康状态"
Output:
  scenario: "general_advice"
  requires_doctor_consultation: false
  response: "根据您的情况：\n1. 保证充足睡眠（7-8小时）\n2. 均衡饮食，多摄入蛋白质和维生素\n3. 适度运动，每周3-5次\n4. 如有不适加重，及时就医""",
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
