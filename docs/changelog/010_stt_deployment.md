---
name: "010: STT 部署文档索引"
category: adr
field: stt
description: 索引指向 whisper.cpp 部署详细文档，供 STT 开发时查阅
date: 2026-05-03
---

# 010: STT 部署文档索引

**日期**: 2026-05-03
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

本 ADR 作为 whisper.cpp STT 部署过程的索引文档，不要求 AI 默认阅读，仅在需要部署或调试 STT 时查阅。

## 文档索引

### 边缘部署技术规格

**文件**: `docs/archive/whisper/edge-deploy-tech-spec.md`

**内容摘要**:
- Raspberry Pi 4B 部署架构
- whisper.cpp 构建配置（Q5_0 量化、ARM NEON、OpenBLAS）
- whisper-server HTTP API 接口
- 后端集成方式（FastAPI + subprocess 管理）
- 性能预期与限制

**何时查阅**: 在树莓派上部署 whisper.cpp STT 时

### WSL2 CUDA 开发环境

**文件**: `docs/archive/whisper/wsl2-cuda-deploy.md`

**内容摘要**:
- WSL2 + RTX 2060 CUDA 环境构建步骤
- CMake 配置与 CUDA 编译器路径问题解决
- WHISPER_CUBLAS 已废弃说明
- 模型量化对照表（tiny 模型）
- Pi 4B 与 WSL2 部署差异对比

**何时查阅**: 在 WSL2 环境下开发或调试 whisper.cpp 时

## 使用原则

- AI 默认阅读本目录下的 ADR 结论文档
- 详细 STT 部署文档仅在需要时通过本文档索引查阅
- 避免将详细部署过程直接引入 AI 上下文，以免污染
