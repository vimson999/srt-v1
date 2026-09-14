#!/usr/bin/env python3
"""Validate production-path and regression gates for srt-visual-director projects.

This validator intentionally checks control-plane invariants rather than visual taste.
It prevents known expensive failure modes from being silently treated as progress.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


PASS_VALUES = {"pass", "passed", "accepted", "approved", "verified", "complete", "completed"}
IMPLEMENTED_VALUES = {"implemented", "complete", "completed", "pass", "passed", "approved"}
BLOCKING_REGRESSION_STATUSES = {"open", "escalated", "needs_fix", "failed"}
SAFE_REGRESSION_STATUSES = {"mechanism_fixed", "verified", "waived_by_user", "closed"}

# Known internal/planning language that should not be emitted as audience copy.
# Keep the list deliberately narrow to avoid turning stylistic preference into a hard gate.
INTERNAL_TEXT_PATTERNS = [
    re.compile(r"\battention_target\b", re.I),
    re.compile(r"\binformation_peak\b", re.I),
    re.compile(r"\bvisual_action\b", re.I),
    re.compile(r"\bshot_function\b", re.I),
    re.compile(r"\bsource_gate\b", re.I),
    re.compile(r"\bevidence_layer\b", re.I),
    re.compile(r"建立节点"),
    re.compile(r"来源门"),
    re.compile(r"证据层"),
    re.compile(r"来源矩阵"),
    re.compile(r"依次激活"),
]

PLANNING_FIELD_NAMES = {
    "attention_target",
    "information_peak",
    "start_state",
    "end_state",
    "information_delta",
    "motion_reason",
    "transition_reason",
    "cut_reason",
    "shot_function",
    "visual_action",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
            if isinstance(row, dict):
                rows.append(row)
    return rows


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value).strip().lower()


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        if value.strip():
            yield value.strip()
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_strings(child)


def audience_strings(shot: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("on_screen_text", "audience_text", "screen_copy"):
        if key in shot:
            out.extend(iter_strings(shot[key]))
    return out


def planning_strings(shot: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in PLANNING_FIELD_NAMES:
        if key in shot:
            out.extend(iter_strings(shot[key]))
    for state in shot.get("development_states", []) or []:
        if isinstance(state, dict):
            for key in ("description", "attention_target"):
                if key in state:
                    out.extend(iter_strings(state[key]))
    return out


def detect_planning_text_leaks(shots: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for shot in shots:
        shot_id = str(shot.get("shot_id", "<unknown>"))
        audience = audience_strings(shot)
        if not audience:
            continue

        planning_norm = {
            normalize_text(text): text
            for text in planning_strings(shot)
            if len(normalize_text(text)) >= 6
        }

        for text in audience:
            norm = normalize_text(text)
            for pattern in INTERNAL_TEXT_PATTERNS:
                if pattern.search(text):
                    issues.append(
                        f"{shot_id}: audience text contains internal planning language: {text!r}"
                    )
                    break

            # Exact reuse of a planning sentence is a strong leak signal.
            if len(norm) >= 6 and norm in planning_norm:
                issues.append(
                    f"{shot_id}: audience text duplicates planning field text: {text!r}"
                )
    return sorted(set(issues))


def value_passes(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in PASS_VALUES


def implementation_passes(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in IMPLEMENTED_VALUES


def nested(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def add(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_path_identity(state: dict[str, Any], errors: list[str]) -> None:
    canonical_entry = state.get("canonical_production_entry")
    content_revision = state.get("content_revision")

    add(bool(canonical_entry), "missing canonical_production_entry", errors)
    add(bool(content_revision), "missing content_revision", errors)

    for scope in ("representative", "expansion_probe", "full_film"):
        block = state.get(scope)
        add(isinstance(block, dict), f"missing {scope} block", errors)
        if not isinstance(block, dict):
            continue
        if canonical_entry:
            add(
                block.get("production_entry") == canonical_entry,
                f"{scope}.production_entry diverges from canonical_production_entry",
                errors,
            )
        if content_revision:
            add(
                block.get("content_revision") == content_revision,
                f"{scope}.content_revision diverges from active content_revision",
                errors,
            )

    fallback = state.get("fallback_renderer")
    add(
        fallback in (None, False, "", "none", "null"),
        "fallback_renderer is active; sample/full production path may be diverging",
        errors,
    )


def check_regressions(state: dict[str, Any], errors: list[str]) -> None:
    regressions = state.get("regressions", [])
    if regressions is None:
        regressions = []
    if not isinstance(regressions, list):
        errors.append("regressions must be an array")
        return

    needs_scan = False
    for item in regressions:
        if not isinstance(item, dict):
            errors.append("regression entry must be an object")
            continue
        rid = item.get("id", "<unknown>")
        severity = str(item.get("severity", "")).upper()
        status = str(item.get("status", "open")).lower()
        occurrence_count = item.get("occurrence_count", 1)
        try:
            occurrence_count = int(occurrence_count)
        except (TypeError, ValueError):
            occurrence_count = 1

        if severity in {"P0", "P1"}:
            needs_scan = True

        if severity == "P0" and status in BLOCKING_REGRESSION_STATUSES:
            errors.append(f"{rid}: unresolved P0 regression blocks production")
        if severity == "P1" and occurrence_count >= 2 and status not in SAFE_REGRESSION_STATUSES:
            errors.append(
                f"{rid}: repeated P1 regression requires mechanism fix before another broad revision"
            )
        if occurrence_count >= 2 and severity in {"P0", "P1"}:
            scan_status = str(item.get("generalization_scan_status", "")).lower()
            mechanism_fix = item.get("mechanism_fix_ref")
            add(
                scan_status in PASS_VALUES,
                f"{rid}: repeated regression requires completed analogous-shot scan",
                errors,
            )
            add(
                bool(mechanism_fix),
                f"{rid}: repeated regression requires mechanism_fix_ref",
                errors,
            )

    if needs_scan:
        scan_status = nested(state, "feedback_generalization_scan", "status")
        add(
            value_passes(scan_status),
            "feedback_generalization_scan.status must pass when P0/P1 regressions are recorded",
            errors,
        )


def validate(project: Path, stage: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    state_path = project / "manifest" / "production_state.json"
    if not state_path.exists():
        return [f"missing required control-plane file: {state_path}"], warnings

    try:
        state = load_json(state_path)
    except Exception as exc:  # pragma: no cover - CLI boundary
        return [f"cannot read production_state.json: {exc}"], warnings

    if not isinstance(state, dict):
        return ["production_state.json must contain a JSON object"], warnings

    add(state.get("schema_version") == 1, "production_state.schema_version must be 1", errors)
    check_path_identity(state, errors)
    check_regressions(state, errors)

    try:
        shots = load_jsonl(project / "storyboard" / "storyboard.jsonl")
    except ValueError as exc:
        errors.append(str(exc))
        shots = []

    for leak in detect_planning_text_leaks(shots):
        errors.append("FR-01 PLANNING_TEXT_LEAK: " + leak)

    representative_status = nested(state, "representative", "review_status")
    add(
        value_passes(representative_status),
        "representative.review_status must pass before scaling",
        errors,
    )

    if stage in {"scale", "full-export"}:
        expansion_status = nested(state, "expansion_probe", "review_status")
        add(
            value_passes(expansion_status),
            "expansion_probe.review_status must pass before broad scaling",
            errors,
        )
        checked = nested(state, "expansion_probe", "materially_different_shots_checked")
        if checked is not None:
            try:
                add(int(checked) >= 3, "expansion probe must check at least 3 materially different shots", errors)
            except (TypeError, ValueError):
                errors.append("expansion_probe.materially_different_shots_checked must be an integer")
        else:
            errors.append("missing expansion_probe.materially_different_shots_checked")

    if stage == "full-export":
        impl = nested(state, "full_film", "implementation_status")
        visual = nested(state, "full_film", "visual_review_status")
        preflight = nested(state, "render_preflight", "status")
        add(implementation_passes(impl), "full_film.implementation_status is not complete", errors)
        add(value_passes(visual), "full_film.visual_review_status must pass", errors)
        add(value_passes(preflight), "render_preflight.status must pass", errors)

        playback = state.get("continuous_playback_review")
        if not isinstance(playback, dict):
            warnings.append(
                "continuous_playback_review is missing; do not claim full continuous-view approval from static checks"
            )
        elif not value_passes(playback.get("status")):
            warnings.append(
                "continuous_playback_review is not pass; export may be technically allowed but full visual-completion claim is not supported"
            )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="project root containing manifest/ and storyboard/")
    parser.add_argument(
        "--stage",
        choices=("sample", "scale", "full-export"),
        default="scale",
        help="gate to evaluate",
    )
    args = parser.parse_args()

    errors, warnings = validate(args.project, args.stage)
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"FAIL: {error}")

    if errors:
        print(f"RESULT: BLOCKED ({len(errors)} failure(s))")
        return 1

    print(f"RESULT: PASS ({args.stage})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
