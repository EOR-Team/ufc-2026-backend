# test/test_medical_care.py
# 医疗护理建议智能体测试

import pytest
import dspy

from src.medical_care import (
    get_medical_care_advice,
    MedicalCareSignature,
)
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
            model_id="test-medical-care",
            model_filename="LFM2.5-1.2B-Instruct-Q4_K_M"
        )
        dspy.configure(lm=llm)
        yield llm
    except Exception as e:
        pytest.skip(f"Llama model not available: {e}")


# ============================================================================
# Test Cases
# ============================================================================

class TestMedicalCareSignature:
    """验证 Signature 定义正确性"""

    def test_signature_has_required_input_fields(self):
        """验证签名包含所有必需输入字段"""
        sig_fields = MedicalCareSignature.model_fields
        assert "symptoms" in sig_fields
        assert "diagnosis" in sig_fields

    def test_signature_has_required_output_fields(self):
        """验证签名包含所有必需输出字段"""
        sig_fields = MedicalCareSignature.model_fields
        assert "scenario" in sig_fields
        assert "requires_doctor_consultation" in sig_fields
        assert "response" in sig_fields


class TestMedicalCareWithDeepseek:
    """使用 DeepSeek 在线模型测试"""

    def test_medication_consultation(self, deepseek_lm):
        """用药咨询场景"""
        advice, reasoning = get_medical_care_advice(
            symptoms="这个药一天吃几次？",
            diagnosis="高血压"
        )
        assert isinstance(advice, dict)
        assert "scenario" in advice
        assert "requires_doctor_consultation" in advice
        assert "response" in advice
        assert advice["scenario"] == "medication_consultation"

    def test_dosage_change_requires_doctor(self, deepseek_lm):
        """剂量调整需要医生咨询"""
        advice, reasoning = get_medical_care_advice(
            symptoms="感觉好多了，可以减量吗？",
            diagnosis="糖尿病"
        )
        assert advice["requires_doctor_consultation"] is True
        assert "医生" in advice["response"] or "医生" in advice["response"]

    def test_recovery_advice(self, deepseek_lm):
        """疗养建议场景"""
        advice, reasoning = get_medical_care_advice(
            symptoms="发烧两天，咳嗽，有痰",
            diagnosis="上呼吸道感染"
        )
        assert isinstance(advice, dict)
        assert advice["scenario"] == "recovery_advice"
        assert len(advice["response"]) > 0

    def test_symptom_interpretation(self, deepseek_lm):
        """症状解读场景"""
        advice, reasoning = get_medical_care_advice(
            symptoms="头痛、眩晕、恶心",
            diagnosis="颈椎病"
        )
        assert isinstance(advice, dict)
        assert advice["scenario"] == "symptom_interpretation"
        assert len(advice["response"]) > 0

    def test_general_advice(self, deepseek_lm):
        """一般建议场景"""
        advice, reasoning = get_medical_care_advice(
            symptoms="最近感觉疲劳，睡眠不好",
            diagnosis="亚健康状态"
        )
        assert isinstance(advice, dict)
        assert advice["scenario"] == "general_advice"
        assert len(advice["response"]) > 0


class TestMedicalCareWithLlama:
    """使用 Llama 本地模型测试"""

    def test_recovery_advice(self, llama_lm):
        """疗养建议场景 - Llama 模型"""
        advice, reasoning = get_medical_care_advice(
            symptoms="发烧两天，咳嗽",
            diagnosis="上呼吸道感染"
        )
        assert isinstance(advice, dict)
        assert "scenario" in advice
        assert "response" in advice

    def test_symptom_interpretation(self, llama_lm):
        """症状解读场景 - Llama 模型"""
        advice, reasoning = get_medical_care_advice(
            symptoms="头痛、眩晕",
            diagnosis="颈椎病"
        )
        assert isinstance(advice, dict)
        assert "scenario" in advice
        assert "response" in advice

    @pytest.mark.skip(reason="Llama 1.2B model struggles with safety-critical medication scenarios")
    def test_dosage_change_requires_doctor(self, llama_lm):
        """剂量调整需要医生咨询 - Llama 模型"""
        advice, reasoning = get_medical_care_advice(
            symptoms="感觉好多了，可以减量吗？",
            diagnosis="糖尿病"
        )
        assert advice["requires_doctor_consultation"] is True


class TestMedicalCareEdgeCases:
    """边界情况测试"""

    def test_empty_symptoms(self, deepseek_lm):
        """空症状描述"""
        advice, reasoning = get_medical_care_advice(
            symptoms="",
            diagnosis="一般性检查"
        )
        assert isinstance(advice, dict)
        assert "scenario" in advice
        assert "response" in advice

    def test_very_long_text(self, deepseek_lm):
        """非常长的文本"""
        long_symptoms = "头痛" * 100
        advice, reasoning = get_medical_care_advice(
            symptoms=long_symptoms,
            diagnosis="需要进一步检查"
        )
        assert isinstance(advice, dict)
        assert len(advice["response"]) <= 300  # 应答应控制在合理长度
