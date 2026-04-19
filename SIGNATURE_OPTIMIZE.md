# Signature 优化工作流

## 目标

在 **相近的 input token 量** 下，通过优化 Signature 设计（字段类型、desc 描述、instructions），提升 clinic_selector 的输出质量。

---

## 核心假设

1. **减少 input 负担** - 尝试精简输入 token 量，同时提高输出质量
2. **output 质量提升** - 决策准确率更高、输出更稳定
3. **可量化评估** - 通过测试用例验证

---

## 优化维度

### 1. 字段类型（Type Annotation）

**现状问题**：
```python
clinic_selection: str = dspy.OutputField(...)  # 无约束
```

**优化方向**：
```python
from typing import Literal

clinic_selection: Literal[
    "emergency_clinic",
    "surgery_clinic",
    "internal_clinic",
    "pediatric_clinic"
] = dspy.OutputField(...)
```

**预期收益**：
- 类型信息参与 prompt 编译，让模型更清楚可枚举值
- 减少"写错 clinic 名"类错误

---

### 2. 字段描述（desc）

**现状问题**：
```python
desc = '''the selected clinic ID. Must be one of: "emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic". Decision priority: 1. Pediatric (if patient is child under 14) > 2. Emergency (if severe symptoms) > 3. Surgery (if surgical intervention needed) > 4. Internal (default for mild/unclear symptoms)'''
```

过于冗长，把"如何判断"写进了 desc。

**优化方向**：
```python
# 方案 A：只描述字段语义
clinic_selection: Literal[...] = dspy.OutputField(
    desc="the selected clinic ID"
)

# 方案 B：分离格式与规则
clinic_selection: Literal[...] = dspy.OutputField(
    desc="clinic to visit",
    prefix="clinic:"
)
```

**原则**：desc 只说"是什么"，不说"怎么做判断"。

---

### 3. 签名级别指令（instructions）

**优化方向**：
```python
dspy.Signature(
    "body_parts, duration, severity, description, other_info -> clinic_selection",
    instructions="""Select the appropriate clinic based on patient symptoms.

Priority order:
1. pediatric_clinic: patient is child under 14 years old
2. emergency_clinic: severe or life-threatening symptoms
3. surgery_clinic: requires surgical intervention
4. internal_clinic: default for unclear or mild symptoms"""
)
```

**关键**：instructions 是签名级别的，可以承载"决策规则"，但仍然要精简。

---

### 4. 模块选择（ChainOfThought vs Predict）

**现状**：使用 `dspy.ChainOfThought`

**优化方向**：
- 保留 ChainOfThought，让模型先推理再输出
- 或尝试 `dspy.Predict` 对比基线

---

## 实验设计

### 实验组

| 组别 | 变化 | input tokens | 预期 |
|------|------|-------------|------|
| A (baseline) | 当前 Signature | ~150 | 基线 |
| B | Literal 类型 + 精简 desc | ~150 | +输出稳定性 |
| C | Literal + instructions 分离 | ~180 | +决策准确率 |
| D | C + 优化过的 CoT | ~200 | 最佳 |

### 评估指标

1. **通过率** - 测试用例通过数
2. **准确率** - 决策正确性（人工抽样）
3. **一致性** - 相同输入多次调用输出一致
4. **input tokens** - 监控不大幅增长

### 测试用例设计

覆盖 4 个诊室的边界情况：

```python
# pediatric_clinic
{"body_parts": "腹部", "duration": "3天", "severity": "轻微", "description": "腹痛", "other_info": ["8岁儿童"]} -> pediatric_clinic

# emergency_clinic
{"body_parts": "胸部", "duration": "30分钟", "severity": "剧烈", "description": "胸痛伴呼吸困难", "other_info": []} -> emergency_clinic

# surgery_clinic
{"body_parts": "手部", "duration": "2小时", "severity": "中等", "description": "手指断裂", "other_info": ["工伤"]} -> surgery_clinic

# internal_clinic (default)
{"body_parts": "头部", "duration": "1周", "severity": "轻微", "description": "偶发头痛", "other_info": []} -> internal_clinic
```

---

## 工作流

```
1. [ ] 准备测试用例（覆盖 4 个诊室 + 边界）
2. [ ] 建立 baseline（A 组）- 当前 Signature 测试通过率
3. [ ] 实现 B 组 - Literal + 精简 desc
4. [ ] 对比 B vs A：通过率、稳定性
5. [ ] 实现 C 组 - 分离 instructions
6. [ ] 对比 C vs B：决策质量
7. [ ] 实现 D 组 - 优化 CoT
8. [ ] 最终对比：所有指标
9. [ ] 选择最佳方案，整理结论
```

---

## 注意事项

1. **控制变量**：每次只改一个维度
2. **记录 token 量**：用 `dspy.settings.configure(track_usage=True)` 监控
3. **随机性**：多次运行取平均（ChainOfThought 有随机性）
4. **边界用例**：特别关注容易混淆的 cases

---

## 实验结果

### 实验汇总（LlamaCppLM LFM2.5-1.2B-Instruct-Q4_K_M）

| 组别 | 变化 | 通过率 | 备注 |
|------|------|--------|------|
| **Baseline** | 当前 Signature (`str` + 长 desc) | **6/6** | 当前最优 |
| B | Literal + 精简 desc | 4/6 | 精简 desc 导致决策线索不足 |
| C | Literal + 详细 instructions | 4/6 | 过多细节干扰 |
| D | Literal + 极简 instructions | 3/6 | 模型过度倾向 emergency |
| E | Literal + 详细 rules in instructions | 3/6 | 同上 |
| F | Literal + 简单 desc | 2/6 | 最差组合 |
| **G** | Literal + **完整 desc** | **5/6** | 次优，接近 baseline |
| H | Literal + 简单 desc (无决策规则) | 3/6 | 证明 desc 中决策规则必要 |
| I | Literal + 完整 desc + 强化 instructions | 3/6 | 过多 instructions 干扰 |

### 关键发现

1. **Literal 类型本身不影响效果** - F(2/6) vs G(5/6) 说明差异在 desc
2. **desc 中的决策规则是关键** - H 组证明精简 desc 会导致效果下降
3. **instructions 过多反而干扰** - I 组 3/6 说明细节要适量
4. **G 组是 Literal 方案中最优的** - 5/6 接近 baseline

### 推荐方案：G 组

```python
from typing import Literal
import dspy

class ClinicSelectorSignatureG(dspy.Signature):
    """诊室选择 - G组优化方案"""

    body_parts: str = dspy.InputField(desc="body parts affected")
    duration: str = dspy.InputField(desc="symptom duration")
    severity: str = dspy.InputField(desc="severity level")
    description: str = dspy.InputField(desc="symptom description")
    other_relevant_info: list[str] = dspy.InputField(desc="other relevant info")

    clinic_selection: Literal[
        "emergency_clinic",
        "surgery_clinic",
        "internal_clinic",
        "pediatric_clinic"
    ] = dspy.OutputField(
        desc='''selected clinic ID. Must be one of: "emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic". Decision priority: 1. Pediatric (if patient is child under 14) > 2. Emergency (if severe symptoms) > 3. Surgery (if surgical intervention needed) > 4. Internal (default for mild/unclear symptoms)'''
    )
```

### 经验总结

| 优化方向 | 效果 | 原因 |
|---------|------|------|
| Literal 类型 | **中性** | 需配合完整 desc 才能达到 5/6 |
| 精简 desc | **负面** | 决策规则是模型判断的必要线索 |
| 详细 instructions | **中性/负面** | 过多细节可能干扰模型 |
| 完整 desc (含规则) | **正面** | G 组证明有效 |

---

## 结论

1. **任务类型决定 desc 优化策略** - 分类任务需要详细 desc，信息提取需要极简 desc
2. **Literal 类型本身不是关键**，关键在于 desc 内容
3. **决策规则必须存在于某个地方**（desc 或 instructions）
4. **减少 input tokens 可显著加速推理**

### 已验证

| Node | 任务类型 | 优化策略 | 结果 |
|------|---------|---------|------|
| clinic_selector | 分类 | Literal + 完整 desc | 5/6，接近 baseline 6/6 |
| condition_collector | 信息提取 | 极简 desc | **成功**：3x 加速，10/10 通过 |
| requirement_collector | 信息提取 | 极简 desc | **成功**：79% desc 压缩，19/19 通过 |

### 待验证

- [ ] route_patcher 优化验证
- [ ] 在 DeepSeek 等更大模型上测试 clinic_selector G 组
