# DSPy Signature Design

This guide covers signature design patterns based on project experience and optimization experiments.

## Signature Structure

A DSPy Signature defines a task with input and output fields:

```python
class MySignature(dspy.Signature):
    """Task description - appears in prompt"""
    input_field: str = dspy.InputField(desc="what the model should receive")
    output_field: str = dspy.OutputField(desc="what the model should produce")
```

## Field Design Guidelines

### InputField

- **desc**: Concise description of the input
- **Avoid**: Overly detailed extraction rules - minimal desc works better
- **Pattern**: Use field name + key context

```python
# Good for extraction tasks (minimal desc)
description_from_user: str = dspy.InputField(desc="user symptom description")

# Good for generation tasks (more context)
response: str = dspy.OutputField(
    desc="personalized medical advice in Chinese, 200 characters or less"
)
```

### OutputField

- **desc**: Define format and constraints clearly
- **Use**: Enums for limited options, JSON for structured output
- **Include**: Quality requirements (length, language, format)

```python
# Limited options
clinic_selection: str = dspy.OutputField(
    desc='must be one of: "emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic"'
)

# Structured JSON output
requirements: str = dspy.OutputField(
    desc="requirements as JSON with when and what keys"
)
```

## Signature Optimization Notes

Based on experiments in this project:

### Information Extraction Tasks

**Rule**: Minimal desc works better for extraction
- Field names are sufficient for the model to understand what to extract
- Detailed extraction rules can反而 hurt performance

```python
# Optimization found in condition_collector.py and requirement_collector.py
class ConditionCollectorSignature(dspy.Signature):
    """Collect user physical condition info (information extraction task).

    Optimization notes (2026-04-19):
    - Based on Signature optimization experiments, minimal desc works better
    - Information extraction tasks don't need detailed extraction rules
    - Field names are sufficient for the model to understand what to extract
    """
    description_from_user: str = dspy.InputField(desc="user symptom description")
    duration: str = dspy.OutputField(desc="symptom duration")  # Minimal
    severity: str = dspy.OutputField(desc="severity level")    # Minimal
```

### Generation Tasks

**Rule**: Timing keywords are essential for generation tasks
- Include words like: 现在 (now), 给医生看病前 (before doctor visit), 拿完药之后 (after getting medicine), 最后 (finally)

```python
# From route_patcher.py
class RoutePatcherSignature(dspy.Signature):
    """Generate route modification patches for hospital navigation (generation task).

    Optimization notes (2026-04-19):
    - Generation task: timing keywords are essential (现在, 给医生看病前, 拿完药之后, 最后)
    - Output format (type/previous/this/next) must be clear but can be concise
    - Minimal desc compression while preserving generation quality
    """
```

## Best Practices

1. **Keep descriptions concise**: More is not always better
2. **Use field names meaningfully**: They carry semantic weight
3. **Include format requirements**: JSON, enum values, length limits
4. **Add decision rules in desc**: When priority matters (e.g., pediatric > emergency > surgery > internal)
5. **Document optimization findings**: Note what works in comments

## Example: Complete Signature

```python
class ClinicSelectorSignature(dspy.Signature):
    """根据患者症状选择合适的诊室"""

    body_parts: str = dspy.InputField(desc="the body parts affected")
    duration: str = dspy.InputField(desc="how long symptoms experienced")
    severity: str = dspy.InputField(
        desc="severity level (轻微/中等/严重 or 轻/中/重)"
    )
    description: str = dspy.InputField(desc="detailed symptom description")
    other_relevant_info: list[str] = dspy.InputField(
        desc="other relevant info (medical history, age, etc.)"
    )

    clinic_selection: str = dspy.OutputField(
        desc='''must be one of: "emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic".
        Decision priority: 1. Pediatric (child under 14) > 2. Emergency (severe) > 3. Surgery (needs operation) > 4. Internal (default)'''
    )
```
