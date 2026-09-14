import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "tests" / "fixtures" / "srt-regression"
REGISTRY = LIB / "cases.json"
TIMECODE_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


def seconds(value: str) -> float:
    match = TIMECODE_RE.search(value)
    if not match:
        raise ValueError(value)
    h, m, s, ms = map(int, match.groups())
    return h * 3600 + m * 60 + s + ms / 1000


def last_end(path: Path) -> float:
    latest = 0.0
    for line in path.read_text(encoding="utf-8").splitlines():
        if "-->" not in line:
            continue
        latest = max(latest, seconds(line.split("-->", 1)[1].strip()))
    return latest


if not REGISTRY.exists():
    raise SystemExit("FAIL: missing cases.json")

data = json.loads(REGISTRY.read_text(encoding="utf-8"))
cases = data.get("cases", [])
if not cases:
    raise SystemExit("FAIL: empty SRT regression case library")

registered = set()
for case in cases:
    case_id = case.get("case_id")
    filename = case.get("file")
    if not case_id or not filename:
        raise SystemExit("FAIL: every case needs case_id and file")
    if case_id in registered:
        raise SystemExit(f"FAIL: duplicate case_id {case_id}")
    registered.add(case_id)

    path = LIB / filename
    if not path.exists():
        raise SystemExit(f"FAIL: missing fixture {filename}")
    text = path.read_text(encoding="utf-8")
    first_timing = next((line for line in text.splitlines() if "-->" in line), "")
    if not first_timing.startswith("00:00:00,000"):
        raise SystemExit(f"FAIL: {filename} is not rebased to 00:00:00,000")

    actual_duration = last_end(path)
    declared = float(case.get("duration_seconds", -1))
    if abs(actual_duration - declared) > 0.01:
        raise SystemExit(
            f"FAIL: duration mismatch for {filename}: declared={declared}, actual={actual_duration}"
        )

    if not case.get("primary_failure_classes"):
        raise SystemExit(f"FAIL: {case_id} has no failure-class mapping")
    if not case.get("must_demonstrate"):
        raise SystemExit(f"FAIL: {case_id} has no must_demonstrate assertions")

unregistered_srt = sorted(
    p.name for p in LIB.glob("*.srt") if p.name not in {case["file"] for case in cases}
)
if unregistered_srt:
    raise SystemExit("FAIL: unregistered SRT fixtures: " + ", ".join(unregistered_srt))

print(f"PASS: {len(cases)} SRT regression cases registered and structurally valid")
