---
name: 文档系统 Memory Bank
category: infra-rule
field: global
description: 文档系统的内存存储，目的在于给AI快速投喂上下文
date: 2026-05-03
---

# 文档系统 Memory Bank

## Part 1: Currently Working

1. 工作整体方向 - `Documentation System FOR AI` 的搭建

2. 当前具体任务 - 创建 Memory Bank 记忆系统

3. 任务的作用：让 AI 快速上手整个项目，并且通过 `Context Engineering` 获得更高质量的输出

4. 任务的工作目录：

- `docs/`

5. 任务开始时间：`2026-05-03`

6. 任务预期结束时间：`2026-05-03`

7. 任务状态：已完成

## Part 2: Context Snapshot

### 当前问题
正在优化 docs/ 的 AI 可读性，目标是将引用准确率从 60% 提升到 90%+

### 已尝试（失败）
- **完整目录结构**：维护成本太高，已废弃（见 PROJECT_OVERVIEW.md 决策）
- **动态 glob 生成**：每次都要完整扫描，性能差，已废弃

### 关键约束
- docs/ 内容会频繁变化，不适合硬编码路径
- AI 需要明确的入口指引，但不是完整清单
- 幽灵引用（不存在的文件引用）是主要问题

### 待确认
- [ ] Context Snapshot 的最佳粒度（按主题？按时间？）
- [ ] 是否需要定期清理旧 snapshot？

### 开发环境
- [ ] 使用 pyenv 管理 Python 3.11.2
