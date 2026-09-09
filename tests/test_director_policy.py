from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


skill = read("SKILL.md").lower()
workflow = read("references/workflow.md").lower()
contracts = read("references/output-contracts.md").lower()
pressure = read("tests/pressure-scenarios.md").lower()

checks = {
    "skill defines the director middle layer": "narrative map" in skill and "visual beat" in skill,
    "workflow starts with narrative planning": "narrative map" in workflow and "chapter arc" in workflow,
    "workflow distinguishes beats from shots": "visual beat" in workflow and "execution shot" in workflow,
    "contracts preserve information delta": "information_delta" in contracts,
    "contracts separate plan and render scores": "plan_score" in contracts and "render_score" in contracts,
    "skill limits background-only storytelling": "background" in skill and "structured foreground" in skill,
    "review checks entry peak and exit": "entry" in skill and "peak" in skill and "exit" in skill,
    "pressure tests renderer-independent direction": "renderer" in pressure and "same" in pressure,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)

if failed:
    raise SystemExit(1)
