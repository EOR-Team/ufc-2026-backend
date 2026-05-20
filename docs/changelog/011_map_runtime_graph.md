---
name: Map 模块运行时图构建重构
category: adr
field: code
description: 将 map.json 的 edges 手动维护改为运行时自动构建，并将路径→指令转换逻辑从 car/ 迁入 map/
date: 2026-05-20
---

# 011: Map 模块运行时图构建重构

**日期**: 2026-05-20
**状态**: 已通过
**决策者**: n1ghts4kura

## 背景

`src/map/` 模块重构前存在两个主要问题：

1. **手动维护 edges 负担重**：`map.json` 中每条边都需要手动定义 `{u, v, name, cost}`，地图扩展时易出错
2. **循环依赖**：`car/adapter.py` 依赖 `map`（调 `get_map()`），而 `map/routes.py` 依赖 `car/adapter.py`（调 `path_to_commands()`），形成 `car → map → car` 循环引用

约束：
- 地图是规整的网格结构（节点坐标均为整数，间距固定）
- `path_to_commands()` 本质是地图几何计算，不涉及硬件控制
- 最小改动原则

## 考虑的方案

| 方案 | 连通性保证 | 维护成本 | 解耦 car/map | 方案对比 |
|------|-----------|----------|-------------|----------|
| A: 运行时按 `\|dx\|+\|dy\|==1` 连边 + 迁入 `path_to_commands()` | 高 | 低 | 是 | **选择** |
| B: 保留手动 edges 但只迁入 `path_to_commands()` | 高 | 高 | 是 | 放弃 |
| C: 方案 A + 额外支持障碍物/禁行边 | 最高 | 中 | 是 | 过度工程 |

## 决策

**选择:** 方案 A

## 理由

1. **消除循环依赖**：删除 `car/adapter.py` 和 `car/typedef.py`，`path_to_commands()` 逻辑迁入 `map/tools.py` 作为 `get_commands()`
2. **零维护成本扩展地图**：新增节点只需在 `map.json` 中加坐标，edges 自动生成，无需手动连线
3. **向后兼容**：`Map.dijkstra()`、`get_main_node_ids()`、`get_main_node_info()` API 保持不变

## 具体变更

| 文件 | 变更 |
|------|------|
| `src/map/typedef.py` | `edges` 改为 `Field(default_factory=list)`，新增 `model_post_init` + `_build_edges()` |
| `src/map/tools.py` | 新增 `_rename_nav_nodes()`（`"road"` → `"road_{x}_{y}"`），新增 `get_commands()` 迁移自 `adapter.py`，`_compute_all_costs` 改为 no-op |
| `src/map/__init__.py` | 新增 `get_commands` 导出 |
| `src/map/routes.py` | `DELETE /map/translate` → `POST /map/commands` |
| `src/car/adapter.py` | **删除** |
| `src/car/typedef.py` | **删除** |

## 放弃的替代方案

- **方案 B**: 没解决 edges 手维问题，不选
- **方案 C**: 当前无禁行/障碍物需求，"设计给未来"违反 Simplicity First

## 后续行动

- [x] 验证 45 对 main-main 全配对 Dijkstra 可达
- [x] 34 个 car 测试全部通过
