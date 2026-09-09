import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").lower()


skill = read("SKILL.md")
direction = read("references/visual-direction.md")
finance = read("references/finance-profile.md")
review = read("references/visual-quality-review.md")
contracts = read("references/output-contracts.md")
reliability = read("references/render-reliability.md")

checks = {
    "skill generalizes accepted examples": "analogous" in skill and "attention cue" in skill,
    "complete scan is not cue coverage": "not cue coverage" in skill and "stay uncued" in skill,
    "direction defines timed attention cues": "timed attention cue" in direction and "target_id" in direction,
    "finance prioritizes named-source evidence": "named-source roll call" in finance and "audience-facing" in finance,
    "finance keeps logos conditional and authentic": "logo" in finance and "authentic" in finance,
    "review inspects cue activation": "cue" in review and "activation" in review and "background salience" in review,
    "contracts define motion cue sidecar": "motion_cues.json" in contracts and "spoken_trigger" in contracts,
    "render ledger is serializable": "json-serializable" in reliability,
    "transient renderer failures use bounded retry": "bounded retry" in reliability,
    "retry timeout is not a universal constant": "universal timeout" in reliability,
    "verification evidence stays proportional": "proportional to" in reliability and "contact sheet" in reliability,
    "gap fillers are homogeneous video": "transparent video" in reliability and "gap filler" in reliability,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)

if failed:
    raise SystemExit(1)


template = json.loads((ROOT / "templates" / "motion_cues.json").read_text(encoding="utf-8"))
if template.get("schema_version") != 1 or template.get("cues") != []:
    raise SystemExit("FAIL: motion cue template must be a valid empty contract")

print("PASS: attention-cue, evidence, salience, and render-gap policy")
