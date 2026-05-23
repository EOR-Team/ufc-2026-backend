---
name: 文档系统 Memory Bank
category: infra-rule
field: global
description: 文档系统的内存存储，目的在于给AI快速投喂上下文
date: 2026-05-23
---

# 文档系统 Memory Bank

## Part 1: Currently Working

1. 工作整体方向 - `navigation` 分支：基于视觉的巡线导航系统

2. 当前具体任务 - 调试/优化巡线、路口检测与 PID 参数

3. 任务的作用：确保小车能准确沿黑线行驶、识别路口、完成路径规划中的转向

4. 任务的工作目录：

- `src/vision/navigator.py`、`src/vision/line_detector.py`、`src/vision/pid_controller.py`、`src/vision/intersection_detector.py`、`src/vision/routes.py`

5. 任务开始时间：`2026-05-23`

6. 任务预期结束时间：`2026-05-30`

7. 任务状态：正在进行

## Part 2: Context Snapshot

### Navigation 分支 (2026-05-23)
- Vision 巡线导航系统已实现：LineDetector (OpenCV 黑线检测) → PIDController (差速转向) → IntersectionDetector (路口识别) → Navigator (状态机)
- 状态机: FOLLOW_LINE → CROSSING → TURNING → ... → DONE
- Mock 模式: 摄像头不可用时自动模拟巡线（每 100 tick 生成虚拟路口），底盘不可用时仅记录日志
- Navigator 直接消费 `get_commands()` 输出: `[{action: "forward"|"turn", param: float}]`
- API: `POST /vision/start_navigate`, `POST /vision/stop`, `GET /vision/status`
- smbus2 替代 smbus，解决 I2C 兼容性

### Phase 1 结果 (2026-05-21) — 历史参考
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

### 开发环境
- [ ] 使用 pyenv 管理 Python 3.11.2

### 已完成的改动 (累计)
- `src/triager/clinic_selector.py`: CoT→Predict, docstring 内嵌 few-shot, config max_tokens=32
- `src/triager/condition_collector.py`: CoT→Predict, docstring 指令, config max_tokens=128
- `src/triager/requirement_collector.py`: docstring 指令, config max_tokens=256
- `src/triager/route_patcher.py`: docstring 指令, config max_tokens=256, 删除 _format_locations
- `model/LFM2.5-1.2B-Instruct-Q4_K_M.*.json`: n_ctx=4096, chat_template.default, max_tokens=512, repeat_penalty=1.1
- `src/main.py`: 默认模型切换为 LFM2.5-1.2B, 新增 vision_router
- `src/vision/`: 完整巡线导航模块（6 个文件）
