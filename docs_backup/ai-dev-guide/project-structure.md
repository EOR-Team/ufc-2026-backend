# Project Structure

This document explains the directory structure of `ufc-2026-backend` for AI coding assistants.

## Directory Layout

```
ufc-2026-backend/
├── src/                    # Main source code
│   ├── __init__.py
│   ├── medical_care.py     # Medical advice agent entry point
│   ├── logger.py           # Colored logging utility
│   ├── utils.py            # Result type, ROOT_DIR
│   ├── llm/                # LLM integrations
│   │   ├── __init__.py
│   │   ├── llama.py        # llama.cpp wrapper + DSPy LM adapter
│   │   └── deepseek.py     # DeepSeek API integration
│   └── triager/            # Hospital navigation agents
│       ├── __init__.py
│       ├── clinic_selector.py      # Select appropriate clinic
│       ├── condition_collector.py  # Collect patient symptoms
│       ├── requirement_collector.py # Collect route requirements
│       └── route_patcher.py       # Modify hospital routes
├── test/                   # pytest unit tests
│   ├── test_clinic_selector.py
│   ├── test_condition_collector.py
│   ├── test_medical_care.py
│   ├── test_requirement_collector.py
│   ├── test_route_patcher.py
│   └── test_speed.py
├── model/                  # LLM model files + configs
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf  # ~700MB quantized model
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.llm.json
│   └── LFM2.5-1.2B-Instruct-Q4_K_M.infer.json
├── docs/                   # AI-friendly development documentation
│   ├── ai-dev-guide/       # This directory
│   ├── dspy-patterns/       # DSPy patterns guide
│   ├── project-conventions/ # Coding standards
│   └── troubleshooting/     # Common issues guide
├── tech_docs/              # Third-party library documentation (DSPy, FastAPI)
├── openspec/               # OpenSpec config-driven development
├── whisper.cpp/            # C++ STT library (git submodule)
└── docs/                   # whisper.cpp deployment guides
```

## Key Entry Points

### Medical Care Agent
- **File**: `src/medical_care.py`
- **Function**: `get_medical_care_advice(symptoms, diagnosis)`
- **Returns**: `(advice_dict, reasoning)` tuple

### Triage Agents (in `src/triager/`)
1. **ClinicSelector** - `select_clinic(body_parts, duration, severity, description, other_relevant_info)`
2. **ConditionCollector** - `collect_condition(description_from_user)`
3. **RequirementCollector** - `collect_requirement(requirement_from_user)`
4. **RoutePatcher** - `patch_route(destination_clinic_id, requirement_summary, origin_route)`

## File Naming Conventions

- Python files: lowercase with underscores (`clinic_selector.py`)
- Agent modules: noun describing function (`clinic_selector.py`, not `select_clinic.py`)
- Test files: `test_<module_name>.py`

## Configuration Files

- Model config: `model/<name>.llm.json` - llama.cpp parameters
- Inference config: `model/<name>.infer.json` - generation parameters (temperature, top_k, etc.)
