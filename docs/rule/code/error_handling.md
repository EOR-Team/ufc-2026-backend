# ERROR-HANDLING 错误处理规范

**日期**: 2026-05-02
**状态**: 草稿
**适用**: Vibe Coding 模式下的 AI 自动开发

---

## 核心原则

> **铁律**: 使用 Result Type 进行错误传播，禁止异常用于业务逻辑
>
> "异常用于程序错误，Result 用于业务失败。"

### 强制规则

**AI 在以下场景必须询问人类，不得自行决定**：
- 需要抛出异常时（区分程序错误 vs 业务失败）
- 需要自定义错误类型时
- 遇到需要向上传播的错误时

### 违反规则的代价

| 违反行为 | 处理方式 |
|----------|----------|
| 用异常处理业务失败 | 重构为 Result 返回 |
| 用布尔值代替 Result | 重构为 Result 类型 |
| 吞掉异常不处理 | 立即修复，添加处理逻辑 |
| 不检查 Result.success | 拒绝合并 |

---

## Result Type 定义

### 定义位置

`src/utils.py` 中的 `Result` 类型：

```python
from pydantic import BaseModel, Field
from typing import Any

class Result(BaseModel):
    """统一的结果对象"""

    success: bool = Field(...)           # 是否成功
    warn: str | None = Field(default=None)   # 警告信息
    error: str | None = Field(default=None)   # 错误信息
    value: Any = Field(default=None)           # 返回值
```

### 字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | `bool` | **必填**。操作是否成功 |
| `value` | `Any` | 成功时的返回值（可选） |
| `warn` | `str \| None` | 非致命警告信息 |
| `error` | `str \| None` | 失败时的错误信息 |

---

## 使用模式

### 成功返回值

```python
def get_model(model_id: str) -> Result:
    if model_id not in _models:
        return Result(success=False, error=f"Model '{model_id}' not found")

    model = _models[model_id]
    return Result(success=True, value=model)
```

### 成功带警告

```python
def load_model(model_id: str, filename: str) -> Result:
    if model_id in _models:
        return Result(success=True, warn=f"Model '{model_id}' already loaded")

    # ... load model ...
    return Result(success=True)
```

### 失败带错误

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

---

## 检查 Result

### 基本检查

```python
result = load_model("my_model", "model.gguf")

if result.success:
    model = result.value
    do_something(model)
else:
    print(f"Failed: {result.error}")
```

### 带警告检查

```python
result = load_model("my_model", "model.gguf")

if result.success:
    if result.warn:
        logger.warning(f"Warning: {result.warn}")
    # Use model...
else:
    logger.error(f"Failed: {result.error}")
```

---

## 反面模式（禁止）

### 不要用异常处理业务失败

```python
# Bad - 业务失败不应抛异常
if not found:
    raise ValueError("Not found")

# Good - 使用 Result
return Result(success=False, error="Not found")
```

### 不要用布尔值代替 Result

```python
# Bad - 语义不清晰
def load_model() -> tuple[bool, Any]:
    if success:
        return True, model
    else:
        return False, None

# Good - Result 提供清晰语义
return Result(success=True, value=model)
# or
return Result(success=False, error="Failed to load model")
```

### 不要为 DSPy 输出使用 Result

```python
# Bad - DSPy 输出不是 Result 类型
result = collector(...)
return Result(success=True, value=result)  # 错误!

# Good - DSPy 返回 (output, reasoning)
return result.clinic_selection, result
```

---

## 最佳实践

### 使用场景

1. **基础设施代码**：模型加载、文件操作、API 调用
2. **外部依赖调用**：数据库、第三方服务
3. **复杂业务逻辑**：需要多步骤处理的函数

### 不要使用场景

1. **DSPy Agent 输出**：返回 `(output, reasoning)` 元组
2. **简单布尔判断**：可直接返回 `True`/`False`
3. **程序错误**：使用异常（文件不存在、类型错误）

### 错误消息规范

```python
# Good - 包含上下文
return Result(success=False, error=f"Model '{model_id}' not found in registry")

# Good - 说明原因和解决方案
return Result(success=False, error="Database connection failed: check DATABASE_URL env var")

# Bad - 模糊消息
return Result(success=False, error="Error")
```

---

## 验证清单

完成实现前，确保每项都已检查：

- [ ] 使用 Result Type 而非异常处理业务失败
- [ ] 错误消息包含上下文
- [ ] 成功时返回值使用 `value` 字段
- [ ] 非致命警告使用 `warn` 字段
- [ ] 使用 `exc_info=True` 记录意外异常
- [ ] DSPy Agent 返回 `(output, reasoning)` 而非 Result
- [ ] 调用方检查 `result.success`
