# Visual Direction

Use this reference when the project has more than a simple title, caption, and
single supporting image. It defines the reusable director layer between the SRT
and any renderer.

## Three layers

Keep three different questions separate:

| Layer | Question | Typical artifact |
| --- | --- | --- |
| Narrative | What is being claimed, supported, challenged, or concluded? | `narrative_map.json`, `chapter_arcs.json` |
| Visual beat | What must the viewer understand now, and what changes by the end of the beat? | `visual_beats.jsonl` |
| Execution shot | What exact timed composition will make that change visible? | `storyboard.jsonl` |

Do not use a larger CSV to hide a missing layer. A table can carry the contracts,
but it must preserve the relationships between claims, beats, and shots.

## Beat versus shot

A beat is an editorial unit of understanding. A shot is an executable interval.
Use multiple shots when the viewer must change attention, layout, evidence, or
source. Keep one shot with several states when continuity helps the viewer read
one unfolding explanation.

Every beat records:

- `start_state`: the visual and editorial state on entry;
- `information_delta`: the new fact, relation, comparison, uncertainty, or conclusion;
- `end_state`: the understanding the viewer should retain;
- `attention_target`: the element that should win attention;
- `cut_reason`: why the beat starts, ends, or changes;
- `visual_responsibility`: `context`, `structured_explanation`, `exact_evidence`, or `mixed`.

Every shot records its `shot_function`, `source_status`, asset role, layout,
motion reason, and transition out. `motion_arc` describes movement; it does not
replace `information_delta`.

## Timed attention cues

Use a timed attention cue when the viewer should stay inside one composition
while the narration changes which visible element matters. Typical triggers are
sequentially named institutions, compared metrics, report facts, chart nodes,
flow steps, risk factors, and conclusion cards.

Each cue maps a source-time window to a stable renderer-visible `target_id`
and records:

- `cue_id`, `shot_id`, `source_start`, and `source_end`;
- `spoken_trigger`: the narrated name, value, or idea that activates it;
- `target_id`: the exact card, row, report region, node, or label to emphasize;
- `emphasis`: the restrained visual change, such as scale, lift, contrast,
  outline, crop, or camera push;
- `inactive_behavior`: how same-level alternatives recede without becoming
  unreadable.

The target should enter, hold through the spoken point, and settle before the
next target wins attention. Motion strength is implementation-specific; use the
smallest change that makes the attention shift legible. Stable holds remain
valid when the narration does not change target.

When the user identifies one successful cue as an example and asks for that
judgment to carry through the film, scan every beat and shot for analogous
attention changes. Generalize the decision rule, not the exact layout or
animation values. Do not limit the revision to the example shot, and do not add
motion to shots that lack a corresponding information or attention change. A
complete scan may legitimately leave most shots uncued; 100% shot motion is not
a completeness metric.

## Function-first visual grammar

Choose a visual grammar because it performs a function, not because the last
shot used a different template.

- `context`: establish setting, atmosphere, or category; related B-roll is often enough.
- `claim`: make the central proposition legible with hierarchy and restraint.
- `evidence`: show an authentic source, exact number, label, or structured data.
- `explanation`: show a process, causal chain, trend, or mechanism with labeled structure.
- `comparison`: place alternatives on a shared scale or aligned frame.
- `transition`: reset attention or move between chapters; do not pretend it proves a claim.
- `pause`: hold the important state so the viewer can read or absorb it.
- `conclusion`: compress the chapter's result and its remaining uncertainty.

Static holds are valid. Use `motion_arc=STATIC_HOLD` with a `motion_reason` such
as “protect reading time” or “give the conclusion weight” when movement would
compete with the information.

## Background responsibility

Background B-roll may provide atmosphere and continuity, but it cannot carry
every kind of meaning:

1. Context, place, and industry mood can use broad semantic footage.
2. Mechanisms, trends, flows, and causal relationships need a structured
   foreground layer even when B-roll remains behind it.
3. Exact numbers, ratings, targets, report conclusions, and named-source claims
   need readable evidence or structured data. Never let a generic clip imply
   exact identity.

Record the background role explicitly as `none_required`, `context_only`, or
`evidence_backing`. A beat with `none_required` is not a missing background;
it may be the correct choice for a readable data hold.

## Continuity and variation

The quality rule is not “every shot must look different.” It is:

> Same has a continuity reason; different has a change reason.

Before reusing a composition, state why the viewer benefits from continuity.
Before changing it, state what new information or attention target requires the
change. Varying crop, scale, speed, opacity, or layout is useful only when it
supports that reason.

## Source status

Use explicit status values such as `verified`, `user_provided`, `narration`, and
`needs_source`. A narration-only claim may be staged as narration, but it must
not be presented as independently verified evidence. Context assets must record
what they may express and what they must not be taken to claim.

## Audience-facing screen copy

Every visible label or explanatory sentence must help the audience understand
the current claim, evidence, comparison, or conclusion. Do not place internal
production language—workflow notes, prompt wording, or statements about how the
video was made—where authentic source evidence should appear. Such process
language is appropriate only when the narration itself discusses that process.

## Renderer boundary

The director chooses the visual argument and its source contracts. Remotion,
HyperFrames, Premiere, After Effects, or another engine implements the same
approved plan. A renderer may expose a technical limitation, but it should not
silently replace an evidence shot with decorative B-roll or redesign the source
of truth.
