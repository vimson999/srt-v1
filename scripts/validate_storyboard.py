#!/usr/bin/env python3
"""Validate the renderer-agnostic V2 storyboard JSONL contract."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


BEAT_ROLES = frozenset({"establish", "develop", "emphasize", "resolve", "bridge"})
VISUAL_ACTIONS = frozenset(
    {
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
)
CONTINUITY_AXES = frozenset(
    {"position", "direction", "color", "shape", "scale", "data_scale", "none"}
)
REQUIRED_TEXT_FIELDS = (
    "chapter",
    "narration_focus",
    "visual_mode",
    "visual_design",
    "motion",
    "asset_need",
    "start_state",
    "information_delta",
    "information_peak",
    "end_state",
    "attention_target",
    "motion_arc",
    "motion_reason",
    "transition_reason",
)
REQUIRED_FIELDS = (
    "schema_version",
    "shot_id",
    "beat_id",
    "beat_position",
    "role_in_beat",
    "start",
    "end",
    *REQUIRED_TEXT_FIELDS,
    "on_screen_text",
    "development_states",
    "reading_hold",
    "visual_action",
    "motion_budget",
    "exit_anchor",
    "entry_anchor",
    "continuity_axis",
    "contrast_reason",
)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _context(line_number: int, shot_id: Any) -> str:
    return f"line {line_number} shot {shot_id or '<missing>'}"


def _validate_anchor(value: Any, field: str, context: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, dict):
        return [f"{context}: {field} must be null or an object"]
    errors: list[str] = []
    for key in ("anchor_id", "kind", "description"):
        if not _text(value.get(key)):
            errors.append(f"{context}: {field}.{key} must be non-empty text")
    return errors


def _validate_motion_layer(value: Any, field: str, context: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{context}: {field} must be an object"]
    errors: list[str] = []
    for key in ("action", "layer", "intensity"):
        if not _text(value.get(key)):
            errors.append(f"{context}: {field}.{key} must be non-empty text")
    return errors


def validate_record(record: dict, line_number: int = 1) -> list[str]:
    """Return all structural errors found in one storyboard shot record."""
    if not isinstance(record, dict):
        return [f"line {line_number}: shot record must be a JSON object"]

    context = _context(line_number, record.get("shot_id"))
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"{context}: missing required field {field}")

    if record.get("schema_version") != 2:
        errors.append(f"{context}: schema_version must be 2")

    for field in ("shot_id", "beat_id", *REQUIRED_TEXT_FIELDS):
        if field in record and not _text(record[field]):
            errors.append(f"{context}: {field} must be non-empty text")

    if "beat_position" in record and (
        not isinstance(record["beat_position"], int)
        or isinstance(record["beat_position"], bool)
        or record["beat_position"] < 1
    ):
        errors.append(f"{context}: beat_position must be an integer >= 1")

    if record.get("role_in_beat") not in BEAT_ROLES:
        errors.append(
            f"{context}: role_in_beat must be one of {', '.join(sorted(BEAT_ROLES))}"
        )

    if record.get("visual_action") not in VISUAL_ACTIONS:
        errors.append(
            f"{context}: visual_action must be one of {', '.join(sorted(VISUAL_ACTIONS))}"
        )

    start = record.get("start")
    end = record.get("end")
    if not _is_number(start):
        errors.append(f"{context}: start must be a finite number")
    if not _is_number(end):
        errors.append(f"{context}: end must be a finite number")
    if _is_number(start) and _is_number(end) and end <= start:
        errors.append(f"{context}: end must be greater than start")
    duration = end - start if _is_number(start) and _is_number(end) else None

    if not isinstance(record.get("on_screen_text"), list):
        errors.append(f"{context}: on_screen_text must be an array")

    states = record.get("development_states")
    if not isinstance(states, list) or not states:
        errors.append(f"{context}: development_states must be a non-empty array")
    else:
        previous_start = -math.inf
        state_ids: set[str] = set()
        for index, state in enumerate(states, start=1):
            state_context = f"{context} development_states[{index}]"
            if not isinstance(state, dict):
                errors.append(f"{state_context} must be an object")
                continue
            state_id = state.get("state_id")
            if not _text(state_id):
                errors.append(f"{state_context}.state_id must be non-empty text")
            elif state_id in state_ids:
                errors.append(f"{state_context}.state_id must be unique within the shot")
            else:
                state_ids.add(state_id)
            relative_start = state.get("relative_start")
            if not _is_number(relative_start):
                errors.append(f"{state_context}.relative_start must be a finite number")
            else:
                if relative_start < 0:
                    errors.append(f"{state_context}.relative_start must be >= 0")
                if duration is not None and relative_start > duration:
                    errors.append(
                        f"{state_context}.relative_start must be within the shot duration"
                    )
                if relative_start < previous_start:
                    errors.append(
                        f"{state_context}.relative_start must be non-decreasing"
                    )
                previous_start = relative_start
            for field in ("description", "attention_target"):
                if not _text(state.get(field)):
                    errors.append(f"{state_context}.{field} must be non-empty text")

    reading_hold = record.get("reading_hold")
    if not isinstance(reading_hold, dict):
        errors.append(f"{context}: reading_hold must be an object")
    else:
        required = reading_hold.get("required")
        if not isinstance(required, bool):
            errors.append(f"{context}: reading_hold.required must be boolean")
        min_seconds = reading_hold.get("min_seconds")
        if min_seconds is not None and (
            not _is_number(min_seconds) or min_seconds < 0
        ):
            errors.append(
                f"{context}: reading_hold.min_seconds must be a finite number >= 0"
            )
        if required is True:
            if not _is_number(min_seconds) or min_seconds <= 0:
                errors.append(
                    f"{context}: required reading_hold needs positive min_seconds"
                )
            if not _text(reading_hold.get("reason")):
                errors.append(
                    f"{context}: required reading_hold needs a non-empty reason"
                )

    motion_budget = record.get("motion_budget")
    if not isinstance(motion_budget, dict):
        errors.append(f"{context}: motion_budget must be an object")
    else:
        errors.extend(
            f"{context}: {error}"
            for error in _validate_motion_layer(
                motion_budget.get("primary"), "motion_budget.primary", context
            )
        )
        supporting = motion_budget.get("supporting")
        if supporting is not None:
            if not isinstance(supporting, dict):
                errors.append(
                    f"{context}: motion_budget.supporting must be null or one object"
                )
            else:
                errors.extend(
                    f"{context}: {error}"
                    for error in _validate_motion_layer(
                        supporting, "motion_budget.supporting", context
                    )
                )
        if not _text(motion_budget.get("background_policy")):
            errors.append(f"{context}: motion_budget.background_policy must be non-empty text")

    errors.extend(_validate_anchor(record.get("exit_anchor"), "exit_anchor", context))
    errors.extend(_validate_anchor(record.get("entry_anchor"), "entry_anchor", context))

    for field in ("evidence_refs", "timed_attention_cues"):
        if field in record and not isinstance(record[field], list):
            errors.append(f"{context}: {field} must be an array")

    continuity_axis = record.get("continuity_axis")
    if continuity_axis not in CONTINUITY_AXES:
        errors.append(
            f"{context}: continuity_axis must be one of {', '.join(sorted(CONTINUITY_AXES))}"
        )

    if record.get("contrast_reason") is not None and not _text(record["contrast_reason"]):
        errors.append(f"{context}: contrast_reason must be null or non-empty text")

    return errors


def validate_sequence(records: list[dict]) -> list[str]:
    """Return structural errors that require more than one shot to detect."""
    if not isinstance(records, list):
        return ["storyboard sequence must be an array"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    beat_positions: dict[str, list[int]] = {}
    previous: dict | None = None

    for index, record in enumerate(records, start=1):
        errors.extend(validate_record(record, index))
        if not isinstance(record, dict):
            continue

        shot_id = record.get("shot_id")
        if _text(shot_id):
            if shot_id in seen_ids:
                errors.append(f"line {index} shot {shot_id}: shot_id must be unique")
            seen_ids.add(shot_id)

        beat_id = record.get("beat_id")
        beat_position = record.get("beat_position")
        if _text(beat_id) and isinstance(beat_position, int) and not isinstance(beat_position, bool):
            beat_positions.setdefault(beat_id, []).append(beat_position)

        start = record.get("start")
        end = record.get("end")
        if _is_number(start) and start < 0:
            errors.append(f"line {index} shot {shot_id or '<missing>'}: start must be >= 0")
        if (
            previous is not None
            and _is_number(previous.get("end"))
            and _is_number(start)
            and start < previous["end"]
        ):
            errors.append(
                f"line {index} shot {shot_id or '<missing>'}: shot overlaps the previous shot"
            )

        if previous is not None:
            axis = record.get("continuity_axis")
            if axis == "none":
                if not _text(record.get("contrast_reason")):
                    errors.append(
                        f"line {index} shot {shot_id or '<missing>'}: interior continuity_axis=none needs contrast_reason"
                    )
            elif axis in CONTINUITY_AXES:
                if previous.get("exit_anchor") is None or record.get("entry_anchor") is None:
                    errors.append(
                        f"line {index} shot {shot_id or '<missing>'}: non-none continuity_axis needs exit_anchor and entry_anchor"
                    )

        previous = record

    for beat_id, positions in beat_positions.items():
        expected = list(range(1, len(positions) + 1))
        if positions != expected:
            errors.append(
                f"beat {beat_id}: beat_position must be contiguous from 1; got {positions}"
            )

    return errors


def validate_storyboard(path: Path) -> list[str]:
    """Load and validate a JSONL storyboard file."""
    path = Path(path)
    if not path.exists():
        return [f"{path}: file does not exist"]

    records: list[dict] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: cannot read file: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {line_number}: shot record must be a JSON object")
            continue
        records.append(record)

    errors.extend(validate_sequence(records))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a V2 storyboard JSONL contract")
    parser.add_argument("storyboard", type=Path, help="Path to storyboard/storyboard.jsonl")
    args = parser.parse_args()

    errors = validate_storyboard(args.storyboard)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    shot_count = sum(
        1
        for line in args.storyboard.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    print(f"PASS: valid storyboard ({shot_count} shots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

