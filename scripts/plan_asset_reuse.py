#!/usr/bin/env python3
"""Rank shared-library assets and plan honest, inspectable reuse."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


REVIEW_FIELDS = {
    "description",
    "tags",
    "status",
    "selection_status",
    "notes",
    "ownership",
    "source_projects",
    "provenance_status",
    "license_status",
    "resolution_warning",
    "acceptance_basis",
    "use_as",
    "do_not_claim_as",
    "search_text",
    "warnings",
}
PUBLICATION_PROVENANCE = {"verified"}
PUBLICATION_LICENSE = {"cleared", "verified", "public_domain", "owned"}
DECISION_PRIORITY = {
    "primary": 4,
    "fallback": 3,
    "review_required": 2,
    "unavailable": 0,
}


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _catalog_assets(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    assets = catalog.get("assets")
    if not isinstance(assets, list):
        raise ValueError("catalog.assets must be an array")
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            raise ValueError(f"catalog.assets[{index}] must be an object")
        asset_id = _text(asset.get("asset_id"))
        if not asset_id:
            raise ValueError(f"catalog.assets[{index}].asset_id must be non-empty text")
        if asset_id in seen:
            raise ValueError(f"duplicate asset_id: {asset_id}")
        seen.add(asset_id)
        result.append(copy.deepcopy(asset))
    return result


def merge_metadata(
    catalog: dict[str, Any], metadata: dict[str, Any] | None
) -> list[dict[str, Any]]:
    """Merge durable review fields without mutating catalog or computed paths."""
    assets = _catalog_assets(catalog)
    metadata_assets = metadata.get("assets", {}) if isinstance(metadata, dict) else {}
    if not isinstance(metadata_assets, dict):
        raise ValueError("metadata.assets must be an object keyed by asset_id")
    for asset in assets:
        manual = metadata_assets.get(asset["asset_id"], {})
        if not isinstance(manual, dict):
            raise ValueError(f"metadata for {asset['asset_id']} must be an object")
        for field in REVIEW_FIELDS:
            if field in manual:
                asset[field] = copy.deepcopy(manual[field])
    return assets


def _need_keywords(need: dict[str, Any]) -> list[str]:
    keywords = need.get("keywords", [])
    if not isinstance(keywords, list):
        raise ValueError(f"need {need.get('shot_id')}: keywords must be an array")
    result: list[str] = []
    for value in keywords:
        normalized = _normalize(value) if isinstance(value, str) else ""
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def _asset_search_text(asset: dict[str, Any]) -> str:
    values: list[str] = []
    for field in (
        "description",
        "search_text",
        "category",
        "type",
        "use_as",
        "acceptance_basis",
    ):
        value = asset.get(field)
        if isinstance(value, str):
            values.append(value)
    tags = asset.get("tags")
    if isinstance(tags, list):
        values.extend(value for value in tags if isinstance(value, str))
    return _normalize(" ".join(values))


def _matched_terms(need: dict[str, Any], asset: dict[str, Any]) -> list[str]:
    search_text = _asset_search_text(asset)
    return [keyword for keyword in _need_keywords(need) if keyword in search_text]


def _selection_status(asset: dict[str, Any]) -> str:
    return _normalize(
        _text(asset.get("selection_status")) or _text(asset.get("status")) or "unreviewed"
    )


def _role_compatible(need: dict[str, Any], asset: dict[str, Any]) -> bool:
    role = _normalize(_text(need.get("asset_role")))
    if not role:
        return True
    category = _normalize(_text(asset.get("category")))
    asset_type = _normalize(_text(asset.get("type")))
    evidence_asset = (
        any(marker in category for marker in ("report", "evidence", "filing", "logo"))
        or asset_type in {"document", "pdf"}
    )
    if role == "evidence":
        return evidence_asset
    if role == "context":
        return not evidence_asset and (
            any(marker in category for marker in ("context", "broll", "video"))
            or asset_type in {"video", "image"}
        )
    if role == "programmatic":
        return False
    return True


def _publication_gate(asset: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    provenance = _normalize(_text(asset.get("provenance_status")) or "unverified")
    license_status = _normalize(_text(asset.get("license_status")) or "unverified")
    if provenance not in PUBLICATION_PROVENANCE:
        reasons.append("provenance_not_verified")
    if license_status not in PUBLICATION_LICENSE:
        reasons.append("license_not_cleared")
    if _selection_status(asset) == "unreviewed":
        reasons.append("selection_review_required")
    return {"required": bool(reasons), "reasons": reasons}


def _usage_records(usage: dict[str, Any], asset_id: str) -> list[dict[str, Any]]:
    assets = usage.get("assets", {}) if isinstance(usage, dict) else {}
    if not isinstance(assets, dict):
        raise ValueError("usage.assets must be an object keyed by asset_id")
    entry = assets.get(asset_id, {})
    if isinstance(entry, list):
        records = entry
    elif isinstance(entry, dict):
        records = entry.get("uses", [])
    else:
        records = []
    return [record for record in records if isinstance(record, dict)] if isinstance(records, list) else []


def _prior_usage(usage: dict[str, Any], asset_id: str) -> dict[str, Any]:
    records = _usage_records(usage, asset_id)
    last = records[-1] if records else {}
    return {
        "count": len(records),
        "last_project_id": last.get("project_id"),
        "last_shot_id": last.get("shot_id"),
    }


def _decision(
    asset: dict[str, Any], matched_terms: list[str], role_compatible: bool
) -> str:
    if not matched_terms or not role_compatible:
        return "unavailable"
    if asset.get("file_exists") is False:
        return "unavailable"
    status = _selection_status(asset)
    if status == "reject":
        return "unavailable"
    if status == "keep":
        return "primary"
    if status in {"backup", "transition_only"}:
        return "fallback"
    return "review_required"


def _candidate_card(
    need: dict[str, Any], asset: dict[str, Any], usage: dict[str, Any]
) -> dict[str, Any]:
    matched = _matched_terms(need, asset)
    role_compatible = _role_compatible(need, asset)
    decision = _decision(asset, matched, role_compatible)
    warnings: list[str] = []
    resolution_warning = asset.get("resolution_warning")
    if isinstance(resolution_warning, str) and resolution_warning.strip():
        warnings.append(resolution_warning.strip())
    asset_warnings = asset.get("warnings")
    if isinstance(asset_warnings, list):
        warnings.extend(
            warning.strip()
            for warning in asset_warnings
            if isinstance(warning, str) and warning.strip() and warning.strip() not in warnings
        )
    prior = _prior_usage(usage, asset["asset_id"])
    return {
        "asset_id": asset["asset_id"],
        "shot_id": need["shot_id"],
        "visual_action": need.get("visual_action"),
        "shot_language": need.get("shot_language"),
        "decision": decision,
        "semantic_fit": {
            "score": len(matched),
            "matched_terms": matched,
            "role_compatible": role_compatible,
            "basis": asset.get("acceptance_basis") or "catalog metadata match",
        },
        "intended_use": asset.get("use_as") or need.get("purpose"),
        "prohibited_interpretation": asset.get("do_not_claim_as"),
        "publication_gate": _publication_gate(asset),
        "prior_usage": prior,
        "selection_status": _selection_status(asset),
        "provenance_status": asset.get("provenance_status"),
        "license_status": asset.get("license_status"),
        "resolution_warning": resolution_warning,
        "warnings": warnings,
    }


def _rank_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        cards,
        key=lambda card: (
            -DECISION_PRIORITY[card["decision"]],
            -card["semantic_fit"]["score"],
            card["prior_usage"]["count"],
            card["asset_id"],
        ),
    )


def _treatment_variation(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    if previous is None:
        return {"varied": False, "dimensions": []}
    dimensions = sorted(
        key
        for key in set(previous) | set(current)
        if previous.get(key) != current.get(key)
    )
    return {"varied": bool(dimensions), "dimensions": dimensions}


def _validate_needs(needs: list[dict[str, Any]]) -> None:
    if not isinstance(needs, list):
        raise ValueError("needs must be an array")
    seen: set[str] = set()
    for index, need in enumerate(needs, start=1):
        if not isinstance(need, dict):
            raise ValueError(f"needs[{index}] must be an object")
        shot_id = _text(need.get("shot_id"))
        if not shot_id:
            raise ValueError(f"needs[{index}].shot_id must be non-empty text")
        if shot_id in seen:
            raise ValueError(f"duplicate need shot_id: {shot_id}")
        seen.add(shot_id)
        if not _text(need.get("purpose")):
            raise ValueError(f"need {shot_id}: purpose must be non-empty text")
        _need_keywords(need)
        treatment = need.get("treatment")
        if treatment is not None and not isinstance(treatment, dict):
            raise ValueError(f"need {shot_id}: treatment must be an object")


def plan_asset_reuse(
    needs: list[dict[str, Any]],
    catalog: dict[str, Any],
    usage: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build ranked candidate cards and an honest, reuse-aware assignment plan."""
    _validate_needs(needs)
    assets = merge_metadata(catalog, metadata)
    candidates_by_shot: dict[str, list[dict[str, Any]]] = {}
    assignments: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    previous_assignment: dict[str, Any] | None = None

    for need in needs:
        shot_id = need["shot_id"]
        cards = _rank_cards([_candidate_card(need, asset, usage) for asset in assets])
        candidates_by_shot[shot_id] = cards
        selected = next(
            (card for card in cards if card["decision"] != "unavailable"), None
        )
        if selected is None:
            gaps.append(
                {
                    "shot_id": shot_id,
                    "need": need["purpose"],
                    "reason": "no_honest_available_candidate",
                    "genuine": True,
                }
            )
            previous_assignment = None
            continue

        treatment = copy.deepcopy(need.get("treatment") or {})
        immediately_reused = (
            previous_assignment is not None
            and previous_assignment["selected_asset_id"] == selected["asset_id"]
        )
        previous_treatment = previous_assignment["treatment"] if immediately_reused else None
        variation = _treatment_variation(previous_treatment, treatment)
        repetition_warning = None
        if immediately_reused and not variation["varied"]:
            repetition_warning = {
                "rule": "immediate_identical_reuse",
                "message": "The same asset is reused in adjacent shots with an identical treatment",
            }
        assignment = {
            "shot_id": shot_id,
            "visual_action": need.get("visual_action"),
            "shot_language": need.get("shot_language"),
            "selected_asset_id": selected["asset_id"],
            "decision": selected["decision"],
            "semantic_fit": selected["semantic_fit"],
            "publication_gate": selected["publication_gate"],
            "prohibited_interpretation": selected["prohibited_interpretation"],
            "prior_usage": selected["prior_usage"],
            "treatment": treatment,
            "treatment_variation": variation,
            "repetition_warning": repetition_warning,
            "resolution_warning": selected["resolution_warning"],
        }
        assignments.append(assignment)
        previous_assignment = assignment

    return {
        "schema_version": 1,
        "candidates_by_shot": candidates_by_shot,
        "assignments": assignments,
        "gaps": gaps,
        "summary": {
            "need_count": len(needs),
            "assignment_count": len(assignments),
            "genuine_gap_count": len(gaps),
            "publication_gate_count": sum(
                assignment["publication_gate"]["required"] for assignment in assignments
            ),
            "immediate_identical_reuse_count": sum(
                assignment["repetition_warning"] is not None for assignment in assignments
            ),
        },
    }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def _load_sidecar(explicit: Path | None, default: Path) -> dict[str, Any] | None:
    path = explicit or default
    if explicit is not None and not path.exists():
        raise ValueError(f"{path}: file does not exist")
    if not path.exists():
        return None
    return _load_json(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan semantic asset reuse from a shared catalog")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--usage", type=Path)
    parser.add_argument("--needs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        catalog = _load_json(args.catalog)
        metadata = _load_sidecar(
            args.metadata, args.catalog.with_name("metadata.json")
        )
        usage = _load_sidecar(
            args.usage, args.catalog.with_name("usage.json")
        ) or {"assets": {}}
        needs_document = _load_json(args.needs)
        needs = needs_document.get("needs")
        report = plan_asset_reuse(needs, catalog, usage, metadata)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(
        f"PASS: planned {report['summary']['assignment_count']} assignments; "
        f"{report['summary']['genuine_gap_count']} genuine gaps"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
