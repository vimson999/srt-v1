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
        "semantic fit over literal visual matching",
        "low-resolution report screenshots are accepted",
        "do not reject or downgrade a user-provided screenshot because of resolution",
    ],
)
assert_contains(
    ROOT / "references" / "asset-library.md",
    [
        "accept user-provided low-resolution report screenshots",
        "resolution is a warning, not an acceptance gate",
    ],
)
assert_contains(
    ROOT / "references" / "finance-profile.md",
    [
        "not a news package",
        "broad meaning is sufficient for context b-roll",
    ],
)
assert_contains(
    ROOT / "references" / "workflow.md",
    [
        "accept user-provided low-resolution report screenshots",
        "semantic fit over literal visual matching",
    ],
)
assert_contains(
    ROOT / "references" / "output-contracts.md",
    [
        "resolution_warning",
        "acceptance_basis",
    ],
)
assert_contains(
    Path("/Users/v9/Downloads/report-video/asset-library/catalog/build-index.mjs"),
    [
        '"resolution_warning"',
        '"acceptance_basis"',
    ],
)

print("PASS: approximate context and low-resolution report acceptance policy")
