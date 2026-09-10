import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "templates" / "shot-language.yaml"
STORYBOARD_TEMPLATE_PATH = ROOT / "templates" / "storyboard.jsonl"

VISUAL_ACTIONS = {
    "establish",
    "focus",
    "compare",
    "accumulate",
    "causal",
    "verify",
    "turn",
    "conclude",
    "pause",
}
LIFECYCLE_FIELDS = ("entry", "development", "peak", "hold", "exit")
PROHIBITED_QUOTA_KEYS = {
    "effect_count",
    "fixed_duration",
    "fixed_layout",
    "fixed_zoom_percent",
    "layout_quota",
    "mandatory_animation",
    "required_effect_count",
}


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise AssertionError(f"missing shot-language registry: {REGISTRY_PATH}")
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "shot-language.yaml must remain JSON-compatible YAML so the skill can "
            "validate it without an optional YAML dependency"
        ) from exc
    assert isinstance(registry, dict), "registry root must be an object"
    return registry


def candidate_ids(registry: dict[str, Any], action: str) -> list[str]:
    return [
        family["id"]
        for family in registry["families"]
        if action in family["visual_actions"]
    ]


def iter_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from iter_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_keys(child)


def iter_values(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_values(child)
    else:
        yield value


def test_registry_supports_action_driven_selection():
    registry = load_registry()
    assert registry["schema_version"] == 1
    assert registry["selection_input"] == "visual_action"
    assert isinstance(registry["families"], list) and registry["families"]

    for action in VISUAL_ACTIONS:
        assert candidate_ids(registry, action), f"no shot-language family covers {action}"


def test_every_family_is_complete_and_renderer_neutral():
    families = load_registry()["families"]
    family_ids = [family["id"] for family in families]
    assert len(family_ids) == len(set(family_ids)), "family ids must be unique"

    for family in families:
        context = f"shot-language family {family.get('id', '<missing>')}"
        assert isinstance(family.get("id"), str) and family["id"].strip(), context
        actions = family.get("visual_actions")
        assert isinstance(actions, list) and actions, f"{context}: visual_actions"
        assert set(actions) <= VISUAL_ACTIONS, f"{context}: unknown visual action"
        for field in ("use_when", "avoid_when"):
            value = family.get(field)
            assert isinstance(value, list) and value, f"{context}: {field}"
            assert all(isinstance(item, str) and item.strip() for item in value), context
        for field in LIFECYCLE_FIELDS:
            value = family.get(field)
            assert isinstance(value, str) and value.strip(), f"{context}: {field}"
        assert (
            isinstance(family.get("motion_personality"), str)
            and family["motion_personality"].strip()
        ), f"{context}: motion_personality"
        handoff = family.get("handoff")
        assert isinstance(handoff, dict), f"{context}: handoff"
        assert isinstance(handoff.get("preferred_axes"), list), context
        assert handoff["preferred_axes"], f"{context}: preferred_axes"
        assert isinstance(handoff.get("contrast_mode"), str), context
        assert handoff["contrast_mode"].strip(), f"{context}: contrast_mode"
        assert family.get("renderer_neutral") is True, context


def test_registry_records_an_explainable_selection_contract():
    contract = load_registry()["shot_record_contract"]
    assert contract["field"] == "shot_language"
    assert contract["family_field"] == "family"
    assert contract["reason_field"] == "selection_reason"
    assert contract["require_reason"] is True


def test_registry_does_not_encode_effect_or_layout_quotas():
    registry = load_registry()
    keys = set(iter_keys(registry))
    assert not keys.intersection(PROHIBITED_QUOTA_KEYS)
    for family in registry["families"]:
        numeric_values = [
            value
            for value in iter_values(family)
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        assert not numeric_values, f"{family['id']} encodes a fixed numeric quota"


def test_storyboard_template_records_a_compatible_explainable_selection():
    registry = load_registry()
    record = json.loads(STORYBOARD_TEMPLATE_PATH.read_text(encoding="utf-8"))
    contract = registry["shot_record_contract"]
    selection = record[contract["field"]]
    family_id = selection[contract["family_field"]]
    reason = selection[contract["reason_field"]]
    family = next(
        (item for item in registry["families"] if item["id"] == family_id), None
    )
    assert family is not None, "storyboard template selects an unknown family"
    assert record["visual_action"] in family["visual_actions"]
    assert isinstance(reason, str) and reason.strip()


def run_tests():
    tests = [
        test_registry_supports_action_driven_selection,
        test_every_family_is_complete_and_renderer_neutral,
        test_registry_records_an_explainable_selection_contract,
        test_registry_does_not_encode_effect_or_layout_quotas,
        test_storyboard_template_records_a_compatible_explainable_selection,
    ]
    for test in tests:
        test()
    print(f"PASS: semantic shot-language registry ({len(tests)} checks)")


if __name__ == "__main__":
    run_tests()
