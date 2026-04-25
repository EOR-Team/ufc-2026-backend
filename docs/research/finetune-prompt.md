# Prompt Finetune 经验总结

## 实验概述

**项目**: ufc-2026-backend triager nodes
**模型**: LlamaCppLM (LFM2.5-1.2B-Instruct-Q4_K_M)
**目标**: 找到每个 node 保持效果的最简 instructions

---

## 全部 Node 实验结果

| Node | 任务类型 | 原始 chars | 最终 chars | 压缩率 | 测试结果 |
|------|---------|-----------|-----------|--------|---------|
| medical_care | 4选1分类 | ~300 | 125 | 58% | 11 passed, 1 skipped |
| clinic_selector | 4选1分类 | ~1100 | 174 | 84% | 16 passed |
| condition_collector | 信息提取(5字段) | ~300 | 80 | 73% | 20 passed |
| requirement_collector | 信息提取(when/what) | ~100 | 67 | 33% | 19 passed |
| route_patcher | 复杂推理(insert/delete) | ~1000 | 255 | 75% | 15 passed, 1 skipped |

---

## 各 Node 详细实验

### 1. medical_care（医疗护理建议）

**任务类型**: 4选1分类（medication_consultation/recovery_advice/symptom_interpretation/general_advice）

| Step | 修改 | 结果 |
|------|------|------|
| 0 | 基准（完整 ~300 chars） | ✅ 2 passed |
| 1 | 删除 Examples | ✅ 2 passed |
| 2 | 简化 Scenario Types 详细 bullet points | ✅ 2 passed |
| 3 | 简化 Safety Rules 详细描述 | ✅ 2 passed |
| 4 | 简化 Response Format 5 条规范 | ✅ 2 passed |
| 5 | 删除 Examples 完全体 | ✅ 2 passed |
| 6 | 简化标题 | ✅ 2 passed |
| 7 | **极限压缩到 ~125 chars** | ✅ **11 passed, 1 skipped** |

**最终 instructions**:
```
Medical Care Advisor in a Chinese hospital.
Output JSON with: scenario (medication_consultation/recovery_advice/symptom_interpretation/general_advice),
requires_doctor (bool), response (Chinese, 200 chars).
```

---

### 2. clinic_selector（诊室选择）

**任务类型**: 4选1分类（pediatric_clinic/emergency_clinic/surgery_clinic/internal_clinic）

| Step | 修改 | 结果 |
|------|------|------|
| 0 | 基准（完整 ~1100 chars） | ✅ 6 passed |
| 1 | 删除 Examples | ✅ 6 passed |
| 2 | 简化 Decision Criteria | ✅ 6 passed |
| 3 | **极限压缩到 1 句话** | ✅ **6 passed** |

**最终 instructions**:
```
Clinic selector in a Chinese hospital. Select: pediatric_clinic (child under 14), emergency_clinic (severe), surgery_clinic (needs operation), internal_clinic (default/mild).
```

---

### 3. condition_collector（身体条件采集）

**任务类型**: 信息提取（duration/severity/body_parts/description/other_relevant_info）

| Step | 修改 | 结果 |
|------|------|------|
| 0 | 基准（完整 ~300 chars） | ✅ 10 passed |
| 1 | 简化到字段列表 | ✅ 10 passed |
| 2 | **极限压缩到 1 句话** | ✅ **10 passed** |

**最终 instructions**:
```
Extract from user text: duration, severity, body_parts, description, other_info.
```

---

### 4. requirement_collector（需求收集）

**任务类型**: 信息提取（when/what 结构化需求）

| Step | 修改 | 结果 |
|------|------|------|
| 0 | 基准（完整 ~100 chars） | ✅ 9 passed |
| 1 | 简化 instructions | ✅ 9 passed |
| 2 | **极限压缩到 1 句话** | ✅ **9 passed** |

**最终 instructions**:
```
Extract requirements (when, what) from user text. Output JSON list.
```

---

### 5. route_patcher（路线修改）

**任务类型**: 复杂推理（insert/delete patch 应用）

| Step | 修改 | 结果 |
|------|------|------|
| 0 | 基准（完整 ~1000 chars） | ✅ 2 passed |
| 1 | 简化 rules，删除 examples | ✅ 2 passed |
| 2 | **极限压缩到 1 句话** | ✅ **2 passed** |

**最终 instructions**:
```
Route patcher in a Chinese hospital. Insert locations based on: "现在"(after entrance), "给医生看病前"(before clinic), "拿完药之后"(after pharmacy), "最后"(before quit). Output JSON: {"patches": [{"type": "insert"|"delete", "previous": loc, "this": loc, "next": loc}]}.
```

---

## 关键发现

### 1. 所有任务类型均可大幅精简
- **分类任务**（medical_care, clinic_selector）：Llama 1.2B 自行推断能力强，详细示例和描述冗余
- **信息提取任务**（condition_collector, requirement_collector）：只需列出字段名即可
- **复杂推理任务**（route_patcher）：规则关键词保留，但详细解释可删除

### 2. 冗余信息可安全删除
以下内容在测试中**无显著影响**：
- Few-shot Examples（多个完整示例）
- 详细的场景描述 bullet points
- 详细的安全规则解释
- Response Format 的多条规范
- 章节标题和结构标记

### 3. 必要信息极简版
最终有效 instructions 仅需：
1. **Role definition**: 角色描述（一句话）
2. **Output format**: 输出格式说明（字段列表或 JSON 结构）
3. **Key rules**（针对复杂任务）: 关键规则关键词

---

## 经验法则

### 何时可精简 Prompt
1. **输出格式简单**（4选1、是否判断、字段列表等）
2. **场景明确且有限**（分类任务、信息提取）
3. **模型本身能力足够**（Llama 1.2B 已验证）

### 何时需保留详细 Prompt
1. **复杂推理任务**（多步骤、链式判断）- route_patcher 仍需保留关键规则
2. **安全关键场景**（医疗、法律、金融）- 建议保留安全检查关键词
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

### 适用模板

#### 分类任务
```
Role definition + Output format specification (选项列表)
```
约 **100-200 chars** 足够

#### 信息提取任务
```
Extract from text: field1, field2, field3.
```
约 **50-100 chars** 足够

#### 复杂推理任务
```
Role + Key rules (关键词及映射) + Output format
```
约 **200-300 chars** 足够，需保留关键规则

---

## 注意事项

1. **安全关键场景**：即使模型表现好，也建议保留安全检查关键词列表
2. **DeepSeek vs Llama**：大模型可能更容忍精简 prompt，小模型需更多引导
3. **测试覆盖**：精简后需确保边界情况测试通过
4. **任务类型决定精简极限**：
   - 分类任务：可压缩到 ~100 chars
   - 信息提取：可压缩到 ~50-80 chars
   - 复杂推理：需保留 ~200-300 chars

---

## 验证记录

对每个 node 完成 prompt tuning 实验：
- [x] medical_care ✅ (Llama: 125 chars 足够)
- [x] clinic_selector ✅ (Llama: 174 chars 足够)
- [x] condition_collector ✅ (Llama: 80 chars 足够)
- [x] requirement_collector ✅ (Llama: 67 chars 足够)
- [x] route_patcher ✅ (Llama: 255 chars 足够)
