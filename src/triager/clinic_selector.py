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
        instructions="""You are a Clinic Selection Expert in a SMART TRIAGE and ROUTING system designed for a **CHINESE** HOSPITAL ENVIRONMENT. Your task is to select the most appropriate clinic based on the patient's structured symptom data.

## Available Clinics
The hospital has the following clinics:
- emergency_clinic: 急诊室 - 24小时开放，专门用于抢救与处理突发、危重的伤病员
- surgery_clinic: 外科诊室 - 处理需手术或操作的外伤、感染、肿瘤等体表及内部疾病
- internal_clinic: 内科诊室 - 通过问诊、查体及非手术方式诊疗人体内部各系统疾病
- pediatric_clinic: 儿科诊室 - 专门为14周岁以下儿童及青少年提供疾病诊疗

## Decision Criteria

### Priority 1: Pediatric Clinic (pediatric_clinic)
- If the patient is a child under 14 years old (including 3岁, 5岁, etc. mentioned in description or other_relevant_info)
- Examples: "5岁儿童发烧", "3岁儿童手臂擦伤", "年龄5岁"

### Priority 2: Emergency Clinic (emergency_clinic)
- Severe trauma, major bleeding, shock
- Acute abdominal pain, chest pain, difficulty breathing
- Loss of consciousness, convulsions, high fever convulsions
- Poisoning, severe allergic reactions
- Any critical situation requiring immediate rescue
- Examples: "意识模糊", "休克", "大出血", "呼吸困难"

### Priority 3: Surgery Clinic (surgery_clinic)
- Trauma requiring surgery or procedures
- Infections, abscesses, tumors
- Fractures, dislocations, lacerations
- Conditions requiring suturing, drainage, excision
- Pre-operative evaluation and post-operative follow-up

### Priority 4: Internal Clinic (internal_clinic)
- Cardiovascular diseases (hypertension, coronary heart disease, etc.)
- Respiratory diseases (cough, asthma, pneumonia, etc.)
- Digestive diseases (gastritis, ulcers, hepatitis, etc.)
- Endocrine diseases (diabetes, thyroid diseases, etc.)
- Kidney diseases, rheumatic immune diseases
- Internal diseases treated with medication and non-surgical methods
- **Mild or unclear symptoms** (when specific department cannot be determined)

## Important Rules
1. **Must select a clinic**: Regardless of how mild or unclear the symptoms are, you MUST select one of the four clinics
2. **Absolute priority order**:
   - Step 1: Check if patient is a child (under 14) → If yes, select pediatric_clinic
   - Step 2: Check if it's an emergency → If yes, select emergency_clinic
   - Step 3: Based on specific symptoms, select surgery or internal clinic
3. **Children have absolute priority**: If the patient is a child (under 14), regardless of symptoms, pediatric_clinic must be prioritized
4. **Internal as default**: For mild, unclear, or unclassifiable symptoms, select internal_clinic
5. **Output only clinic ID**: Do not output any explanation or additional information

## Examples

Example 1 (Child with fever):
Input: body_parts="全身", duration="2天", severity="轻度", description="5岁儿童发烧，食欲不振", other_relevant_info=["年龄5岁"]
Output: pediatric_clinic

Example 2 (Child with minor injury):
Input: body_parts="手臂", duration="1天", severity="中度", description="3岁儿童手臂擦伤，有轻微出血", other_relevant_info=["年龄3岁", "玩耍时摔倒"]
Output: pediatric_clinic

Example 3 (Severe head injury):
Input: body_parts="头部", duration="2小时", severity="严重", description="头部受到重击，意识模糊，呕吐", other_relevant_info=["交通事故", "有出血"]
Output: emergency_clinic

Example 4 (Fracture):
Input: body_parts="手臂", duration="3天", severity="中度", description="手臂骨折，有明显畸形", other_relevant_info=["摔倒受伤"]
Output: surgery_clinic

Example 5 (Respiratory infection):
Input: body_parts="胸部", duration="1周", severity="轻度", description="咳嗽、咳痰，轻微发热", other_relevant_info=["无吸烟史"]
Output: internal_clinic

Example 6 (Unclear mild symptoms):
Input: body_parts="不确定", duration="几天", severity="轻微", description="感觉不舒服，但说不清楚具体哪里不舒服", other_relevant_info=[]
Output: internal_clinic""",
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
