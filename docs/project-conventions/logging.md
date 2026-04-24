# Logging Standards

This document covers the logging patterns used in `ufc-2026-backend`.

## Logger Module

The project uses a custom logger in `src/logger.py` that provides colored console output.

## Import and Basic Usage

```python
from src import logger

logger.info("操作完成")
logger.warning("警告信息")
logger.error(f"错误: {e}")
logger.debug("调试信息")
```

## Log Levels

| Level | Use Case | Color |
|-------|----------|-------|
| `DEBUG` | Detailed debugging info | Cyan (dim) |
| `INFO` | Normal operations | Green |
| `WARNING` | Potential issues | Yellow (bold) |
| `ERROR` | Errors that need attention | Red (bold) |
| `CRITICAL` | Serious failures | Red (bold) |

## Log Format

```
[2026-04-24 22:30:15] INFO     src.triager: Loading model...
[2026-04-24 22:30:16] WARNING  src.llm: Model already loaded
[2026-04-24 22:30:17] ERROR    src.llm: Failed to load model: File not found
```

## Usage Examples

### Standard Logging

```python
# Informational
logger.info("Starting model loading")
logger.info(f"Loaded model: {model_id}")

# Warnings (non-fatal issues)
logger.warning(f"Model {model_id} already exists")
logger.warning("Using default configuration")

# Errors (with context)
logger.error(f"Failed to load model: {filename}")
logger.error(f"Unexpected error: {e}", exc_info=True)  # Stack trace
```

### Debug Logging

```python
# Only shows with DEBUG level
logger.debug(f"Input: {input_data}")
logger.debug(f"Intermediate result: {result}")
```

### Function Entry/Exit

```python
def my_function(param: str) -> Result:
    logger.debug(f"my_function called with param={param}")

    result = do_something(param)

    logger.debug(f"my_function returning success={result.success}")
    return result
```

## File Logging (Optional)

For file logging alongside console:

```python
from src.logger import setup_file_logging

# Setup file logging (writes to ./logs/ufc_YYYYMMDD_HHMMSS.log)
setup_file_logging()

# Or specify custom directory
setup_file_logging(log_dir="/var/log/ufc")
```

## Best Practices

### Do

```python
# Use f-strings for formatting
logger.info(f"Loaded model: {model_id}")

# Include relevant context
logger.error(f"Failed to process request: {request_id}")

# Use exc_info for unexpected exceptions
logger.error(f"Unexpected error: {e}", exc_info=True)

# Log at appropriate levels
logger.info("Starting operation X")  # Key milestones
logger.debug("Step 1 of 3")         # Detailed flow
```

### Don't

```python
# Don't use print()
print(f"Result: {result}")  # Wrong - no colors, no file output

# Don't log sensitive data
logger.info(f"API key: {api_key}")  # Wrong - secret exposure

# Don't over-log
logger.info("About to call function")
logger.info("Calling function")  # Redundant
logger.info("Function returned")

# Don't log everything at ERROR
logger.error("User logged in")  # Wrong - use INFO
```

## ColoredFormatter

The `ColoredFormatter` adds ANSI color codes to log output:

```python
# From src/logger.py
LEVEL_COLORS = {
    "DEBUG": CYAN + DIM,
    "INFO": GREEN,
    "WARNING": YELLOW + BOLD,
    "ERROR": RED + BOLD,
    "CRITICAL": RED + BOLD,
}
```

When viewing logs in a terminal, errors appear in red, warnings in yellow, etc.

## Aliases

For convenience:

```python
from src import logger
logger.warn = logger.warning  # Alias (deprecated)
logger.err = logger.error     # Alias
```

## Integration with Result Type

```python
def load_model(model_id: str) -> Result:
    if model_id in _models:
        return Result(success=True, warn=f"Model '{model_id}' already loaded")

    result = do_load(model_id)

    if not result.success:
        logger.error(f"Failed to load model '{model_id}': {result.error}")
        return result

    logger.info(f"Successfully loaded model: {model_id}")
    return Result(success=True, value=result.value)
```
