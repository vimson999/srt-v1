from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def assert_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8").lower()
    missing = [snippet for snippet in snippets if snippet.lower() not in text]
    if missing:
        raise SystemExit(f"FAIL {path}: missing {missing}")


assert_contains(
    ROOT / "SKILL.md",
    [
        "reuse existing assets for the full-length composition",
        "material quantity is not a production blocker",
        "looping is allowed",
        "report reuse separately from unique footage",
    ],
)
assert_contains(
    ROOT / "references" / "asset-library.md",
    [
        "looping and reuse are allowed",
        "do not treat additional footage as required",
    ],
)
assert_contains(
    ROOT / "references" / "workflow.md",
    [
        "reuse existing assets",
        "unique footage is a quality diagnostic, not a go/no-go gate",
    ],
)

print("PASS: full-length reuse policy")
