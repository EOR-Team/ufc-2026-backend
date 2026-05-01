# Agent Composition

This guide covers how to compose multiple DSPy agents into workflows.

## Agent Overview

This project contains four main triage agents:

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| `ClinicSelector` | Route to appropriate clinic | Symptoms, duration, severity | Clinic ID |
| `ConditionCollector` | Extract symptom details | User description | Duration, severity, body parts, description, other info |
| `RequirementCollector` | Extract route requirements | User requirement text | List of {when, what} |
| `RoutePatcher` | Modify hospital route | Destination, requirements, current route | Modified route + patches |

## Data Flow

```
User Input
    │
    ▼
ConditionCollector ──────► ClinicSelector ──────► RoutePatcher
    │                         │                      │
    │                         │                      │
    └─────────────────────────┴──────────────────────┘
                    │
                    ▼
            RequirementCollector
                    │
                    ▼
              (back to RoutePatcher)
```

## Composition Patterns

### Sequential Composition

```python
def triage_pipeline(user_description: str, user_requirement: str):
    # Step 1: Collect condition
    condition, _ = collect_condition(user_description)

    # Step 2: Select clinic
    clinic_id, _ = select_clinic(
        body_parts=condition.body_parts,
        duration=condition.duration,
        severity=condition.severity,
        description=condition.description,
        other_relevant_info=condition.other_relevant_info
    )

    # Step 3: Collect requirements
    requirements, _ = collect_requirement(user_requirement)

    # Step 4: Patch route
    final_route, patches = patch_route(
        destination_clinic_id=clinic_id,
        requirement_summary=requirements
    )

    return {
        "clinic": clinic_id,
        "route": final_route,
        "patches": patches
    }
```

### Parallel Collection

```python
async def parallel_triage(user_description: str, user_requirement: str):
    # Run condition and requirement collection in parallel
    condition_task = asyncio.to_thread(collect_condition, user_description)
    requirement_task = asyncio.to_thread(collect_requirement, user_requirement)

    condition, requirement = await asyncio.gather(condition_task, requirement_task)

    # Continue with clinic selection...
    clinic_id, _ = select_clinic(...)
    return clinic_id, condition, requirement
```

## Return Type Consistency

All agents return `(result, reasoning)`:

```python
# Condition collector
duration, severity, body_parts, description, other_relevant_info = result
# Or access via attributes
result.duration
result.severity

# Clinic selector
clinic_selection, reasoning = result
# clinic_selection is a string like "internal_clinic"

# Route patcher
final_route, patches = result
# final_route is a list of location IDs
# patches is a list of {type, previous, this, next} dicts
```

## Error Handling in Compositions

```python
def safe_triage_pipeline(user_description: str, user_requirement: str):
    try:
        # Collect condition
        condition, reasoning = collect_condition(user_description)
        if not condition:
            return Result(success=False, error="Failed to collect condition")

        # Select clinic
        clinic_id, _ = select_clinic(...)
        if clinic_id not in AVAILABLE_CLINICS:
            return Result(success=False, error=f"Invalid clinic: {clinic_id}")

        # Continue...
        return Result(success=True, value={...})

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return Result(success=False, error=str(e))
```

## Medical Care Agent

The `MedicalCareAgent` works differently - it's called after a diagnosis is made:

```python
def get_medical_care_advice(symptoms: str, diagnosis: str) -> tuple[dict, object]:
    """
    Called AFTER doctor provides diagnosis.
    Generates personalized care advice.
    """
    result = collector(
        instructions="""Medical Care Advisor in a Chinese hospital...""",
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

## Best Practices

1. **Always handle None/empty returns**: Agents may fail to extract
2. **Log intermediate results**: For debugging multi-agent flows
3. **Validate outputs**: Check clinic_id is in AVAILABLE_LOCATIONS
4. **Return reasoning for inspection**: Second tuple element
5. **Keep compositions simple**: Prefer clear sequential flow over clever parallelism
