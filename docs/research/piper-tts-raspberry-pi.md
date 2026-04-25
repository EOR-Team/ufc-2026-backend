# Piper TTS 树莓派 4B 部署调研报告

> 调研时间：2026-04-25
> 目标硬件：Raspberry Pi 4B 4GB + Coral TPU
> 结论：Piper TTS 是目前唯一适合树莓派 4B 的本地神经网络 TTS 方案

---

## 1. 技术架构

| 层级 | 技术 |
|------|------|
| **模型架构** | VITS（Variational Inference Text-to-Speech） |
| **模型格式** | ONNX（导出后量化） |
| **推理引擎** | ONNX Runtime |
| **前端** | espeak-ng（音素合成） |
| **语言绑定** | Python C extension |

> **Insight**: VITS 是一种单阶段因果模型，比两阶段模型（melgan/vocoder）延迟更低。ONNX 量化后利用 ARM NEON SIMD 指令集，在 Cortex-A72 上能获得不错的并行加速。

---

## 2. 硬件需求（树莓派 4B 4GB）

| 指标 | 要求 |
|------|------|
| **内存** | < 1GB（medium 模型实测） |
| **CPU** | ARM Cortex-A72 1.5GHz（4核） |
| **系统架构** | ARM64（32位不行） |
| **存储** | 模型约 80-150MB + 依赖 |
| **声卡** | USB DAC 或 3.5mm（可选） |

> 实测案例：有人在树莓派 5（8GB）上跑过 Pi 5 + Qwen2.5-0.5B + Piper，单次问答可控制在 10 秒内。

---

## 3. 安装部署

### 方式一：二进制包（推荐，最简单）

```bash
# 1. 下载 ARM64 二进制包
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz

# 2. 解压
tar -xvf piper_arm64.tar.gz

# 3. 验证
echo "你好世界" | ./piper --model zh_CN-huayan-medium.onnx --output_file test.wav
```

### 方式二：pip 安装（Python 项目内集成时推荐）

```bash
pip install piper-tts
```

---

## 4. 中文语音模型

| 模型 | 质量 | 下载链接 |
|------|------|----------|
| `zh_CN-huayan-x_low` | 更快、更轻 | onnx + json |
| `zh_CN-huayan-medium` | 较好音质 | onnx + json |

每个模型需要 **两个文件**：`.onnx` 模型 + `.onnx.json` 配置

```bash
# 下载 medium 模型（推荐）
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx.json
```

---

## 5. Python API 用法

```python
import wave
from piper import PiperVoice

def generate_audio(audio_path: str, text: str):
    voice = PiperVoice.load(
        "zh_CN-huayan-medium.onnx",
        "zh_CN-huayan-medium.onnx.json"
    )

    with wave.open(audio_path, 'wb') as wav_file:
        wav_file.setnchannels(1)           # 单声道
        wav_file.setsampwidth(2)           # 16-bit
        wav_file.setframerate(voice.config.sample_rate)  # 22050 Hz
        voice.synthesize(text, wav_file=wav_file)

# 调用
generate_audio("/path/to/output.wav", "你好，欢迎使用 Piper 语音合成")
```

---

## 6. 命令行用法

```bash
# 基本用法
echo "今天天气真不错" | ./piper --model zh_CN-huayan-medium.onnx --output_file output.wav

# 带语速调节（默认 1.0）
echo "测试文字" | ./piper --model zh_CN-huayan-medium.onnx --output_file output.wav --length_scale 1.2

# 直接文件输入
./piper --model zh_CN-huayan-medium.onnx --input_text_file text.txt --output_file output.wav
```

---

## 7. 系统依赖（完整列表）

```bash
# ARM64 / 树莓派 OS 64-bit
sudo apt install --no-install-recommends \
    ca-certificates \
    libatomic1 \
    libgomp1 \
    alsa-utils       # 音频输出
```

---

## 8. 部署检查清单

```
1. [ ] 确认系统是 64-bit (arm64/aarch64)
       uname -m  →  应输出 aarch64

2. [ ] 下载并解压 piper ARM64 二进制包
       wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
       tar -xvf piper_arm64.tar.gz

3. [ ] 下载中文语音模型（两个文件都要）
       zh_CN-huayan-medium.onnx
       zh_CN-huayan-medium.onnx.json

4. [ ] 安装系统依赖（espeak-ng 会打包在二进制包里）
       如遇缺失 lib：sudo apt install libatomic1 libgomp1

5. [ ] 验证
       echo "测试中文语音" | ./piper --model models/zh_CN-huayan-medium.onnx --output_file test.wav
```

---

## 9. 性能参考

| 模型质量 | 推理速度（实时率） | 内存占用 |
|----------|-------------------|----------|
| `x_low` | ~0.1x RT（非常快） | < 500MB |
| `medium` | ~0.2-0.3x RT | < 800MB |

> x_low 几乎可以实时合成，medium 在 3-5x 实时（合成 1 秒语音需要 3-5 秒），对于后台 TTS 任务完全可接受。

---

## 10. 注意事项

1. **Raspberry Pi OS 64-bit 是必须的** — 32 位系统不支持 ARM NEON 优化
2. **Coral TPU 完全用不上** — TTS 的 RNN/Transformer 架构和 Coral 的 CNN 架构不兼容
3. **模型文件路径** — `.onnx` 和 `.onnx.json` 必须在同一目录，或在加载时指定完整路径
4. **输出格式** — 仅支持 WAV（16-bit PCM），后续如需 MP3/OGG 需 FFmpeg 转码
5. **中文口音** — 目前只有 `huayan` 一个中文音色可用，没有多角色选择

---

## 11. Coral TPU 说明

Coral TPU 是 **CNN 专用加速器**（Edge TPU ASIC），适合图像分类、目标检测等 CNN 任务。

**TTS 无法利用 Coral TPU** 的原因：
- Coral TPU 优化用于 CNN（卷积神经网络）
- TTS 使用 VITS（RNN/Transformer 架构）
- 硬件架构层面的不匹配，不是软件问题

**建议**：Coral TPU 留给视觉任务（相机、缺陷检测、物体识别），不要尝试用于 TTS。

---

## 12. 相关资源

- Piper 项目：https://github.com/OHF-Voice/piper1-gpl
- 中文模型下载：https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/zh/zh_CN/huayan
- pip 包：https://pypi.org/project/piper-tts/
