---
name: Vision 巡线导航标定工作流设计
category: adr
field: code
description: 三脚本标定系统（场景采集 + PID 动态测试 + 底盘物理验证）配合 Claude Code 数据分析，形成闭环参数调优流程
date: 2026-05-23
---

# 013: Vision 巡线导航标定工作流设计

**日期**: 2026-05-23
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

Vision 巡线导航模块（ADR-012）已从理论上设计完成，但大量参数为估算值（Kp=30, Ki=1.0, AREA_THRESHOLD_RATIO=0.3, FORWARD_DISTANCE=0.1 等）。从设计到现实需要一套系统化的标定工作流——采集真实数据、分析偏差、迭代调参——而非盲目试凑。

约束：
- 树莓派运行脚本，人类通过 VNC 观察画面，Claude Code 在笔记本上分析数据
- 标定参数硬编码在源码中，Claude Code 直接修改 `.py` 文件
- 人类只负责观察 + 反馈，不记录数据

## 考虑的方案

| 方案 | 工具 | 自动化 | 选否原因 |
|------|------|--------|----------|
| A: 三脚本 + Claude Code 数据分析 | 3 个独立 Python 脚本 + JSONL 日志 | Claude Code 读日志分析、改代码 | **选择** |
| B: 单一大脚本含所有模式 | 1 个脚本多个子命令 | Claude Code 读日志分析 | 职责过重，维护困难 |
| C: Jupyter Notebook 交互 | Notebook cells | 手动跑 cells | 不符合项目技术栈（无 Jupyter 依赖） |

## 决策

**选择:** 方案 A

## 理由

1. **职责清晰**：三个脚本各有独立依赖和产出，互不干扰
2. **Claude Code 天然适配 JSONL**：可以直接 `Read` 日志文件做统计分析，不需要额外工具
3. **人类角色明确**：只看和反馈，不用分心记录
4. **参数在源码中**：保持与项目编码规范一致，不需要额外的配置文件

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                      标定闭环                           │
│                                                        │
│  树莓派 (VNC)                 笔记本 (Claude Code)     │
│  ┌──────────────┐            ┌──────────────────┐     │
│  │ 脚本采集数据  │──JSONL──→│ Read + 分析      │     │
│  │ 人类观察行为  │──描述──→│ 给出参数建议      │     │
│  │              │←─改代码─│ Edit .py 文件    │     │
│  └──────────────┘            └──────────────────┘     │
│        ↑                                               │
│        └── 迭代直到参数收敛 ────────────────────────── │
└─────────────────────────────────────────────────────────┘
```

### 三脚本

| 脚本 | 依赖 | 产出目录 | 用途 |
|------|------|---------|------|
| `test/test_vision_scene.py` | LineDetector, IntersectionDetector | `data/vision_calib/line_scene/` | 画面验证、路口采样 |
| `test/test_vision_pid.py` | LineDetector, PIDController | `data/vision_calib/pid_test/` | PID 偏差/电机输出动态采集 |
| `test/test_chassis_calib.py` | car.control | `data/vision_calib/chassis/` | 底盘物理标定（速度验证） |

### 数据流

- **JSONL 采样**：20Hz（每 50ms 一帧完整检测数据）
- **Console log**：10Hz（每 100ms 一行摘要）
- **文件组织**：按场景分子目录，文件名由 `--tag` 参数指定

### 标定闭环

```
Phase 1-2: test_vision_scene.py → Claude Code 读 line_scene/ → 建议阈值
Phase 4:   test_vision_pid.py    → Claude Code 读 pid_test/   → 建议 PID 增益
Phase 5-7: Navigator.run()       → Claude Code 读运行日志     → 微调参数
Phase 附:  test_chassis_calib.py → Claude Code 读 chassis/    → 更新 V_FORWARD/V_ROTATE
```

## 交互模式

每个脚本默认运行在 **record 模式**（采集 + 记录），可选 `--display` 标志打开 OpenCV 实时画面叠加。

### test_vision_scene.py

```
python -m test.test_vision_scene --tag on_line_take1           # record 模式，纯数据采集
python -m test.test_vision_scene --tag near_junction --display # 带画面显示
```

record 字段（JSONL）：
```json
{"t": 0.0, "area": 3420, "vertical": 3, "horizontal": 0, "ratio": 0.09, "deviation": 0.12, "line_detected": true, "at_intersection": false}
```

### test_vision_pid.py

```
python -m test.test_vision_pid --tag straight_line_take1
python -m test.test_vision_pid --tag disturb_test --display
```

record 字段（JSONL）：
```json
{"t": 0.0, "deviation": 0.35, "line_detected": true, "left_speed": 25, "right_speed": 15, "kp": 30.0, "ki": 1.0, "kd": 10.0}
```

### test_chassis_calib.py

```
python -m test.test_chassis_calib
```

交互流程：
1. 脚本执行 `forward(1.0)` × 3，`turn(360)` × 3
2. 每次执行后打日志
3. 人类测量实际值，反馈给 Claude Code
4. Claude Code 计算新标定值并改 `car/LOBOROBOT.py` 中的 `V_FORWARD` / `V_ROTATE`

## 具体变更

| 文件 | 变更 |
|------|------|
| `test/test_vision_scene.py` | 场景采集脚本（新增） |
| `test/test_vision_pid.py` | PID 动态采集脚本（新增） |
| `test/test_chassis_calib.py` | 底盘标定脚本（新增） |
| `data/vision_calib/` | 标定数据目录（新增） |

## 放弃的替代方案

- **方案 B**: 单一脚本所有模式 → 参数和依赖混杂，Claude Code 定位问题时扫描范围过大
- **方案 C**: Jupyter Notebook → 项目不依赖 Jupyter，引入额外技术栈

## 后续行动

- [ ] 实现三脚本
- [ ] 在实车环境执行 Phase 1-7 标定流程
- [ ] 根据实采数据更新 ADR-012 中的参数初值
