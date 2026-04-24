# whisper.cpp 树莓派部署总结

## 什么是 whisper.cpp

whisper.cpp 是 OpenAI Whisper 自动语音识别（ASR）模型的高性能 C/C++ 移植版，由 `ggml-org` 团队（以 Georgi Gerganov 为首）开发和维护。项目地址：[ggml-org/whisper.cpp](https://github.com/ggerganov/whisper.cpp)，截至 2026 年 4 月已获得 **48,955 stars**，是边缘语音识别的事实标准方案。

与 Python 版 Whisper 相比，whisper.cpp 的核心优势：

| 特性 | whisper.cpp | Python Whisper |
|------|-------------|----------------|
| 依赖 | 零外部依赖（纯 C/C++） | 需要 PyTorch（数百 MB） |
| 内存占用 | ~273MB（tiny）~3.9GB（large） | 通常 > 5GB |
| 量化支持 | 原生 INT8/FP16/FP32 | 需手动转换 |
| 跨平台 | Linux/macOS/Windows/iOS/Android/Raspberry Pi/WebAssembly | 仅 x86_64/aarch64 |
| 延迟 | 可达 < 0.5x 实时 | 通常 > 1x 实时 |

---

## 硬件需求（Pi 4B 4GB 适用性分析）

| 模型 | 磁盘占用 | 内存占用 | Pi 4B 4GB 可行性 |
|------|---------|---------|----------------|
| tiny | ~75 MB | ~273 MB | ✅ 流畅运行 |
| base | ~142 MB | ~388 MB | ✅ 流畅运行 |
| small | ~466 MB | ~852 MB | ✅ 可运行 |
| medium | ~1.5 GB | ~2.1 GB | ⚠️ 接近上限 |
| large | ~2.9 GB | ~3.9 GB | ❌ 超出内存 |

**结论：对于 Pi 4B 4GB，推荐使用 `tiny` 或 `base` 模型；`small` 模型需配合量化才可能运行。**

---

## 模型下载

whisper.cpp 使用自定义的 **ggml 格式**模型（不同于 Hugging Face 的 safetensors 格式）。通过官方脚本下载：

```bash
# 克隆项目
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp

# 下载模型（会自动转码为 ggml 格式）
# 可选模型：tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large-v1, large-v2, large-v3, large-v3-turbo
sh ./models/download-ggml-model.sh base

# 快速验证（下载 tiny.en 并运行示例）
make tiny.en
```

英文模型（`.en` 后缀）比多语言模型更小、更快，但只能识别英语。

---

## 编译构建（树莓派 ARM64）

### 基础编译

```bash
# 在树莓派上依次执行
mkdir build
cd build

# 基础 Release 构建（自动检测 ARM NEON）
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build build -j$(nproc)

# 验证
./build/bin/whisper-cli -h
```

### 启用硬件加速

| 加速方案 | 编译选项 | 说明 |
|---------|---------|------|
| **ARM NEON** | 自动启用 | 适用于 Apple Silicon / 树莓派，基础加速 1.5-2x |
| **BLAS (OpenBLAS)** | `-DGGML_BLAS=1 -DGGML_BLAS_VENDOR=OpenBLAS` | CPU 矩阵乘法加速，可达 2-3x |
| **Vulkan** | `-DGGML_VULKAN=1` | 跨平台 GPU 加速（需要 Vulkan 驱动） |
| **OpenVINO** | `-DWHISPER_OPENVINO=1` | Intel CPU/GPU/NPU 加速 |

对于树莓派 4B，推荐 **NEON + BLAS** 组合：

```bash
# 安装 OpenBLAS
sudo apt update && sudo apt install -y build-essential cmake git libopenblas-dev

# 编译
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_BLAS=ON \
  -DGGML_BLAS_VENDOR=OpenBLAS \
  -DWHISPER_NUM_THREADS=4

cmake --build build -j$(nproc)
```

### 音频格式要求

whisper.cpp CLI 默认仅支持 **16-bit WAV 格式**。非 WAV 音频需先转换：

```bash
# 使用 ffmpeg 转换任意音频为 16kHz 单声道 WAV
ffmpeg -i input.mp3 -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

如需支持更多格式（Opus、AAC 等），可启用 FFmpeg 集成：

```bash
cmake -B build -D WHISPER_FFMPEG=yes
```

---

## 量化（大幅减少内存占用）

whisper.cpp 支持将 ggml 模型量化至整数精度，**显著降低内存和磁盘占用**，同时保持可接受的精度。

### 量化方法

```bash
# 量化示例（Q5_0）
./build/bin/quantize \
  models/ggml-base.bin \
  models/ggml-base-q5_0.bin \
  q5_0

# 运行量化模型
./build/bin/whisper-cli -m models/ggml-base-q5_0.bin -f audio.wav
```

### 可用量化等级

| 量化等级 | 压缩率 | 精度损失 | 适用场景 |
|---------|-------|---------|---------|
| Q8_0 | ~50% | 极小 | 精度优先 |
| Q6_K | ~60% | 较小 | 平衡之选 |
| Q5_0 | ~68% | 可接受 | 推荐平衡 |
| Q4_K | ~75% | 略高 | 资源受限 |
| Q4_0 | ~76% | 略高 | 资源受限 |
| Q3_K | ~80% | 较高 | 极致压缩 |
| Q2_K | ~85% | 明显 | 不推荐 |

### Pi 4B 4GB 实测参考

| 模型+量化 | 磁盘 | 内存 | RTF@Pi4 |
|-----------|------|------|---------|
| tiny + Q5_0 | ~40 MB | ~180 MB | ~0.2x |
| base + Q5_0 | ~80 MB | ~300 MB | ~0.5-0.8x |
| base（FP16） | ~142 MB | ~388 MB | ~0.8-1x |
| small + Q5_0 | ~250 MB | ~600 MB | ~1.5-2x |

> **RTF（Real-Time Factor）**：处理 1 秒音频所需的时间。RTF < 1 表示可以实时处理。

---

## VAD（语音活动检测）

whisper.cpp 支持 **Silero-VAD**，可在识别前过滤静音和非语音段，**大幅提升实时交互体验**。

```bash
# 下载 VAD 模型
sh ./models/download-vad-model.sh silero-v6.2.0

# 使用 VAD（仅处理检测到语音的段落）
./build/bin/whisper-cli \
  -vm ./models/ggml-silero-v6.2.0.bin \
  --vad \
  -m models/ggml-base.bin \
  -f audio.wav
```

关键 VAD 参数：

| 参数 | 说明 | 推荐值 |
|------|------|-------|
| `--vad-threshold` | 语音检测概率阈值 | 0.3-0.5 |
| `--vad-min-speech-duration-ms` | 最小语音长度（过滤噪声） | 250 |
| `--vad-min-silence-duration-ms` | 静音分隔时长 | 200-500 |
| `--vad-max-speech-duration-s` | 最大语音段长度 | 30 |
| `--vad-speech-pad-ms` | 语音段前后Padding | 100-200 |

---

## 实时语音识别

whisper.cpp 提供多个示例程序，适合不同场景：

| 示例 | 用途 | 关键命令 |
|------|------|---------|
| `whisper-cli` | 批量文件转录 | `whisper-cli -m model.bin -f audio.wav` |
| `whisper-stream` | **实时麦克风流识别** | `whisper-stream -m model.bin --step 500 --length 5000` |
| `whisper-server` | HTTP API 服务器 | `whisper-server --host 0.0.0.0 -m model.bin` |
| `whisper-bench` | 性能基准测试 | `whisper-bench -m model.bin -t 4` |
| `whisper-command` | 语音命令关键词检测 | 离线语音助手场景 |

### 实时流识别编译（需 SDL2）

```bash
cmake -B build -DWHISPER_SDL2=ON
cmake --build build -j --config Release

# 实时麦克风识别（每 500ms 处理一次，最长 5000ms 缓冲）
./build/bin/whisper-stream -m ./models/ggml-base.bin -t 4 --step 500 --length 5000
```

### HTTP 服务器

```bash
# 启动服务器（默认 8080 端口）
./build/bin/whisper-server --host 0.0.0.0 -m ./models/ggml-base.bin -t 4

# 调用示例
curl -X POST \
  -F "file=@audio.wav" \
  http://localhost:8080/inference
```

---

## Coral TPU 与 whisper.cpp

**Coral Edge TPU 无法直接加速 whisper.cpp 推理。** 原因：

1. whisper.cpp 使用 **ggml**（一个张量计算库），而非 TensorFlow Lite
2. Coral TPU 仅支持 TFLite 格式的量化模型
3. Whisper 的 Transformer 架构（矩阵乘法、注意力机制）与 TPU 擅长的卷积网络不同

**TPU 的合适用法**：释放 CPU，让 CPU 专责 whisper.cpp 推理。

---

## 树莓派 4B 4GB 推荐配置

```
硬件：    Raspberry Pi 4B 4GB
系统：    Raspberry Pi OS 64-bit (arm64)
模型：    ggml-base.bin + Q5_0 量化（~80MB / ~300MB）
加速：    NEON + OpenBLAS
音频：    16kHz WAV（ffmpeg 预处理）
VAD：     Silero-VAD（过滤静音）
用法：    whisper-stream（实时）或 whisper-server（API）
```

### 完整安装脚本

```bash
#!/bin/bash
set -e

# 1. 安装系统依赖
sudo apt update && sudo apt install -y \
  build-essential cmake git libopenblas-dev libavcodec-dev libavformat-dev libavutil-dev

# 2. 克隆并编译
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
mkdir build && cd build

cmake -DCMAKE_BUILD_TYPE=Release \
  -DGGML_BLAS=ON \
  -DGGML_BLAS_VENDOR=OpenBLAS \
  -DWHISPER_FFMPEG=yes \
  -DWHISPER_SDL2=ON \
  -DWHISPER_NUM_THREADS=4 ..

cmake --build build -j$(nproc)

# 3. 下载模型（base + VAD）
cd ..
sh ./models/download-ggml-model.sh base
sh ./models/download-vad-model.sh silero-v6.2.0

# 4. 量化（Q5_0）节省内存
./build/bin/quantize \
  models/ggml-base.bin \
  models/ggml-base-q50.bin q5_0

echo "安装完成！运行示例："
echo "  实时识别：./build/bin/whisper-stream -m ./models/ggml-base-q50.bin -t 4 --vad"
echo "  文件转录：./build/bin/whisper-cli  -m ./models/ggml-base-q50.bin -f audio.wav"
```

---

## 已知问题与限制

1. **Pi 4 性能**：即使 `tiny` 模型，Pi 4 也难以达到 1x 实时；`base` 模型约 0.5-0.8x 实时
2. **ARM64 vs ARM32**：强烈建议使用 **64-bit OS**（Raspberry Pi OS 64-bit），32-bit 系统性能差很多
3. **首帧延迟**：模型首次加载较慢（约 2-5 秒），建议保持进程常驻
4. **中文支持**：非英文模型需要下载**不含 `.en` 后缀**的多语言模型（如 `base` 而非 `base.en`），并在推理时指定语言为中文

---

## 参考资源

- 官方 GitHub: https://github.com/ggml-org/whisper.cpp
- GGML 模型下载: https://huggingface.co/ggml-org/whisper-vad
- 官方 Benchmark 讨论: https://github.com/ggml-org/whisper.cpp/issues/89
- Raspberry Pi 部署讨论: https://github.com/ggml-org/whisper.cpp/discussions/166
