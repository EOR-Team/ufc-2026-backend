# Test Debugging Guide

This guide covers debugging test failures in `ufc-2026-backend`.

## Running Tests

### Basic Test Run

```bash
pytest
```

### Run Specific Test File

```bash
pytest test/test_clinic_selector.py
```

### Run Specific Test

```bash
pytest test/test_clinic_selector.py::test_function_name
```

### Run with Output

```bash
pytest -v  # Verbose output
pytest -s  # Show print statements
pytest -vv # More verbose
```

## Coverage

### Generate Coverage Report

```bash
pytest --cov=src --cov-report=term-missing
```

### Minimum Requirement

- **Coverage**: 80% minimum
- Check report for missing lines marked with `>>`

### HTML Coverage Report

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

## Common Test Failures

### 1. AssertionError

```python
# Actual vs expected mismatch
AssertionError: assert result == "internal_clinic"
# Got: "surgery_clinic"
```

**Debugging:**
```python
# Add print statements
result = select_clinic(...)
print(f"DEBUG: got {result[0]}, expected {expected}")
assert result[0] == expected
```

### 2. DSPy Signature Errors

```
dspy.exceptions.InvalidSignatureError
```

**Causes:**
- Missing InputField or OutputField
- Field type annotation missing
- Field not passed to collector

**Fix:**
```python
class MySignature(dspy.Signature):
    input_field: str = dspy.InputField(desc="description")
    output_field: str = dspy.OutputField(desc="description")

result = collector(input_field=value)  # Pass all inputs
```

### 3. Model Not Loaded

```
RuntimeError: Model not loaded
```

**Fix:**
```python
# Ensure model is loaded before tests
from src.llm import load_model
load_model("test", "LFM2.5-1.2B-Instruct-Q4_K_M")
```

### 4. JSON Parsing Errors

```
json.JSONDecodeError
```

**In route_patcher tests:**
```python
# The model returns JSON, but it may have format variations
# Tests handle this with fallback parsing
try:
    data = json.loads(result.requirements)
except json.JSONDecodeError:
    data = json.loads(result.requirements.replace("'", '"'))
```

### 5. Import Errors

```
ModuleNotFoundError: No module named 'src'
```

**Fix:**
```bash
# Run from project root
cd /path/to/ufc-2026-backend
pytest

# Or set PYTHONPATH
export PYTHONPATH=/path/to/ufc-2026-backend:$PYTHONPATH
pytest
```

## Test Structure

### Arrange-Act-Assert (AAA)

```python
def test_select_clinic_returns_internal_for_mild_symptoms():
    """Test that mild symptoms route to internal clinic."""
    # Arrange - set up test data
    symptoms = "轻微头痛"
    duration = "2天"
    severity = "轻微"

    # Act - perform the action
    result = select_clinic(
        body_parts="头部",
        duration=duration,
        severity=severity,
        description=symptoms,
        other_relevant_info=[]
    )

    # Assert - verify results
    clinic_id, reasoning = result
    assert clinic_id == "internal_clinic"
```

### Testing Error Cases

```python
def test_load_model_returns_error_for_missing_file():
    """Test that missing model file returns error Result."""
    result = load_model("nonexistent", "missing_file")

    assert result.success is False
    assert result.error is not None
    assert "not found" in result.error.lower()
```

### Testing with Mocks

```python
from unittest.mock import patch

def test_load_model_uses_cache():
    """Test that already-loaded models return cached instance."""
    # First load
    result1 = load_model("test", "model_file")
    assert result1.success is True

    # Second load should warn about cache
    result2 = load_model("test", "model_file")
    assert result2.success is True
    assert result2.warn is not None  # Should warn about cache
```

## Debugging Tips

### 1. Inspect DSPy Reasoning

```python
result = select_clinic(...)
print(f"Output: {result.clinic_selection}")
print(f"Reasoning: {result.reasoning}")  # ChainOfThought reasoning
```

### 2. Print Intermediate Values

```python
def my_function(input_data):
    logger.debug(f"Input: {input_data}")
    result = process(input_data)
    logger.debug(f"Intermediate: {result}")
    return final_result
```

### 3. Run Single Test with Full Output

```bash
pytest test/test_route_patcher.py::test_apply_patches_empty -vv -s
```

### 4. Check Test Isolation

```bash
# Run tests in random order to catch dependencies
pytest --randomly
```

## Test File Reference

| File | Tests |
|------|-------|
| `test_clinic_selector.py` | Clinic selection logic |
| `test_condition_collector.py` | Symptom extraction |
| `test_requirement_collector.py` | Route requirement extraction |
| `test_route_patcher.py` | Route patching logic |
| `test_medical_care.py` | Medical advice generation |
| `test_speed.py` | Performance tests |

## CI/CD Notes

In CI environments:
- Model files should be mocked or cached
- Run `pytest --cov=src` to enforce 80% coverage
- Check `cobertura-coverage.xml` for coverage trends
