---
name: 文档系统规则
category: infra-rule
field: global
description: 定义文档元数据标准与修改要求
date: 2026-05-02
---

# 文档系统规则

**状态**: 已通过
**更新**: 2026-05-02

---

## 元数据标准

所有 `docs/` 下的文档**必须**在文件头部声明 YAML frontmatter：

```markdown
---
name: 文档标题
category: 文档类型
field: 作用域
description: 简短描述
date: YYYY-MM-DD
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 文档标题，**不一定与文件名相同** |
| `category` | 是 | 文档类型，描述文档本身是什么 |
| `field` | 是 | 作用域，声明本文件生效/引用的工作领域 |
| `description` | 是 | 一句话简短概括 |
| `date` | 是 | 最后更新日期，**修改内容后必须同步更新** |

### Category 定义（文档类型）

| category | 含义 | 适用文档 |
|----------|------|----------|
| `infra-rule` | 文档系统基础设施规则 | `docs/RULE.md` |
| `policy` | 操作规程/约束性规则 | `changelog/RULE.md`、`rule/SECURITY.md` |
| `adr` | 架构决策记录 | `decisions/adr-*.md`、`changelog/00x_*.md` |
| `guide` | 操作指南与教程 | `ai-dev-guide/quick-start.md` |
| `reference` | 技术参考手册 | 待定 |
| `concept` | 概念解释与项目概述 | `PROJECT_OVERVIEW.md` |

### Field 定义（作用域）

`field` 为枚举值，按需扩充：

| field | 含义 | 适用文档 |
|-------|------|----------|
| `global` | 文档系统级，任意操作前必读 | `docs/RULE.md` |
| `adr` | 架构决策相关工作 | `changelog/RULE.md`、`decisions/adr-*.md` |
| `code` | 代码编写 | `rule/code/coding_style.md` |
| `security` | 安全相关 | `rule/security.md` |
| `tts` | 语音合成相关 | `changelog/001_tts_solution.md` |
| `stt` | 语音识别相关 | 待定 |

---

## 修改要求

- 修改文档内容后**必须**同步更新 `date` 字段
- `category` 和 `field` 应与文档实际职责匹配，避免误标
- 新增 `field` 值前需确认是否符合枚举语义，优先复用现有值