#!/usr/bin/env python3
"""Import newly supplied media into a shared asset-library drop zone.

The agent calls this utility after the user says that requested assets are
ready. It never deletes the supplied files. Imports are content-hash based, so
repeating the same intake is safe and does not create duplicate raw assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}
DOCUMENT_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS
CATEGORIES = {"video", "images", "reports", "logos"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def category_for_path(path: Path) -> str:
    """Respect an optional category folder, otherwise infer conservatively."""
    parts = {part.lower() for part in path.parts[:-1]}
    for category in CATEGORIES:
        if category in parts:
            return category
    extension = path.suffix.lower()
    if extension in VIDEO_EXTENSIONS:
        return "video"
    if extension in DOCUMENT_EXTENSIONS:
        return "reports"
    return "images"


def _candidate_files(source: Path) -> list[Path]:
    if not source.exists():
        return []
    return sorted(
        (
            path
            for path in source.rglob("*")
            if path.is_file()
            and not any(part.startswith(".") for part in path.relative_to(source).parts)
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: str(path).lower(),
    )


def _raw_files(raw_root: Path) -> list[Path]:
    if not raw_root.exists():
        return []
    return sorted((path for path in raw_root.rglob("*") if path.is_file()))


def _destination(raw_root: Path, category: str, source: Path, digest: str) -> Path:
    target = raw_root / category / source.name
    if not target.exists():
        return target
    if sha256_file(target) == digest:
        return target

    stem = source.stem
    suffix = source.suffix
    candidate = target.with_name(f"{stem}__{digest[:8]}{suffix}")
    counter = 2
    while candidate.exists():
        if sha256_file(candidate) == digest:
            return candidate
        candidate = target.with_name(f"{stem}__{digest[:8]}_{counter}{suffix}")
        counter += 1
    return candidate


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def intake_assets(
    factory_root: Path,
    project_id: str,
    source: Path | None = None,
    *,
    run_index: bool = True,
) -> dict:
    """Copy new media from a project's drop zone and refresh the catalog."""
    factory_root = factory_root.expanduser().resolve()
    library_root = factory_root / "asset-library"
    source = (source or library_root / "inbox" / project_id).expanduser().resolve()
    raw_root = library_root / "raw"
    catalog_root = library_root / "catalog"
    source.mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        (raw_root / category).mkdir(parents=True, exist_ok=True)
    catalog_root.mkdir(parents=True, exist_ok=True)

    existing_hashes: dict[str, Path] = {}
    for path in _raw_files(raw_root):
        existing_hashes.setdefault(sha256_file(path), path)

    imported: list[dict] = []
    duplicates: list[dict] = []
    ignored: list[dict] = []

    for candidate in _candidate_files(source):
        digest = sha256_file(candidate)
        if digest in existing_hashes:
            duplicates.append(
                {
                    "source_path": str(candidate),
                    "existing_path": str(existing_hashes[digest]),
                    "sha256": digest,
                }
            )
            continue

        category = category_for_path(candidate.relative_to(source))
        target = _destination(raw_root, category, candidate, digest)
        if target.exists() and sha256_file(target) == digest:
            duplicates.append(
                {
                    "source_path": str(candidate),
                    "existing_path": str(target),
                    "sha256": digest,
                }
            )
            existing_hashes.setdefault(digest, target)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate, target)
        existing_hashes[digest] = target
        imported.append(
            {
                "source_path": str(candidate),
                "raw_path": str(target),
                "category": category,
                "sha256": digest,
            }
        )

    known_suffixes = SUPPORTED_EXTENSIONS
    for candidate in sorted(
        (
            path
            for path in source.rglob("*")
            if path.is_file()
            and not any(part.startswith(".") for part in path.relative_to(source).parts)
            and path.suffix.lower() not in known_suffixes
        ),
        key=lambda path: str(path).lower(),
    ):
        ignored.append({"source_path": str(candidate), "reason": "unsupported_media_type"})

    run_timestamp = datetime.now(timezone.utc)
    log = {
        "schema_version": 1,
        "library_id": "report-video-asset-library",
        "project_id": project_id,
        "source": str(source),
        "updated_at": run_timestamp.isoformat(),
        "imported": imported,
        "duplicates": duplicates,
        "ignored": ignored,
    }
    _write_json(catalog_root / "intake_log.json", log)
    safe_project_id = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in project_id
    ) or "intake"
    _write_json(
        catalog_root / "intake_logs" / f"{run_timestamp.strftime('%Y%m%dT%H%M%S%fZ')}-{safe_project_id}.json",
        log,
    )

    index_updated = False
    warnings: list[str] = []
    builder = catalog_root / "build-index.mjs"
    if run_index:
        if builder.exists():
            subprocess.run(["node", str(builder)], cwd=catalog_root, check=True)
            index_updated = True
        else:
            warnings.append("index_builder_missing")

    return {
        "factory_root": str(factory_root),
        "project_id": project_id,
        "source": str(source),
        "imported_count": len(imported),
        "duplicate_count": len(duplicates),
        "ignored_count": len(ignored),
        "index_updated": index_updated,
        "warnings": warnings,
        "imported": imported,
        "duplicates": duplicates,
        "ignored": ignored,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Intake new media into a shared asset library")
    parser.add_argument("--factory-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--no-index", action="store_true", help="Only import files; skip catalog rebuild")
    args = parser.parse_args()
    result = intake_assets(
        args.factory_root,
        args.project_id,
        args.source,
        run_index=not args.no_index,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
