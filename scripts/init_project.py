#!/usr/bin/env python3
"""Initialize a renderer-agnostic visual-director project from a final SRT.

This utility is intentionally dependency-free. It creates the standard
projects/<project_id>/ skeleton, initializes the shared asset-library sibling
and its project drop zone, copies the SRT, extracts a clean script.txt, and
writes project.json. It never overwrites an existing project.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

TIMECODE_RE = re.compile(
    r"^\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}(?:\s+.*)?$"
)
TAG_RE = re.compile(r"<[^>]+>")
SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def sanitize_project_id(value: str) -> str:
    value = value.strip().replace(" ", "_")
    value = SAFE_ID_RE.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_-")
    return value.lower() or "untitled_project"


def srt_to_script(srt_text: str) -> str:
    """Extract narration text from SRT while preserving subtitle order."""
    paragraphs: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if current:
            text = " ".join(part.strip() for part in current if part.strip()).strip()
            if text:
                paragraphs.append(text)
            current = []

    for raw_line in srt_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line.isdigit() or TIMECODE_RE.match(line):
            continue
        line = TAG_RE.sub("", line).strip()
        if line:
            current.append(line)

    flush()
    return "\n".join(paragraphs) + ("\n" if paragraphs else "")


def initialize_project(
    factory_root: Path,
    srt_path: Path,
    *,
    project_id: str | None = None,
    profile: str = "finance",
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    subtitle_burn_in: bool = True,
) -> Path:
    factory_root = factory_root.expanduser().resolve()
    srt_path = srt_path.expanduser().resolve()

    if not srt_path.exists():
        raise FileNotFoundError(f"SRT not found: {srt_path}")
    if srt_path.suffix.lower() != ".srt":
        raise ValueError(f"Expected .srt input, got: {srt_path.name}")

    pid = sanitize_project_id(project_id or srt_path.stem)
    projects_root = factory_root / "projects"
    project = projects_root / pid

    if project.exists():
        raise FileExistsError(
            f"Project already exists: {project}. Continue it explicitly or choose another project_id; no overwrite performed."
        )

    dirs = [
        "input",
        "storyboard",
        "data",
        "manifest",
        "output/preview",
        "output/final",
        "scripts",
    ]
    for rel in dirs:
        (project / rel).mkdir(parents=True, exist_ok=True)

    asset_library_dirs = [
        f"inbox/{pid}",
        "raw/video",
        "raw/images",
        "raw/reports",
        "raw/logos",
        "processed/video",
        "processed/images",
        "processed/thumbnails",
        "catalog",
    ]
    asset_library = factory_root / "asset-library"
    for rel in asset_library_dirs:
        (asset_library / rel).mkdir(parents=True, exist_ok=True)

    catalog_defaults = {
        "catalog/assets.json": {
            "schema_version": 1,
            "library_id": "report-video-asset-library",
            "root": "asset-library",
            "resolution_key": "asset_id",
            "assets": [],
        },
        "catalog/metadata.json": {
            "schema_version": 1,
            "library_id": "report-video-asset-library",
            "description": "人工或 AI 审核后保存的稳定素材说明；不要把它当作自动索引临时文件。",
            "assets": {},
        },
        "catalog/review_queue.json": {
            "schema_version": 1,
            "library_id": "report-video-asset-library",
            "items": [],
        },
        "catalog/usage.json": {
            "schema_version": 1,
            "library_id": "report-video-asset-library",
            "projects": [],
            "assets": {},
        },
    }
    for rel, payload in catalog_defaults.items():
        catalog_path = asset_library / rel
        if not catalog_path.exists():
            catalog_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    shutil.copy2(srt_path, project / "input" / "subtitles.srt")
    srt_text = srt_path.read_text(encoding="utf-8-sig", errors="replace")
    (project / "input" / "script.txt").write_text(
        srt_to_script(srt_text), encoding="utf-8"
    )

    # Placeholders are valid JSON and intentionally empty until later phases.
    placeholders = {
        "storyboard/timeline.json": {},
        "data/financials.json": {},
        "data/charts.json": {},
        "data/institutions.json": {},
        "manifest/assets.json": {
            "schema_version": 1,
            "asset_library": {
                "root": "../../asset-library",
                "catalog": "../../asset-library/catalog/assets.json",
                "drop_zone": f"../../asset-library/inbox/{pid}",
                "resolution": "asset_id",
                "remotion_mount": "assets",
            },
            "assets": [],
        },
        "manifest/shot_assets.json": {
            "schema_version": 1,
            "asset_library": {
                "root": "../../asset-library",
                "catalog": "../../asset-library/catalog/assets.json",
                "drop_zone": f"../../asset-library/inbox/{pid}",
                "resolution": "asset_id",
            },
            "shots": [],
        },
        "manifest/missing_assets.json": {"schema_version": 1, "items": []},
    }
    for rel, payload in placeholders.items():
        (project / rel).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    project_json = {
        "schema_version": 1,
        "project_id": pid,
        "profile": profile,
        "source": "input/subtitles.srt",
        "status": "director_planning",
        "aspect_ratio": f"{width // _gcd(width, height)}:{height // _gcd(width, height)}",
        "width": width,
        "height": height,
        "fps": fps,
        "subtitle_burn_in": subtitle_burn_in,
        "asset_library": {
            "root": "../../asset-library",
            "catalog": "../../asset-library/catalog/assets.json",
            "drop_zone": f"../../asset-library/inbox/{pid}",
            "resolution": "asset_id",
            "remotion_mount": "assets",
        },
        "renderer": None,
    }
    (project / "project.json").write_text(
        json.dumps(project_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return project


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize an srt-visual-director project")
    parser.add_argument("srt", type=Path, help="Final SRT file")
    parser.add_argument(
        "--factory-root",
        type=Path,
        default=Path.cwd(),
        help="Root containing/receiving projects/ (default: current directory)",
    )
    parser.add_argument("--project-id", help="Override project id; defaults to sanitized SRT filename")
    parser.add_argument("--profile", default="finance")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--no-burn-subtitles", action="store_true")
    args = parser.parse_args()

    project = initialize_project(
        args.factory_root,
        args.srt,
        project_id=args.project_id,
        profile=args.profile,
        width=args.width,
        height=args.height,
        fps=args.fps,
        subtitle_burn_in=not args.no_burn_subtitles,
    )
    print(project)


if __name__ == "__main__":
    main()
