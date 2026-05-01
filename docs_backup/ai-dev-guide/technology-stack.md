# Technology Stack

This document explains the technology stack used in `ufc-2026-backend`.

## Core AI Framework

### DSPy (Declarative Self-Programming)

DSPy is Stanford's framework for composable LM programs. This project uses:

- **Signatures**: Declarative task definitions with `InputField` and `OutputField`
- **ChainOfThought**: Wraps signatures for interpretable reasoning
- **Modules**: Reusable building blocks like `dspy.ChainOfThought(Signature)`

```python
import dspy

class MySignature(dspy.Signature):
    """Task description"""
    input_field: str = dspy.InputField(desc="description")
    output_field: str = dspy.OutputField(desc="description")

collector = dspy.ChainOfThought(MySignature)
result = collector(instructions="...", input_field=value)
```

## Local LLM

### llama.cpp (GGUF Format)

Local inference via `llama-cpp-python` with CUDA acceleration.

- **Model format**: GGUF (quantized, e.g., Q4_K_M)
- **Config files**:
  - `*.llm.json`: llama.cpp parameters (n_gpu_layers, n_ctx, etc.)
  - `*.infer.json`: generation parameters (temperature, top_k, etc.)
- **Model loading**: `src/llm/llama.py` - `load_model(model_id, model_filename)`
- **DSPy adapter**: `LlamaCppLM` class wraps llama.cpp for DSPy compatibility

### whisper.cpp (Speech-to-Text)

C++ STT library with CUDA support, managed as a git submodule.

- **Location**: `whisper.cpp/`
- **Deployment**: See `whisper_cpp_deploy_wsl2_cuda.md`
- **Purpose**: Voice interaction support

## Cloud LLM

### litellm

Unified API for multiple LLM providers (DeepSeek, OpenAI, etc.).

- **File**: `src/llm/deepseek.py`
- **Usage**: Standard chat completion interface

## Backend

### FastAPI

Async Python web framework for API endpoints.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/route")
async def get_route(clinic_id: str):
    return {"clinic": clinic_id}
```

## Dependencies

```
# AI/LLM
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

## Development Tools

- **Testing**: pytest with `--cov=src` for coverage
- **Logging**: Custom `src/logger.py` with colored output
- **Type checking**: Pydantic for runtime validation
