---
name: "009: 模型加载与故障排除索引"
category: adr
field: code
description: 索引指向故障排除详细文档，供调试时查阅
date: 2026-05-03
---

# 009: 模型加载与故障排除索引

**日期**: 2026-05-03
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

本 ADR 作为故障排除过程的索引文档，不要求 AI 默认阅读，仅在遇到问题时查阅。

## 文档索引

### 模型加载故障排除

**文件**: `docs/archive/troubleshooting/model-loading.md`

**内容摘要**:
- Model File Not Found 诊断与解决
- Wrong CUDA Version 诊断与解决
- Insufficient GPU Memory 解决思路
- Invalid Model Format 诊断与解决
- Config 文件问题排查

**何时查阅**: 模型加载失败时

### 常见错误处理

**文件**: `docs/archive/troubleshooting/common-errors.md`

**内容摘要**:
- DSPy 错误（InvalidSignatureError、FieldNotFoundError）
- LLM 错误（ModelNotFoundError、ContextLengthExceeded、CUDANotAvailable）
- Python 错误（ModuleNotFoundError、Circular Import）
- JSON 错误（JSONDecodeError、InvalidJSONFormat）
- Type Errors、Path Errors、FastAPI ValidationError

**何时查阅**: 遇到具体错误码时快速定位

### 测试调试指南

**文件**: `docs/archive/troubleshooting/test-debugging.md`

**内容摘要**:
- pytest 基本用法与覆盖率
- 常见测试失败调试方法
- DSPy reasoning 调试技巧
- AAA 测试结构规范

**何时查阅**: 调试测试失败或编写新测试时

## 使用原则

- AI 默认阅读本目录下的 ADR 结论文档
- 详细故障排除文档仅在遇到问题时通过本文档索引查阅
- 避免将详细调试过程直接引入 AI 上下文，以免污染
