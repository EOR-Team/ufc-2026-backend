---
name: 项目概览
category: concept
field: global
description: AI 助手在项目中建立世界观的基准文档
date: 2026-05-02
---

# 项目概览

本文档为 AI 助手在 `ufc-2026-backend` 项目中执行任何任务前建立的"世界观"。如果世界观不正确，后续所有构建都会偏离目标。

## 1. 项目做什么

**UFC 2026 Backend** 是一个医院导航与智能分诊系统后端，提供：

| 能力 | 描述 |
|------|------|
| **语音交互** | STT (Whisper) + TTS (Piper) 实现语音输入输出 |
| **诊室选择** | AI Agent 根据患者症状选择合适诊室 |
| **路线规划** | 根据目的地和用户需求（如"现在去洗手间"、"看病前"）生成/修改医院导航路线 |
| **机器人控制** | `/car/*` API 接口实现底盘运动控制 |

### 核心用户流程

```
用户（语音）→ STT → LLM 推理 → Route Patcher → 车辆控制 → TTS → 用户
                     ↓
              Map + Dijkstra Pathfinder
```

## 2. 项目边界

| 边界 | 描述 |
|------|------|
| **范围内** | 单机器人室内导航、语音咨询、本地/云端 LLM 推理 |
| **范围外** | 多机器人协作、实时地图更新、传感器融合 |
| **外部依赖** | whisper.cpp（语音）、llama.cpp（本地 LLM）、DeepSeek API（云端 LLM） |
| **输出形式** | REST API + 音频文件。无前端或移动端组件 |

### 这个项目不是什么

- 不是通用聊天机器人
- 不是地图渲染系统
- 不是实时追踪系统
- 不是医疗诊断系统（仅提供位置/路线建议）

## 3. 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **AI 框架** | DSPy | 基于 Signature 的任务定义，ChainOfThought 推理 |
| **本地 LLM** | llama-cpp-python + GGUF（Q4 量化） | CUDA 加速的离线推理 |
| **云端 LLM** | DeepSeek API（通过 litellm） | 本地 GPU 不可用时的在线推理 |
| **STT** | whisper.cpp | 支持 CUDA 的语音转文字 |
| **TTS** | Piper | 使用 RNN-T 模型实现文字转语音 |
| **后端** | FastAPI + uvicorn + Pydantic | REST API + 运行时类型验证 |
| **测试** | pytest + pytest-cov | 80%+ 覆盖率的单元/集成测试 |

### 核心依赖

```
# AI / LLM
dspy
litellm
llama-cpp-python

# 后端
fastapi
uvicorn
pydantic

# 工具
python-dotenv
```

## 4. 目录结构

```
ufc-2026-backend/
├── src/                    # 业务代码
│   ├── main.py            # FastAPI 入口，lifespan 管理（whisper-server, LLM 配置）
│   ├── logger.py         # 彩色日志工具（info, debug, error）
│   ├── utils.py          # Result 类型、ROOT_DIR 常量
│   │
│   ├── map/              # 医院地图模块
│   │   ├── map.json      # 节点/边图数据（惰性加载）
│   │   ├── typedef.py    # Pydantic 模型：Node, Edge, Map
│   │   ├── tools.py      # get_map() 带模块级缓存
│   │   ├── routes.py     # /map/* API 端点
│   │   └── __init__.py
│   │
│   ├── car/               # 机器人底盘控制（mock/logging）
│   │   ├── control.py    # forward, backward, turn, stop
│   │   ├── adapter.py    # 硬件适配器接口
│   │   ├── routes.py     # /car/* API 端点
│   │   └── __init__.py
│   │
│   ├── triager/           # 分诊 + 路线修改 Agent
│   │   ├── route_patcher.py  # DSPy CoT 路线修改
│   │   ├── routing.py    # 主分诊路由器
│   │   ├── clinic_selector.py
│   │   ├── condition_collector.py
│   │   ├── requirement_collector.py
│   │   └── __init__.py
│   │
│   ├── voice/             # 语音模块
│   │   ├── stt.py         # STT 路由器
│   │   ├── tts.py         # TTS 路由器
│   │   ├── whisper_manager.py  # whisper.cpp 生命周期管理
│   │   └── piper_tts_service.py
│   │
│   └── llm/               # LLM 适配器
│       ├── llama.py       # llama.cpp 封装 + DSPy LM 适配器
│       ├── deepseek.py    # DeepSeek API 集成
│       └── __init__.py
│
├── test/                   # pytest 测试（要求 80%+ 覆盖率）
│   ├── test_route_patcher.py
│   ├── test_clinic_selector.py
│   ├── test_condition_collector.py
│   ├── test_requirement_collector.py
│   ├── test_medical_care.py
│   └── ...
│
├── docs/                   # AI 友好的开发文档
│   ├── RULE.md            # 文档系统规则
│   ├── PROJECT_OVERVIEW.md # 本文件
│   ├── README.md          # 文档说明
│   ├── changelog/          # 架构决策记录 (ADR)
│   │   ├── RULE.md        # ADR 规范
│   │   └── 001_tts_solution.md
│   │   └── ...
│   └── rule/               # 开发规则
│       ├── SECURITY.md    # 安全规范
│       ├── TDD.md         # TDD 工作流
│       └── code/           # 代码规范
│           ├── coding_style.md
│           └── error_handling.md
│
├── model/                  # LLM 模型文件 + 配置
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.llm.json
│   └── LFM2.5-1.2B-Instruct-Q4_K_M.infer.json
│
├── tech_docs/              # 第三方库文档
├── openspec/               # OpenSpec 配置驱动开发
├── piper/                  # Piper TTS 模型
├── outputs/                # 生成的输出文件（TTS 音频等）
└── whisper.cpp/            # C++ STT 库（git 子模块）
```

### 核心入口点

#### 主应用 (`src/main.py`)

FastAPI 应用入口，负责 lifespan 管理（whisper-server、LLM 配置初始化）、CORS 配置和路由器注册。

#### 地图模块 (`src/map/`)

医院地图管理模块，提供节点查询、边权重计算和最短路径计算功能。地图数据惰性加载到内存，权重在首次调用时计算。

#### 分诊与路线修改 (`src/triager/`)

AI Agent 核心模块，负责：
- **诊室选择**：根据患者症状选择合适诊室
- **路线修改**：根据用户临时需求（如"中途去洗手间"）调整既定路线

#### 车辆控制 (`src/car/`)

机器人底盘控制模块，提供前进、后退、转向、停止等基础操作。当前实现为 mock 模式（仅记录日志），待硬件适配后替换为真实控制指令。

#### 语音模块 (`src/voice/`)

语音输入输出模块：
- **STT**：通过 whisper.cpp 将语音转为文字
- **TTS**：通过 Piper 将文字转为语音

#### LLM 适配器 (`src/llm/`)

统一的大语言模型接口，支持本地 llama.cpp 推理和 DeepSeek 云端 API，通过 DSPy 框架调用。

### 地图数据结构

医院地图（`src/map/map.json`）使用节点-边图结构：

| 节点类型 | 含义 | 示例 |
|----------|------|------|
| `main` | 患者实际访问的位置 | `entrance`, `surgery_clinic`, `toilet` |
| `nav` | 导航路径点（交叉口） | `crossroad1`, `crossroad2` |

边权重默认使用曼哈顿距离（`|x1-x2| + |y1-y2|`），在首次调用 `get_map()` 时惰性计算。

当未提供 `origin_route` 时，`patch_route()` 生成默认路线：按 `(y, x)` 坐标排序 map.json 中所有 `main` 节点，取前 6 个作为标准访问顺序。

---

## 状态：已稳定

此概览描述了项目的完整能力边界，已涵盖核心模块功能和安全保障要求。

### 待扩展内容

- **平台/模块状态**：各模块完成度、已知限制
- **架构与运行时约束**：纯函数要求、跨运行时差异