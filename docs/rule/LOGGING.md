# LOGGING 日志规范

**日期**: 2026-05-02
**状态**: 草稿
**适用**: Vibe Coding 模式下的 AI 自动开发

---

## 核心原则

> **铁律**: 禁止使用 print()，必须使用 logger
>
> "print() 没有颜色，没有文件输出，没有日志级别。"

### 强制规则

**AI 在以下场景必须询问人类，不得自行决定**：
- 需要自定义日志格式时
- 需要添加第三方日志库时
- 需要将日志输出到非标准位置时

### 违反规则的代价

| 违反行为 | 处理方式 |
|----------|----------|
| 使用 print() | 强制替换为 logger.info/warning/error |
| 记录敏感数据 | 立即删除，审查数据流 |
| 日志级别错误 | 重新评估并修正 |
| 过度记录 | 删除冗余日志 |

---

## 日志级别

| 级别 | 使用场景 | 颜色 |
|------|----------|------|
| `DEBUG` | 详细调试信息 | 青色（暗淡） |
| `INFO` | 正常操作 | 绿色 |
| `WARNING` | 潜在问题（不致命） | 黄色（加粗） |
| `ERROR` | 需要关注的错误 | 红色（加粗） |
| `CRITICAL` | 严重失败 | 红色（加粗） |

---

## 日志格式

```
[2026-04-24 22:30:15] INFO     src.triager: Loading model...
[2026-04-24 22:30:16] WARNING  src.llm: Model already loaded
[2026-04-24 22:30:17] ERROR    src.llm: Failed to load model: File not found
```

格式说明：
- 时间戳：`[YYYY-MM-DD HH:MM:SS]`
- 级别：`INFO/WARNING/ERROR`
- 模块：`src.triager`
- 消息：操作描述

---

## 基本用法

### 导入方式

```python
from src import logger

logger.info("操作完成")
logger.warning("警告信息")
logger.error(f"错误: {e}")
logger.debug("调试信息")
```

### 标准日志示例

```python
# 信息日志 - 关键里程碑
logger.info("Starting model loading")
logger.info(f"Loaded model: {model_id}")

# 警告日志 - 非致命问题
logger.warning(f"Model {model_id} already exists")
logger.warning("Using default configuration")

# 错误日志 - 包含上下文
logger.error(f"Failed to load model: {filename}")
logger.error(f"Unexpected error: {e}", exc_info=True)  # 包含堆栈跟踪
```

### 调试日志

```python
# 仅在 DEBUG 级别显示
logger.debug(f"Input: {input_data}")
logger.debug(f"Intermediate result: {result}")
```

### 函数入口/出口

```python
def my_function(param: str) -> Result:
    logger.debug(f"my_function called with param={param}")

    result = do_something(param)

    logger.debug(f"my_function returning success={result.success}")
    return result
```

---

## 敏感数据处理（红线）

### 禁止记录的内容

```python
# 绝对禁止
logger.info(f"API key: {api_key}")           # API 密钥
logger.debug(f"Password: {password}")       # 密码
logger.info(f"Token: {token}")              # 令牌
logger.debug(f"Phone: {phone_number}")      # 手机号
logger.info(f"ID card: {id_card}")          # 身份证
```

### 验证清单

每次日志记录前：
- [ ] 不包含 API 密钥或密码
- [ ] 不包含用户令牌或 session
- [ ] 不包含个人身份信息（PII）
- [ ] 不包含医疗记录

---

## 日志最佳实践

### 正确做法

```python
# 使用 f-string 格式化
logger.info(f"Loaded model: {model_id}")

# 包含相关上下文
logger.error(f"Failed to process request: {request_id}")

# 使用 exc_info 记录意外异常
logger.error(f"Unexpected error: {e}", exc_info=True)

# 在适当级别记录
logger.info("Starting operation X")  # 关键里程碑
logger.debug("Step 1 of 3")         # 详细流程
```

### 错误做法

```python
# 禁止使用 print()
print(f"Result: {result}")           # 错误 - 无颜色、无文件输出

# 禁止敏感数据
logger.info(f"API key: {api_key}")   # 错误 - 泄露密钥

# 禁止过度记录
logger.info("About to call function")
logger.info("Calling function")      # 冗余
logger.info("Function returned")

# 禁止所有都记为 ERROR
logger.error("User logged in")       # 错误 - 应使用 INFO
```

---

## 与 Result Type 集成

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

- [ ] 所有 print() 已替换为 logger
- [ ] 无敏感数据记录
- [ ] 日志级别使用正确
- [ ] 日志消息清晰且有上下文
- [ ] 异常日志包含堆栈跟踪
- [ ] 与 Result Type 模式集成
