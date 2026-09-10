#!/usr/bin/env python3
"""Review storyboard sequences without turning aesthetic guidance into hard rules."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
STORYBOARD_VALIDATOR = ROOT / "scripts" / "validate_storyboard.py"
SHOT_LANGUAGE_REGISTRY = ROOT / "templates" / "shot-language.yaml"
SHOT_RECIPE_REGISTRY = ROOT / "templates" / "shot-recipe.json"

INTENSITY = {"low": 1, "medium": 2, "high": 3}
ACTION_ENERGY = {
    "establish": "low",
    "focus": "medium",
    "compare": "medium",
    "accumulate": "medium",
    "causal": "medium",
    "verify": "low",
    "turn": "high",
    "conclude": "low",
    "pause": "low",
}


def _load_storyboard_validator():
    spec = importlib.util.spec_from_file_location("validate_storyboard", STORYBOARD_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load storyboard validator: {STORYBOARD_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def _finding(severity: str, shot_ids: list[str], rule: str, message: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "shot_ids": shot_ids,
        "rule": rule,
        "message": message,
    }


def _shot_ids_for_error(error: str, records: list[dict]) -> list[str]:
    match = re.search(r"line (\d+)", error)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(records):
            shot_id = records[index].get("shot_id")
            if isinstance(shot_id, str) and shot_id:
                return [shot_id]
    beat_match = re.search(r"beat ([^:]+):", error)
    if beat_match:
        beat_id = beat_match.group(1)
        return [
            str(record.get("shot_id"))
            for record in records
            if record.get("beat_id") == beat_id and record.get("shot_id")
        ]
    return []


def _contract_rule(error: str) -> str:
    if any(term in error for term in ("continuity_axis", "entry_anchor", "exit_anchor", "contrast_reason")):
        return "handoff_contract"
    if "beat_position" in error:
        return "beat_progression"
    return "contract_error"


def _is_complex(record: dict) -> bool:
    states = record.get("development_states")
    text = record.get("on_screen_text")
    return (
        isinstance(states, list)
        and len(states) >= 3
        or isinstance(text, list)
        and len(text) >= 4
    )


def _energy(record: dict) -> str:
    action_energy = ACTION_ENERGY.get(record.get("visual_action"), "medium")
    primary = record.get("motion_budget", {}).get("primary", {})
    intensity = primary.get("intensity")
    if intensity == "high":
        return "high"
    if record.get("visual_action") == "pause":
        return "low"
    return action_energy


def _reading_hold_required(record: dict) -> bool:
    hold = record.get("reading_hold")
    return isinstance(hold, dict) and hold.get("required") is True


def _load_language_actions() -> dict[str, set[str]]:
    registry = _load_json(SHOT_LANGUAGE_REGISTRY)
    return {
        family["id"]: set(family["visual_actions"])
        for family in registry.get("families", [])
        if isinstance(family, dict) and isinstance(family.get("id"), str)
    }


def _load_recipes() -> dict[str, dict]:
    registry = _load_json(SHOT_RECIPE_REGISTRY)
    return {
        recipe["id"]: recipe
        for recipe in registry.get("recipes", [])
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str)
    }


def _reference_findings(
    records: list[dict],
    language_actions: dict[str, set[str]],
    recipes: dict[str, dict],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for record in records:
        shot_id = str(record.get("shot_id") or "<missing>")
        action = record.get("visual_action")
        selection = record.get("shot_language")
        family: str | None = None
        if selection is not None:
            if not isinstance(selection, dict):
                findings.append(
                    _finding("error", [shot_id], "unsupported_shot_language", "shot_language must be an object when selected")
                )
            else:
                family = selection.get("family")
                reason = selection.get("selection_reason")
                if family not in language_actions:
                    findings.append(
                        _finding("error", [shot_id], "unsupported_shot_language", f"Unknown Shot Language family: {family}")
                    )
                elif action not in language_actions[family]:
                    findings.append(
                        _finding(
                            "error",
                            [shot_id],
                            "unsupported_shot_language",
                            f"Shot Language {family} does not support visual_action {action}",
                        )
                    )
                if not isinstance(reason, str) or not reason.strip():
                    findings.append(
                        _finding("error", [shot_id], "unsupported_shot_language", "Selected Shot Language needs selection_reason")
                    )

        recipe_stage = "shot_recipe" in record or "recipe_gap" in record
        recipe_selection = record.get("shot_recipe")
        recipe_gap = record.get("recipe_gap")
        if recipe_stage and recipe_selection is None:
            if not isinstance(recipe_gap, str) or not recipe_gap.strip():
                findings.append(
                    _finding(
                        "error",
                        [shot_id],
                        "unsupported_shot_recipe",
                        "Recipe stage without a selection needs a non-empty recipe_gap",
                    )
                )
            continue
        if recipe_selection is not None:
            if not isinstance(recipe_selection, dict):
                findings.append(
                    _finding("error", [shot_id], "unsupported_shot_recipe", "shot_recipe must be null or an object")
                )
                continue
            if recipe_gap is not None:
                findings.append(
                    _finding(
                        "error",
                        [shot_id],
                        "unsupported_shot_recipe",
                        "Selected Shot Recipe requires recipe_gap to be null",
                    )
                )
            recipe_id = recipe_selection.get("id")
            reason = recipe_selection.get("selection_reason")
            recipe = recipes.get(recipe_id)
            if recipe is None:
                findings.append(
                    _finding("error", [shot_id], "unsupported_shot_recipe", f"Unknown Shot Recipe: {recipe_id}")
                )
            else:
                if family is not None and recipe.get("shot_language") != family:
                    findings.append(
                        _finding(
                            "error",
                            [shot_id],
                            "unsupported_shot_recipe",
                            f"Shot Recipe {recipe_id} does not match Shot Language {family}",
                        )
                    )
                if action not in recipe.get("visual_actions", []):
                    findings.append(
                        _finding(
                            "error",
                            [shot_id],
                            "unsupported_shot_recipe",
                            f"Shot Recipe {recipe_id} does not support visual_action {action}",
                        )
                    )
            if not isinstance(reason, str) or not reason.strip():
                findings.append(
                    _finding("error", [shot_id], "unsupported_shot_recipe", "Selected Shot Recipe needs selection_reason")
                )
    return findings


def _repetition_findings(records: list[dict]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    start = 0
    while start < len(records):
        signature = (records[start].get("visual_mode"), records[start].get("visual_action"))
        end = start + 1
        while end < len(records) and (
            records[end].get("visual_mode"), records[end].get("visual_action")
        ) == signature:
            end += 1
        if end - start >= 3:
            shot_ids = [str(record.get("shot_id")) for record in records[start:end]]
            findings.append(
                _finding(
                    "warning",
                    shot_ids,
                    "repeated_visual_pattern",
                    f"{len(shot_ids)} consecutive shots repeat visual_mode={signature[0]} and visual_action={signature[1]}; review sequence variety and editorial purpose",
                )
            )
        start = end
    return findings


def _release_findings(records: list[dict]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not _is_complex(record):
            continue
        hold = record.get("reading_hold")
        protected = isinstance(hold, dict) and hold.get("required") is True
        next_record = records[index + 1] if index + 1 < len(records) else None
        followed_by_pause = next_record is not None and next_record.get("visual_action") == "pause"
        if not protected and not followed_by_pause:
            shot_ids = [str(record.get("shot_id"))]
            if next_record is not None:
                shot_ids.append(str(next_record.get("shot_id")))
            findings.append(
                _finding(
                    "warning",
                    shot_ids,
                    "missing_cognitive_release",
                    "A complex information peak has neither a protected reading hold nor a following pause shot",
                )
            )
    return findings


def _motion_findings(records: list[dict]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for record in records:
        budget = record.get("motion_budget")
        if not isinstance(budget, dict):
            continue
        primary = budget.get("primary")
        supporting = budget.get("supporting")
        if not isinstance(primary, dict) or not isinstance(supporting, dict):
            continue
        primary_level = INTENSITY.get(primary.get("intensity"))
        supporting_level = INTENSITY.get(supporting.get("intensity"))
        if (
            primary_level is not None
            and supporting_level is not None
            and supporting_level >= primary_level
            and supporting_level > INTENSITY["low"]
        ):
            shot_id = str(record.get("shot_id") or "<missing>")
            findings.append(
                _finding(
                    "warning",
                    [shot_id],
                    "unbalanced_motion_budget",
                    "Supporting motion is as intense as or stronger than the primary information motion",
                )
            )
    return findings


def review_sequence(
    records: list[dict],
    *,
    director_summary: str | None = None,
    render_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return structured errors, warnings, and an inspectable energy curve."""
    validator = _load_storyboard_validator()
    findings = [
        _finding("error", _shot_ids_for_error(error, records), _contract_rule(error), error)
        for error in validator.validate_sequence(records)
    ]
    findings.extend(_reference_findings(records, _load_language_actions(), _load_recipes()))
    findings.extend(_repetition_findings(records))
    findings.extend(_release_findings(records))
    findings.extend(_motion_findings(records))

    energy_curve = [
        {
            "shot_id": record.get("shot_id"),
            "beat_id": record.get("beat_id"),
            "role_in_beat": record.get("role_in_beat"),
            "visual_action": record.get("visual_action"),
            "complexity": "complex" if _is_complex(record) else "simple",
            "energy": _energy(record),
            "reading_hold": _reading_hold_required(record),
        }
        for record in records
        if isinstance(record, dict)
    ]
    return {
        "schema_version": 1,
        "shot_count": len(records),
        "findings": findings,
        "energy_curve": energy_curve,
        "inputs": {
            "director_summary": director_summary is not None,
            "render_review": render_review is not None,
        },
        "summary": {
            "errors": sum(finding["severity"] == "error" for finding in findings),
            "warnings": sum(finding["severity"] == "warning" for finding in findings),
        },
    }


def _load_jsonl(path: Path) -> tuple[list[dict], list[dict[str, Any]]]:
    records: list[dict] = []
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.append(
                _finding("error", [], "contract_error", f"line {line_number}: invalid JSON: {exc.msg}")
            )
            continue
        if not isinstance(value, dict):
            findings.append(
                _finding("error", [], "contract_error", f"line {line_number}: shot record must be an object")
            )
            continue
        records.append(value)
    return records, findings


def _load_optional_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return _load_json(path)


def _load_optional_text(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a V2 storyboard sequence")
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("--director-summary", type=Path)
    parser.add_argument("--render-review", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        records, load_findings = _load_jsonl(args.storyboard)
        report = review_sequence(
            records,
            director_summary=_load_optional_text(args.director_summary),
            render_review=_load_optional_json(args.render_review),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "schema_version": 1,
            "shot_count": 0,
            "findings": [_finding("error", [], "input_contract", str(exc))],
            "energy_curve": [],
            "inputs": {"director_summary": False, "render_review": False},
            "summary": {"errors": 1, "warnings": 0},
        }
        load_findings = []

    if load_findings:
        report["findings"] = load_findings + report["findings"]
        report["summary"]["errors"] += len(load_findings)

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
