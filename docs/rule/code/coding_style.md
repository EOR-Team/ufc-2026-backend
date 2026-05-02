---
name: CODING-STYLE 代码风格规范
category: rule
field: code
description: 定义命名规范、代码风格与日志标准
date: 2026-05-02
---

# CODING-STYLE 代码风格规范

**日期**: 2026-05-02
**状态**: 草稿
**适用**: Vibe Coding 模式下的 AI 自动开发

---

## 核心原则

### 违反规则的代价

| 违反行为 | 处理方式 |
|----------|----------|
| 无类型注解 | 拒绝合并，退回重写 |
| 使用 print() | 强制替换为 logger |
| 命名不符合规范 | 强制替换，审查全文件 |
| 函数超过 50 行 | 拆分为更小的函数 |
| 文件超过 800 行 | 按功能拆分为多个模块 |
| 硬编码配置值 | 提取为常量 |

---

## 第一部分：命名规范

### 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Python 文件 | snake_case | `clinic_selector.py` |
| 测试文件 | `test_<模块名>.py` | `test_clinic_selector.py` |
| 配置文件 | 小写下划线或精确名称 | `model/llm.json` |

### 函数命名

**使用 snake_case**：

```python
# Good
def get_medical_care_advice():
def select_clinic():
def collect_condition():

# Bad
def getMedicalCareAdvice():   # camelCase
def SelectClinic():           # PascalCase
```

### 变量命名

**使用 snake_case**：

```python
# Good
clinic_id
requirement_summary

# Bad
clinicId             # camelCase
requirementFromUser  # camelCase
```

### 布尔变量

**添加前缀 `is_`, `has_`, `should_`, `can_`**：

```python
# Good
is_valid
has_results
can_proceed

# Bad
valid      # 无前缀
results    # 无前缀
```

### 集合命名

**单数名词表示单个，复数表示集合**：

```python
clinic        # 单个诊所
clinics       # 诊所列表
requirement   # 单个需求
requirements  # 需求列表
```

### 类命名

**使用 PascalCase**：

```python
# Good
class MedicalCareSignature:
class ClinicSelectorSignature:

# Bad
class medical_care_signature:  # snake_case
```

### DSPy 特定命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Signature | `<Feature>Signature` | `MedicalCareSignature` |
| ChainOfThought | `<Feature>Cot` | `RoutePatcherCot` |
| 模块级实例 | lowercase | `collector = ...` |
| DSPy 字段 | snake_case | `body_parts` |

### 常量命名

**使用 UPPER_SNAKE_CASE**：

```python
# Good
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Bad
max_retries = 3     # 小写
maxRetries = 3      # camelCase
```

### 类型命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Pydantic Models | PascalCase | `class Result(BaseModel)` |
| 类型别名 | PascalCase | `MedicalAdvice` |

---

## 第二部分：代码风格

### PEP 8 + 项目扩展

| 规则 | 标准 |
|------|------|
| 行长度 | 最多 120 字符 |
| 缩进 | 4 空格（禁止 Tab） |
| 顶级定义间空行 | 2 行 |
| 函数定义间空行 | 1 行 |

### 类型注解（强制）

**所有函数签名必须有类型注解**：

```python
# Good
def get_medical_care_advice(symptoms: str, diagnosis: str) -> tuple[dict, object]:
    ...

# Bad - 无类型注解
def get_medical_care_advice(symptoms, diagnosis):
    ...
```

**检查要求**：
- 参数必须标注类型
- 返回值必须标注类型

### 注释规范

**使用中文注释，以 `# ` 格式**：

```python
# 这是中文注释
result = load_model(model_id, filename)  # 加载模型

# Section header 示例
# ========================================
# 模型管理
# ========================================
```

### 代码大小限制

| 限制 | 标准 |
|------|------|
| 单个函数 | 最多 50 行 |
| 单个文件 | 最多 800 行 |

**超出时**：必须拆分为更小的模块/函数

---

## 第三部分：日志规范

### 日志级别

| 级别 | 使用场景 | 颜色 |
|------|----------|------|
| `DEBUG` | 详细调试信息 | 青色（暗淡） |
| `INFO` | 正常操作 | 绿色 |
| `WARNING` | 潜在问题（不致命） | 黄色（加粗） |
| `ERROR` | 需要关注的错误 | 红色（加粗） |
| `CRITICAL` | 严重失败 | 红色（加粗） |

### 日志格式

```
[2026-04-24 22:30:15] INFO     src.triager: Loading model...
[2026-04-24 22:30:16] WARNING  src.llm: Model already loaded
[2026-04-24 22:30:17] ERROR    src.llm: Failed to load model: File not found
```

### 基本用法

```python
from src import logger

logger.info("操作完成")
logger.warning("警告信息")
logger.error(f"错误: {e}", exc_info=True)
logger.debug("调试信息")
```

### 敏感数据处理（红线）

**绝对禁止记录**：

```python
logger.info(f"API key: {api_key}")       # API 密钥
logger.debug(f"Password: {password}")  # 密码
logger.info(f"Token: {token}")         # 令牌
logger.debug(f"Phone: {phone}")        # 手机号
```

### 与 Result Type 集成

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

---

## 验证清单

完成实现前，确保每项都已检查：

### 命名检查
- [ ] 文件名使用 snake_case
- [ ] 函数名使用 snake_case
- [ ] 类名使用 PascalCase
- [ ] 常量使用 UPPER_SNAKE_CASE
- [ ] 布尔变量有正确前缀
- [ ] 无 camelCase 残留

### 类型注解检查
- [ ] 所有函数有类型注解
- [ ] 参数类型已标注
- [ ] 返回值类型已标注

### 日志检查
- [ ] 所有 print() 已替换为 logger
- [ ] 无敏感数据记录
- [ ] 日志级别使用正确

### 代码质量检查
- [ ] 函数不超过 50 行
- [ ] 文件不超过 800 行
- [ ] 中文注释清晰
- [ ] 硬编码值已提取为常量