---
name: CLAUDE.md
date: 2026-05-03
attention: ONLY EDIT BY USER SELF
---

# CLAUDE.md

## BEFORE BEGINNING

**MUST**: 请你先深入阅读一遍 @docs/RULE.md 和 @docs/PRINCPLE.md，将他们作为第一守则牢记在心。

## 项目概述

这是一个模拟医院场景下的聊天机器人与配套的机器人小车的后端服务器。

功能有：

1. 帮助用户规划就诊路径的聊天机器人模块 ( in @src/triager/ )

2. 给予用户建议的聊天机器人模块 ( in @src/medical_care.py )

3. 机器人小车控制模块 ( in @src/car/ )

4. 语音对话模块 ( in @src/voice/ )

更多内容请查看 @docs/overview/。

## 当前上下文信息

请查看 @docs/memory/。

## 文档快速导航

请查看 @docs/index/。

## 常用指令

**BEFORE COMMANDING**: 请在项目根目录下通过 `venv/` 激活虚拟环境。

**TIPS**: 不要尝试自行启动后端服务器，除非用户**要求**。你应该将这项工作**交给用户自行启动**。

### 后端服务器

- 常规启动: ```python -m src.main```

- 使用在线LLM启动: ```python -m src.main --llm_online```

### 测试

```python -m test.xxx_file_name```
