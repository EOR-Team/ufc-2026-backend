# Change Record

> 记录项目所有实质性修改，按时间倒序排列。

---

## 2026-05-13

### 1. 本地 LLM 模型替换: Qwen2.5-2B → Qwen3.5-0.8B

- **作者**: Claude Opus 4.7 (n1ghts4kura 请求)
- **类型**: 模型升级
- **文件**:
  - `model/Qwen3.5-0.8B-Q4_K_M.gguf` — 新增，从 HuggingFace `unsloth/Qwen3.5-0.8B-GGUF` 下载
  - `model/Qwen3.5-0.8B-Q4_K_M.llm.json` — 新增，模型加载配置
  - `model/Qwen3.5-0.8B-Q4_K_M.infer.json` — 新增，推理参数配置
  - `src/main.py:51` — 修改 `model_filename` 引用

### 2. 本地 LLM CPU 推理加速优化

- **作者**: Claude Opus 4.7 (n1ghts4kura 请求)
- **类型**: 性能优化
- **文件**:
  - `model/Qwen3.5-0.8B-Q4_K_M.llm.json` — n_threads 4→5, 新增 n_threads_batch/n_batch/use_mlock/use_mmap/type_k/type_v
  - `src/llm/llama.py:107-112` — 新增模型 warmup 推理
  - AVX2 重编译经验证不需要 — 当前 llama-cpp-python 0.3.23 已启用 AVX2/FMA/F16C/OpenMP/BMI2

### 3. Triager 指令精简 + DSPy max_tokens 限制

- **作者**: Claude Opus 4.7 (n1ghts4kura 请求)
- **类型**: 性能优化
- **摘要**: 将所有 triager 模块的 `instructions=` 字符串压缩约 50%，并为每个 collector() 调用添加 `max_tokens` 参数尽早停止生成。
- **文件**:
  - `src/triager/clinic_selector.py:80-81` — 指令中文化 + `max_tokens=20`
  - `src/triager/condition_collector.py:90-91` — 指令精简 + `max_tokens=500`（首次 150，后调整为 500）
  - `src/triager/requirement_collector.py:79-80` — 指令结构化 + `max_tokens=250`（首次 100，后调整为 250）
  - `src/triager/route_patcher.py:153-154` — 指令中文化 + `max_tokens=400`（首次 200，后调整为 400）

### 4. KV Cache Q8_0 移除 & max_tokens 调优 (修复)

- **日期**: 2026-05-14
- **作者**: Claude Opus 4.7
- **类型**: 问题修复
- **原因**: 
  - `type_k`/`type_v` 需要整数类型，初始配置使用了字符串 "q8_0" 导致启动崩溃
  - 修正为整数 8 后，Q8_0 KV cache 量化导致 0.8B 小模型输出质量严重下降，CoT 推理 trace 极其冗长（千级 token），耗时 40-60 分钟
  - `max_tokens=150` 不足以覆盖 CoT 推理 + 多字段 JSON 输出，导致 JSON 截断 → 解析失败 → 返回默认值
- **修复**:
  - `model/Qwen3.5-0.8B-Q4_K_M.llm.json` — 移除 `type_k`/`type_v`，恢复默认 fp16 KV cache
  - `src/triager/condition_collector.py` — max_tokens 150→500 + 指令加"简洁输出"
  - `src/triager/requirement_collector.py` — max_tokens 100→250 + 指令加"简洁输出"
  - `src/triager/route_patcher.py` — max_tokens 200→400 + 指令加"简洁"

### 5. 测试结果 (2026-05-14)

| Endpoint | 耗时 | 结果 |
|----------|------|------|
| `/triager/select_clinic` | ~15s | ✅ internal_clinic |
| `/triager/collect_condition` | ~24s | ✅ 正确提取症状字段 |
| `/triager/collect_requirement` | ~12s | ✅ 返回需求列表 |
| `/triager/patch_route` | ~13s | ✅ 路线已修改 |
