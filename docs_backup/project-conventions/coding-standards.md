# Coding Standards

This document outlines coding standards for the `ufc-2026-backend` project.

## Python Standards

### PEP 8 Compliance

Follow PEP 8 guidelines with these project-specific rules:

- **Line length**: Max 120 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Blank lines**: Two blank lines between top-level definitions

### Type Annotations

**All function signatures MUST have type annotations:**

```python
# Good
def get_medical_care_advice(symptoms: str, diagnosis: str) -> tuple[dict, object]:
    ...

# Bad - no types
def get_medical_care_advice(symptoms, diagnosis):
    ...
```

### Imports

```python
# Standard library
import json
from pathlib import Path

# Third party
import dspy
from pydantic import BaseModel

# Local
from src.utils import Result
from src import logger
```

## File Organization

### Directory Structure

Organize by **feature/domain**, not by type:

```
# Good
src/
├── medical_care.py      # Medical advice agent
├── triager/
│   ├── clinic_selector.py
│   ├── condition_collector.py
│   └── route_patcher.py

# Bad - organizing by type
src/
├── agents/
│   ├── medical_care.py
│   ├── clinic_selector.py
│   └── ...
├── utils/
│   └── ...
```

### File Naming

- **Python files**: lowercase with underscores (`clinic_selector.py`)
- **Test files**: `test_<module_name>.py`
- **Config files**: lowercase with underscores

## Function Design

### Small Functions

Functions should be small (<50 lines). If a function exceeds this, consider splitting it.

### Single Responsibility

Each function should do one thing well.

### Docstring Format

```python
# function_name
# Description of what the function does
#
# @author name
# @date YYYY-MM-DD
#
# Additional details if needed

def my_function(param1: str, param2: int) -> Result:
    """
    Brief description.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Result object with success/error status
    """
    pass
```

## Code Comments

### Inline Comments

Use **Chinese** comments with `# ` format:

```python
# 这是中文注释
result = load_model(model_id, filename)  # 加载模型

# Bad - English comment
# This is a comment
result = load_model(model_id, filename)
```

### Comment Style

```python
# Section header
# ========================================
# 模型管理
# ========================================

# Inline note
value = something()  # 注释说明

# Important warning
# 注意: 不要在此处修改
```

## Error Handling

### Result Type Pattern

Use the `Result` type from `src/utils.py`:

```python
from src.utils import Result

def load_model(model_id: str) -> Result:
    if model_id in _models:
        return Result(success=True, warn=f"Model '{model_id}' already loaded")
    # ... load model ...
    return Result(success=True)

def risky_operation() -> Result:
    try:
        result = do_something()
        return Result(success=True, value=result)
    except ValueError as e:
        return Result(success=False, error=str(e))
```

### Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether operation succeeded |
| `value` | `Any` | Result value on success |
| `warn` | `str \| None` | Warning message (non-fatal) |
| `error` | `str \| None` | Error message on failure |

## Logging

Use the `src/logger.py` module:

```python
from src import logger

logger.info("操作成功")
logger.warning("警告信息")
logger.error(f"错误: {e}", exc_info=True)  # exc_info for stack traces
logger.debug("调试信息")
```

**Never use `print()`** - always use logger.

## Testing

### Test Structure

```python
def test_function_name_scenario():
    """
    Descriptive name explaining the scenario under test.
    """
    # Arrange - set up test data
    input_data = "test input"

    # Act - perform the action
    result = my_function(input_data)

    # Assert - verify results
    assert result.success is True
    assert result.value == expected
```

### Test Naming

Use descriptive names that explain the expected behavior:

```python
# Good
def test_returns_empty_array_when_no_markets_match_query():
    ...

def test_throws_error_when_api_key_is_missing():
    ...

# Bad
def test_basic():
    ...

def test_case1():
    ...
```

### Coverage Requirement

- **Minimum coverage**: 80%
- Run with: `pytest --cov=src --cov-report=term-missing`
