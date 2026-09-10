# Visual Quality Review

Use this reference after the execution plan exists and before a full export.
Textual planning and rendered appearance answer different questions, so keep
the reviews separate.

## Hard gates

Every shot must pass these gates before it can be approved, regardless of its
function:

- no misleading identity, source, number, or causal implication;
- source status agrees with how the shot is presented;
- critical text, numbers, labels, and captions are readable;
- charts and evidence remain outside the subtitle safe zone;
- all asset, chart, data, font, and media references resolve;
- source and local timecodes are valid;
- the shot is executable by the selected renderer;
- the audio/caption timing contract is preserved.
- every timed attention cue resolves to a visible target and does not hide or
  distort the underlying evidence.

Record the result as `hard_gate_status=pass|fail|needs_review`. A low soft score
does not excuse a hard-gate failure.

## Function-weighted soft review

Score each dimension from 0–5, then choose weights according to `shot_function`:

- claim fit — does the visual make the narrated claim clearer?
- specificity — is it concrete enough for the responsibility of the claim?
- information progression — is the `information_delta` visible?
- hierarchy — is there one clear attention target and readable order?
- rhythm — do holds, entrances, exits, and transitions fit the narration?
- continuity or contrast — is the relation to adjacent shots intentional?
- repetition — is reuse treated deliberately rather than mechanically?

An atmosphere opener may weight rhythm and setting above specificity. An
evidence shot may weight source fidelity, readability, and hierarchy above
novelty. A comparison may weight shared scale and information progression above
background coverage. Do not fail a purposeful pause merely because its motion
score is low.

Store the weighted result as `plan_score` before rendering and `render_score`
after rendering. Keep reviewer notes and the failing dimension next to the
score so a revision has a clear target.

## Review sequence

### 1. Plan review

Review the narrative map, chapter arcs, visual beats, and execution shots. Check
that every beat has a start state, information delta, end state, attention
target, visual responsibility, and cut reason. Look for:

- a direct SRT-to-template rotation;
- numbers or conclusions expressed only through mood footage;
- a beat whose end state is unchanged without a continuity or pause reason;
- evidence requested for every continuation shot even when one source already
  fulfills the beat;
- transitions that hide a missing argument rather than move the argument.

### 2. Representative render review

Render a 30–90 second section that exercises the visual system. For each key
shot inspect three states:

1. **Entry frame** — does the viewer know where to look?
2. **Information peak** — can the new fact or relationship be read and understood?
3. **Exit frame** — is the result held long enough and does it hand off cleanly?

Inspect important transitions as a 2–4 second motion sample. Check animation
speed, layering, caption collision, entry/exit behavior, and whether motion
competes with the spoken point.

For a shot with multiple attention targets, inspect more than one cue
activation and the handoff between targets. Confirm that the active target
wins attention, inactive peers remain legible, and the cue starts and settles
inside the correct SRT-derived window.

Review background salience in the final composite, not only foreground-only
frames. Include the brightest evidence-heavy shot and a context-led shot; fail
the review when background highlights or motion compete with the evidence or
captions even if measured video coverage is 100%.

### 3. Full-film review

After the representative section passes, review the full piece at low resolution
for chapter rhythm, attention fatigue, repeated layouts, abrupt transitions,
unresolved claims, and the balance of context, explanation, evidence, and pause.
If a cue behavior was approved as a reusable example, verify that analogous
attention changes across the full timeline received the same decision rule.
Then run the renderer's technical preflight and export. A high background
coverage percentage cannot replace this review.

## Revision protocol

When a review fails, revise the smallest responsible layer:

- wrong argument or missing relationship → narrative map or chapter arc;
- unclear viewer change → visual beat;
- valid idea but unexecutable composition → execution shot;
- readable plan but poor appearance or timing → renderer implementation or motion;
- unsupported exact claim → source/evidence contract, not decorative treatment.

Log the reason, changed artifact, old score, new score, and whether the change
was verified in a render. Do not silently overwrite an approved plan.
