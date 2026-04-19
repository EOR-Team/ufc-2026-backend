# Condition Collector 模块创建流程

本文档记录 `condition_collector` 和 `test_condition_collector` 的完整创建流程。

---

## 1. 需求分析

### 功能目标
从用户的自然语言描述中提取身体不适的相关信息，用于医疗分诊场景。

### 输出字段定义
| 字段 | 类型 | 描述 |
|------|------|------|
| `duration` | str | 症状持续时间 |
| `severity` | str | 严重程度（轻微/中等/严重） |
| `body_parts` | str | 受影响的身体部位 |
| `description` | str | 具体症状描述 |
| `other_relevant_info` | list[str] | 其他相关信息（如病史） |

### 设计约束
- 使用 **DSPy** 框架进行 LLM 编排
- 支持本地模型（Llama CPP）和在线模型（DeepSeek）
- 使用 **ChainOfThought** 推理模式

---

## 2. Signature 设计

### 错误做法 ❌

```python
class ConditionCollectorSignature(dspy.Signature):
    instructions: str = dspy.InputField(...)  # 错误！
    description_from_user: str = dspy.InputField(...)
    # ...
```

**原因**：在 DSPy 中，`instructions` 是父类 `Signature` 的内置属性。将其定义为 `InputField` 会遮蔽父类属性，导致 `json_schema_extra` 变为 `None`，引发 `TypeError: 'NoneType' object is not subscriptable`。

### 正确做法 ✅

```python
class ConditionCollectorSignature(dspy.Signature):
    description_from_user: str = dspy.InputField(
        desc = "the description from user about the user's current feelings and conditions"
    )

    duration: str = dspy.OutputField(
        desc = "the duration of how long the user has been experiencing..."
    )

    severity: str = dspy.OutputField(
        desc = "the severity or level of discomfort..."
    )

    body_parts: str = dspy.OutputField(
        desc = "the body parts that are affected by the symptoms..."
    )

    description: str = dspy.OutputField(
        desc = "a concrete description of the user's symptom or main complaint..."
    )

    other_relevant_info: list[str] = dspy.OutputField(
        desc = "any other relevant information that is helpful for nurse..."
    )
```

**要点**：
- `instructions` **不**定义为字段，而是在调用时作为 kwargs 传入
- `other_relevant_info` 使用 `list[str]` 类型声明，确保 DSPy 解析为列表

---

## 3. 实现代码 (`condition_collector.py`)

```python
import dspy

class ConditionCollectorSignature(dspy.Signature):
    description_from_user: str = dspy.InputField(...)
    duration: str = dspy.OutputField(...)
    severity: str = dspy.OutputField(...)
    body_parts: str = dspy.OutputField(...)
    description: str = dspy.OutputField(...)
    other_relevant_info: list[str] = dspy.OutputField(...)

collector = dspy.ChainOfThought(
    ConditionCollectorSignature
)

def collect_condition(description_from_user: str):
    return collector(
        instructions="collect the user's body condition information...",
        description_from_user=description_from_user
    )
```

### 关键点
- 使用 `dspy.ChainOfThought` 包装 Signature
- `instructions` 作为 kwargs 传递给 collector，不在 Signature 中定义
- 导出 `collect_condition` 函数供外部调用

---

## 4. 测试文件结构 (`test_condition_collector.py`)

### 4.1 Fixtures

```python
@pytest.fixture(scope="module")
def deepseek_lm():
    try:
        llm = DeepseekLM()
        dspy.configure(lm=llm)
        yield llm
    except ValueError:
        pytest.skip("DEEPSEEK_API_KEY not available")

@pytest.fixture(scope="module")
def llama_lm():
    try:
        llm = LlamaCppLM(
            model_id="test-condition-collector",
            model_filename="LFM2.5-1.2B-Instruct-Q4_K_M"
        )
        dspy.configure(lm=llm)
        yield llm
    except Exception as e:
        pytest.skip(f"Llama model not available: {e}")
```

### 4.2 Few-Shot Examples

```python
FEW_SHOT_EXAMPLES = [
    {
        "input": "我的脚有点疼。",
        "expected": {
            "body_parts": "脚",
            "severity": "轻微",
            "duration": "",
            "description": "脚部疼痛",
            "other_relevant_info": [],
        },
    },
    # ... 更多示例
]
```

### 4.3 评估指标

```python
def condition_collector_metric(example, pred, trace=None):
    expected = example.expected
    checks = {
        "body_parts": validate_field(pred.body_parts, expected["body_parts"], "body_parts"),
        "severity": validate_field(pred.severity, expected["severity"], "severity"),
        # ...
    }
    return sum(checks.values()) / len(checks)
```

### 4.4 测试类

| 测试类 | 描述 |
|--------|------|
| `TestConditionCollectorWithLlama` | 使用 Llama 本地模型测试 |
| `TestConditionCollectorWithDeepseek` | 使用 DeepSeek 在线模型测试 |
| `TestConditionCollectorSignature` | 验证 Signature 定义正确性 |
| `TestConditionCollectorEdgeCases` | 边界情况测试 |

---

## 5. 常见问题与解决方案

### 问题 1：DSPy Signature 创建失败

**错误**：
```
TypeError: 'NoneType' object is not subscriptable
```

**原因**：`instructions` 字段遮蔽了父类属性

**解决**：将 `instructions` 从 Signature 字段移除，改为调用时传入 kwargs

---

### 问题 2：输出类型不匹配

**错误**：
```
AssertionError: assert ('some string' is not None and False)
```

**原因**：Signature 中定义为 `str`，但测试期望 `list`

**解决**：将类型声明改为 `list[str]`

---

### 问题 3：测试期望值与 Signature 描述不一致

**问题**：`severity` 期望值包含疼痛性质描述（如"有点疼"），违背了 Signature 中"只包含程度"的定义

**解决**：调整期望值，使其符合 Signature 描述：
- "有点疼" → "轻微"
- "很难受" → "严重"

---

## 6. 验证流程

### 运行所有测试
```bash
source venv/bin/activate
python -m pytest test/test_condition_collector.py -v
```

### 预期结果
```
======================== 20 passed in 272.79s ========================
```

### 测试覆盖率
- Signature 定义验证（3 个测试）
- Llama 模型集成测试（10 个测试）
- DeepSeek 模型集成测试（4 个测试）
- 边界情况测试（3 个测试）

---

## 7. 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| LLM 编排框架 | DSPy | 支持多模型、热切换、内置 ChainOfThought |
| 推理模式 | ChainOfThought | 提供可解释的推理过程 |
| 输出解析 | 类型注解 | 利用 Python 类型系统让 DSPy 自动解析 |
| 测试策略 | 双模型测试 | 兼顾本地开发（Llama）和线上精度（DeepSeek） |

---

## 8. 文件清单

```
src/triager/
├── __init__.py
└── condition_collector.py    # 核心实现

test/
└── test_condition_collector.py  # 完整测试套件
```

---

## 9. 后续优化方向

1. **Few-Shot 示例优化** - 添加更多边界情况示例
2. **评估指标增强** - 支持部分匹配和模糊匹配
3. **性能测试** - 测量不同模型的响应时间
4. **Mock 测试** - 添加不依赖实际 LLM 的单元测试

---

## 10. clinic_selector 创建总结

### 10.1 创建背景

从 EOR-Team/ufc-2026 的 `clinic_selector.py` 迁移到 DSPy 架构：

| 维度 | 原代码 | 新架构 |
|------|--------|--------|
| LLM 框架 | `agents` + `Runner` | DSPy (`dspy.Signature`, `dspy.ChainOfThought`) |
| 函数设计 | online/offline 分离 | 统一 `select_clinic()` 函数 |
| 诊所列表 | 动态生成 (clinic_id_to_name_and_description) | 固定四种诊所 |
| logit bias | 复杂配置 | 未迁移 |
| typedef | ClinicSelectionOutput | 未迁移 |

### 10.2 关键决策

1. **统一函数设计**：不区分 online/offline，通过 DSPy 配置切换模型
2. **固定诊所列表**：使用 emergency_clinic, surgery_clinic, internal_clinic, pediatric_clinic 四种固定值
3. **决策优先级嵌入 instructions**：儿童 > 急诊 > 外科/内科

### 10.3 测试结果

```
16 passed (Llama + DeepSeek 双模型)
- Signature 验证: 3 tests ✅
- Llama 本地模型集成: 6 tests ✅
- DeepSeek 在线模型集成: 4 tests ✅
- 边界情况测试: 3 tests ✅
```

### 10.4 诊所决策逻辑

```
优先级 1: 儿科 (pediatric_clinic)
├── 判断条件: 患者是儿童（14岁以下）
└── 证据来源: description 中的年龄描述 ("5岁儿童发烧") 或 other_relevant_info ("年龄5岁")

优先级 2: 急诊 (emergency_clinic)
├── 判断条件: 危急症状
└── 证据来源: description ("意识模糊", "休克", "大出血", "呼吸困难")

优先级 3: 外科 (surgery_clinic)
├── 判断条件: 需要手术/操作的外伤
└── 证据来源: description ("骨折", "脓肿", "撕裂伤")

优先级 4: 内科 (internal_clinic)
└── 默认选项: 轻微/不明确/慢性症状
```

### 10.5 模型能力差异

| 用例 | LFM 1.2B 本地模型 | DeepSeek 输出 |
|------|-------------------|---------------|
| 儿童发烧 | pediatric_clinic ✅ | pediatric_clinic ✅ |
| 儿童轻微伤 | pediatric_clinic ✅ | pediatric_clinic ✅ |
| 严重外伤 | emergency_clinic ✅ | emergency_clinic ✅ |
| 骨折 | surgery_clinic ✅ | surgery_clinic ✅ |
| 呼吸道感染 | internal_clinic ✅ | internal_clinic ✅ |
| 不明确症状 | internal_clinic ✅ | internal_clinic ✅ |

**结论**: LFM 1.2B 模型对诊所选择任务表现良好，可能因为输出格式简单（只需输出一个诊所ID）。

### 10.6 创建检查清单

- [x] 确认输入字段（来自 condition_collector 输出）
- [x] 设计 Signature（输入5字段，输出1字段）
- [x] 编写详细 instructions（包含决策逻辑和示例）
- [x] 实现 `select_clinic()` 函数
- [x] 测试验证 (Llama + DeepSeek)
- [x] 不迁移 logit bias / online-offline 分离 / typedef 定义

---

## 11. 重构经验总结 (requirement_collector 重构)

### 10.1 重构背景

从 EOR-Team/ufc-2026 的原始实现迁移到当前 DSPy 架构：

| 维度 | 原代码 | 新架构 |
|------|--------|--------|
| LLM 框架 | `agents` + `Runner` | DSPy (`dspy.Signature`, `dspy.ChainOfThought`) |
| 模型调用 | 区分 `online` / `offline` 分离函数 | 统一 `collector()` + DSPy 配置 |
| 指令管理 | 硬编码 100+ 行 instructions | 通过 `instructions` kwargs 注入 |
| 输出验证 | 手动 JSON 解析 + ValidationError | 复用现有 JSON 解析逻辑 |
| Logit Bias | 复杂配置控制输出格式 | **未迁移** (按需求简化) |

### 10.2 关键决策

1. **完全重写 vs 增量修改**: 选择完全重写，确保架构一致性
2. **保留 Signature**: 已有 Signature 定义，无需重新设计
3. **instructions 整合**: 将原 100+ 行指令转换为 DSPy ChainOfThought 格式
4. **不迁移 logit bias**: 按需求简化，暂不保留

### 10.3 重构验证

```
测试结果: 19/19 passed (Llama + DeepSeek 双模型)
- Signature 验证: 3 tests ✅
- Llama 本地模型集成: 10 tests ✅
- DeepSeek 在线模型集成: 4 tests ✅
- 边界情况测试: 3 tests ✅
```

### 10.4 模型能力差异

| 用例 | LFM 1.2B 本地模型输出 | DeepSeek 输出 |
|------|----------------------|---------------|
| 简单需求提取 | 返回空列表 (能力不足) | 完全正确 |
| 多需求提取 | 返回空列表 | 完全正确 |
| 空需求 | 正确返回 `[]` | 正确返回 `[]` |

**结论**: LFM 1.2B 本地模型对复杂指令理解能力有限，在正式部署中应使用更大模型或在线模型。

### 10.5 重构检查清单

- [x] 确认 Signature 定义已存在且正确
- [x] 将原指令转换为 DSPy ChainOfThought instructions 格式
- [x] 保持 `collect_requirement(input_str)` 函数签名
- [x] 返回 `(requirements_list, reasoning)` 元组格式
- [x] 复用现有 JSON 解析逻辑
- [x] 测试验证 (Llama + DeepSeek)
- [x] 不迁移 logit bias / online-offline 分离 / typedef 定义

### 10.6 可复用的模式

```
重构模板:
1. 读取原代码的 instructions 指令
2. 检查现有 Signature 是否满足需求
3. 如需更新 instructions，替换 collector() 调用的 kwargs
4. 验证 JSON 解析逻辑
5. 运行测试套件确认
```
