# triager 节点 fallback 测试

from src.triager import clinic_selector, condition_collector, requirement_collector, route_patcher


def test_select_clinic_falls_back_to_internal_clinic(monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("model failed")

    monkeypatch.setattr(clinic_selector, "collector", raise_error)

    result = clinic_selector.select_clinic(
        body_parts="头部",
        duration="1天",
        severity="轻微",
        description="头痛",
        other_relevant_info=[]
    )

    assert result == "internal_clinic"


def test_collect_condition_falls_back_to_default_structure(monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("model failed")

    monkeypatch.setattr(condition_collector, "collector", raise_error)

    result = condition_collector.collect_condition("我头疼三天了")

    assert result == {
        "duration": "未填写",
        "severity": "未填写",
        "body_parts": "未填写",
        "description": "未填写",
        "other_relevant_info": [],
    }


def test_collect_requirement_falls_back_to_empty_list(monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("model failed")

    monkeypatch.setattr(requirement_collector, "collector", raise_error)

    result = requirement_collector.collect_requirement("我想先去洗手间")

    assert result == []


def test_collect_requirement_accepts_dict_output(monkeypatch):
    class FakeResult:
        requirements = {"when": "给医生看病前", "what": "去洗手间"}

    def fake_collector(**kwargs):
        return FakeResult()

    monkeypatch.setattr(requirement_collector, "collector", fake_collector)

    result = requirement_collector.collect_requirement("我想先去洗手间")

    assert result == [{"when": "给医生看病前", "what": "去洗手间"}]


def test_select_clinic_accepts_dict_response(monkeypatch):
    class FakeResult(dict):
        pass

    def fake_collector(**kwargs):
        return FakeResult(clinic_selection="surgery_clinic")

    monkeypatch.setattr(clinic_selector, "collector", fake_collector)

    result = clinic_selector.select_clinic(
        body_parts="腹部",
        duration="1天",
        severity="中度",
        description="腹痛",
        other_relevant_info=[]
    )

    assert result == "surgery_clinic"


def test_patch_route_falls_back_to_origin_route(monkeypatch):
    class FakeCot:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, **kwargs):
            raise RuntimeError("model failed")

    monkeypatch.setattr(route_patcher, "RoutePatcherCot", FakeCot)

    origin_route = ["entrance", "registration_center", "quit"]
    result = route_patcher.patch_route(
        destination_clinic_id="internal_clinic",
        requirement_summary=[],
        origin_route=origin_route,
    )

    assert result == origin_route