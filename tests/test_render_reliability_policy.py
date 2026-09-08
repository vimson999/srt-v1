from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def assert_contains(path: Path, snippets: list[str]) -> None:
    content = path.read_text(encoding="utf-8").lower()
    missing = [snippet for snippet in snippets if snippet.lower() not in content]
    if missing:
        raise SystemExit(f"FAIL {path}: missing {missing}")


assert_contains(
    ROOT / "SKILL.md",
    [
        "scope boundary",
        "repeatable rules",
        "references/render-reliability.md",
        "render segments muted",
        "writable temporary storage",
    ],
)
assert_contains(
    ROOT / "references" / "render-reliability.md",
    [
        "preflight",
        "smoke render",
        "render ledger",
        "retry only that range",
        "assemble the correctly trimmed or source-ranged audio once",
        "never delete a broad cache",
        "actual duration and frame count",
    ],
)
assert_contains(
    ROOT / "references" / "output-contracts.md",
    [
        "render_manifest.json",
        "start_frame,end_frame",
        "audio_mode",
    ],
)

print("PASS: render reliability and generic-scope policy")
