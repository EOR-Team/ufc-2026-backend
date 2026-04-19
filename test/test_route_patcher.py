# test/test_route_patcher.py
# 路线修改器测试

import pytest
import dspy

from src.triager.route_patcher import (
    patch_route,
    RoutePatcherSignature,
    apply_patches,
    AVAILABLE_LOCATIONS,
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
            model_id="test-route-patcher",
            model_filename="LFM2.5-1.2B-Instruct-Q4_K_M"
        )
        dspy.configure(lm=llm)
        yield llm
    except Exception as e:
        pytest.skip(f"Llama model not available: {e}")


# ============================================================================
# Test Cases
# ============================================================================

DEFAULT_ROUTE = ["entrance", "registration_center", "surgery_clinic", "payment_center", "pharmacy", "quit"]


class TestRoutePatcherSignature:
    """验证 Signature 定义正确性"""

    def test_signature_has_required_input_fields(self):
        """验证签名包含所有必需输入字段"""
        sig_fields = RoutePatcherSignature.model_fields
        assert "destination_clinic_id" in sig_fields
        assert "requirement_summary" in sig_fields
        assert "current_route" in sig_fields

    def test_signature_has_required_output_fields(self):
        """验证签名包含所有必需输出字段"""
        sig_fields = RoutePatcherSignature.model_fields
        assert "patches" in sig_fields


class TestApplyPatches:
    """测试 apply_patches 函数"""

    def test_empty_patches_returns_original_route(self):
        """空 patches 应返回原路线"""
        route = ["entrance", "registration_center", "quit"]
        result = apply_patches(route, [])
        assert result == route

    def test_insert_location_middle(self):
        """在中间位置插入"""
        route = ["entrance", "registration_center", "surgery_clinic", "quit"]
        patches = [
            {"type": "insert", "previous": "registration_center", "this": "toilet", "next": "surgery_clinic"}
        ]
        result = apply_patches(route, patches)
        assert "toilet" in result
        idx_reg = result.index("registration_center")
        idx_toilet = result.index("toilet")
        assert idx_toilet == idx_reg + 1

    def test_insert_location_append(self):
        """插入到末尾（next 为 None）"""
        route = ["entrance", "registration_center", "quit"]
        patches = [
            {"type": "insert", "previous": "registration_center", "this": "toilet"}
        ]
        result = apply_patches(route, patches)
        assert "toilet" in result
        idx_reg = result.index("registration_center")
        idx_toilet = result.index("toilet")
        assert idx_toilet == idx_reg + 1

    def test_delete_location(self):
        """删除中间节点"""
        route = ["entrance", "registration_center", "surgery_clinic", "quit"]
        patches = [
            {"type": "delete", "previous": "registration_center", "this": "surgery_clinic", "next": "payment_center"}
        ]
        result = apply_patches(route, patches)
        assert "surgery_clinic" not in result
        assert "registration_center" in result

    def test_clinic_replacement(self):
        """诊室替换: surgery_clinic → internal_clinic"""
        route = ["entrance", "registration_center", "surgery_clinic", "payment_center", "quit"]
        patches = [
            {"type": "delete", "previous": "registration_center", "this": "surgery_clinic", "next": "payment_center"},
            {"type": "insert", "previous": "registration_center", "this": "internal_clinic", "next": "payment_center"}
        ]
        result = apply_patches(route, patches)
        assert "internal_clinic" in result
        assert "surgery_clinic" not in result


class TestRoutePatcherWithLlama:
    """使用 Llama 本地模型测试"""

    def test_no_modification_needed(self, llama_lm):
        """无修改需求 - 保持原路线"""
        result, patches = patch_route(
            destination_clinic_id="surgery_clinic",
            requirement_summary=[],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        assert len(result) > 0

    def test_insert_toilet_before_doctor(self, llama_lm):
        """看病前去洗手间"""
        result, patches = patch_route(
            destination_clinic_id="surgery_clinic",
            requirement_summary=[{"when": "给医生看病前", "what": "去洗手间"}],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        has_restroom = "toilet" in result or "restroom" in result
        assert has_restroom, f"Expected toilet or restroom in result, got: {result}"
        assert "surgery_clinic" in result

    @pytest.mark.skip(reason="Llama 1.2B model lacks capability for clinic replacement tasks")
    def test_clinic_replacement_surgery_to_internal(self, llama_lm):
        """诊室替换: surgery_clinic → internal_clinic"""
        result, patches = patch_route(
            destination_clinic_id="internal_clinic",
            requirement_summary=[],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        assert "internal_clinic" in result
        assert "surgery_clinic" not in result


class TestRoutePatcherWithDeepseek:
    """使用 DeepSeek 在线模型测试"""

    def test_insert_toilet_now(self, deepseek_lm):
        """现在去洗手间 - 插入到 entrance 后"""
        result, patches = patch_route(
            destination_clinic_id="surgery_clinic",
            requirement_summary=[{"when": "现在", "what": "去洗手间"}],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        has_restroom = "toilet" in result or "restroom" in result
        assert has_restroom, f"Expected toilet or restroom in result, got: {result}"
        idx_entrance = result.index("entrance")
        idx_restroom = result.index("toilet") if "toilet" in result else result.index("restroom")
        assert idx_restroom == idx_entrance + 1

    def test_insert_after_pharmacy(self, deepseek_lm):
        """拿完药之后去洗手间"""
        result, patches = patch_route(
            destination_clinic_id="surgery_clinic",
            requirement_summary=[{"when": "拿完药之后", "what": "去洗手间"}],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        has_restroom = "toilet" in result or "restroom" in result
        assert has_restroom, f"Expected toilet or restroom in result, got: {result}"
        idx_pharmacy = result.index("pharmacy")
        idx_restroom = result.index("toilet") if "toilet" in result else result.index("restroom")
        assert idx_restroom == idx_pharmacy + 1

    def test_clinic_replacement_surgery_to_pediatric(self, deepseek_lm):
        """诊室替换: surgery_clinic → pediatric_clinic"""
        result, patches = patch_route(
            destination_clinic_id="pediatric_clinic",
            requirement_summary=[],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        assert "pediatric_clinic" in result
        assert "surgery_clinic" not in result

    def test_combined_requirements(self, deepseek_lm):
        """组合需求: 看病前 + 拿药后"""
        result, patches = patch_route(
            destination_clinic_id="internal_clinic",
            requirement_summary=[
                {"when": "给医生看病前", "what": "去洗手间"},
                {"when": "拿完药之后", "what": "打印报告"}
            ],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        has_restroom = "toilet" in result or "restroom" in result
        assert has_restroom, f"Expected toilet or restroom in result, got: {result}"
        # 模型可能用 print_shop 或其他相关名称
        has_print = "print_shop" in result or any("print" in loc for loc in result)
        assert has_print, f"Expected print_shop or related in result, got: {result}"
        assert "internal_clinic" in result


class TestRoutePatcherEdgeCases:
    """边界情况测试"""

    def test_empty_route(self, deepseek_lm):
        """空路线"""
        result, patches = patch_route(
            destination_clinic_id="surgery_clinic",
            requirement_summary=[],
            origin_route=["entrance", "quit"]
        )
        assert isinstance(result, list)

    def test_multiple_insertions(self, deepseek_lm):
        """多个插入需求"""
        result, patches = patch_route(
            destination_clinic_id="surgery_clinic",
            requirement_summary=[
                {"when": "现在", "what": "去洗手间"},
                {"when": "给医生看病前", "what": "打印报告"}
            ],
            origin_route=DEFAULT_ROUTE.copy()
        )
        assert isinstance(result, list)
        assert len(result) >= len(DEFAULT_ROUTE)
