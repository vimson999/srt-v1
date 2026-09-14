import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validate_production.py"

spec = importlib.util.spec_from_file_location("validate_production", SCRIPT)
vp = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(vp)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def base_state():
    return {
        "schema_version": 1,
        "standard_revision": "design-r1",
        "content_revision": "content-r1",
        "canonical_production_entry": "src/Root.tsx#MainComposition",
        "representative": {
            "production_entry": "src/Root.tsx#MainComposition",
            "content_revision": "content-r1",
            "review_status": "pass",
        },
        "expansion_probe": {
            "production_entry": "src/Root.tsx#MainComposition",
            "content_revision": "content-r1",
            "review_status": "pass",
            "materially_different_shots_checked": 4,
        },
        "full_film": {
            "production_entry": "src/Root.tsx#MainComposition",
            "content_revision": "content-r1",
            "implementation_status": "implemented",
            "visual_review_status": "pass",
        },
        "fallback_renderer": None,
        "feedback_generalization_scan": {"status": "pass"},
        "render_preflight": {"status": "pass"},
        "continuous_playback_review": {"status": "pass"},
        "regressions": [],
    }


def project_with(state, shots=None):
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    write_json(root / "manifest" / "production_state.json", state)
    write_jsonl(root / "storyboard" / "storyboard.jsonl", shots or [])
    return td, root


def test_valid_project_passes_scale_and_export():
    td, root = project_with(base_state())
    try:
        errors, _ = vp.validate(root, "scale")
        assert errors == []
        errors, _ = vp.validate(root, "full-export")
        assert errors == []
    finally:
        td.cleanup()


def test_sample_full_path_divergence_blocks_scale():
    state = base_state()
    state["full_film"]["production_entry"] = "src/Fallback.tsx#GenericFilm"
    td, root = project_with(state)
    try:
        errors, _ = vp.validate(root, "scale")
        assert any("diverges from canonical_production_entry" in e for e in errors)
    finally:
        td.cleanup()


def test_active_fallback_renderer_blocks_scale():
    state = base_state()
    state["fallback_renderer"] = "generic-card-renderer"
    td, root = project_with(state)
    try:
        errors, _ = vp.validate(root, "scale")
        assert any("fallback_renderer is active" in e for e in errors)
    finally:
        td.cleanup()


def test_planning_text_leak_blocks_scale():
    shots = [
        {
            "shot_id": "S01",
            "attention_target": "在统一时间线中建立节点1",
            "on_screen_text": "在统一时间线中建立节点1",
        }
    ]
    td, root = project_with(base_state(), shots)
    try:
        errors, _ = vp.validate(root, "scale")
        assert any("PLANNING_TEXT_LEAK" in e for e in errors)
    finally:
        td.cleanup()


def test_repeated_p1_without_mechanism_fix_blocks_scale():
    state = base_state()
    state["regressions"] = [
        {
            "id": "R-7",
            "class": "EXAMPLE_ONLY_FIX",
            "severity": "P1",
            "status": "escalated",
            "occurrence_count": 2,
            "generalization_scan_status": "pass",
            "mechanism_fix_ref": None,
        }
    ]
    td, root = project_with(state)
    try:
        errors, _ = vp.validate(root, "scale")
        assert any("mechanism_fix_ref" in e for e in errors)
        assert any("repeated P1 regression" in e for e in errors)
    finally:
        td.cleanup()


def test_repeated_p1_can_resume_after_mechanism_fix_and_scan():
    state = base_state()
    state["regressions"] = [
        {
            "id": "R-7",
            "class": "EXAMPLE_ONLY_FIX",
            "severity": "P1",
            "status": "verified",
            "occurrence_count": 2,
            "generalization_scan_status": "pass",
            "mechanism_fix_ref": "src/director/audience-copy.ts@r2",
        }
    ]
    td, root = project_with(state)
    try:
        errors, _ = vp.validate(root, "scale")
        assert errors == []
    finally:
        td.cleanup()


def test_expansion_probe_is_required_before_scale():
    state = base_state()
    state["expansion_probe"]["review_status"] = "pending"
    state["expansion_probe"]["materially_different_shots_checked"] = 1
    td, root = project_with(state)
    try:
        errors, _ = vp.validate(root, "scale")
        assert any("expansion_probe.review_status" in e for e in errors)
        assert any("at least 3 materially different shots" in e for e in errors)
    finally:
        td.cleanup()
