# Sequence and Full-Film Review

Single-shot validity does not prove that a sequence reads well. Run
`scripts/review_sequence.py` after the canonical storyboard validator and
before renderer handoff to inspect repeated visual logic, cognitive release,
handoff integrity, reference compatibility, motion balance, and the planned
energy curve.

The review separates structural errors from editorial warnings. Errors block
handoff because the contract or a stable reference is invalid. Warnings are
prompts for human or agent review; they do not turn aesthetic taste into a hard
production gate.

## Command

```bash
python3 scripts/review_sequence.py \
  projects/<project_id>/storyboard/storyboard.jsonl \
  --director-summary projects/<project_id>/storyboard/director_summary.md \
  --render-review projects/<project_id>/storyboard/render-review.json \
  --output projects/<project_id>/storyboard/sequence-review.json
```

`director_summary.md` and rendered-review JSON are optional. Their presence is
recorded in the report so later review can distinguish contract-only analysis
from a review that also had editorial or rendered context. The deterministic
rules do not claim to inspect pixels.

The command exits non-zero when any `error` finding exists. Warnings alone keep
the exit code at zero.

## Finding contract

Every finding contains:

```json
{
  "severity": "warning",
  "shot_ids": ["S04", "S05", "S06"],
  "rule": "repeated_visual_pattern",
  "message": "Review the repeated visual logic and its editorial purpose"
}
```

Stable severities are `error` and `warning`. Stable rules currently include:

| Rule | Severity | Meaning |
| --- | --- | --- |
| `contract_error` | error | A shot fails the canonical structural contract |
| `beat_progression` | error | Beat positions are not contiguous |
| `handoff_contract` | error | Anchors, continuity axis, or contrast reason are invalid |
| `unsupported_shot_language` | error | A selected family is missing, unexplained, or incompatible with the action |
| `unsupported_shot_recipe` | error | A selected recipe is missing, unexplained, or incompatible with the family/action |
| `repeated_visual_pattern` | warning | Three or more consecutive shots repeat both visual mode and action |
| `missing_cognitive_release` | warning | A complex peak has neither a protected hold nor a following pause |
| `unbalanced_motion_budget` | warning | Supporting motion competes with primary information motion |

The repetition and complexity thresholds are diagnostics, not aesthetic laws.
A repeated pattern may be intentional, and a dense shot may remain readable
without a separate pause. Resolve warnings by inspecting the narration,
evidence burden, and rendered sequence rather than mechanically changing a
layout.

## Energy curve

`energy_curve` records one annotation per shot:

`shot_id,beat_id,role_in_beat,visual_action,complexity,energy,reading_hold`

`complexity` is `complex` when a shot has at least three development states or
at least four on-screen text items; otherwise it is `simple`. `energy` is a
small `low/medium/high` annotation derived from semantic action and primary
motion intensity. These values make consecutive density and release visible;
they do not prescribe a fixed number of energetic shots per chapter.

## Review order

1. Run `scripts/validate_storyboard.py` for the canonical shot and sequence
   contract.
2. Run `scripts/review_sequence.py` and resolve every error.
3. Inspect warnings against the actual Beat progression and narration.
4. After rendering representative frames or a sequence, revisit warnings with
   the rendered-review metadata available.
5. Preserve unresolved editorial warnings in the handoff instead of silently
   treating them as passed.

Sequence review complements Evidence, Timed Attention Cue, Render Review, and
Render Reliability. It cannot authenticate a report, prove a cue lands on the
right frame, judge legibility, or verify an exported media file.
