# Execution Handoff

## Renderer boundary

The visual-director output is renderer-agnostic. Remotion, HyperFrames, Premiere, AE, or another engine consumes the same storyboard/timeline/assets contracts.

Do not let the renderer redesign source-of-truth data unless an explicit error is found.

The renderer is selected after the narrative map, visual beats, execution shots,
and representative review are valid. HyperFrames and Remotion are execution
choices, not substitutes for visual direction. To compare renderers, keep the
same approved shot plan, assets, timing, and data on both sides.

## V2 shot contract handoff

The renderer consumes `storyboard/storyboard.jsonl` as the canonical Phase 1
shot contract. It must preserve Beat position/role, the state progression from
`start_state` through `development_states` and `information_peak` to
`end_state`, the chosen `visual_action`, and the `motion_budget`.

When Phase 2 selection is complete, the renderer also consumes
`shot_language.family` as the reusable visual grammar and preserves its
shot-specific `selection_reason`. The family narrows how the lifecycle should
be expressed; it does not authorize the renderer to replace the shot's state,
motion budget, evidence, or handoff contracts.

When a canonical Shot Recipe exists, pass its `id` and declarative
`reference_implementation` to the renderer adapter. The adapter maps the five
ordered lifecycle phases to concrete primitives while preserving source data,
state order, attention cues, reading holds, motion responsibilities, and
handoff anchors. Read `references/shot-recipes.md`; never treat a renderer
component as the source recipe.

Transitions must consume `transition_reason`, `exit_anchor`, `entry_anchor`,
and `continuity_axis`. If `continuity_axis=none`, the renderer may use a clean
hard cut when `contrast_reason` explains the editorial turn. It must not add a
decorative transition merely to hide a missing handoff. Evidence and Timed
Attention Cue data remain the authority for exact source content and cue
timing; Render Review and Render Reliability remain the authority for visual
inspection and export execution.

Before opening the renderer, run `scripts/review_sequence.py` and attach
`storyboard/sequence-review.json`. Resolve every error. Review warnings against
the actual narration and intended energy curve; do not mechanically change a
layout merely to silence a diagnostic threshold. Read
`references/sequence-review.md` for the stable finding contract.

## Recommended persistent engine layout

For repeated programmatic production, prefer one reusable engine and many project folders:

```text
report-video/
  engine/
  asset-library/
  projects/
    project-a/
    project-b/
```

Do not scaffold and reinstall a new Remotion project for every episode when a reusable engine already exists.

Do not copy the shared asset library into an episode. Resolve project
`asset_id` references through the catalog or a documented renderer mount. Keep
project-local media only when it is genuinely owned by that episode.

## Subtitle rule

Any rendered review or final video burns subtitles in by default unless the user opts out.

- SRT is a dedicated caption layer.
- Preserve subtitle timing.
- When rendering an excerpt, apply the correct time offset.
- Keep a subtitle-safe region free from chart labels and critical numbers.
- Do not duplicate full subtitle sentences as foreground explanatory copy.

## First render strategy

1. Validate all JSON and media refs.
2. Complete plan review, then render a representative 30–90s section first if the visual system is unproven.
3. Inspect entry, peak, and exit states plus important 2–4s transitions. For
   multi-target shots, inspect at least two timed cue activations and their
   handoff; record render review separately from plan review.
4. After approval, scale the same design system to the full timeline.
5. Use preview quality first (e.g. 720p) for full-length V1; render final 1080p after review.

For high-background finance programs, include a coverage report in the handoff:
target coverage, measured coverage, unique usable footage seconds, semantic
alternates, and any conspicuous reuse. Background visibility/opacity is a
separate visual check from coverage.

For the operational preflight, segmented retry strategy, audio muxing, temp-file
safety, and post-render media verification, read
`references/render-reliability.md`. Keep those mechanics renderer-agnostic so
the same handoff applies when the engine changes.
