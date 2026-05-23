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

2. 当前具体任务 - Vision 巡线导航模块重构已完成（2026-05-23），后续待实车标定

3. 任务的作用：重构后的巡线系统使用轮廓长宽比路口检测、自适应阈值二值化、标定物理接口过路口/转向、终点检测自动停车

4. 任务的工作目录：

- `src/vision/navigator.py`（362 行）、`src/vision/line_detector.py`（144 行）、`src/vision/pid_controller.py`（88 行）、`src/vision/intersection_detector.py`（88 行）、`src/vision/routes.py`、`src/car/control.py`

5. 任务开始时间：`2026-05-23`

6. 任务预期结束时间：`2026-05-30`

7. 任务状态：代码重构已完成，待实车标定验证

## Part 2: Context Snapshot

### Navigation 分支 (2026-05-23 重构完成)
- Vision 巡线导航系统已重构：LineDetector (自适应阈值 + 终点检测) → PIDController (Ki=1.0) → IntersectionDetector (轮廓长宽比分类 + 30% 面积阈值) → Navigator (状态机 + car/control.py 标定接口)
- 路口检测: 竖线(h/w>2) + 横线(w/h>2) 同时存在 + 总面积 > ROI 30% → 3帧防抖确认
- 过路口: `car.control.forward(0.1)` 前进 0.1m（基于 V_FORWARD=0.215 m/s 标定）
- 转向: `car.control.turn(±90)`（基于 V_ROTATE=96.0 deg/s 标定）
- 终点检测: 上半 40% 连续 3 帧无黑线 → 自动 DONE
- 状态机: FOLLOW_LINE → CROSSING → TURNING → ... → DONE
- Mock 模式: 摄像头不可用时强制底盘 mock，每 100 tick 生成虚拟路口；过路口/转向 mock 阶段 time.sleep(2)
- Navigator 直接消费 `get_commands()` 输出: `[{action: "forward"|"turn", param: float}]`
- 运动控制分离: 巡线差速保留直接电机控制，过路口/转向走 car/control.py 标定接口
- TODO: get_commands() 设计重构
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
