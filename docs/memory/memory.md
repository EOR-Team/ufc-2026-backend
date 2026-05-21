---
name: 文档系统 Memory Bank
category: infra-rule
field: global
description: 文档系统的内存存储，目的在于给AI快速投喂上下文
date: 2026-05-20
---

# 文档系统 Memory Bank

## Part 1: Currently Working

1. 工作整体方向 - `perf-opt` 分支：优化本地 LLM (LFM2.5-1.2B) 推理速度

2. 当前具体任务 - Phase 1 已完成，待定下一阶段任务

3. 任务的作用：通过 Prompt 优化（CoT→Predict + docstring 指令 + max_tokens 限制）减少推理时间

4. 任务的工作目录：

- `src/triager/clinic_selector.py`、`src/triager/condition_collector.py`、`src/triager/requirement_collector.py`、`src/triager/route_patcher.py`

5. 任务开始时间：`2026-05-20`

6. 任务预期结束时间：`2026-05-21`

7. 任务状态：Phase 1 已完成

## Part 2: Context Snapshot

### Phase 1 结果 (2026-05-21)
- ClinicSelector: 82s → 9-15s (5-9x, CoT→Predict + docstring few-shot + config max_tokens=32)
- ConditionCollector: CoT→Predict, pipeline ~19s
- Pipeline 总时长 ~77-85s (未达 30s 目标)
- 最终使用模型：LFM2.5-1.2B-Instruct-Q4_K_M（替代 Qwen3.5-0.8B）

### DSPy 3.2.1 关键发现
- `instructions=` 直接被忽略，必须放 Signature docstring
- `max_tokens=` 直接被忽略，必须用 `config=dict(max_tokens=N)`

### 关键约束
- docs/ 内容会频繁变化，不适合硬编码路径
- AI 需要明确的入口指引，但不是完整清单
- 幽灵引用（不存在的文件引用）是主要问题

### 待确认
- [ ] Context Snapshot 的最佳粒度（按主题？按时间？）
- [ ] 是否需要定期清理旧 snapshot？

### 开发环境
- [ ] 使用 pyenv 管理 Python 3.11.2

### 已完成的改动
- `src/triager/clinic_selector.py`: CoT→Predict, docstring 内嵌 few-shot, config max_tokens=32
- `src/triager/condition_collector.py`: CoT→Predict, docstring 指令, config max_tokens=128
- `src/triager/requirement_collector.py`: docstring 指令, config max_tokens=256
- `src/triager/route_patcher.py`: docstring 指令, config max_tokens=256, 删除 _format_locations
- `model/LFM2.5-1.2B-Instruct-Q4_K_M.*.json`: n_ctx=4096, chat_template.default, max_tokens=512, repeat_penalty=1.1
- `model/Qwen3.5-0.8B-Q4_K_M.*.json`: 同上配置更新
- `src/main.py`: 默认模型切换为 LFM2.5-1.2B
