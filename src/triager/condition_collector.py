# triager/condition_collector.py
# 用户身体条件采集
#
# @author n1ghts4kura
# @date 2026-04-18
#

import dspy


class ConditionCollectorSignature(dspy.Signature):

    description_from_user: str = dspy.InputField(
        desc = "the description from user about the user's current feelings and conditions"
    )

    duration: str = dspy.OutputField(
        desc = "the duration of how long the user has been experiencing the uncomfortable symptoms (e.g., “三个月”, “两天”, etc.). Left it empty if the user does not mention the duration."
    )

    severity: str = dspy.OutputField(
        desc = "the severity or level of discomfort that the user is experiencing him/herself (e.g., “轻微”, “中等”, “严重”, etc.). **This field should only capture the degree or intensity of the discomfort. It should not contain descriptions of the pain nature (e.g., “刺痛”, “钝痛”) or other characteristics of the symptom itself, which belong in the `description` field. This field should also not contain purely emotional interjections (e.g., “哎呀”, “啊呀”) or filler words. Extract and output the descriptive content about the degree only.**"
    )

    body_parts: str = dspy.OutputField(
        desc = "the body parts that are affected by the symptoms (e.g., “胸部”, “头部”, etc.), or where the user is feeling uncomfortable (e.g., “全身”, etc.). This field **specifically captures the anatomical location(s) of the current discomfort.**"
    )

    description: str = dspy.OutputField(
        desc = "a concrete description of the user's symptom or main complaint** (e.g., “阵发性刺痛”, “持续性钝痛并伴有头晕”, “脚踝肿胀疼痛”). **This field should detail the nature and characteristics of the discomfort itself, rather than just a summary label."
    )

    other_relevant_info: list[str] = dspy.OutputField(
        desc = "any other relevant information that is helpful for nurse to diagnose the user's condition and do triage for the user."
    )


collector = dspy.ChainOfThought(
    ConditionCollectorSignature
)

def collect_condition(description_from_user: str):
    return collector(
        instructions = "collect the user's body condition information from the description provided by the user. Extract and output the duration, severity, body parts affected, a concrete description of the symptoms, and any other relevant information that can help nurses diagnose the user's condition and perform triage. Pay special attention to accurately capturing the severity level and the specific body parts involved, as well as providing a detailed description of the symptoms.",
        description_from_user = description_from_user
    )


__all__ = [
    "collect_condition"
]
