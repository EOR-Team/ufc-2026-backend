# ChainOfThought Usage

This guide explains when and how to use ChainOfThought wrapping in DSPy.

## What is ChainOfThought

ChainOfThought (CoT) wraps a Signature to produce interpretable reasoning. Instead of directly outputting results, the model first generates reasoning steps.

## When to Use CoT

### Use CoT for:

1. **Complex decisions**: When the model needs to reason through options
2. **Multi-step tasks**: When intermediate steps matter
3. **Interpretability needed**: When you want to understand how conclusions were reached
4. **Extraction tasks**: Information extraction benefits from reasoning about context

### Consider alternatives for:

1. **Simple transformations**: Direct mapping might be more efficient
2. **High-volume operations**: CoT adds latency and token overhead
3. **Very short outputs**: When reasoning cost exceeds response cost

## How to Use CoT

### Basic Pattern

```python
import dspy

class MySignature(dspy.Signature):
    input_field: str = dspy.InputField(desc="input")
    output_field: str = dspy.OutputField(desc="output")

# Create the collector
collector = dspy.ChainOfThought(MySignature)

# Use it
result = collector(instructions="Task instructions", input_field=value)

# Access results
print(result.output_field)      # The output
# Reasoning is available in the reasoning attribute if needed
```

### With Custom Instructions

```python
result = collector(
    instructions="Specific instructions for this call",
    input_field=value
)
```

## CoT in This Project

### Medical Care Agent

```python
# From src/medical_care.py
class MedicalCareSignature(dspy.Signature):
    symptoms: str = dspy.InputField(desc="patient's symptoms description")
    diagnosis: str = dspy.InputField(desc="doctor's diagnosis result")
    scenario: str = dspy.OutputField(desc="one of: medication_consultation, recovery_advice...")
    requires_doctor_consultation: bool = dspy.OutputField(...)
    response: str = dspy.OutputField(...)

collector = dspy.ChainOfThought(MedicalCareSignature)

def get_medical_care_advice(symptoms: str, diagnosis: str) -> tuple[dict, object]:
    result = collector(
        instructions="""Medical Care Advisor in a Chinese hospital. Output JSON...""",
        symptoms=symptoms,
        diagnosis=diagnosis
    )
    advice_dict = {
        "scenario": result.scenario,
        "requires_doctor_consultation": result.requires_doctor_consultation,
        "response": result.response
    }
    return advice_dict, result
```

### Route Patcher

```python
# From src/triager/route_patcher.py
class RoutePatcherCot(dspy.ChainOfThought):
    """路线修改器的 CoT 模块"""
    pass

cot = RoutePatcherCot(RoutePatcherSignature)
result = cot(instructions=..., destination_clinic_id=..., ...)
patches = result.patches
```

## Return Type Pattern

All agent functions in this project return `(result, reasoning)`:

```python
def my_agent(input_field: str) -> tuple[ResultType, object]:
    result = collector(instructions="...", input_field=input_field)
    return result.output_field, result  # (output, reasoning)
```

The tuple allows:
- `result[0]`: The actual output for use in code
- `result[1]`: The full reasoning object for debugging/inspection

## Customizing CoT Behavior

### Extended Instructions

```python
result = collector(
    instructions="""Extended instructions with:
    - Context about the task
    - Format requirements
    - Priority rules
    - Examples if helpful""",
    input_field=value
)
```

### Multiple Input Fields

```python
result = collector(
    field1=value1,
    field2=value2,
    field3=value3
)
# Access all outputs via result attributes
```

## Best Practices

1. **Write clear instructions**: Include format, priority, and constraints
2. **Use consistent return patterns**: Always return `(output, reasoning)`
3. **Document optimization findings**: Note what instruction patterns work
4. **Test reasoning quality**: Not just output accuracy, but reasoning soundness
