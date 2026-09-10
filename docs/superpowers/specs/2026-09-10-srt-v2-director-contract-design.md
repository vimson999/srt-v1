# SRT Visual Director V2 Director Contract

**Status:** Approved for staged implementation by the user in the continuation request.

**Goal:** Upgrade `srt-v1` from a strong single-shot guidance skill into a sequence-aware visual-director contract that describes how information enters, develops, peaks, holds, and hands off between shots.

## Baseline and scope

The repository is at the initial `feat: initialize srt visual director skill` commit. It already contains the reusable SRT initialization workflow, shared asset-library policy, Evidence rules, subtitle-aware handoff guidance, Render Review expectations, and Render Reliability guidance. It does not yet materialize a machine-readable storyboard contract for the middle directing layer.

V2 adds only the missing middle contract:

```text
Narrative Map → Chapter → Visual Beat → Shot → Shot States → Visual Action → Shot Language → Renderer
```

`Visual Beat` is the existing editorial unit that groups shots into one understandable visual sentence. V2 does not add a separate `Shot Group` layer. Evidence, Timed Attention Cue, Render Review, and Render Reliability remain separate source/QA responsibilities and are referenced by the new shot contract rather than reimplemented there.

## Design decisions

### One canonical rich storyboard contract

`storyboard/storyboard.jsonl` is the canonical Phase 1 artifact. Each non-empty line is one executable shot record. `storyboard/storyboard.csv` remains a compact, backward-compatible review/export surface; it is not a second source of truth for the rich fields.

The record keeps the existing timing and editorial fields and adds the missing directing fields. Existing lifecycle names `start_state`, `information_delta`, and `end_state` are preserved. The state machine is completed with `development_states`, `information_peak`, and `reading_hold` rather than renaming fields or creating an alternate state model.

### Beat progression

Every shot carries `beat_id`, `beat_position`, and `role_in_beat`. The role vocabulary is intentionally small:

`establish`, `develop`, `emphasize`, `resolve`, `bridge`.

Positions start at 1 within each beat and increase without gaps in timeline order. This expresses Beat progression without introducing another hierarchy. A beat can therefore move from evidence establishment, through accumulation or emphasis, to a conclusion or bridge into the next beat.

### Shot information state

The state contract is explicit but renderer-agnostic:

- `start_state`: what the viewer sees or understands on entry.
- `development_states`: ordered state changes during the shot. Each state has a stable `state_id`, a relative cue position, a description, and an attention target.
- `information_peak`: the most important visual conclusion of the shot.
- `reading_hold`: whether the peak needs protected reading time, an optional minimum hold, and the editorial reason.
- `information_delta`: the understanding gained across the shot.
- `end_state`: what is true when the shot exits.

`reading_hold.min_seconds` is shot guidance, not a global duration rule. A renderer may honor it, but the director must still justify the hold in `reading_hold.reason`.

### Visual Action and motion budget

`visual_action` names the semantic operation performed by the shot. The initial vocabulary is:

`establish`, `focus`, `compare`, `accumulate`, `causal`, `verify`, `turn`, `conclude`, `pause`.

One primary semantic action is required. `motion_budget` records one primary motion responsibility, an optional supporting motion, and a background policy. The contract makes the attention hierarchy inspectable without requiring a fixed animation library or forcing every shot to animate.

### Shot handoff

Each record has a direct handoff contract:

`transition_reason`, `exit_anchor`, `entry_anchor`, `continuity_axis`, and `contrast_reason`.

Anchors identify the visual object or property that carries attention across the cut. `continuity_axis` may be `position`, `direction`, `color`, `shape`, `scale`, `data_scale`, or `none`. An intentional discontinuity uses `none` plus a non-empty `contrast_reason`; the validator does not force a decorative transition when a clean hard cut is editorially correct.

The first shot may have a null entry anchor and the final shot may have a null exit anchor. All interior transitions must either provide anchors and a continuity axis or explicitly justify the contrast.

## Canonical record shape

The following is a valid illustrative record, not an episode-specific source of truth:

```json
{
  "schema_version": 2,
  "shot_id": "S01",
  "beat_id": "B01",
  "beat_position": 1,
  "role_in_beat": "establish",
  "start": 0.0,
  "end": 4.5,
  "chapter": "evidence",
  "narration_focus": "建立报告证据语境",
  "visual_mode": "REPORT_EVIDENCE",
  "visual_design": "Authentic report page with a restrained readability layer",
  "on_screen_text": ["Institutional report"],
  "motion": "enter → verify → hold",
  "asset_need": "authentic_report_page",
  "start_state": "The report page is present but not yet identified",
  "development_states": [
    {
      "state_id": "S01-state-1",
      "relative_start": 0.0,
      "description": "Locate the source page and institution mark",
      "attention_target": "report-page"
    },
    {
      "state_id": "S01-state-2",
      "relative_start": 1.4,
      "description": "Mark the exact evidence region",
      "attention_target": "target-price-region"
    }
  ],
  "information_peak": "The viewer can identify the authentic report as the evidence source",
  "reading_hold": {
    "required": true,
    "min_seconds": 1.0,
    "reason": "The source identity must remain readable before the next comparison"
  },
  "information_delta": "The source becomes attributable rather than generic context",
  "end_state": "The evidence region is ready to become the next shot's comparison anchor",
  "attention_target": "target-price-region",
  "motion_arc": "enter → locate → verify → hold → handoff",
  "motion_reason": "Verification needs a controlled reveal and a readable hold",
  "visual_action": "verify",
  "motion_budget": {
    "primary": {
      "action": "region_reveal",
      "layer": "evidence",
      "intensity": "medium"
    },
    "supporting": {
      "action": "slow_push",
      "layer": "background",
      "intensity": "low"
    },
    "background_policy": "ambient_only"
  },
  "transition_reason": "Move from source attribution to the first comparable value",
  "exit_anchor": {
    "anchor_id": "target-price-region",
    "kind": "evidence_region",
    "description": "The verified target-price region"
  },
  "entry_anchor": null,
  "continuity_axis": "none",
  "contrast_reason": null,
  "evidence_refs": ["report-page-01"],
  "timed_attention_cues": []
}
```

## Validation rules

The dependency-free `scripts/validate_storyboard.py` validates:

1. required legacy and V2 fields;
2. field types, supported role/action/axis values, and time ordering;
3. ordered development states within the shot;
4. reading-hold semantics;
5. one primary motion budget with at most one supporting motion;
6. unique shot IDs and contiguous beat positions;
7. interior handoff contracts, including justified intentional contrast cuts.

The validator reports all errors with line/shot context and exits non-zero for invalid JSONL. It does not judge aesthetic quality, exact source claims, or rendered pixels; those remain the responsibility of Evidence review, Timed Attention Cue review, Render Review, and Render Reliability.

## Staged delivery

### Phase 0 — Plan and contract baseline

Commit the design and implementation plan, record the current test-environment limitation, and keep the branch isolated.

### Phase 1 — Director middle layer

Add the canonical JSONL contract, validator, initialization skeleton, CSV projection header, references, templates, and tests for Beat progression, Shot Information State, Visual Action, Motion Budget, and Shot Handoff.

### Phase 2 — Shot Language registry

Map semantic actions to reusable shot-language families without copying a card library. Each family documents fit, non-fit, lifecycle, motion personality, and transition behavior.

### Phase 3 — Shot Recipes and references

Turn selected shot languages into renderer-agnostic recipes with reference implementations and renderer adapters. Keep the recipe downstream of semantic action and state, not the other way around.

### Phase 4 — Sequence and full-film review

Add Beat/sequence checks for visual energy, layout repetition, attention handoff, evidence prominence, breathing room, and contrast justification. Review consecutive shots and representative renders, not only isolated frames.

### Phase 5 — Asset organization and automation

Use OpenMontage-inspired indexing, semantic retrieval, usage history, and reuse-aware assembly while preserving the current asset-library provenance, acceptance, and licensing boundaries.

