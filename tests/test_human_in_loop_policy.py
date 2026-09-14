from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


skill = read("SKILL.md").lower()
policy = read("references/human-in-loop.md").lower()

checks = {
    "skill routes to human-in-loop policy": "references/human-in-loop.md" in skill,
    "default production is autonomous": "autonomous production" in skill and "autonomous production" in policy,
    "standing authorization is explicit": "standing authorization" in skill and "standing authorization" in policy,
    "confirmation is not quality control": "confirmation is not a quality-control mechanism" in skill,
    "known regressions are self-repaired": "repair it autonomously" in skill and "repair it autonomously" in policy,
    "explicit review checkpoint remains valid": "explicit review checkpoint" in skill and "explicit review checkpoint" in policy,
    "external consequential actions still stop": "externally consequential" in skill and "consequential external action" in policy,
    "old ceremonial three-checkpoint contract removed": "keep the user-facing workflow to three checkpoints" not in skill,
    "old export confirmation ritual removed": "start a long mp4 render only after an explicit request" not in skill,
    "user approval is not qa evidence": "do not use user confirmation" in skill,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)

if failed:
    raise SystemExit("human-in-loop policy regression: " + "; ".join(failed))
