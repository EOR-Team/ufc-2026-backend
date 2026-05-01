# 007: 常见错误处理

**日期**: 2026-04-24
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

项目中遇到的常见错误需要标准化处理方式，以加速问题诊断和修复。

## 考虑的方案

| 方案 | 可操作性 | 覆盖面 | 结论 |
|------|----------|--------|------|
| 分散问题记录 | ❌ 难查 | - | 放弃 |
| 集中错误指南 | ✅ | ✅ | **选择** |

## 决策

**选择:** 建立集中的常见错误处理指南

## DSPy 错误

### InvalidSignatureError

原因：Signature 缺少必需字段或格式错误。

```python
# 检查：所有字段有正确注解 + 类型
class MySignature(dspy.Signature):
    input_field: str = dspy.InputField(desc="description")
    output_field: str = dspy.OutputField(desc="description")
```

### FieldNotFoundError

原因：访问了未定义的输出字段。

```python
# 正确访问字段名
result = collector(...)
print(result.output_field)  # 使用在 OutputField 中定义的名称
```

## JSON 解析错误

### JSONDecodeError

原因：DSPy 模型输出可能包含格式问题。

```python
# 回退解析
try:
    data = json.loads(result.requirements)
except json.JSONDecodeError:
    data = json.loads(result.requirements.replace("'", '"'))
```

### 改进方法

```python
collector = dspy.ChainOfThought(Signature)
result = collector(
    instructions="Output valid JSON only, no markdown fences",
    ...
)
```

## 调试工作流

1. **读取完整错误回溯** - 显示确切行号和调用栈
2. **检查错误类型** - 对照本指南快速修复
3. **启用调试日志**：`logger.setLevel(logging.DEBUG)`
4. **运行单测隔离**：`pytest test/test_file.py::test_name -vv -s`

## 后续行动

- [ ] 持续补充新发现的错误模式