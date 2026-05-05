---
name: "008: TTS 研究文档索引"
category: adr
field: tts
description: 索引指向 TTS 研究详细文档，供需要时查阅
date: 2026-05-03
---

# 008: TTS 研究文档索引

**日期**: 2026-05-03
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

本 ADR 作为 TTS 研究过程的索引文档，不要求 AI 默认阅读，仅在需要深入研究时查阅。

## 文档索引

### TTS 方案对比

**文件**: `docs/archive/research/tts-solution-comparison.md`

**内容摘要**:
- Piper TTS、espeak-ng、EdgeTTS、Coqui XTTS、OpenAI TTS 方案对比
- Coral TPU 与 TTS 不兼容的原因分析

**何时查阅**: 需要了解 TTS 方案选型历史或 Coral TPU 兼容性细节时

### Piper TTS 详细部署

**文件**: `docs/archive/research/piper-tts-raspberry-pi.md`

**内容摘要**:
- Piper TTS 树莓派 4B 部署详细步骤
- 中文语音模型下载与配置
- 性能参考与注意事项

**何时查阅**: 需要在树莓派上部署 Piper TTS 时

### Prompt Finetune 实验记录

**文件**: `docs/archive/research/finetune-prompt.md`

**内容摘要**:
- 5 个 DSPy node 的 prompt 精简实验记录
- 各任务类型的 prompt 压缩率与最终效果

**何时查阅**: 需要优化 DSPy Signature instructions 时

## 使用原则

- AI 默认阅读本目录下的 ADR 结论文档
- 详细研究过程文档仅在需要时通过本文档索引查阅
- 避免将详细过程文档直接引入 AI 上下文，以免污染
