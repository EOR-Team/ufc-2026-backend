# Whisper.cpp WSL2 CUDA 部署记录

## 环境

| 项目 | 值 |
|------|-----|
| Host OS | WSL2 (Ubuntu) |
| GPU | NVIDIA GeForce RTX 2060 6GB |
| Driver | 591.86 |
| CUDA | 13.2.51 |
| CMake | 3.28.3 |
| GCC | 13.3.0 |

## 构建步骤

### 1. 克隆仓库

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
```

### 2. 配置 CMake（CUDA 加速）

> 注意：`WHISPER_CUBLAS` 已废弃，必须使用 `GGML_CUDA`。

```bash
# 需指定 CUDA 编译器路径，否则 CMake 找不到 nvcc
CUDACXX=/usr/local/cuda/bin/nvcc \
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc
```

### 3. 编译

```bash
cmake --build build -j$(nproc)
```

### 4. 下载模型

```bash
bash ./models/download-ggml-model.sh tiny
```

### 5. 量化模型（Q5_0）

```bash
./build/bin/whisper-quantize \
  ./models/ggml-tiny.bin \
  ./models/ggml-tiny-q50.bin \
  q5_0
```

量化效果：
- 原始 tiny：144.05 MB
- Q5_0 量化后：27.94 MB（体积减少 80%）

### 6. 启动 whisper-server

```bash
./build/bin/whisper-server \
  -m ./models/ggml-tiny-q50.bin \
  --port 8080 \
  --language zh \
  --host 127.0.0.1
```

启动输出关键信息：
```
ggml_cuda_init: found 1 CUDA devices (Total VRAM: 6143 MiB):
  Device 0: NVIDIA GeForce RTX 2060, compute capability 7.5
whisper_backend_init_gpu: using CUDA0 backend
{"status":"ok"}
```

## 遇到的问题

### CMake 找不到 CUDA 编译器

**错误：**
```
CMake Error at ggml/src/ggml-cuda/CMakeLists.txt:58 (enable_language):
  No CMAKE_CUDA_COMPILER could be found.
```

**原因：** CMake 需要显式指定 `CMAKE_CUDA_COMPILER`，因为 CUDA Toolkit 安装在非标准路径。

**解决：** 手动指定 `CUDACXX` 环境变量和 `CMAKE_CUDA_COMPILER` 路径。

### WHISPER_CUBLAS 已废弃

**错误：**
```
WHISPER_CUBLAS is deprecated and will be removed in the future.
Use GGML_CUDA instead
```

**解决：** 只使用 `-DGGML_CUDA=ON`，不启用 `WHISPER_CUBLAS`。

### ffmpeg 未安装（无 sudo）

WSL2 当前环境无 sudo 权限，无法安装 `ffmpeg`。whisper.cpp 核心构建不受影响，但无法测试非 WAV 格式音频转换。**在 Raspberry Pi 部署时需安装 ffmpeg。**

## 模型量化对照（tiny）

| 量化级别 | 磁盘大小 | 内存占用 | 精度损失 |
|---------|---------|---------|---------|
| 原始 (FP16) | ~75 MB | ~273 MB | 无 |
| Q5_0 | ~28 MB | ~180 MB | 极小 |
| Q4_0 | ~22 MB | ~160 MB | 较小 |

**Q5_0 选型理由（中文语音）：**
- tiny 模型本身已足够小，量化收益主要是降低内存峰值
- Q5_0 精度损失极小，适合中文音节复杂度高的场景
- Q4 系列在中文字识别上精度损失相对明显

## 验证

### Health Check

```bash
curl http://127.0.0.1:8080/health
# {"status":"ok"}
```

### GPU 加速确认

启动日志中可见：
- `use gpu = 1`
- `CUDA0 total size = 29.30 MB`（模型已加载至 GPU）
- `backends = 2`（CPU + CUDA）

## 目录结构

```
whisper.cpp/
├── build/
│   └── bin/
│       ├── whisper-server    # HTTP API 服务
│       ├── whisper-cli       # CLI 推理工具
│       └── whisper-quantize  # 量化工具
└── models/
    ├── ggml-tiny.bin        # 原始模型 (FP16)
    └── ggml-tiny-q50.bin    # Q5_0 量化模型
```

## Pi 4B 部署差异（相对于 WSL2）

| 项目 | WSL2 (开发) | Raspberry Pi 4B (生产) |
|------|------------|----------------------|
| 加速 | CUDA (RTX 2060) | ARM NEON + OpenBLAS |
| 量化 | Q5_0 | Q5_0 |
| ffmpeg | 未安装 | 必须安装 |
| 模型路径 | 本地路径 | `/home/pi/whisper.cpp/models/` |
| 进程管理 | 手动启动 | FastAPI subprocess 管理 |

Pi 4B 构建命令（参考 tech spec）：
```bash
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_BLAS=ON \
  -DGGML_BLAS_VENDOR=OpenBLAS \
  -DWHISPER_FFMPEG=yes \
  -DGGML_NUM_THREADS=4
```
