# triager/condition_collector.py
# User physical condition collector
#
# @author n1ghts4kura
# @date 2026-04-18
#
# Refactored from EOR-Team/ufc-2026/src/smart_triager/triager/condition_collector.py

import dspy


class ConditionCollectorSignature(dspy.Signature):
    """Collect user physical condition info (information extraction task).

    Optimization notes (2026-04-19):
    - Based on Signature optimization experiments, minimal desc works better
    - Information extraction tasks don't need detailed extraction rules
    """

    description_from_user: str = dspy.InputField(
        desc="user symptom description"
    )

    duration: str = dspy.OutputField(
        desc="symptom duration"
    )

    severity: str = dspy.OutputField(
        desc="severity level"
    )

    body_parts: str = dspy.OutputField(
        desc="affected body parts"
    )

    description: str = dspy.OutputField(
        desc="symptom description"
    )

    other_relevant_info: list[str] = dspy.OutputField(
        desc="other relevant info"
    )


collector = dspy.ChainOfThought(
    ConditionCollectorSignature
)


def collect_condition(description_from_user: str):
    return collector(
        instructions="Extract from user text: duration, severity, body_parts, description, other_info.",
        description_from_user=description_from_user
    )


__all__ = [
    "collect_condition"
]
