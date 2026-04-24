# Whisper.cpp 边缘部署技术规格书

## 目标

在 **Raspberry Pi 4B 4GB** 上部署 whisper.cpp 作为 **中文语音识别（STT）** 服务，为现有 FastAPI 后端提供离线语音转文字能力。

---

## 硬件 / 环境

| 项目 | 规格 |
|------|------|
| 设备 | Raspberry Pi 4B 4GB |
| 系统 | Raspberry Pi OS 64-bit (arm64) |
| 辅助硬件 | Google Coral Edge TPU USB（用于其他图像任务，不参与 whisper.cpp） |
| Python | 3.9+（系统自带） |
| 音频预处理 | ffmpeg（转换任意格式 → 16kHz WAV） |

---

## Whisper.cpp 构建配置

| 配置项 | 值 | 说明 |
|--------|----|------|
| 模型 | `ggml-tiny`（多语言版） | ~75MB disk / ~273MB RAM |
| 量化 | **Q5_0** | 约 40MB disk / ~180MB RAM |
| ARM NEON | ✅ 启用 | 编译自动检测，1.5-2x 加速 |
| OpenBLAS | ✅ 启用 | `-DGGML_BLAS=ON`，额外 2-3x 加速 |
| FFmpeg 支持 | ✅ 启用 | `-DWHISPER_FFMPEG=yes`，支持 MP3/OGG/AAC 等格式 |
| SDL2 | ❌ 不启用 | 仅实时麦克风场景需要 |
| VAD (Silero) | ❌ 不启用 | 仅实时语音场景需要 |

**量化选 Q5_0 的原因**：
- `tiny` 模型本身已足够小，量化收益主要是降低内存峰值（~273MB → ~180MB）
- Q5_0 精度损失极小，适合中文语音识别
- 不选 Q4_0/Q4_K：中文音节复杂度高，Q4 精度损失相对明显

---

## 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Raspberry Pi 4B                          │
│                                                             │
│   ┌─────────────┐      ┌─────────────────────────────────┐ │
│   │  FastAPI    │      │  whisper-server (whisper.cpp)    │ │
│   │  Backend    │ ────►│  127.0.0.1:8080                 │ │
│   │  (本项目)   │      │                                 │ │
│   │             │◄──── │  tiny-q5_0 (ggml 模型)          │ │
│   └──────┬──────┘      │  ffmpeg 预处理                   │ │
│          │             └─────────────────────────────────┘ │
│          │                                                 │
│          │  临时文件: /tmp/whisper_*.wav                  │
└──────────┴─────────────────────────────────────────────────┘
```

**whisper-server** 是 whisper.cpp 内置的 HTTP 服务器，提供 OAI 风格的 REST API：
- POST `/inference` — 上传音频文件，转录为文字
- GET `/health` — 健康检查
- 无需自建 API 层

---

## API 接口

### 健康检查

```
GET http://127.0.0.1:8080/health
```

响应示例：
```json
{ "status": "ok" }
```

### 语音转文字

```
POST http://127.0.0.1:8080/inference
Content-Type: multipart/form-data

file: <音频文件>
```

支持的音频格式（ffmpeg 预处理）：
- MP3, OGG, AAC, FLAC, M4A, WAV 等
- ffmpeg 自动转换为 16kHz 单声道 WAV 后推理

响应示例：
```json
{
  "text": "这是一段测试音频的转录结果"
}
```

---

## STT 用途

前端上传语音文件 → FastAPI 接收 → 转发 whisper-server → 返回文字给前端。

音频文件不上传到云端，**完全在本地处理**，满足隐私和离线需求。

---

## 后端集成方式

FastAPI 与 whisper-server 部署在**同一台 Pi** 上：

| 项目 | 值 |
|------|----|
| whisper-server 绑定地址 | `127.0.0.1:8080`（仅本地访问） |
| FastAPI 调用地址 | `http://127.0.0.1:8080/inference` |
| 启动方式 | **手动** — FastAPI 启动时通过 `subprocess` 拉起 whisper-server，FastAPI 关闭时一并终止 |
| 进程管理 | FastAPI 使用 `subprocess.Popen` 管理 whisper-server 生命周期，**不依赖 systemd** |
| 自动重启 | ❌ 不需要 |

```python
# FastAPI 启动时：拉起 whisper-server
# FastAPI 关闭时：通过 subprocess 一起终止
```

---

## 文件上传处理流程

```
前端 POST /upload-audio
        │
        ▼
┌─────────────────┐
│  FastAPI 接收    │  ←  音频文件暂存 Pi 本地 /tmp
│  (本项目)        │
└────────┬────────┘
         │ ffmpeg 转换为 16kHz WAV
         ▼
┌─────────────────┐
│ whisper-server   │  ←  POST http://127.0.0.1:8080/inference
│ (whisper.cpp)   │  ←  返回 JSON { "text": "..." }
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  删除临时文件     │  ←  /tmp 下的 wav 文件自动清理
└─────────────────┘
```

---

## 安装部署步骤（清单）

- [ ] 1. 安装系统依赖（cmake, build-essential, git, libopenblas-dev, ffmpeg）
- [ ] 2. 克隆 whisper.cpp 仓库
- [ ] 3. CMake 配置（NEON + OpenBLAS + FFmpeg）
- [ ] 4. `make -j$(nproc)` 编译
- [ ] 5. 下载 `ggml-tiny.bin` 模型（多语言版，含中文）
- [ ] 6. 量化模型为 Q5_0（`./quantize models/ggml-tiny.bin models/ggml-tiny-q50.bin q5_0`）
- [ ] 7. 启动 whisper-server（指定模型路径和线程数）
- [ ] 8. 验证：上传音频文件 → 收到中文转录文字

---

## 推理参数

| 参数 | 值 | 说明 |
|------|----|------|
| 语言 | 固定中文 `--language zh` | 跳过语言检测，提升速度和准确率 |
| 线程数 | `--threads 4` | Pi4 4核 CPU |

---

## 性能预期

| 指标 | 值 |
|------|----|
| 模型加载时间 | 约 2-3 秒（首次） |
| 内存占用（运行时） | ~180-200 MB |
| 中文语音转文字延迟 | 取决于音频长度，`tiny` 模型约 0.2-0.5x 实时 |
| 音频长度 10 秒 | 处理时间约 2-5 秒 |
| 音频长度 30 秒 | 处理时间约 6-15 秒 |

---

## 限制与注意事项

1. **中文识别**：必须使用**不含 `.en` 后缀**的多语言模型，否则无法识别中文
2. **音频格式**：whisper.cpp 仅原生支持 16-bit WAV，其他格式由 ffmpeg 预处理
3. **实时性**：`tiny` 模型虽可运行，但非真正实时（RTF > 1），适合批量处理场景
4. **Coral TPU**：不参与 whisper.cpp 推理，释放 CPU 资源专注语音识别
5. **进程常驻**：建议保持 whisper-server 进程运行，避免反复加载模型的延迟
6. **线程数**：`--threads 4`（Pi4 4核 CPU），过多线程反而因内存带宽瓶颈降速
