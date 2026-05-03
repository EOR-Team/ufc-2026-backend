# TTS 方案对比调研报告

> 调研时间：2026-04-25
> 目标硬件：Raspberry Pi 4B 4GB + Coral TPU

---

## 方案对比

| 方案 | 本地/云端 | 内存占用 | 中文支持 | 质量 | Coral TPU | 结论 |
|------|-----------|----------|----------|------|-----------|------|
| **Piper TTS** | 本地 | < 1GB | ✅ 单一音色 | 中等 | ❌ 不支持 | **推荐** |
| **espeak-ng** | 本地 | < 50MB | ✅ 机械音 | 差 | ❌ 不支持 | 仅极简场景 |
| **EdgeTTS** | 云端 | - | ✅ 优秀 | 高 | - | 需联网 |
| **Coqui XTTS v2** | 本地 | ~4GB VRAM | ✅ 优秀 | 高 | ❌ 不支持 | 需 GPU |
| **OpenAI TTS** | 云端 | - | ✅ 优秀 | 高 | - | 需联网 |

---

## 各方案详细说明

### 1. Piper TTS ✅ 推荐

- **定位**：专为树莓派优化的本地神经网络 TTS
- **模型**：VITS，ONNX 量化格式
- **中文**：仅 `huayan` 一个音色
- **内存**：< 1GB
- **性能**：medium 模型约 3-5x 实时
- **部署**：二进制包 或 pip，一键安装

### 2. espeak-ng

- **定位**：超轻量 formant 合成
- **中文**：支持但机械感强
- **内存**：< 50MB
- **适用**：仅需要"能出声"的极简场景

### 3. EdgeTTS

- **定位**：微软 Azure TTS API 的 Python 封装
- **本质**：云端服务，必须联网
- **质量**：高
- **结论**：不适合离线边缘部署

### 4. Coqui XTTS v2

- **定位**：高质量神经网络 TTS，支持语音克隆
- **内存**：需要 ~4GB VRAM
- **ARM CPU**：实测"very slow"，几乎不可用
- **结论**：仅适合高配 GPU 环境

### 5. Coral TPU 与 TTS 的兼容性

**结论**：Coral TPU 无法加速任何 TTS 工作负载。

原因：
- Coral TPU 是 CNN 专用加速器（Edge TPU ASIC）
- TTS 模型使用 RNN/Transformer 架构（VITS、FastSpeech2 等）
- 硬件架构层面的不匹配

**建议**：Coral TPU 用于视觉任务，不要用于 TTS。

---

## 最终推荐

| 场景 | 推荐方案 |
|------|----------|
| **本地离线 + 中文 + 树莓派 4B** | Piper TTS |
| **极简场景，能出声就行** | espeak-ng |
| **中文高质量（可联网）** | Azure/Google/阿里云 TTS API |
| **真正本地高质量（换硬件）** | Jetson Orin Nano（6GB VRAM 可跑 XTTS v2） |
