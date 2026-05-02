---
name: "005: DSPy Signature 设计原则"
category: adr
field: code
description: 确定 DSPy Signature 命名与设计规范
date: 2026-04-19
---

# 005: DSPy Signature 设计原则

**日期**: 2026-04-19
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

通过实验发现 DSPy Signature 的描述文字并非越多越好，需要根据任务类型区分优化策略。

## 考虑的方案

| 方案 | 信息提取 | 生成任务 | 结论 |
|------|----------|----------|------|
| 详细 desc | ❌ 反而影响理解 | ✅ | 部分适用 |
| Minimal desc | ✅ 字段名携带语义 | ❌ 缺少关键信息 | 部分适用 |
| 任务区分优化 | ✅ | ✅ | **选择** |

## 决策

**选择:** 根据任务类型调整 desc 详细程度

## 理由

1. **信息提取任务**：Field 名称本身携带足够语义，详细规则可能反而影响模型理解
2. **生成任务**：Timing keywords（现在、给医生看病前、拿完药之后、最后）至关重要
3. **实验验证**：通过 condition_collector 和 route_patcher 实验确认

## 信息提取任务

**规则**: Minimal desc 效果更好

```python
class ConditionCollectorSignature(dspy.Signature):
    """Collect user physical condition info (information extraction task)."""
    description_from_user: str = dspy.InputField(desc="user symptom description")
    duration: str = dspy.OutputField(desc="symptom duration")      # Minimal
    severity: str = dspy.OutputField(desc="severity level")        # Minimal
```

## 生成任务

**规则**: Timing keywords 至关重要

需要包含：
- 现在 (now)
- 给医生看病前 (before doctor visit)
- 拿完药之后 (after getting medicine)
- 最后 (finally)

```python
class RoutePatcherSignature(dspy.Signature):
    """Generate route modification patches for hospital navigation (generation task).

    Optimization notes:
    - Generation task: timing keywords are essential
    - Output format (type/previous/this/next) must be clear but concise
    """
```

## 最佳实践

1. **保持描述简洁**: More is not always better
2. **Field 名称有意义**: 携带语义权重
3. **格式要求明确**: JSON、枚举值、长度限制
4. **优先级规则写入 desc**: 例：`Decision priority: Pediatric > Emergency > Surgery > Internal`
5. **记录优化发现**: 在注释中注明实验结论