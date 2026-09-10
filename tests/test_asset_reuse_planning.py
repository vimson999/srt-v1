import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "plan_asset_reuse.py"

spec = importlib.util.spec_from_file_location("plan_asset_reuse", SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit("FAIL: cannot load scripts/plan_asset_reuse.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def context_asset(
    asset_id: str = "electronics_line",
    *,
    status: str = "backup",
    provenance: str = "verified",
    license_status: str = "cleared",
) -> dict:
    return {
        "asset_id": asset_id,
        "type": "video",
        "category": "context_broll",
        "description": "Electronics manufacturing line with automated equipment",
        "tags": ["electronics", "manufacturing", "factory", "wide"],
        "status": status,
        "provenance_status": provenance,
        "license_status": license_status,
        "acceptance_basis": "Broad semantic context only",
        "use_as": "Electronics manufacturing context",
        "do_not_claim_as": "The exact company facility or narrated event",
        "file_exists": True,
        "resolution_warning": None,
    }


def report_asset() -> dict:
    return {
        "asset_id": "report_page_lowres",
        "type": "image",
        "category": "report_evidence",
        "description": "Authentic institutional report page with target-price region",
        "tags": ["report", "target price", "institution", "evidence"],
        "status": "keep",
        "provenance_status": "verified",
        "license_status": "cleared",
        "acceptance_basis": "User-provided authentic report screenshot",
        "use_as": "Report evidence backing and source attribution",
        "do_not_claim_as": "Readable exact wording outside verified source text",
        "file_exists": True,
        "resolution_warning": "Low resolution; do not transcribe unreadable pixels",
    }


def need(
    shot_id: str,
    *,
    purpose: str = "Electronics manufacturing context",
    keywords: list[str] | None = None,
    asset_role: str = "context",
    treatment: dict | None = None,
) -> dict:
    return {
        "shot_id": shot_id,
        "visual_action": "establish" if asset_role == "context" else "verify",
        "shot_language": "context_establish" if asset_role == "context" else "report_reveal",
        "purpose": purpose,
        "keywords": keywords or ["electronics", "manufacturing"],
        "asset_role": asset_role,
        "treatment": treatment
        or {
            "trim": "00:00-00:04",
            "crop": "wide",
            "scale": "base",
            "speed": "normal",
            "opacity": "base",
            "layout": "full_frame",
        },
    }


def catalog(*assets: dict) -> dict:
    return {
        "schema_version": 1,
        "library_id": "report-video-asset-library",
        "assets": list(assets),
    }


def empty_usage() -> dict:
    return {
        "schema_version": 1,
        "library_id": "report-video-asset-library",
        "projects": [],
        "assets": {},
    }


def cards_for(report: dict, shot_id: str) -> list[dict]:
    return report["candidates_by_shot"][shot_id]


def assignment_for(report: dict, shot_id: str) -> dict:
    return next(item for item in report["assignments"] if item["shot_id"] == shot_id)


def test_honest_related_context_asset_ranks_as_fallback():
    report = mod.plan_asset_reuse(
        [need("S01")], catalog(context_asset()), empty_usage()
    )
    card = cards_for(report, "S01")[0]
    assert card["asset_id"] == "electronics_line"
    assert card["decision"] == "fallback"
    assert card["semantic_fit"]["matched_terms"] == ["electronics", "manufacturing"]
    assert card["prohibited_interpretation"] == "The exact company facility or narrated event"
    assert assignment_for(report, "S01")["selected_asset_id"] == "electronics_line"


def test_unverified_asset_remains_usable_for_preview_behind_publication_gate():
    asset = context_asset(status="keep", provenance="unverified", license_status="unverified")
    report = mod.plan_asset_reuse([need("S01")], catalog(asset), empty_usage())
    card = cards_for(report, "S01")[0]
    assert card["decision"] == "primary"
    assert card["publication_gate"]["required"] is True
    assert card["publication_gate"]["reasons"] == [
        "provenance_not_verified",
        "license_not_cleared",
    ]


def test_low_resolution_authentic_report_is_retained_with_warning():
    report_need = need(
        "S01",
        purpose="Verify the institutional report target price",
        keywords=["report", "target price"],
        asset_role="evidence",
    )
    report = mod.plan_asset_reuse(
        [report_need], catalog(report_asset()), empty_usage()
    )
    card = cards_for(report, "S01")[0]
    assert card["decision"] == "primary"
    assert card["resolution_warning"] == "Low resolution; do not transcribe unreadable pixels"
    assert assignment_for(report, "S01")["selected_asset_id"] == "report_page_lowres"
    assert report["gaps"] == []


def test_context_asset_cannot_satisfy_an_evidence_need():
    misleading = context_asset(status="keep")
    misleading["description"] = "Presenter discusses a report and target price"
    misleading["tags"] = ["report", "target price"]
    evidence_need = need(
        "S01",
        purpose="Verify the institutional report target price",
        keywords=["report", "target price"],
        asset_role="evidence",
    )
    report = mod.plan_asset_reuse(
        [evidence_need], catalog(misleading), empty_usage()
    )
    assert report["assignments"] == []
    assert report["gaps"][0]["reason"] == "no_honest_available_candidate"
    assert cards_for(report, "S01")[0]["semantic_fit"]["role_compatible"] is False


def test_immediate_identical_reuse_is_flagged_not_hidden():
    same_treatment = need("S01")["treatment"]
    report = mod.plan_asset_reuse(
        [
            need("S01", treatment=dict(same_treatment)),
            need("S02", treatment=dict(same_treatment)),
        ],
        catalog(context_asset(status="keep")),
        empty_usage(),
    )
    second = assignment_for(report, "S02")
    assert second["selected_asset_id"] == "electronics_line"
    assert second["repetition_warning"]["rule"] == "immediate_identical_reuse"
    assert second["treatment_variation"]["varied"] is False


def test_varied_reuse_is_allowed_and_records_changed_dimensions():
    first = need("S01")
    varied = dict(first["treatment"])
    varied.update({"trim": "00:06-00:10", "crop": "detail", "speed": "slow"})
    report = mod.plan_asset_reuse(
        [first, need("S02", treatment=varied)],
        catalog(context_asset(status="keep")),
        empty_usage(),
    )
    second = assignment_for(report, "S02")
    assert second["repetition_warning"] is None
    assert second["treatment_variation"] == {
        "varied": True,
        "dimensions": ["crop", "speed", "trim"],
    }


def test_genuine_gap_requires_no_honest_available_candidate():
    unrelated = context_asset(status="keep")
    unrelated["asset_id"] = "city_skyline"
    unrelated["description"] = "Generic city skyline at night"
    unrelated["tags"] = ["city", "night", "skyline"]
    unrelated["use_as"] = "General urban context"
    report = mod.plan_asset_reuse([need("S01")], catalog(unrelated), empty_usage())
    assert report["assignments"] == []
    assert report["gaps"] == [
        {
            "shot_id": "S01",
            "need": "Electronics manufacturing context",
            "reason": "no_honest_available_candidate",
            "genuine": True,
        }
    ]


def test_prior_usage_is_exposed_without_changing_asset_identity():
    usage = empty_usage()
    usage["assets"]["electronics_line"] = {
        "uses": [
            {"project_id": "episode_old", "shot_id": "S08", "sequence_index": 8}
        ]
    }
    report = mod.plan_asset_reuse(
        [need("S01")], catalog(context_asset(status="keep")), usage
    )
    card = cards_for(report, "S01")[0]
    assert card["prior_usage"] == {
        "count": 1,
        "last_project_id": "episode_old",
        "last_shot_id": "S08",
    }
    assert card["asset_id"] == "electronics_line"


def test_durable_metadata_guides_semantic_fit_without_overwriting_path():
    asset = context_asset(status="keep")
    asset["description"] = "Unreviewed clip"
    asset["tags"] = []
    asset["path"] = "raw/video/electronics_line.mp4"
    metadata = {
        "assets": {
            "electronics_line": {
                "description": "Reviewed electronics manufacturing line",
                "tags": ["electronics", "manufacturing"],
                "status": "backup",
                "path": "must-not-replace-computed-path.mp4",
            }
        }
    }
    merged = mod.merge_metadata(catalog(asset), metadata)
    assert merged[0]["path"] == "raw/video/electronics_line.mp4"
    report = mod.plan_asset_reuse([need("S01")], catalog(asset), empty_usage(), metadata)
    assert cards_for(report, "S01")[0]["decision"] == "fallback"


def test_equally_fitting_less_used_asset_ranks_first():
    used = context_asset("used_line", status="keep")
    fresh = context_asset("fresh_line", status="keep")
    usage = empty_usage()
    usage["assets"]["used_line"] = {
        "uses": [
            {"project_id": "old", "shot_id": "S01"},
            {"project_id": "old", "shot_id": "S02"},
        ]
    }
    report = mod.plan_asset_reuse([need("S01")], catalog(used, fresh), usage)
    assert [card["asset_id"] for card in cards_for(report, "S01")[:2]] == [
        "fresh_line",
        "used_line",
    ]


def test_cli_writes_plan_without_mutating_catalog_metadata_or_usage():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        catalog_path = root / "assets.json"
        metadata_path = root / "metadata.json"
        usage_path = root / "usage.json"
        needs_path = root / "needs.json"
        output_path = root / "reuse-plan.json"
        catalog_path.write_text(json.dumps(catalog(context_asset())), encoding="utf-8")
        metadata_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "assets": {
                        "electronics_line": {
                            "description": "Reviewed electronics manufacturing line",
                            "tags": ["electronics", "manufacturing", "reviewed"],
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        usage_path.write_text(json.dumps(empty_usage()), encoding="utf-8")
        needs_path.write_text(json.dumps({"needs": [need("S01")]}), encoding="utf-8")
        before = {
            path.name: path.read_bytes()
            for path in (catalog_path, metadata_path, usage_path)
        }
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--catalog",
                str(catalog_path),
                "--metadata",
                str(metadata_path),
                "--usage",
                str(usage_path),
                "--needs",
                str(needs_path),
                "--output",
                str(output_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        output = json.loads(output_path.read_text(encoding="utf-8"))
        assert assignment_for(output, "S01")["selected_asset_id"] == "electronics_line"
        after = {
            path.name: path.read_bytes()
            for path in (catalog_path, metadata_path, usage_path)
        }
    assert before == after


def test_cli_rejects_an_explicit_missing_metadata_path():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        catalog_path = root / "assets.json"
        usage_path = root / "usage.json"
        needs_path = root / "needs.json"
        output_path = root / "reuse-plan.json"
        missing_metadata = root / "missing-metadata.json"
        catalog_path.write_text(json.dumps(catalog(context_asset())), encoding="utf-8")
        usage_path.write_text(json.dumps(empty_usage()), encoding="utf-8")
        needs_path.write_text(json.dumps({"needs": [need("S01")]}), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--catalog",
                str(catalog_path),
                "--metadata",
                str(missing_metadata),
                "--usage",
                str(usage_path),
                "--needs",
                str(needs_path),
                "--output",
                str(output_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    assert result.returncode == 1
    assert "missing-metadata.json" in result.stdout


def run_tests():
    tests = [
        test_honest_related_context_asset_ranks_as_fallback,
        test_unverified_asset_remains_usable_for_preview_behind_publication_gate,
        test_low_resolution_authentic_report_is_retained_with_warning,
        test_context_asset_cannot_satisfy_an_evidence_need,
        test_immediate_identical_reuse_is_flagged_not_hidden,
        test_varied_reuse_is_allowed_and_records_changed_dimensions,
        test_genuine_gap_requires_no_honest_available_candidate,
        test_prior_usage_is_exposed_without_changing_asset_identity,
        test_durable_metadata_guides_semantic_fit_without_overwriting_path,
        test_equally_fitting_less_used_asset_ranks_first,
        test_cli_writes_plan_without_mutating_catalog_metadata_or_usage,
        test_cli_rejects_an_explicit_missing_metadata_path,
    ]
    for test in tests:
        test()
    print(f"PASS: semantic asset reuse planning ({len(tests)} checks)")


if __name__ == "__main__":
    run_tests()
