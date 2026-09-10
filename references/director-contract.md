# V2 Director Contract

This reference defines the middle directing layer between an editorial Visual
Beat and a renderer. It is intentionally renderer-agnostic and complements the
existing Evidence, Timed Attention Cue, Render Review, and Render Reliability
contracts.

## Hierarchy

Use the existing hierarchy:

```text
Narrative Map → Chapter → Visual Beat → Shot → Shot States
```

Visual Beat is the grouping unit. It is the visual sentence that may contain
several executable shots; do not add a separate Shot Group layer.

The canonical rich artifact is `storyboard/storyboard.jsonl`, one shot per
non-empty line. `storyboard/storyboard.csv` is only a compact review/export
projection.

## Beat progression

Every shot has a `beat_id`, a one-based `beat_position`, and a `role_in_beat`.
The role vocabulary is deliberately small:

- `establish`: make the visual question or evidence context legible.
- `develop`: add the next meaningful piece of information.
- `emphasize`: focus attention on the most important object or difference.
- `resolve`: let the Beat's visual conclusion settle.
- `bridge`: preserve or hand off the anchor into the next Beat.

Positions must be contiguous within each Beat in timeline order. A six-
institution sequence can therefore use `establish` once, `develop` repeatedly,
`emphasize` for the synchronized focus, and `resolve` or `bridge` for the
consensus and next comparison.

## Shot information state

Keep the lifecycle explicit:

1. `start_state` — what is visible or understood on entry.
2. `development_states` — ordered information changes inside the shot. Each
   object has `state_id`, `relative_start`, `description`, and
   `attention_target`.
3. `information_peak` — the single most important visual conclusion.
4. `reading_hold` — whether the peak needs protected reading time, an optional
   minimum, and the reason that justifies it.
5. `information_delta` — what the viewer understands now that they did not
   understand at the start.
6. `end_state` — the stable state handed to the next shot.

`reading_hold.min_seconds` is a local production hint. It is not a global
fixed-duration rule, and it should not be filled merely because every shot is
expected to have the same rhythm.

## Visual Action

`visual_action` describes the semantic operation, not an effect name:

`establish`, `focus`, `compare`, `accumulate`, `causal`, `verify`, `turn`,
`conclude`, `pause`.

Choose one primary action. A shot may use several small animation primitives,
but they must serve that one information operation. Evidence verification,
comparison, causal explanation, accumulation, and conclusion should not all be
expressed as the same generic scale-up.

## Shot Language selection

After the semantic action is stable, use `templates/shot-language.yaml` to
retrieve compatible Shot Language families. Select against the shot's
information lifecycle, evidence burden, motion budget, and handoff; do not
select by effect novelty or a forced layout rotation.

Record the downstream choice as:

```json
{
  "shot_language": {
    "family": "aligned_comparison",
    "selection_reason": "The target prices need one truthful baseline before the consensus can be judged"
  }
}
```

The selected family must include the shot's `visual_action`, and the reason
must explain the shot-specific information or attention problem. Phase 1
records remain valid before this enrichment; a shot advancing to Shot Recipe
or renderer handoff should have one explainable selection. Read
`references/shot-language.md` for the registry and extension rules.

## Motion Budget

`motion_budget` makes attention priority inspectable:

```json
{
  "primary": {"action": "region_reveal", "layer": "evidence", "intensity": "medium"},
  "supporting": {"action": "slow_push", "layer": "background", "intensity": "low"},
  "background_policy": "ambient_only"
}
```

The primary motion is required. Supporting motion is optional and limited to
one responsibility by default. Background motion is atmosphere, not a second
foreground argument. Do not turn this budget into a fixed animation library or
require every shot to animate.

## Shot handoff

Every shot explains `transition_reason`. An `exit_anchor` is the last visual
object or property that carries attention; an `entry_anchor` is what the next
shot inherits. Anchors contain `anchor_id`, `kind`, and `description`.

`continuity_axis` identifies the carried relation:

`position`, `direction`, `color`, `shape`, `scale`, `data_scale`, or `none`.

For an interior transition, provide anchors and a non-`none` axis, or make the
cut intentionally discontinuous with `continuity_axis=none` and a meaningful
`contrast_reason`. The first shot may have a null entry anchor; the final shot
may have a null exit anchor. A hard cut is a valid editorial choice when its
contrast is explained.

## Boundaries

This contract does not verify whether a report is authentic, whether a number
is correct, whether attention cues land on the right frame, or whether a render
has readable pixels and reliable media output. Those remain the responsibility
of Evidence, Timed Attention Cue, Render Review, and Render Reliability. Use
`scripts/validate_storyboard.py` for structural and sequence validation before
handoff.
