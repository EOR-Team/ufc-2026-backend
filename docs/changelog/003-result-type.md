# 003: Result Type 模式

**日期**: 2026-04-24
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

项目需要统一错误处理方式，避免使用异常或布尔元组导致的隐式错误传播问题。

## 考虑的方案

| 方案 | 显式错误 | 可携带警告 | 一致性 | 结论 |
|------|----------|------------|--------|------|
| Result 类型 | ✅ | ✅ | ✅ | **选择** |
| 异常抛出 | ✅ | ❌ | ❌ | 放弃 |
| 布尔元组 | ❌ | ❌ | ❌ | 放弃 |

## 决策

**选择:** 使用 Result 类型进行错误传播

## 理由

1. **显式错误处理**：必须检查 `success` 字段，无法忽略
2. **可携带警告**：`warn` 字段用于非致命问题，不影响主流程
3. **一致的信封格式**：API 响应、模型加载、文件操作统一格式

## 定义

```python
class Result(BaseModel):
    success: bool
    value: Any = None
    warn: str | None = None
    error: str | None = None
```

## 使用场景

| 场景 | 返回方式 |
|------|----------|
| 基础设施代码（模型加载、文件 I/O） | `Result` |
| DSPy Agent 输出 | `(output, reasoning)` 元组 |

## 最佳实践

1. 包含上下文：`error=f"Failed to load model '{model_id}': {e}"`
2. 使用 `exc_info=True` 记录意外异常
3. 警告使用 `logger.warning()`
4. DSPy 输出包装在 Result 中是**反模式**

## 后续行动

- [ ] 在新模块中强制使用 Result 类型