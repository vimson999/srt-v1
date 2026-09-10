import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "review_sequence.py"
TEMPLATE = json.loads((ROOT / "templates" / "storyboard.jsonl").read_text(encoding="utf-8"))

spec = importlib.util.spec_from_file_location("review_sequence", SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit("FAIL: cannot load scripts/review_sequence.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


ACTION_LANGUAGE = {
    "establish": "context_establish",
    "compare": "aligned_comparison",
    "pause": "pause_hold",
    "turn": "clean_cut",
}


def make_shot(
    number: int,
    *,
    visual_mode: str,
    visual_action: str,
    state_count: int = 1,
    hold_required: bool = False,
) -> dict:
    shot = copy.deepcopy(TEMPLATE)
    shot_id = f"S{number:02d}"
    shot["shot_id"] = shot_id
    shot["beat_id"] = "B01"
    shot["beat_position"] = number
    shot["role_in_beat"] = "establish" if number == 1 else "develop"
    shot["start"] = float((number - 1) * 4)
    shot["end"] = float(number * 4)
    shot["visual_mode"] = visual_mode
    shot["visual_action"] = visual_action
    shot["shot_language"] = {
        "family": ACTION_LANGUAGE[visual_action],
        "selection_reason": f"Exercise {visual_action} behavior in {shot_id}",
    }
    shot["development_states"] = [
        {
            "state_id": f"{shot_id}-state-{index}",
            "relative_start": float(index - 1),
            "description": f"Development state {index}",
            "attention_target": f"target-{number}",
        }
        for index in range(1, state_count + 1)
    ]
    shot["reading_hold"] = {
        "required": hold_required,
        "min_seconds": 0.8 if hold_required else None,
        "reason": "Dense information needs protected reading" if hold_required else None,
    }
    shot["entry_anchor"] = None
    shot["exit_anchor"] = {
        "anchor_id": f"anchor-{number}",
        "kind": "concept",
        "description": f"Exit anchor for {shot_id}",
    }
    shot["continuity_axis"] = "none" if number == 1 else "position"
    shot["contrast_reason"] = None
    return shot


def link_sequence(shots: list[dict]) -> list[dict]:
    for index in range(1, len(shots)):
        shots[index]["entry_anchor"] = copy.deepcopy(shots[index - 1]["exit_anchor"])
        shots[index]["continuity_axis"] = "position"
        shots[index]["contrast_reason"] = None
    return shots


def findings_for(report: dict, rule: str) -> list[dict]:
    return [finding for finding in report["findings"] if finding["rule"] == rule]


def test_flags_three_consecutive_identical_layout_action_patterns():
    shots = link_sequence(
        [
            make_shot(i, visual_mode="COMPARISON", visual_action="compare")
            for i in range(1, 4)
        ]
    )
    report = mod.review_sequence(shots)
    findings = findings_for(report, "repeated_visual_pattern")
    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert findings[0]["shot_ids"] == ["S01", "S02", "S03"]


def test_warns_when_complex_peak_has_no_protected_release():
    shots = link_sequence(
        [
            make_shot(
                1,
                visual_mode="CHART",
                visual_action="compare",
                state_count=3,
                hold_required=False,
            ),
            make_shot(2, visual_mode="COMPARISON", visual_action="compare", state_count=2),
        ]
    )
    report = mod.review_sequence(shots)
    findings = findings_for(report, "missing_cognitive_release")
    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert findings[0]["shot_ids"] == ["S01", "S02"]


def test_missing_handoff_is_a_blocking_error():
    shots = link_sequence(
        [
            make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish"),
            make_shot(2, visual_mode="COMPARISON", visual_action="compare"),
        ]
    )
    shots[1]["entry_anchor"] = None
    report = mod.review_sequence(shots)
    findings = findings_for(report, "handoff_contract")
    assert findings
    assert all(finding["severity"] == "error" for finding in findings)


def test_clean_contrast_cut_with_reason_is_valid():
    shots = link_sequence(
        [
            make_shot(1, visual_mode="CHART", visual_action="compare"),
            make_shot(2, visual_mode="SECTION_TITLE", visual_action="turn"),
        ]
    )
    shots[1]["entry_anchor"] = None
    shots[1]["continuity_axis"] = "none"
    shots[1]["contrast_reason"] = "Replace dense evidence with a new decision frame"
    report = mod.review_sequence(shots)
    assert findings_for(report, "handoff_contract") == []


def test_unsupported_shot_language_is_an_error():
    shots = [make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish")]
    shots[0]["shot_language"]["family"] = "invented_effect_stack"
    report = mod.review_sequence(shots)
    findings = findings_for(report, "unsupported_shot_language")
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"


def test_unsupported_shot_recipe_is_an_error():
    shot = make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish")
    shot["shot_recipe"] = {
        "id": "invented_recipe",
        "selection_reason": "Exercise unsupported recipe handling",
    }
    report = mod.review_sequence([shot])
    findings = findings_for(report, "unsupported_shot_recipe")
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"


def test_explicit_recipe_stage_requires_selection_or_gap():
    shot = make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish")
    shot["shot_recipe"] = None
    shot["recipe_gap"] = None
    report = mod.review_sequence([shot])
    findings = findings_for(report, "unsupported_shot_recipe")
    assert len(findings) == 1
    assert "recipe_gap" in findings[0]["message"]


def test_compatible_recipe_selection_is_accepted():
    shot = make_shot(1, visual_mode="COMPARISON", visual_action="compare")
    shot["shot_recipe"] = {
        "id": "aligned_value_comparison",
        "selection_reason": "The values share one supported scale",
    }
    shot["recipe_gap"] = None
    report = mod.review_sequence([shot])
    assert findings_for(report, "unsupported_shot_recipe") == []


def test_unbalanced_supporting_motion_is_a_warning():
    shot = make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish")
    shot["motion_budget"]["primary"]["intensity"] = "medium"
    shot["motion_budget"]["supporting"] = {
        "action": "background_push",
        "layer": "background",
        "intensity": "medium",
    }
    report = mod.review_sequence([shot])
    findings = findings_for(report, "unbalanced_motion_budget")
    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"


def test_malformed_reading_hold_is_reported_without_crashing():
    shot = make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish")
    shot["reading_hold"] = "invalid"
    report = mod.review_sequence([shot])
    assert any(finding["severity"] == "error" for finding in report["findings"])
    assert report["energy_curve"][0]["reading_hold"] is False


def test_valid_sequence_has_energy_annotations_and_no_findings():
    shots = link_sequence(
        [
            make_shot(1, visual_mode="SECTION_TITLE", visual_action="establish"),
            make_shot(
                2,
                visual_mode="COMPARISON",
                visual_action="compare",
                state_count=3,
                hold_required=True,
            ),
            make_shot(3, visual_mode="DATA_HERO", visual_action="pause"),
        ]
    )
    report = mod.review_sequence(shots)
    assert report["findings"] == []
    assert [item["shot_id"] for item in report["energy_curve"]] == ["S01", "S02", "S03"]
    assert report["energy_curve"][1]["complexity"] == "complex"
    assert report["energy_curve"][2]["energy"] == "low"


def test_cli_accepts_optional_markdown_director_summary():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        storyboard = tmp_path / "storyboard.jsonl"
        summary = tmp_path / "director_summary.md"
        storyboard.write_text(json.dumps(TEMPLATE, ensure_ascii=False) + "\n", encoding="utf-8")
        summary.write_text("# Director Summary\n\nSequence context.\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                str(storyboard),
                "--director-summary",
                str(summary),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["inputs"]["director_summary"] is True


def run_tests():
    tests = [
        test_flags_three_consecutive_identical_layout_action_patterns,
        test_warns_when_complex_peak_has_no_protected_release,
        test_missing_handoff_is_a_blocking_error,
        test_clean_contrast_cut_with_reason_is_valid,
        test_unsupported_shot_language_is_an_error,
        test_unsupported_shot_recipe_is_an_error,
        test_explicit_recipe_stage_requires_selection_or_gap,
        test_compatible_recipe_selection_is_accepted,
        test_unbalanced_supporting_motion_is_a_warning,
        test_malformed_reading_hold_is_reported_without_crashing,
        test_valid_sequence_has_energy_annotations_and_no_findings,
        test_cli_accepts_optional_markdown_director_summary,
    ]
    for test in tests:
        test()
    print(f"PASS: sequence review ({len(tests)} checks)")


if __name__ == "__main__":
    run_tests()
