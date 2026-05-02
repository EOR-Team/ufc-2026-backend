---
name: "002: Coral TPU 与 TTS 不兼容"
category: adr
field: tts
description: 确定 Coral TPU 与 Piper TTS 不兼容的决策记录
date: 2026-04-25
---

# 002: Coral TPU 与 TTS 不兼容

**日期**: 2026-04-25
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

评估 Coral TPU 是否能加速 TTS 工作负载，以确定硬件选型策略。

## 考虑的方案

| 方案 | 架构 | TTS 加速 | 结论 |
|------|------|----------|------|
| Coral TPU | CNN 专用加速器 | ❌ 不支持 | **选择** |
| Jetson Orin Nano | GPU (6GB VRAM) | ✅ 可跑 XTTS | 备选方案 |
| 联网方案 | 云端 API | ✅ 高质量 | 备选方案 |

## 决策

**选择:** Coral TPU 不用于 TTS

## 理由

1. **硬件架构不匹配**：Coral TPU 是 Edge TPU ASIC，专为 CNN 设计；TTS 模型使用 RNN/Transformer 架构（VITS、FastSpeech2 等）
2. **软件层面不支持**：TPU 编译器不支持 TTS 模型中的循环结构，缺乏相应算子优化
3. **实际验证**：Coral TPU 无法加速任何 TTS 工作负载已通过技术调研确认

## 放弃的替代方案

- **Jetson Orin Nano**: 可跑 XTTS v2，但成本和功耗远高于 Coral TPU，仅在高配置需求时考虑

## 后续行动

- [ ] Coral TPU 专项用于视觉任务（图像分类、目标检测）