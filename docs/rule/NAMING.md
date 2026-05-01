# NAMING 命名规范

**日期**: 2026-05-02
**状态**: 草稿
**适用**: Vibe Coding 模式下的 AI 自动开发

---

## 核心原则

> **铁律**: 命名不一致即 bug
>
> "命名是设计的一部分，混乱的命名预示着混乱的设计。"

### 强制规则

**AI 在以下场景必须询问人类，不得自行决定**：
- 需要使用非标准缩写时
- 遇到领域特定术语时
- 多单词组合的边界不明确时

### 违反规则的代价

| 违反行为 | 处理方式 |
|----------|----------|
| 命名使用 camelCase | 强制替换为 snake_case |
| 类名使用 snake_case | 强制替换为 PascalCase |
| 常量使用小写 | 强制替换为 UPPER_SNAKE_CASE |
| 布尔变量无前缀 | 强制添加 is_/has_/should_/can_ |

---

## Python 文件命名

### Python 文件

**使用小写下划线**：

| 正确 | 错误 | 原因 |
|------|------|------|
| `clinic_selector.py` | `clinicSelector.py` | 禁止 camelCase |
| `clinic_selector.py` | `clinic-selector.py` | 禁止 kebab-case |
| `route_patcher.py` | `routePatcher.py` | 禁止 camelCase |

### 测试文件

**使用 `test_<模块名>.py`**：

| 正确 | 错误 | 原因 |
|------|------|------|
| `test_clinic_selector.py` | `clinic_selector_test.py` | 应以 test_ 开头 |
| `test_medical_care.py` | `TestMedicalCare.py` | PascalCase 不用于测试文件 |

### 配置文件

**使用小写下划线或精确模型名称**：

```
model/llm.json  ✓
model/LFM2.5-1.2B-Instruct-Q4_K_M.llm.json  ✓
```

---

## 函数命名

### Python 函数

**使用 snake_case**：

```python
# Good
def get_medical_care_advice():
def select_clinic():
def collect_condition():

# Bad
def getMedicalCareAdvice():   # camelCase
def SelectClinic():           # PascalCase
def collect_condition():      # ✓ 正确
```

### DSPy Agent 函数

**使用 `<action>_<target>` 或 `<target>_<action>` 模式**：

```python
def select_clinic()      # 选择诊所
def collect_condition()  # 收集病情
def patch_route()        # 修补路由
```

---

## 变量命名

### 一般变量

**使用 snake_case**：

```python
# Good
clinic_id
requirement_summary
user_input

# Bad
clinicId           # camelCase
requirementFromUser  # camelCase
```

### 布尔变量

**添加前缀 `is_`, `has_`, `should_`, `can_`**：

```python
# Good
is_valid
has_results
requires_doctor_consultation
can_proceed

# Bad
valid
results
doctorConsultation  # 无前缀
```

### 集合命名

**单数名词表示单个元素，复数表示集合**：

```python
clinic      # 单个诊所
clinics     # 诊所列表
requirement # 单个需求
requirements  # 需求列表
```

---

## 类命名

### Python 类

**使用 PascalCase**：

```python
# Good
class MedicalCareSignature:
class ClinicSelectorSignature:
class RoutePatcherSignature:

# Bad
class medical_care_signature:  # snake_case
class medical_care_signature:  # snake_case
```

### DSPy Signatures

**使用 `<Feature>Signature` 模式**：

```python
class MedicalCareSignature:    # ✓
class ClinicSelectorSignature:  # ✓
class RoutePatcherSignature:    # ✓
```

### DSPy ChainOfThought

**使用 `<Feature>Cot` 或 `<Feature>Collector` 模式**：

```python
class RoutePatcherCot:    # ✓
collector = ...           # 模块级实例使用 lowercase
```

---

## 常量命名

### 常量

**使用 UPPER_SNAKE_CASE**：

```python
# Good
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# Bad
max_retries = 3        # 小写
maxRetries = 3         # camelCase
```

---

## 模块命名

### Python 模块

**使用小写下划线**：

```python
# Good
from src.llm import ...
from src.triager import ...

# Bad
from src.LLM import ...      # PascalCase
from src.triager.clinic_selector import ...
```

---

## 类型命名

### Pydantic Models

**使用 PascalCase**：

```python
class Result(BaseModel):      # ✓
class MedicalAdvice(BaseModel):  # ✓
```

### 类型别名

**使用 PascalCase 或描述性名称**：

```python
Result = Result
MedicalAdvice = dict
```

---

## 快速参考表

| 类型 | 规范 | 示例 |
|------|------|------|
| Python 文件 | snake_case | `clinic_selector.py` |
| 测试文件 | test_<name>.py | `test_clinic_selector.py` |
| 函数 | snake_case | `select_clinic()` |
| 类 | PascalCase | `MedicalCareSignature` |
| 变量 | snake_case | `clinic_id` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| 布尔变量 | is_/has_ 前缀 | `is_valid` |
| DSPy 字段 | snake_case | `body_parts` |
| 模块 | snake_case | `src.llm` |

---

## 验证清单

完成实现前，确保每项都已检查：

- [ ] 文件名使用 snake_case
- [ ] 测试文件以 test_ 开头
- [ ] 函数名使用 snake_case
- [ ] 类名使用 PascalCase
- [ ] 常量使用 UPPER_SNAKE_CASE
- [ ] 布尔变量有正确前缀
- [ ] 集合命名使用单数/复数区分
- [ ] 无 camelCase 残留
