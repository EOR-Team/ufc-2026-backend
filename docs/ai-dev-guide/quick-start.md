# Quick Start for AI-Assisted Development

This guide helps AI coding assistants understand how to work with this project effectively.

## Before Writing Code

1. **Read the project structure** in `docs/ai-dev-guide/project-structure.md`
2. **Check existing patterns** in `src/triager/` for similar functionality
3. **Review DSPy patterns** in `docs/dspy-patterns/`
4. **Check conventions** in `docs/project-conventions/`

## Common Development Patterns

### Creating a New DSPy Agent

```python
# 1. Create signature in src/triager/my_agent.py
import dspy

class MyAgentSignature(dspy.Signature):
    """Task description in English for DSPy"""
    input_field: str = dspy.InputField(desc="input description")
    output_field: str = dspy.OutputField(desc="output description")

collector = dspy.ChainOfThought(MyAgentSignature)

def my_agent(input_field: str) -> tuple[str, object]:
    result = collector(
        instructions="Task-specific instructions for the model",
        input_field=input_field
    )
    return result.output_field, result

# 2. Add tests in test/test_my_agent.py
# 3. Follow naming: select_clinic, collect_condition, patch_route
```

### Adding a New LLM Integration

```python
# In src/llm/my_llm.py
# Follow pattern from src/llm/deepseek.py
# Implement standard chat completion interface
# Update requirements.txt if new dependencies needed
```

### Model Loading Pattern

```python
# Load model for inference
from src.llm import llama
result = llama.load_model("my_model", "model_filename")
if not result.success:
    logger.error(f"Failed: {result.error}")
```

## Testing Requirements

- **Minimum coverage**: 80%
- **Test structure**: `test/test_<module_name>.py`
- **Naming**: Descriptive names explaining behavior under test

```python
def test_returns_empty_array_when_no_markets_match_query():
    """Good: describes expected behavior"""
    ...

def test_calc():
    """Bad: too vague"""
    ...
```

## File Organization

- **New feature**: Create module in appropriate `src/<domain>/` directory
- **New test**: Add to `test/` following `test_<module>.py` naming
- **Config changes**: Update relevant `*.json` files in `model/`

## Important Conventions

1. **Comments in Chinese** using `# ` format
2. **Docstring header format**:
   ```python
   # function_name
   # Description
   #
   # @author name
   # @date YYYY-MM-DD
   ```
3. **Return Result type** for functions that can fail:
   ```python
   return Result(success=False, error="message")
   ```
4. **Use logging**: `from src import logger`

## Troubleshooting

See `docs/troubleshooting/` for common issues:
- Model loading failures
- Test debugging
- DSPy errors
