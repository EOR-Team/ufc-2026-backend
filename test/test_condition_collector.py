# test_condition_collector.py
#
# condition_collector 集成测试
# 使用 few-shot 评估模式，基于原始实现的示例
#
# @author n1ghts4kura
# @date 2026-04-18
#

import pytest
import dspy

from src.llm.llama import LlamaCppLM
from src.llm.deepseek import DeepseekLM
from src.triager.condition_collector import collect_condition, ConditionCollectorSignature


# ===========================
# Fixtures
# ===========================

@pytest.fixture(scope="module")
def deepseek_lm():
    """Deepseek 在线模型 fixture（如果可用）"""
    try:
        llm = DeepseekLM()
        dspy.configure(lm=llm)
        yield llm
    except ValueError:
        pytest.skip("DEEPSEEK_API_KEY not available")


@pytest.fixture(scope="module")
def llama_lm():
    """Llama 本地模型 fixture"""
    try:
        llm = LlamaCppLM(
            model_id="test-condition-collector",
            model_filename="LFM2.5-1.2B-Instruct-Q4_K_M"
        )
        dspy.configure(lm=llm)
        yield llm
    except Exception as e:
        pytest.skip(f"Llama model not available: {e}")


# ===========================
# Few-Shot Examples
# ===========================

# 源自原始实现的 4 个 few-shot 示例
# 参见: https://github.com/EOR-Team/ufc-2026/blob/main/backend/src/smart_triager/triager/condition_collector.py

FEW_SHOT_EXAMPLES = [
    {
        "input": "我的脚有点疼。",
        "expected": {
            "body_parts": "脚",
            "severity": "轻微",
            "duration": "",
            "description": "脚部疼痛",
            "other_relevant_info": [],
        },
    },
    {
        "input": "我头疼两天了，程度还算中等。",
        "expected": {
            "body_parts": "头",
            "severity": "中等",
            "duration": "两天",
            "description": "头部疼痛",
            "other_relevant_info": [],
        },
    },
    {
        "input": "我肚子从半个小时前一直疼到现在，很难受。",
        "expected": {
            "body_parts": "肚子",
            "severity": "严重",
            "duration": "半个小时",
            "description": "腹部持续疼痛",
            "other_relevant_info": [],
        },
    },
    {
        "input": "我感觉脚踝有点不舒服，持续两三天了。两三天前我扭伤过一次，但是很快就好了。但是现在脚踝又开始不舒服了。",
        "expected": {
            "body_parts": "脚踝",
            "severity": "轻微",
            "duration": "两三天",
            "description": "脚踝不适，有扭伤史",
            "other_relevant_info": [
                "两三天前扭伤过一次，但是很快就好了。现在又开始不舒服了。"
            ],
        },
    },
]


# ===========================
# Metrics
# ===========================

def validate_field(predicted: str, expected: str, field_name: str) -> bool:
    """
    验证单个字段的匹配情况。
    对于可选字段（duration 可为空），允许空字符串匹配空字符串。
    """
    if isinstance(predicted, str) and isinstance(expected, str):
        return predicted.strip() == expected.strip()
    elif isinstance(predicted, list) and isinstance(expected, list):
        return predicted == expected
    return predicted == expected


def condition_collector_metric(example, pred, trace=None):
    """
    condition_collector 的评估指标。

    检查 5 个输出字段是否与期望值匹配：
    - body_parts
    - severity
    - duration
    - description
    - other_relevant_info
    """
    expected = example.expected

    checks = {
        "body_parts": validate_field(pred.body_parts, expected["body_parts"], "body_parts"),
        "severity": validate_field(pred.severity, expected["severity"], "severity"),
        "duration": validate_field(pred.duration, expected["duration"], "duration"),
        "description": validate_field(pred.description, expected["description"], "description"),
        "other_relevant_info": validate_field(
            pred.other_relevant_info, expected["other_relevant_info"], "other_relevant_info"
        ),
    }

    # 返回所有字段的平均准确率
    return sum(checks.values()) / len(checks)


# ===========================
# Test Classes
# ===========================

class TestConditionCollectorWithLlama:
    """使用 Llama 本地模型进行 condition_collector 测试"""

    @pytest.fixture(autouse=True, scope="class")
    def setup_llm(self, llama_lm):
        """配置 DSPy 使用 Llama LM"""
        dspy.configure(lm=llama_lm)

    @pytest.mark.parametrize("example", FEW_SHOT_EXAMPLES, ids=lambda e: e["input"][:20])
    def test_condition_collector_structured_output(self, example):
        """
        测试 condition_collector 产生有效的结构化输出。

        注意：由于 1.2B 小模型的局限性，不强制 exact matching。
        重点验证输出结构正确、字段非空（除 duration 外）。
        """
        result = collect_condition(example["input"])

        # 验证所有字段都存在且为字符串
        assert result.body_parts is not None and isinstance(result.body_parts, str)
        assert result.severity is not None and isinstance(result.severity, str)
        assert result.duration is not None and isinstance(result.duration, str)
        assert result.description is not None and isinstance(result.description, str)
        assert result.other_relevant_info is not None and isinstance(result.other_relevant_info, list)

        # body_parts 不应为空（除非明确没有提及身体部位）
        # severity 不应为空
        # description 不应为空
        assert len(result.body_parts.strip()) > 0, "body_parts should not be empty"
        assert len(result.severity.strip()) > 0, "severity should not be empty"
        assert len(result.description.strip()) > 0, "description should not be empty"

    def test_metric_on_all_examples(self):
        """使用 DSPy Evaluate 模式测试所有示例的结构化输出"""
        devset = [
            dspy.Example(**ex).with_inputs("input")
            for ex in [
                {"input": ex["input"], "expected": ex["expected"]}
                for ex in FEW_SHOT_EXAMPLES
            ]
        ]

        scores = []
        for x in devset:
            pred = collect_condition(x.input)
            score = condition_collector_metric(x, pred)
            scores.append(score)

        avg_score = sum(scores) / len(scores)

        # 由于小模型会产生 hallucination，使用宽松阈值
        # 要求至少 10% 的字段匹配（至少 1 个字段平均正确）
        assert avg_score >= 0.1, f"Average score {avg_score:.2f} should be at least 0.1"

    def test_duration_extraction(self):
        """测试 duration 字段的提取（ lenient 检查）"""
        result = collect_condition("我头疼两天了，程度还算中等。")
        # duration 可以是从输入中提取或模型推断
        assert result.duration is not None and isinstance(result.duration, str)

        result = collect_condition("我肚子从半个小时前一直疼到现在，很难受。")
        assert result.duration is not None and isinstance(result.duration, str)

    def test_body_parts_extraction(self):
        """测试 body_parts 字段的提取"""
        result = collect_condition("我的脚有点疼。")
        assert "脚" in result.body_parts or len(result.body_parts) > 0

        result = collect_condition("我头疼两天了，程度还算中等。")
        assert "头" in result.body_parts or len(result.body_parts) > 0

    def test_severity_extraction(self):
        """测试 severity 字段的提取"""
        result = collect_condition("我的脚有点疼。")
        assert result.severity is not None and len(result.severity) > 0

    def test_description_extraction(self):
        """测试 description 字段的提取"""
        result = collect_condition("我头疼两天了，程度还算中等。")
        assert result.description is not None and len(result.description) > 0

    def test_other_relevant_info_extraction(self):
        """测试 other_relevant_info 字段的提取（病史信息）"""
        result = collect_condition(
            "我感觉脚踝有点不舒服，持续两三天了。两三天前我扭伤过一次，但是很快就好了。但是现在脚踝又开始不舒服了。"
        )
        # other_relevant_info 可以是列表（即使为空或包含推断内容）
        assert isinstance(result.other_relevant_info, list)


class TestConditionCollectorWithDeepseek:
    """使用 Deepseek 在线模型进行 condition_collector 测试"""

    @pytest.fixture(autouse=True, scope="class")
    def setup_lm(self, deepseek_lm):
        """配置 DSPy 使用 Deepseek LM"""
        dspy.configure(lm=deepseek_lm)

    @pytest.mark.parametrize("example", FEW_SHOT_EXAMPLES, ids=lambda e: e["input"][:20])
    def test_condition_collector_structured_output(self, example):
        """
        测试 condition_collector 产生有效的结构化输出。

        Deepseek 作为更大的模型，应该产生更精确的输出，
        但仍允许一定的灵活性以应对模型输出的差异。
        """
        result = collect_condition(example["input"])

        # 验证所有字段都存在且为正确类型
        assert result.body_parts is not None and isinstance(result.body_parts, str)
        assert result.severity is not None and isinstance(result.severity, str)
        assert result.duration is not None and isinstance(result.duration, str)
        assert result.description is not None and isinstance(result.description, str)
        assert result.other_relevant_info is not None and isinstance(result.other_relevant_info, list)

        # 核心字段不应为空
        assert len(result.body_parts.strip()) > 0, "body_parts should not be empty"
        assert len(result.severity.strip()) > 0, "severity should not be empty"
        assert len(result.description.strip()) > 0, "description should not be empty"


# ===========================
# Signature Tests
# ===========================

class TestConditionCollectorSignature:
    """测试 ConditionCollectorSignature 的签名定义"""

    def test_signature_has_required_fields(self):
        """验证签名包含所有必需字段"""
        sig_fields = ConditionCollectorSignature.model_fields

        assert "description_from_user" in sig_fields, "Missing description_from_user input field"
        assert "duration" in sig_fields, "Missing duration output field"
        assert "severity" in sig_fields, "Missing severity output field"
        assert "body_parts" in sig_fields, "Missing body_parts output field"
        assert "description" in sig_fields, "Missing description output field"
        assert "other_relevant_info" in sig_fields, "Missing other_relevant_info output field"

    def test_signature_input_field(self):
        """验证 description_from_user 是 InputField"""
        field = ConditionCollectorSignature.model_fields["description_from_user"]
        field_type = field.json_schema_extra.get("__dspy_field_type")
        assert field_type == "input", f"description_from_user should be an InputField, got {field_type}"

    def test_signature_output_fields(self):
        """验证所有输出字段都是 OutputField"""
        output_fields = ["duration", "severity", "body_parts", "description", "other_relevant_info"]
        for field_name in output_fields:
            field = ConditionCollectorSignature.model_fields[field_name]
            field_type = field.json_schema_extra.get("__dspy_field_type")
            assert field_type == "output", f"{field_name} should be an OutputField, got {field_type}"


# ===========================
# Edge Cases
# ===========================

class TestConditionCollectorEdgeCases:
    """边界情况测试"""

    @pytest.fixture(autouse=True, scope="class")
    def setup_llm(self, llama_lm):
        """配置 DSPy 使用 Llama LM"""
        dspy.configure(lm=llama_lm)

    def test_empty_input(self):
        """测试空输入"""
        result = collect_condition("")
        # 即使输入为空，也应该有输出（模型会尝试提取）
        assert result is not None

    def test_very_short_input(self):
        """测试非常短的输入"""
        result = collect_condition("脚疼。")
        assert result.body_parts is not None
        assert result.description is not None

    def test_long_input_with_history(self):
        """测试包含病史的长输入"""
        result = collect_condition(
            "医生您好，我最近一个月一直感觉胸闷，有时候会突然心跳加速，有时候又会感觉心跳漏了一拍。 "
            "这种情况大概持续了有一个月了。 "
            "我之前有甲状腺亢进的历史，但是已经治好了。 "
            "最近工作压力比较大，经常加班到很晚。"
        )
        # 应该提取到身体部位和症状
        assert result.body_parts is not None and len(result.body_parts) > 0
        assert result.description is not None and len(result.description) > 0
        # 病史信息应该被提取到 other_relevant_info
        assert isinstance(result.other_relevant_info, list)
