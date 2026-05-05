---
name: "004: 日志规范"
category: adr
field: code
description: 确定统一日志格式与敏感数据处理规范
date: 2026-04-24
---

# 004: 日志规范

**日期**: 2026-04-24
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

项目需要统一的日志规范以便于调试和监控，需要在控制台输出可读性强的日志。

## 考虑的方案

| 方案 | 彩色输出 | 文件日志 | 可用性 | 结论 |
|------|----------|----------|--------|------|
| src/logger.py (ColoredFormatter) | ✅ | 可选 | 内置 | **选择** |
| print() | ❌ | ❌ | 内置 | 放弃 |
| 标准 logging + 第三方库 | ✅ | ✅ | 需安装 | 过度 |

## 决策

**选择:** 使用 src/logger.py 的 ColoredFormatter

## 理由

1. **内置可用**：无需额外依赖，直接 import 使用
2. **彩色输出**：不同级别不同颜色，便于快速识别
3. **可选文件日志**：可通过 `setup_file_logging()` 开启

## 日志级别

| 级别 | 使用场景 | 颜色 |
|------|----------|------|
| DEBUG | 详细调试信息 | Cyan (dim) |
| INFO | 正常操作 | Green |
| WARNING | 潜在问题 | Yellow (bold) |
| ERROR | 需要关注的错误 | Red (bold) |
| CRITICAL | 严重故障 | Red (bold) |

## 格式

```
[2026-04-24 22:30:15] INFO     src.triager: Loading model...
```

## 最佳实践

### Do

```python
logger.info(f"Loaded model: {model_id}")
logger.error(f"Failed to load model: {filename}", exc_info=True)
```

### Don't

```python
print(f"Result: {result}")           # 使用 logger
logger.info(f"API key: {api_key}")    # 不要记录敏感数据
logger.error("User logged in")        # INFO 级别不要用 ERROR
```

## 与 Result 集成

```python
if not result.success:
    logger.error(f"Failed to load model '{model_id}': {result.error}")
    return result
```

## 文件日志（可选）

```python
from src.logger import setup_file_logging
setup_file_logging(log_dir="/var/log/ufc")
```