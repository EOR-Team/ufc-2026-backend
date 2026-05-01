# Result Type Pattern

This document explains the `Result` type pattern used for consistent error handling.

## Overview

The `Result` type (from `src/utils.py`) provides a consistent way to represent success/failure with optional value, warning, or error.

## Definition

```python
# src/utils.py
from pydantic import BaseModel, Field
from typing import Any

class Result(BaseModel):
    """统一的结果对象"""

    success: bool = Field(...)       # 是否成功
    warn: str | None = Field(default=None)  # 警告信息
    error: str | None = Field(default=None) # 错误信息
    value: Any = Field(default=None)         # 返回值
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | **Required**. Whether the operation succeeded |
| `value` | `Any` | The return value on success (optional) |
| `warn` | `str \| None` | Non-fatal warning message |
| `error` | `str \| None` | Error message on failure |

## Usage Patterns

### Success with Value

```python
def get_model(model_id: str) -> Result:
    if model_id not in _models:
        return Result(success=False, error=f"Model '{model_id}' not found")

    model = _models[model_id]
    return Result(success=True, value=model)
```

### Success with Warning

```python
def load_model(model_id: str, filename: str) -> Result:
    if model_id in _models:
        return Result(success=True, warn=f"Model '{model_id}' already loaded")

    # ... load model ...
    return Result(success=True)
```

### Failure with Error

```python
def risky_operation(config: dict) -> Result:
    try:
        result = do_something(config)
        return Result(success=True, value=result)
    except ValueError as e:
        return Result(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return Result(success=False, error="An unexpected error occurred")
```

## Checking Results

```python
result = load_model("my_model", "model.gguf")

if result.success:
    model = result.value
    do_something(model)
else:
    print(f"Failed: {result.error}")
```

### With Warnings

```python
result = load_model("my_model", "model.gguf")

if result.success:
    if result.warn:
        logger.warning(f"Warning: {result.warn}")
    # Use model...
else:
    logger.error(f"Failed: {result.error}")
```

## Result in DSPy Agents

DSPy agents typically return `(result, reasoning)` tuples, not `Result`:

```python
# src/triager/clinic_selector.py
def select_clinic(...) -> tuple[str, object]:
    result = collector(instructions=..., ...)
    return result.clinic_selection, result  # (output, reasoning)
```

The `Result` type is used for infrastructure code (model loading, file I/O).

## Anti-Patterns

### Don't Use Result for DSPy Outputs

```python
# Bad - DSPy outputs are not Result type
result = collector(...)
return Result(success=True, value=result)  # Wrong!

# Good - DSPy agents return (output, reasoning)
return result.clinic_selection, result
```

### Don't Raise Exceptions for Expected Failures

```python
# Bad
if not found:
    raise ValueError("Not found")

# Good - use Result for expected failures
return Result(success=False, error="Not found")
```

### Don't Use Booleans for Complex Results

```python
# Bad
def load_model() -> tuple[bool, Any]:
    if success:
        return True, model
    else:
        return False, None

# Good - Result provides clear semantics
return Result(success=True, value=model)
# or
return Result(success=False, error="Failed to load model")
```

## Best Practices

1. **Use Result for infrastructure code**: Model loading, file operations, API calls
2. **Return tuples for DSPy agents**: `(output, reasoning)`
3. **Always check `success` before accessing `value`**
4. **Include context in error messages**: What failed, why, what to do
5. **Log warnings**: Use `logger.warning()` for non-fatal issues
6. **Use `exc_info=True`**: For exceptions that shouldn't happen
