# Project Overview

This document establishes the "worldview" for AI assistants before they begin any task in `ufc-2026-backend`. If the worldview is wrong, everything built afterwards will drift further from the target.

## 1. What This Project Does

**UFC 2026 Backend** is a hospital navigation and intelligent triage system backend. It provides:

| Capability | Description |
|-----------|-------------|
| **Voice Interaction** | STT (Whisper) + TTS (Piper) for voice input/output |
| **Clinic Selection** | AI agent selects appropriate clinic based on patient symptoms |
| **Route Planning** | Generates/modifies hospital navigation routes based on destination and user requirements like "现在去洗手间" (go to toilet now) or "看病前" (before seeing doctor) |
| **Robot Control** | `/car/*` API endpoints for chassis movement control |

### Core User Flow

```
User (Voice) → STT → LLM Reasoning → Route Patcher → Car Control → TTS → User
                      ↓
               Map + Dijkstra Pathfinder
```

## 2. Project Boundaries

| Boundary | Description |
|----------|-------------|
| **In Scope** | Single-robot indoor navigation, voice consultation, LLM reasoning (local/cloud) |
| **Out of Scope** | Multi-robot coordination, real-time map updates, sensor fusion |
| **External Dependencies** | whisper.cpp (speech), llama.cpp (local LLM), DeepSeek API (cloud LLM) |
| **Output Form** | REST API + audio files. No frontend or mobile components |

### What This Project Is NOT

- Not a general-purpose chatbot
- Not a map rendering system
- Not a real-time tracking system
- Not a medical diagnosis system (only provides location/route advice)

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **AI Framework** | DSPy | Signature-based task definition, ChainOfThought reasoning |
| **Local LLM** | llama-cpp-python + GGUF (Q4 quantized) | Offline inference with CUDA acceleration |
| **Cloud LLM** | DeepSeek API (via litellm) | Online inference when local GPU unavailable |
| **STT** | whisper.cpp | Speech-to-text with CUDA support |
| **TTS** | Piper | Text-to-speech with RNN-T models |
| **Backend** | FastAPI + uvicorn + Pydantic | REST API + runtime type validation |
| **Testing** | pytest + pytest-cov | Unit/integration tests with 80%+ coverage |

### Key Libraries

```
# AI / LLM
dspy
litellm
llama-cpp-python

# Backend
fastapi
uvicorn
pydantic

# Utils
python-dotenv
```

## 4. Directory Structure

```
ufc-2026-backend/
├── src/                    # Business code
│   ├── main.py            # FastAPI entry point, lifespan management (whisper-server, LLM config)
│   ├── logger.py         # Colored logging utility (info, debug, error)
│   ├── utils.py          # Result type, ROOT_DIR constant
│   │
│   ├── map/              # Hospital map module
│   │   ├── map.json      # Node/edge graph data (lazy-loaded)
│   │   ├── typedef.py    # Pydantic models: Node, Edge, Map
│   │   ├── tools.py      # get_map() with module-level cache
│   │   ├── routes.py     # /map/* API endpoints
│   │   └── __init__.py
│   │
│   ├── car/               # Robot chassis control (mock/logging)
│   │   ├── control.py    # forward, backward, turn, stop
│   │   ├── adapter.py    # Hardware adapter interface
│   │   ├── routes.py     # /car/* API endpoints
│   │   └── __init__.py
│   │
│   ├── triager/           # Triage + route modification agents
│   │   ├── route_patcher.py  # DSPy CoT for route modification
│   │   ├── routing.py    # Main triage router
│   │   ├── clinic_selector.py
│   │   ├── condition_collector.py
│   │   ├── requirement_collector.py
│   │   └── __init__.py
│   │
│   ├── voice/             # Speech modules
│   │   ├── stt.py         # STT router
│   │   ├── tts.py         # TTS router
│   │   ├── whisper_manager.py  # whisper.cpp lifecycle
│   │   └── piper_tts_service.py
│   │
│   └── llm/               # LLM adapters
│       ├── llama.py       # llama.cpp wrapper + DSPy LM adapter
│       ├── deepseek.py    # DeepSeek API integration
│       └── __init__.py
│
├── test/                   # pytest tests (80%+ coverage required)
│   ├── test_route_patcher.py
│   ├── test_clinic_selector.py
│   ├── test_condition_collector.py
│   ├── test_requirement_collector.py
│   ├── test_medical_care.py
│   └── ...
│
├── docs/                   # AI-friendly development documentation
│   ├── ai-dev-guide/
│   │   ├── PROJECT_OVERVIEW.md  # This file
│   │   ├── project-structure.md  # (To be updated)
│   │   ├── quick-start.md
│   │   └── technology-stack.md  # (To be updated)
│   ├── dspy-patterns/       # DSPy patterns guide
│   ├── project-conventions/ # Coding standards
│   └── troubleshooting/     # Common issues guide
│
├── model/                  # LLM model files + configs
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.llm.json
│   └── LFM2.5-1.2B-Instruct-Q4_K_M.infer.json
│
├── tech_docs/              # Third-party library documentation
├── openspec/               # OpenSpec config-driven development
├── piper/                  # Piper TTS models
├── outputs/                # Generated output files (TTS audio, etc.)
└── whisper.cpp/            # C++ STT library (git submodule)
```

### Key Entry Points

#### Main Application
- **File**: `src/main.py`
- **Purpose**: FastAPI app with lifespan management, CORS, router registration

#### Map Module (`src/map/`)
```python
from src.map import get_map

map_data = get_map()
main_ids = map_data.get_main_node_ids()        # Get all main node IDs
info = map_data.get_main_node_info()           # {node_id: {name, description}}
path = map_data.dijkstra("entrance", "surgery_clinic")  # Returns node ID list
```

#### Route Patcher (`src/triager/route_patcher.py`)
```python
from src.triager.route_patcher import patch_route

# Returns modified route based on requirements
result = patch_route(
    destination_clinic_id="surgery_clinic",
    requirement_summary=[{"when": "现在", "what": "去洗手间"}],
    origin_route=["entrance", "registration_center", "surgery_clinic", "quit"]
)
```

#### Car Control (`src/car/`)
```python
from src.car.control import forward, backward, turn, stop

forward(1.5)   # Move forward 1.5 meters
turn(90)       # Turn right 90 degrees
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Python modules | lowercase + underscores | `clinic_selector.py` |
| Agent modules | noun describing function | `route_patcher.py`, not `patch_route.py` |
| Test files | `test_<module_name>.py` | `test_route_patcher.py` |
| DSPy Signatures | PascalCase with Signature suffix | `RoutePatcherSignature` |
| DSPy CoT classes | PascalCase with Cot suffix | `RoutePatcherCot` |

## Map Data Structure

The hospital map (`src/map/map.json`) uses a node-edge graph:

### Node Types

| Type | Meaning | Examples |
|------|---------|----------|
| `main` | Actual locations patients visit | `entrance`, `surgery_clinic`, `toilet` |
| `nav` | Navigation waypoints (intersections) | `crossroad1`, `crossroad2` |

### Edge Cost

- **Default cost**: Manhattan distance (`|x1-x2| + |y1-y2|`)
- Edge costs are computed lazily on first `get_map()` call

### Default Route Generation

When `origin_route` is not provided, `patch_route()` generates a default route:
- Selects all `main` nodes from map.json
- Sorts by `(y, x)` coordinates (top-to-bottom, left-to-right)
- Takes first 6 nodes as the standard visit order

---

## Status: Incomplete

This overview will be expanded with:
- **Platform/Module Status**: Completion status, known limitations per module
- **Architecture & Runtime Constraints**: API availability, pure function requirements, cross-runtime differences
- **Coding Conventions**: Naming rules, function boundaries, error handling patterns