import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validate_storyboard.py"

spec = importlib.util.spec_from_file_location("validate_storyboard", SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit("FAIL: cannot load scripts/validate_storyboard.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


VALID_SHOT = {
    "schema_version": 2,
    "shot_id": "S01",
    "beat_id": "B01",
    "beat_position": 1,
    "role_in_beat": "establish",
    "start": 0.0,
    "end": 4.5,
    "chapter": "evidence",
    "narration_focus": "建立报告证据语境",
    "visual_mode": "REPORT_EVIDENCE",
    "visual_design": "Authentic report page with a restrained readability layer",
    "on_screen_text": ["Institutional report"],
    "motion": "enter → verify → hold",
    "asset_need": "authentic_report_page",
    "start_state": "The report page is present but not yet identified",
    "development_states": [
        {
            "state_id": "S01-state-1",
            "relative_start": 0.0,
            "description": "Locate the source page and institution mark",
            "attention_target": "report-page",
        },
        {
            "state_id": "S01-state-2",
            "relative_start": 1.4,
            "description": "Mark the exact evidence region",
            "attention_target": "target-price-region",
        },
    ],
    "information_peak": "The viewer can identify the authentic report as the evidence source",
    "reading_hold": {
        "required": True,
        "min_seconds": 1.0,
        "reason": "The source identity must remain readable before the next comparison",
    },
    "information_delta": "The source becomes attributable rather than generic context",
    "end_state": "The evidence region is ready to become the next comparison anchor",
    "attention_target": "target-price-region",
    "motion_arc": "enter → locate → verify → hold → handoff",
    "motion_reason": "Verification needs a controlled reveal and a readable hold",
    "visual_action": "verify",
    "motion_budget": {
        "primary": {
            "action": "region_reveal",
            "layer": "evidence",
            "intensity": "medium",
        },
        "supporting": {
            "action": "slow_push",
            "layer": "background",
            "intensity": "low",
        },
        "background_policy": "ambient_only",
    },
    "transition_reason": "Move from source attribution to the first comparable value",
    "exit_anchor": {
        "anchor_id": "target-price-region",
        "kind": "evidence_region",
        "description": "The verified target-price region",
    },
    "entry_anchor": None,
    "continuity_axis": "none",
    "contrast_reason": None,
    "evidence_refs": ["report-page-01"],
    "timed_attention_cues": [],
}


def test_accepts_complete_shot_contract():
    assert mod.validate_record(VALID_SHOT) == []


def test_requires_information_peak_and_development_states():
    record = copy.deepcopy(VALID_SHOT)
    record.pop("information_peak")
    record["development_states"] = []
    errors = mod.validate_record(record)
    assert any("information_peak" in error for error in errors)
    assert any("development_states" in error for error in errors)


def test_rejects_motion_budget_with_two_supporting_actions():
    record = copy.deepcopy(VALID_SHOT)
    record["motion_budget"]["supporting"] = [
        {"action": "slow_push", "layer": "background"},
        {"action": "drift", "layer": "decoration"},
    ]
    errors = mod.validate_record(record)
    assert any("supporting" in error for error in errors)


def test_requires_reason_for_interior_contrast_cut():
    first = copy.deepcopy(VALID_SHOT)
    second = copy.deepcopy(VALID_SHOT)
    first["shot_id"], second["shot_id"] = "S01", "S02"
    first["beat_position"], second["beat_position"] = 1, 2
    first["end"], second["start"] = 4.5, 4.5
    second["end"] = 8.0
    second["entry_anchor"] = None
    second["continuity_axis"] = "none"
    second["contrast_reason"] = None
    errors = mod.validate_sequence([first, second])
    assert any("contrast_reason" in error for error in errors)


def test_requires_contiguous_positions_inside_each_beat():
    first = copy.deepcopy(VALID_SHOT)
    second = copy.deepcopy(VALID_SHOT)
    first["shot_id"], second["shot_id"] = "S01", "S02"
    first["beat_position"], second["beat_position"] = 1, 3
    first["end"], second["start"] = 4.5, 4.5
    second["end"] = 8.0
    errors = mod.validate_sequence([first, second])
    assert any("beat_position" in error for error in errors)


def test_accepts_continuous_handoff_between_interior_shots():
    first = copy.deepcopy(VALID_SHOT)
    second = copy.deepcopy(VALID_SHOT)
    first["shot_id"], second["shot_id"] = "S01", "S02"
    first["beat_position"], second["beat_position"] = 1, 2
    first["end"], second["start"] = 4.5, 4.5
    second["end"] = 8.0
    second["role_in_beat"] = "develop"
    second["entry_anchor"] = copy.deepcopy(first["exit_anchor"])
    second["continuity_axis"] = "position"
    errors = mod.validate_sequence([first, second])
    assert errors == []


def run_tests():
    tests = [
        test_accepts_complete_shot_contract,
        test_requires_information_peak_and_development_states,
        test_rejects_motion_budget_with_two_supporting_actions,
        test_requires_reason_for_interior_contrast_cut,
        test_requires_contiguous_positions_inside_each_beat,
        test_accepts_continuous_handoff_between_interior_shots,
    ]
    for test in tests:
        test()
    print(f"PASS: storyboard contract ({len(tests)} checks)")


if __name__ == "__main__":
    run_tests()

