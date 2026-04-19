# test/test_clinic_selector.py
# 诊室选择智能体测试

import pytest
import dspy

from src.triager.clinic_selector import select_clinic, ClinicSelectorSignature
from src.llm.llama import LlamaCppLM
from src.llm.deepseek import DeepseekLM


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def deepseek_lm():
    try:
        llm = DeepseekLM()
        dspy.configure(lm=llm)
        yield llm
    except ValueError:
        pytest.skip("DEEPSEEK_API_KEY not available")


@pytest.fixture(scope="module")
def llama_lm():
    try:
        llm = LlamaCppLM(
            model_id="test-clinic-selector",
            model_filename="LFM2.5-1.2B-Instruct-Q4_K_M"
        )
        dspy.configure(lm=llm)
        yield llm
    except Exception as e:
        pytest.skip(f"Llama model not available: {e}")


# ============================================================================
# Test Cases
# ============================================================================

VALID_CLINICS = ["emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic"]


class TestClinicSelectorSignature:
    """验证 Signature 定义正确性"""

    def test_signature_has_required_input_fields(self):
        """验证签名包含所有必需输入字段"""
        sig_fields = ClinicSelectorSignature.model_fields
        assert "body_parts" in sig_fields, "Missing body_parts input field"
        assert "duration" in sig_fields, "Missing duration input field"
        assert "severity" in sig_fields, "Missing severity input field"
        assert "description" in sig_fields, "Missing description input field"
        assert "other_relevant_info" in sig_fields, "Missing other_relevant_info input field"

    def test_signature_has_required_output_fields(self):
        """验证签名包含所有必需输出字段"""
        sig_fields = ClinicSelectorSignature.model_fields
        assert "clinic_selection" in sig_fields, "Missing clinic_selection output field"

    def test_clinic_selection_is_output_field(self):
        """验证 clinic_selection 是 OutputField"""
        field = ClinicSelectorSignature.model_fields["clinic_selection"]
        field_type = field.json_schema_extra.get("__dspy_field_type")
        assert field_type == "output", f"clinic_selection should be an OutputField, got {field_type}"


class TestClinicSelectorWithLlama:
    """使用 Llama 本地模型测试"""

    def test_child_fever_returns_pediatric(self, llama_lm):
        """5岁儿童发烧 → pediatric_clinic"""
        result, reasoning = select_clinic(
            body_parts="全身",
            duration="2天",
            severity="轻度",
            description="5岁儿童发烧，食欲不振",
            other_relevant_info=["年龄5岁"]
        )
        assert result == "pediatric_clinic"

    def test_child_minor_injury_returns_pediatric(self, llama_lm):
        """3岁儿童手臂擦伤 → pediatric_clinic"""
        result, reasoning = select_clinic(
            body_parts="手臂",
            duration="1天",
            severity="中度",
            description="3岁儿童手臂擦伤，有轻微出血",
            other_relevant_info=["年龄3岁", "玩耍时摔倒"]
        )
        assert result == "pediatric_clinic"

    def test_severe_head_injury_returns_emergency(self, llama_lm):
        """严重头部外伤 → emergency_clinic"""
        result, reasoning = select_clinic(
            body_parts="头部",
            duration="2小时",
            severity="严重",
            description="头部受到重击，意识模糊，呕吐",
            other_relevant_info=["交通事故", "有出血"]
        )
        assert result == "emergency_clinic"

    def test_fracture_returns_surgery(self, llama_lm):
        """骨折 → surgery_clinic"""
        result, reasoning = select_clinic(
            body_parts="手臂",
            duration="3天",
            severity="中度",
            description="手臂骨折，有明显畸形",
            other_relevant_info=["摔倒受伤"]
        )
        assert result == "surgery_clinic"

    def test_respiratory_infection_returns_internal(self, llama_lm):
        """呼吸道感染 → internal_clinic"""
        result, reasoning = select_clinic(
            body_parts="胸部",
            duration="1周",
            severity="轻度",
            description="咳嗽、咳痰，轻微发热",
            other_relevant_info=["无吸烟史"]
        )
        assert result == "internal_clinic"

    def test_unclear_mild_symptoms_returns_internal(self, llama_lm):
        """轻微不明确症状 → internal_clinic"""
        result, reasoning = select_clinic(
            body_parts="不确定",
            duration="几天",
            severity="轻微",
            description="感觉不舒服，但说不清楚具体哪里不舒服",
            other_relevant_info=[]
        )
        assert result == "internal_clinic"


class TestClinicSelectorWithDeepseek:
    """使用 DeepSeek 在线模型测试"""

    def test_child_fever_returns_pediatric(self, deepseek_lm):
        """5岁儿童发烧 → pediatric_clinic"""
        result, reasoning = select_clinic(
            body_parts="全身",
            duration="2天",
            severity="轻度",
            description="5岁儿童发烧，食欲不振",
            other_relevant_info=["年龄5岁"]
        )
        assert result == "pediatric_clinic"

    def test_severe_trauma_returns_emergency_or_surgery(self, deepseek_lm):
        """严重腹痛 → emergency_clinic 或 surgery_clinic（两者都合理）"""
        result, reasoning = select_clinic(
            body_parts="腹部",
            duration="1小时",
            severity="严重",
            description="急性腹痛，伴有恶心呕吐",
            other_relevant_info=["空腹"]
        )
        assert result in ["emergency_clinic", "surgery_clinic"]

    def test_skin_infection_returns_surgery(self, deepseek_lm):
        """皮肤感染 → surgery_clinic"""
        result, reasoning = select_clinic(
            body_parts="背部",
            duration="5天",
            severity="中度",
            description="背部有个脓肿，疼痛明显",
            other_relevant_info=["糖尿病史"]
        )
        assert result == "surgery_clinic"

    def test_chronic_condition_returns_internal(self, deepseek_lm):
        """慢性病 → internal_clinic"""
        result, reasoning = select_clinic(
            body_parts="全身",
            duration="多年",
            severity="轻微",
            description="长期高血压，定期复查",
            other_relevant_info=["高血压病史"]
        )
        assert result == "internal_clinic"


class TestClinicSelectorEdgeCases:
    """边界情况测试"""

    def test_valid_clinic_selection(self, deepseek_lm):
        """验证返回值是有效诊所ID"""
        result, reasoning = select_clinic(
            body_parts="头部",
            duration="1天",
            severity="轻微",
            description="轻微头痛",
            other_relevant_info=[]
        )
        assert result in VALID_CLINICS

    def test_reasoning_is_returned(self, deepseek_lm):
        """验证返回 reasoning"""
        result, reasoning = select_clinic(
            body_parts="胸部",
            duration="3天",
            severity="中度",
            description="咳嗽伴低烧",
            other_relevant_info=["抽烟史"]
        )
        assert reasoning is not None

    def test_empty_other_relevant_info(self, deepseek_lm):
        """验证空列表处理"""
        result, reasoning = select_clinic(
            body_parts="胃部",
            duration="1周",
            severity="轻度",
            description="胃部不适，食欲下降",
            other_relevant_info=[]
        )
        assert result in VALID_CLINICS
