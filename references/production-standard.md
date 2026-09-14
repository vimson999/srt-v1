# Standard-driven production

Read before authoring a sample, extending a film, or recovering a quality
regression. A sample tests production decisions; it does not define a separate
quality tier. The full film executes the same decisions over more content.

Also read `failure-regression.md` before scaling a representative sample into a
full film or after any repeated quality failure. The regression rules are stop
conditions, not optional advice.

## 1. Establish the authority before the output

Use three scopes:

- **Reusable rules (this skill):** how to derive, implement and verify visual
  explanations. They survive a different topic, company and renderer.
- **Project standard (`DESIGN.md`):** the brief translated into explicit
  typography, composition, evidence, attention, background, caption and
  transition decisions. Record a `standard_revision`. Each consequential rule
  states when it applies, the visible result required, and how it is checked.
- **Case artifacts:** shot content, exact data, selected media, implementation
  and review evidence. They demonstrate application, not a universal layout.

On continuation, locate the existing brief, DESIGN, active shot contract and
production implementation first. Preserve working authored scenes. Do not
replace available source work with screenshot reconstruction or ask the user
to choose a new visual approach simply because a previous export regressed.

If the standard was never recorded, reconstruct its decision record from the
brief, explicit decisions and available source implementation; label genuinely
inferred choices and resolve material ambiguity. A sample can corroborate a
decision but cannot be treated as the sole authority. Define a missing standard
before more production. Do not retroactively declare every incidental feature
of an accepted clip mandatory.

Keep the standard stable during production. A necessary change records its
reason, affected rules and affected shots, then revalidates those shots. A
deadline does not authorize silently weakening it. A requested diagnostic
draft may be delivered honestly as incomplete; it is not conformance evidence.

## 2. Realize every shot's argument

Use the existing storyboard and `shot_review.jsonl`; do not create another
editorial hierarchy. Before a shot is considered implemented, resolve:

| Responsibility | Required realization | Check |
| --- | --- | --- |
| Information | What appears or changes from entry to peak and exit; the foreground explains the actual claim | Compare the rendered states with the planned information delta |
| Evidence | Verified data, units, source identity, caveats and legible interpretation | Inspect source-backed values and actual chart geometry; labels and marks share the same scale |
| Attention | Spoken trigger → stable visible target → readable hold and handoff | Check actual SRT windows and rendered cue changes, not evenly divided shot time |
| Composition | Deliberate reading order, usable source crop, whitespace and subtitle safe area | Inspect the final composite at review size; use real visible geometry when measuring |
| Background | Explicit role, selected source range, treatment and temporal behavior, or a justified absence | Inspect the chosen trim at multiple times and in motion; a thumbnail does not certify a long clip |
| Completion | Concrete implementation location and current rendered evidence | Record pending work rather than inheriting a pass from another shot |

Reuse a component or adapter when it realizes these responsibilities for the
specific shot. A shared runtime is not the problem. Collapsing distinct planned
states into a title, narration paragraph and small image is an implementation
gap even when the recipe schema validates. Extend the compatible realization
or author the missing scene behavior; keep the source argument intact.

Individual attention to every shot does **not** require one code component per
shot, one unique background per shot, constant animation, or a layout quota.
Purposeful holds and repeated comparison layouts remain valid. Background-free
work remains valid when the brief and shot role call for it. For a profile that
requires visible context, check layer presence, perceived visibility and
non-competition separately in the actual composite.

## 3. One production path, two output scopes

Implement a representative range in the canonical production composition.
Select it for information and execution risks, not automatically the opening.
If a contiguous excerpt misses a materially different later challenge, add a
small targeted check of that challenge. Sample approval covers what was
actually exercised; later scenes still require implementation and review.

Preview, full review and final read the same active shot plan, data, asset
bindings, scene implementation and caption layer. Frame range, resolution,
codec and other delivery settings may differ. A separate polished demo path
followed by a fallback full-film path breaks this contract. If a prototype
already exists, integrate its authored behavior into the production path and
check the overlapping range before extending it.

Record the standard revision separately from the render/content revision.
The first identifies the rules; the second identifies their concrete execution.
See `render-reliability.md` for safe segment reuse after a source change.

### Mandatory expansion probe

Do not jump directly from one accepted sample to broad full-film production.
After the representative sample passes, extend the **same canonical production
entry and content revision** into a small expansion probe that covers at least
3–5 materially different later shots (or an equivalent set that exercises the
known risks). The probe exists to catch the common failure where the sample is
hand-authored but later content collapses into generic cards, fallback scenes,
or a lower-quality renderer.

Record the control-plane state in `manifest/production_state.json` and run:

```bash
python3 scripts/validate_production.py PROJECT --stage scale
```

A blocked scale gate means stop broad generation/rendering. Fix the production
mechanism and rerun the smallest useful sample; do not spend tokens producing a
new full revision merely to see whether the same failure still exists.

## 4. Full coverage of decisions, honest coverage of checks

For every shot, keep `standard_ref`, `standard_revision`, `implementation_ref`,
`implementation_status`, applicable `rule_checks` and `review_evidence` in its
existing review record. A rule check states `rule_id`, applicability/reason,
status and evidence. Evidence identifies revision, frame/time range, artifact,
method, observation and review scope. Suggested implementation states are
`pending`, `implemented`, and `needs_revision`; none implies visual approval.
Use empty evidence and null scores until a check actually occurs.

Review entry, information peak and exit across the complete timeline. Inspect
additional states where attention changes; inspect important transitions and
chapter sequences in motion. Geometry, schema and smoke tests are technical
evidence, not proof of explanatory quality or sustained viewing rhythm.
Record continuous-playback coverage separately from frame sampling. Do not
claim to have watched the entire film based on contact sheets.

Keep four conclusions separate: implementation completeness, technical export
verification, agent visual review, and user acceptance of a specific artifact.
Acceptance of a review file does not authorize a new export or publication,
erase recorded limitations, or approve every incidental design choice. If a
source change affects an accepted artifact, retain the historical acceptance
and mark the newer output's review state independently.

Before a final export, run:

```bash
python3 scripts/validate_production.py PROJECT --stage full-export
```

This gate does not claim aesthetic excellence. It prevents known production
regressions from being silently promoted into a final render: sample/full path
divergence, active fallback generation, repeated unresolved failure classes,
planning-text leakage, incomplete full-film implementation/review, and missing
render preflight.

## 5. Failure escalation instead of patch loops

When a user reports a defect, first decide whether it is local or a recurrence
class. For P0/P1 failures use the canonical classes in `failure-regression.md`.
A user example is evidence of a class, not permission to repair only that one
shot.

If the same P0/P1 class appears a second time in the project:

1. stop broad production;
2. record `occurrence_count >= 2` and mark the regression `escalated`;
3. identify and change the responsible production mechanism/path;
4. scan analogous shots across the whole plan/implementation;
5. render a focused regression sample;
6. resume only after `validate_production.py` passes.

The default response to a repeated systemic failure must not be “patch another
version”. This rule exists specifically to reduce expensive iteration and token
waste.

## Frequent decision traps

| Temptation | Required response |
| --- | --- |
| “The sample is good, so derive the standard from it.” | Locate the existing brief, DESIGN and source implementation; sample pixels are supporting regression evidence. |
| “Same fonts and colors means the same standard.” | Check each shot's information, evidence, cue timing, composition and background responsibilities. |
| “The recipe has all lifecycle fields.” | Verify that those phases actually create the promised visual change. |
| “Technical checks passed; the rest should be fine.” | Keep unviewed states unreviewed and fix known implementation gaps before claiming conformance. |
| “This accepted case used many custom components.” | Preserve the reasoning and checks, not its component count or file structure. |
| “The user showed one broken shot; fix that shot.” | Classify the failure and scan all analogues before declaring it fixed. |
| “The first fix failed; try another cosmetic patch.” | On the second P0/P1 occurrence, stop and repair the production mechanism. |
