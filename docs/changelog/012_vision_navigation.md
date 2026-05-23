---
name: Vision 视觉巡线导航系统设计
category: adr
field: code
description: 采用 OpenCV 黑线检测 + PID 差速控制 + 路口识别 + 状态机架构实现巡线导航，支持硬件/Mock 双模式
date: 2026-05-23
---

# 012: Vision 视觉巡线导航系统设计

**日期**: 2026-05-23
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

`src/map/tools.py::get_commands()` 已将路径转为 `[{action, param}]` 指令序列（forward N 米 → turn ±90° → ...），但缺少将这些指令转为实际行驶行为的执行层。需要一个视觉巡线系统来：

1. 沿地面黑线行驶（PID 闭环控制）
2. 在网格路口处执行转向
3. 在开发机（无摄像头/底盘）上可测试

约束：
- 处理 320×240 低分辨率 USB 摄像头输入
- 树莓派算力有限，算法需轻量
- 必须支持 Mock 模式用于离线开发

## 考虑的方案

| 方案 | 精度 | 计算开销 | 可调试性 | 方案对比 |
|------|------|----------|----------|----------|
| A: 轮廓面积法 + PID 差速 + 状态机 | 中 | 低（纯 OpenCV） | 高（Mock 模式） | **选择** |
| B: 霍夫线变换 + 纯几何导航 | 中高 | 中 | 低 | 放弃 |
| C: 深度学习语义分割 | 高 | 高（需 GPU） | 低 | 过度工程 |

## 决策

**选择:** 方案 A

## 理由

1. **计算开销低**：自适应阈值 + 轮廓查找 + Sobel 边缘检测均为 O(n) 操作，适合树莓派
2. **PID 闭环可控**：Kp=30, Ki=0, Kd=10 为保守起点，现场可调优
3. **Mock 模式零成本**：摄像头不可用时每 100 tick 模拟路口，底盘不可用时仅日志记录
4. **状态机清晰**：6 个状态（IDLE/FOLLOW_LINE/CROSSING/TURNING/DONE/STOPPED）覆盖所有运行时场景

## 架构

```
get_commands() → Navigator.set_commands()
                       ↓
              Navigator.run() — 状态机循环
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
  LineDetector   PIDController  IntersectionDetector
  (黑线偏差)     (差速转向)     (路口识别)
        ↓              ↓              ↓
        └──────────────┼──────────────┘
                       ↓
               Robot (底盘) 或 Mock 日志
```

### 状态机

```
IDLE → FOLLOW_LINE → CROSSING → TURNING → FOLLOW_LINE → ... → DONE
                   ↘                              ↗
                    STOPPED (emergency)
```

- FOLLOW_LINE: 读取帧 → 检测黑线偏差 → PID 差速 → 检测路口
- CROSSING: 固定时长直行过路口 → 判断是否还需过路口 / 是否该转向 / 是否结束
- TURNING: 按角度 × 固定速率执行转向 → 进入下一段 FOLLOW_LINE

### 路口检测策略

双信号融合 + 防抖：
1. **轮廓面积突变**：当前帧面积 > 历史均值 × 2.5（路口处黑线区域更大）
2. **水平边缘检测**：Sobel X 方向检测横向线条（交叉路口特征）
3. **防抖**：连续 3 帧确认才判定路口，避免误检

### Mock 模式

| 条件 | 行为 |
|------|------|
| 摄像头不可用 | 每 MOCK_INTERSECTION_TICKS(100) tick 自动生成虚拟路口 |
| 底盘不可用（无 smbus/RPi.GPIO） | 电机指令仅记录日志，不调用硬件 |

## 具体变更

| 文件 | 变更 |
|------|------|
| `src/vision/navigator.py` | 状态机导航控制器（新增 417 行） |
| `src/vision/line_detector.py` | OpenCV 黑线检测（新增 154 行） |
| `src/vision/pid_controller.py` | PID 差速控制器（新增 81 行） |
| `src/vision/intersection_detector.py` | 路口检测器（新增 118 行） |
| `src/vision/routes.py` | FastAPI 路由（新增 97 行） |
| `src/main.py` | 注册 vision_router |

## 放弃的替代方案

- **方案 B**: 霍夫线变换精度略高但计算量大，树莓派帧率可能不足
- **方案 C**: 需要 GPU 推理，树莓派 + Coral TPU 方案已在 ADR-002 中被排除

## 后续行动

- [ ] 实车标定 PID 参数（Kp, Ki, Kd）
- [ ] 标定 INTERSECTION_FORWARD_TIME, TURN_DURATION_90, LINE_FOLLOW_BASE_SPEED
- [ ] 验证真实路口检测准确率
