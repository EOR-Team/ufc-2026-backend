---
name: TDD 工作流规范
category: rule
field: code
description: 定义 RED-GREEN-REFACTOR 循环与测试编写标准
date: 2026-05-02
---

# TDD 工作流规范

**日期**: 2026-05-02
**状态**: 草稿
**适用**: Vibe Coding 模式下的 AI 自动开发

---

## 核心原则

> **铁律**: 没有失败的测试 = 没有生产代码
>
> "If you didn't watch the test fail, you don't know if it tests the right thing."

### 强制规则

**AI 在以下例外场景必须询问人类，不得自行跳过 TDD**：
- 一次性原型开发
- 配置文件创建
- 初始项目搭建

### 违反规则的代价

| 违反行为 | 处理方式 |
|----------|----------|
| 代码先于测试 | 删除所有实现代码，重新开始 RED |
| 测试立即通过 | 说明测试无效，未验证正确性 |
| "以后再添加测试" | 删除代码，从 TDD 开始 |
| 保留代码"作为参考" | 严格删除，无例外 |

---

## RED-GREEN-REFACTOR 循环（决策树）

```
START **创建五个阶段(RED, VERIFY RED, GREEN, VERIFY GREEN, REFACTOR)的TODO LIST**
  │
  ▼
RED 阶段：编写失败测试
  │ 编写最小测试，描述预期行为
  │ 测试名称必须清晰（动词+场景+预期）
  │
  ▼
VERIFY RED：运行测试，确认失败
  │ 测试必须因预期原因失败
  │ 如果测试立即通过 → 测试无效，重新写
  │
  ▼
GREEN 阶段：编写最小实现
  │ 只编写通过测试所需的最小代码
  │ 禁止：过度工程、添加测试未要求的功能
  │
  ▼
VERIFY GREEN：运行测试，确认通过
  │
  ▼
REFACTOR 阶段（如需要）
  │ 仅在测试通过后进行
  │ 删除重复、改进名称、提取辅助函数
  │ 保持所有测试仍然通过
  │
  ▼
DONE
```

### 阶段约束

**RED 阶段必须满足**：
- 测试名称不含 "and"（一次只测试一件事）
- 测试真实行为而非 mock
- 清晰的预期结果

**GREEN 阶段必须满足**：
- 最简单代码通过测试
- 不添加测试未要求的功能
- 不预测未来需求

**REFACTOR 阶段必须满足**：
- 测试必须已经通过
- 不改变代码行为
- 保持所有测试通过

---

## 触发条件

### 必须触发 TDD 的场景

- 新功能开发
- Bug 修复
- 重构
- 行为更改

### 例外场景（必须询问）

- 一次性原型
- 配置文件
- 初始项目搭建

---

## 测试编写规范

### 测试命名规则

| 好的命名 | 坏的命名 | 原因 |
|----------|----------|------|
| `test_user_login_success` | `test_login` | 具体场景 |
| `test_retries_3_times_on_failure` | `test_retry_logic` | 包含预期行为 |
| `test_returns_empty_list_when_no_results` | `test_get_data` | 包含预期结果 |
| `test_raises ValueError_on_invalid_input` | `test_error` | 包含异常预期 |

### 测试结构规范

```python
def test_xxx():
    """描述：做什么事 + 预期结果"""
    # Arrange - 准备测试数据
    input_data = ...

    # Act - 执行被测操作
    result = function_under_test(input_data)

    # Assert - 验证预期
    assert result == expected
```

### Good vs Bad 示例

**Good（清晰名称，测试真实行为）**：
```python
def test_retries_failed_operations_3_times():
    """验证重试机制在失败3次后停止"""
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("fail")
        return "success"

    result = retry_operation(operation)
    assert result == "success"
    assert attempts == 3
```

**Bad（模糊名称，测试 mock 而非真实代码）**：
```python
def test_retry_works():
    """测试重试功能 - 模糊名称，无意义"""
    mock = Mock()
    mock.return_value = "success"
    retry_operation(mock)
    assert mock.called
```

### Mock 使用规范

**允许使用 mock 的场景**：
- 外部 API 调用（如 HTTP 请求）
- 数据库连接
- 第三方服务

**禁止使用 mock 的场景**：
- 验证内部实现细节
- 测试自身模块的内部逻辑

---

## 验证清单

完成实现前，确保当前 *TODO LIST* 为空（如果不为空，询问用户是否可以清空以进行 FINAL CHECK UP），然后根据下面的标准 **创建 TODO LIST** 来辅助检查。一项一项的完成之后才能结束验收。

- [ ] 每个新函数/方法有对应测试
- [ ] 实现前运行测试并观察到失败
- [ ] 每个测试因预期原因失败
- [ ] 编写最小代码通过测试
- [ ] 所有测试通过，无错误/警告
- [ ] 代码覆盖率 >= 80%

---

## AI 行为边界

### 强制询问条款

**AI 在 Vibe Coding 模式下必须询问人类的场景**：
1. 遇到例外条款（原型、配置、初始搭建）时
2. 测试无法编写时（需求不清晰）
3. 遇到边界情况未定义时
4. 违反铁律但不确定如何处理时

**询问格式**：
```
[AI 询问] 在执行 [动作] 前，需要确认：
- 原因：[为什么需要询问]
- 选项：[可接受的选项列表]
- 建议：[AI 的推荐]
```

### 边界规则

1. **测试优先** - 所有实现必须先有失败的测试
2. **删除重写** - 如果实现代码先于测试被写，必须删除并重新开始
3. **禁止保留** - 不能将错误写的代码"保留作为参考"
4. **最小实现** - 只编写通过当前测试所需的最小代码
5. **强制验证** - "Watch it fail"是不可跳过的强制步骤

### 证据驱动哲学

```
AI: "我写了代码，应该能工作"
正确回应: "运行测试看是否失败"

不是假设正确，而是要求证据。
```

---

## 常见错误与处理

| 错误 | 处理方式 |
|------|----------|
| 测试立即通过 | 删除测试，重新编写有效测试 |
| 实现代码先于测试 | 删除所有实现代码，从 RED 开始 |
| 无法编写测试 | 询问需求澄清，不要猜测 |
| 过度工程 | 删除额外代码，只保留最小实现 |
| 测试覆盖率不足 | 增加测试用例，覆盖边界条件 |

---

## 测试文件命名规范

**格式**: `{简短标题}.py`

**规则**：
- 只允许：大小写字母、数字、下划线
- 必须以字母或下划线开头
- 不得以数字开头
- 建议使用 `test_` 前缀（单元测试）或功能描述

**有效命名**：
```
test_user_login.py
TestAuthModule.py
retry_logic_test.py
```

**无效命名**：
```
test-user-login.py    # 包含连字符
123_test.py           # 以数字开头
test login.py         # 包含空格
```

---

## 示例：完整的 TDD 流程

### 场景

需要实现一个 `retry_operation` 函数：失败重试 3 次后返回错误。

### RED 阶段

```python
# test_retry_operation.py

def test_retries_3_times_then_raises():
    """验证失败3次后抛出异常"""
    attempts = 0

    def failing_operation():
        nonlocal attempts
        attempts += 1
        raise ValueError(f"attempt {attempts}")

    try:
        retry_operation(failing_operation, max_retries=3)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "attempt 3" in str(e)
        assert attempts == 3
```

运行测试：`pytest test_retry_operation.py` → **失败** ✓

### GREEN 阶段

```python
# retry.py

def retry_operation(operation, max_retries=3):
    """执行操作，失败重试最多 max_retries 次"""
    last_error = None
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            last_error = e
            continue
    raise last_error
```

运行测试：`pytest test_retry_operation.py` → **通过** ✓

### REFACTOR 阶段

当前实现已经足够简单，无需重构。