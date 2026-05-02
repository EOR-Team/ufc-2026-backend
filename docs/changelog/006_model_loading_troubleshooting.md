---
name: "006: 模型加载故障排除"
category: adr
field: code
description: 记录模型加载问题的排查过程与解决方案
date: 2026-04-24
---

# 006: 模型加载故障排除

**日期**: 2026-04-24
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

GGUF 模型加载常见问题需要标准化排查流程，以提高调试效率。

## 考虑的方案

| 方案 | 可操作性 | 覆盖面 | 结论 |
|------|----------|--------|------|
| 分散文档 | ❌ 难查 | - | 放弃 |
| 集中故障排除指南 | ✅ | ✅ | **选择** |

## 决策

**选择:** 建立集中的 GGUF 模型加载故障排除指南

## 常见问题与解决方案

### 1. Model File Not Found

```python
# 诊断
from pathlib import Path
model_path = Path("model")
print(f"Model dir exists: {model_path.exists()}")
print(f"Contents: {list(model_path.glob('*.gguf'))}")

# 解决：验证文件名匹配 config（.llm.json, .infer.json）
```

### 2. Wrong CUDA Version

```bash
# 诊断
nvcc --version
nvidia-smi

# 解决：重装 llama-cpp-python with CUDA
CMAKE_ARGS="-DGGML_CUDA=ON" pip install llama-cpp-python \
    --extra-index-url https://abetlen.github.io/llama-cpp-python-cu12/
```

### 3. Insufficient GPU Memory

解决方案：
1. 使用更小的量化模型（Q4_K_M 而非 Q8）
2. 减少 context size（n_ctx: 32768 → 8192）
3. 关闭其他 GPU 应用
4. 临时使用 CPU fallback（n_gpu_layers: 0）

### 4. Invalid Model Format

```bash
# 诊断
file model/xxx.gguf
md5sum model/xxx.gguf

# 解决：重新下载或验证 GGUF 格式
```

## 配置参考

### .llm.json (llama.cpp 参数)

```json
{
    "n_gpu_layers": 0,
    "seed": "default",
    "n_ctx": 32768,
    "n_threads": 4,
    "flash_attn": true,
    "chat_format": "chatml"
}
```

### .infer.json (生成参数)

```json
{
    "temperature": 0.1,
    "top_k": 50,
    "logit_bias": {}
}
```

## 调试工作流

1. **读取完整错误回溯** - 显示确切行号和调用栈
2. **检查错误类型** - 对照本指南快速修复
3. **启用调试日志**：`logger.setLevel(logging.DEBUG)`
4. **运行单测隔离**：`pytest test/test_file.py::test_name -vv -s`