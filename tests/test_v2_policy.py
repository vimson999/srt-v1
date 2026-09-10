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
        "Visual Beat",
        "storyboard/storyboard.jsonl",
        "do not add a separate Shot Group",
        "visual_action",
        "motion_budget",
        "transition_reason",
    ],
)
assert_contains(
    ROOT / "references" / "output-contracts.md",
    [
        "storyboard/storyboard.jsonl",
        "development_states",
        "information_peak",
        "reading_hold",
        "entry_anchor",
        "exit_anchor",
    ],
)
assert_contains(
    ROOT / "references" / "workflow.md",
    [
        "beat progression",
        "information state",
        "one primary semantic action",
        "attention handoff",
    ],
)
assert_contains(
    ROOT / "references" / "execution-handoff.md",
    [
        "exit_anchor",
        "entry_anchor",
        "continuity_axis",
    ],
)
assert_contains(
    ROOT / "references" / "director-contract.md",
    [
        "start_state",
        "development_states",
        "information_peak",
        "reading_hold",
        "visual_action",
        "motion_budget",
        "continuity_axis",
    ],
)

print("PASS: v2 director policy")

