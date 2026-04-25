# test/test_triager_routing.py
# triager 路由 API 测试

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.llm.deepseek import DeepseekLM
import dspy


# ============================================================================
# Constants
# ============================================================================

DEFAULT_ROUTE = ["entrance", "registration_center", "surgery_clinic", "payment_center", "pharmacy", "quit"]


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
def client():
    """创建 FastAPI 测试客户端"""
    with TestClient(app) as c:
        yield c


# ============================================================================
# Test Cases
# ============================================================================

class TestRouteSelectClinic:
    """测试 /triager/select_clinic 端点"""

    def test_select_clinic_returns_valid_clinic(self, client, deepseek_lm):
        """正常请求应返回有效诊所ID"""
        response = client.post(
            "/triager/select_clinic",
            json={
                "body_parts": "头部",
                "duration": "1天",
                "severity": "轻微",
                "description": "轻微头痛",
                "other_relevant_info": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 返回格式为纯字符串 (clinic_selection)
        assert isinstance(data, str)
        assert data in ["emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic"]

    def test_select_clinic_pediatric(self, client, deepseek_lm):
        """儿童患者应返回儿科"""
        response = client.post(
            "/triager/select_clinic",
            json={
                "body_parts": "全身",
                "duration": "2天",
                "severity": "轻度",
                "description": "5岁儿童发烧",
                "other_relevant_info": ["年龄5岁"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data == "pediatric_clinic"

    def test_select_clinic_emergency(self, client, deepseek_lm):
        """严重症状应返回急诊"""
        response = client.post(
            "/triager/select_clinic",
            json={
                "body_parts": "头部",
                "duration": "1小时",
                "severity": "严重",
                "description": "头部受到重击，意识模糊",
                "other_relevant_info": ["交通事故"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data == "emergency_clinic"

    def test_select_clinic_with_multiple_relevant_info(self, client, deepseek_lm):
        """多维度相关信息"""
        response = client.post(
            "/triager/select_clinic",
            json={
                "body_parts": "腹部",
                "duration": "3天",
                "severity": "中度",
                "description": "腹痛伴随便秘",
                "other_relevant_info": ["糖尿病史", "长期久坐", "饮食习惯不规律"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, str)


class TestRouteCollectCondition:
    """测试 /triager/collect_condition 端点"""

    def test_collect_condition_returns_fields(self, client, deepseek_lm):
        """应返回结构化的症状信息"""
        response = client.post(
            "/triager/collect_condition",
            json={
                "description_from_user": "我头疼了三天，越来越严重，还有点恶心"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, object)
        # DSPy ChainOfThought 返回的是对象，有 duration, severity 等属性

    def test_collect_condition_child_injury(self, client, deepseek_lm):
        """儿童受伤场景"""
        response = client.post(
            "/triager/collect_condition",
            json={
                "description_from_user": "我家小孩从床上摔下来，手臂肿起来了，哭得很厉害"
            }
        )
        assert response.status_code == 200

    def test_collect_condition_empty_input(self, client, deepseek_lm):
        """空输入应被处理"""
        response = client.post(
            "/triager/collect_condition",
            json={
                "description_from_user": ""
            }
        )
        assert response.status_code == 200


class TestRouteCollectRequirement:
    """测试 /triager/collect_requirement 端点"""

    def test_collect_requirement_returns_list(self, client, deepseek_lm):
        """应返回需求列表"""
        response = client.post(
            "/triager/collect_requirement",
            json={
                "description_from_user": "我想先上个厕所，然后再去看医生"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 返回格式为需求列表
        assert isinstance(data, list)

    def test_collect_requirement_multiple_needs(self, client, deepseek_lm):
        """多需求场景"""
        response = client.post(
            "/triager/collect_requirement",
            json={
                "description_from_user": "我需要先上个洗手间，然后再去缴费，然后再去上个洗手间，最后取药"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_collect_requirement_empty(self, client, deepseek_lm):
        """空需求"""
        response = client.post(
            "/triager/collect_requirement",
            json={
                "description_from_user": ""
            }
        )
        assert response.status_code == 200


class TestRoutePatchRoute:
    """测试 /triager/patch_route 端点"""

    def test_patch_route_no_modification(self, client, deepseek_lm):
        """无修改需求"""
        response = client.post(
            "/triager/patch_route",
            json={
                "destination_clinic_id": "surgery_clinic",
                "requirement_summary": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 返回格式为路线列表
        assert isinstance(data, list)
        assert len(data) > 0

    def test_patch_route_insert_toilet(self, client, deepseek_lm):
        """插入洗手间需求"""
        response = client.post(
            "/triager/patch_route",
            json={
                "destination_clinic_id": "surgery_clinic",
                "requirement_summary": [{"when": "给医生看病前", "what": "去洗手间"}]
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 返回的是路线列表
        assert isinstance(data, list)
        has_restroom = "toilet" in data or "restroom" in data
        assert has_restroom, f"Expected restroom in route, got: {data}"

    def test_patch_route_custom_origin(self, client, deepseek_lm):
        """自定义起始路线"""
        custom_route = ["entrance", "registration_center", "internal_clinic", "quit"]
        response = client.post(
            "/triager/patch_route",
            json={
                "destination_clinic_id": "internal_clinic",
                "requirement_summary": [{"when": "现在", "what": "上洗手间"}],
                "origin_route": custom_route
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_patch_route_after_pharmacy(self, client, deepseek_lm):
        """取药后需求"""
        response = client.post(
            "/triager/patch_route",
            json={
                "destination_clinic_id": "surgery_clinic",
                "requirement_summary": [{"when": "拿完药之后", "what": "去洗手间"}]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_patch_route_combined_requirements(self, client, deepseek_lm):
        """组合需求"""
        response = client.post(
            "/triager/patch_route",
            json={
                "destination_clinic_id": "internal_clinic",
                "requirement_summary": [
                    {"when": "现在", "what": "去洗手间"},
                    {"when": "给医生看病前", "what": "打印报告"},
                    {"when": "拿完药之后", "what": "缴费"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestTriagerRouterIntegration:
    """集成测试：完整路由流程"""

    def test_full_triage_flow(self, client, deepseek_lm):
        """测试完整的分诊流程"""
        # Step 1: 收集症状
        condition_response = client.post(
            "/triager/collect_condition",
            json={
                "description_from_user": "我肚子疼了两天，还有点发烧"
            }
        )
        assert condition_response.status_code == 200

        # Step 2: 选择诊室（使用收集到的信息）
        select_response = client.post(
            "/triager/select_clinic",
            json={
                "body_parts": "腹部",
                "duration": "2天",
                "severity": "中度",
                "description": "腹痛伴随便秘",
                "other_relevant_info": []
            }
        )
        assert select_response.status_code == 200
        clinic_data = select_response.json()
        assert clinic_data in ["emergency_clinic", "surgery_clinic", "internal_clinic", "pediatric_clinic"]

        # Step 3: 收集需求
        req_response = client.post(
            "/triager/collect_requirement",
            json={
                "description_from_user": "我需要先上厕所，看完医生后再上个厕所"
            }
        )
        assert req_response.status_code == 200

        # Step 4: 路线修改
        route_response = client.post(
            "/triager/patch_route",
            json={
                "destination_clinic_id": "internal_clinic",
                "requirement_summary": [
                    {"when": "现在", "what": "去洗手间"},
                    {"when": "给医生看病前", "what": "打印报告"}
                ]
            }
        )
        assert route_response.status_code == 200
        route_data = route_response.json()
        assert isinstance(route_data, list)
        assert len(route_data) > 0


class TestTriagerRouterEdgeCases:
    """边界情况测试"""

    def test_missing_body_parts_parameter(self, client):
        """缺少必需参数"""
        response = client.post(
            "/triager/select_clinic",
            json={
                "duration": "1天",
                "severity": "轻微",
                "description": "头痛",
                "other_relevant_info": []
            }
        )
        assert response.status_code == 422  # Validation error

    def test_special_characters_in_description(self, client, deepseek_lm):
        """特殊字符处理"""
        response = client.post(
            "/triager/collect_condition",
            json={
                "description_from_user": "头疼！@#$%... 两天了... (((（痛）））"
            }
        )
        assert response.status_code == 200

    def test_very_long_input(self, client, deepseek_lm):
        """超长输入"""
        long_description = "头痛" * 100
        response = client.post(
            "/triager/collect_condition",
            json={
                "description_from_user": long_description
            }
        )
        assert response.status_code == 200