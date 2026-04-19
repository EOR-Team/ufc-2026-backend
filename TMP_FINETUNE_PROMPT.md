# Prompt Finetune 经验总结

## 实验概述

**项目**: `src/medical_care.py` - 医疗护理建议智能体
**模型**: LlamaCppLM (LFM2.5-1.2B-Instruct-Q4_K_M)
**目标**: 找到保持效果的最简 instructions

---

## 实验步骤与结果

| Step | 修改 | Llama 测试结果 | 结论 |
|------|------|---------------|------|
| 0 | 基准（完整 ~1200 字） | ✅ 2 passed | 起点 |
| 1 | 删除 Examples | ✅ 2 passed | Examples 不必需 |
| 2 | 简化 Scenario Types 详细 bullet points | ✅ 2 passed | 详细描述冗余 |
| 3 | 简化 Safety Rules 详细描述 | ✅ 2 passed | 关键词列表足够 |
| 4 | 简化 Response Format 5 条规范 | ✅ 2 passed | 一句话足够 |
| 5 | 删除 Examples 完全体 | ✅ 2 passed | 无影响 |
| 6 | 简化标题（Scenario Types → Scenario Classification） | ✅ 2 passed | 标题格式无关 |
| 7 | **极限压缩到 ~125 字** | ✅ **11 passed, 1 skipped** | **临界点** |

---

## 关键发现

### 1. 模型自身能力是关键
- Llama 1.2B 对简单场景分类任务（4选1）有较强能力
- 模型能自行推断场景分类，无需详细示例

### 2. 冗余信息可安全删除
以下内容在测试中**无显著影响**：
- Few-shot Examples（4个完整示例）
- 详细的场景描述 bullet points
- 详细的安全规则解释
- Response Format 的5条规范

### 3. 必要信息极简版
最终有效 instructions 仅需：
```
Medical Care Advisor in a Chinese hospital.
Output JSON with: scenario (medication_consultation/recovery_advice/symptom_interpretation/general_advice),
requires_doctor (bool), response (Chinese, 200 chars).
```
约 **125 字符**（原始 ~300 字符）

---

## 经验法则

### 何时可精简 Prompt
1. **输出格式简单**（4选1、是否判断等）
2. **场景明确且有限**（分类任务）
3. **模型本身能力足够**（已验证）

### 何时需保留详细 Prompt
1. **复杂推理任务**（多步骤、链式判断）
2. **安全关键场景**（医疗、法律、金融）
3. **边界情况多**（需示例覆盖）
4. **模型能力不足**（小模型、易混淆任务）

### 精简策略
```
1. 先用完整 prompt 建立基准
2. 逐步删除（Examples → 详细描述 → 标题）
3. 每步验证测试通过率
4. 找到临界点后停止
5. 保留必要的安全/格式关键信息
```

---

## 适用模板

### 分类任务（如 medical_care）
```
Role definition + Output format specification
```

### 复杂推理任务（如 route_patcher）
```
Role + Scenarios + Rules + Constraints + Examples
```
route_patcher 需保留更多结构，因其：
- 输出是结构化 patches
- 需理解插入/删除语义
- 多步推理链

---

## 注意事项

1. **安全关键场景**：即使模型表现好，也建议保留安全检查关键词列表
2. **DeepSeek vs Llama**：大模型可能更容忍精简 prompt，小模型需更多引导
3. **测试覆盖**：精简后需确保边界情况测试通过

---

## 后续验证建议

对每个 node 做 prompt tuning 实验：
- [x] medical_care ✅ (Llama: 125 chars 足够)
- [x] clinic_selector ✅ (Llama: 174 chars 足够)
- [ ] condition_collector
- [ ] requirement_collector
- [ ] route_patcher
