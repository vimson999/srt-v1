# Failure regression gates

This document exists to prevent known production failures from being rediscovered project by project.
It is not another visual hierarchy and it does not add another director layer. It converts repeated real-production failures into stop conditions.

Read this file before scaling a representative sample into a full film, when a user reports a quality regression, and before claiming that a visual problem has been fixed.

## Principle

A lesson learned is not a fix until the next run is prevented from taking the same failing path.

The production loop is therefore:

`failure -> classify -> generalize -> gate -> verify -> resume`

not:

`failure -> patch example -> rerender -> discover same class elsewhere`.

## Severity

- **P0 production-path failure** — continuing production is expected to waste substantial work or tokens. Stop broad production immediately.
- **P1 systemic visual failure** — the same mechanism can affect many shots. Fix the mechanism and scan analogous shots before resuming.
- **P2 local defect** — genuinely isolated implementation issue. Local repair is allowed, but verify that it is actually isolated.

A P0 or P1 class that appears a second time in the same project is automatically an escalation. Do not produce another broad revision until the mechanism or production path has changed and the analogous-shot scan is complete.

## Canonical failure classes

### FR-01 PLANNING_TEXT_LEAK — P0

**Failure:** internal director/planning language appears as audience-facing screen copy.

Examples include instructions such as building a node, activating a source matrix, passing a source gate, entering an evidence layer, or raw field names such as `attention_target`, `information_peak`, `visual_action`, and `shot_function`.

**Required behavior:**

- Planning fields are never a fallback source for `on_screen_text`.
- If audience-facing copy or an actual graphic implementation is missing, the shot is `not_implemented`; it is not auto-filled with planning rationale.
- A detected leak blocks sample acceptance and full-film scaling.

### FR-02 SAMPLE_FULL_PATH_DIVERGENCE — P0

**Failure:** a polished sample and the full film use different production entries, content revisions, scene implementations, or a fallback renderer/generator.

**Required behavior:**

- Representative sample, expansion probe, full review, and final render use the same canonical production entry and active content revision.
- Delivery parameters may change; visual implementation may not silently switch after the sampled range.
- Any fallback renderer or generic full-film generator must be explicit and is a failure unless the user requested a diagnostic downgrade.

### FR-03 TEMPLATE_COLLAPSE — P0/P1

**Failure:** distinct arguments collapse into `title + paragraph + small image/card`, or a small set of generic panels is used to fill the remaining timeline.

**Required behavior:**

- Shared components are allowed only when they realize the shot's actual information change.
- Before broad scaling, extend the accepted sample into an **expansion probe** of at least 3–5 materially different later shots (or an equivalent representative set) and review them.
- If later shots lose evidence, hierarchy, state progression, or specific visual responsibility, scaling stops.

### FR-04 PROXY_METRIC_OVERCLAIM — P1

**Failure:** technical success, schema validity, background coverage, contact sheets, decoding, or screenshot bounds are reported as visual/directorial success.

**Required behavior:**

Keep these conclusions separate:

1. implementation completeness;
2. technical export verification;
3. sampled frame review;
4. continuous playback review;
5. user acceptance of a specific artifact.

No conclusion may inherit `pass` from another category.

### FR-05 BACKGROUND_LAYER_CONFUSION — P1

**Failure:** background existence/coverage is treated as proof that the background is perceptible, semantically suitable, or non-competing.

**Required behavior:** record and review separately:

- layer present;
- perceptually visible in the final composite;
- semantic fit for the selected trim;
- salience/non-competition with evidence, numbers, and captions.

### FR-06 EXAMPLE_ONLY_FIX — P1

**Failure:** the user points out one example, only that shot is repaired, while analogous structures remain unchanged.

**Required behavior:**

- classify the feedback;
- define the recurrence condition;
- scan the full plan/implementation for analogues;
- record affected and intentionally unaffected shots;
- then repair the class, not only the example.

A complete scan does not mean every shot receives the same effect.

### FR-07 STATE_WITHOUT_VISUAL_CHANGE — P1

**Failure:** internal shot states exist in JSON but only add another card, change an outline, or satisfy a field without creating a meaningful change in viewer understanding.

**Required behavior:** each meaningful internal state must perform a semantic visual action such as establish, locate evidence, change scale, align comparison, expose conflict, eliminate an alternative, reorganize a relationship, conclude, or deliberately hold for reading.

State count is never a quality metric.

### FR-08 STATIC_REVIEW_AS_MOTION_REVIEW — P1

**Failure:** contact sheets or isolated screenshots are used to claim timing, motion, transition, reading duration, or sustained rhythm quality.

**Required behavior:** sampled frames and continuous playback have separate evidence and statuses. Motion claims require motion review.

### FR-09 RENDER_PREFLIGHT_MISSING — P1

**Failure:** long export begins before representative speed, temporary storage, resumability, codec/media compatibility, and recovery strategy are checked.

**Required behavior:** run render preflight before a long export; use resumable segmentation when failure cost is high.

### FR-10 REPEATED_PATCH_LOOP — P0

**Failure:** the same P0/P1 class occurs twice while production continues through local patches.

**Required behavior:**

- stop broad generation/rendering;
- mark the class `escalated`;
- identify the mechanism/path responsible;
- change that mechanism or path;
- run a focused regression sample;
- complete the analogous-shot scan;
- only then resume.

A third cosmetic patch is prohibited as the default response.

## Required project state

For non-trivial long-form production, keep `manifest/production_state.json` as a small control-plane record. It is not a storyboard and must not duplicate shot content.

Recommended shape:

```json
{
  "schema_version": 1,
  "standard_revision": "design-r3",
  "content_revision": "content-r7",
  "canonical_production_entry": "src/Root.tsx#MainComposition",
  "representative": {
    "production_entry": "src/Root.tsx#MainComposition",
    "content_revision": "content-r7",
    "review_status": "pass"
  },
  "expansion_probe": {
    "production_entry": "src/Root.tsx#MainComposition",
    "content_revision": "content-r7",
    "review_status": "pass",
    "materially_different_shots_checked": 5
  },
  "full_film": {
    "production_entry": "src/Root.tsx#MainComposition",
    "content_revision": "content-r7",
    "implementation_status": "implemented",
    "visual_review_status": "pass"
  },
  "fallback_renderer": null,
  "feedback_generalization_scan": {
    "status": "pass"
  },
  "render_preflight": {
    "status": "pass"
  },
  "regressions": []
}
```

A regression item should contain:

`id,class,severity,status,occurrence_count,mechanism_fix_ref,generalization_scan_status,evidence`

Suggested statuses are `open`, `escalated`, `mechanism_fixed`, `verified`, and `waived_by_user`. A waiver must identify the exact diagnostic downgrade the user requested; silence or impatience is not a waiver.

## Mandatory gates

Use `scripts/validate_production.py`.

### Before broad scaling

```bash
python3 scripts/validate_production.py PROJECT --stage scale
```

This gate checks at minimum:

- representative review passed;
- expansion probe passed;
- representative, probe, and full film share the canonical production entry and content revision;
- no fallback renderer is active;
- no unresolved/escalated P0 or repeated P1 regression remains;
- feedback generalization scan passed when regressions exist;
- storyboard audience text does not directly leak planning fields or known internal planning language.

### Before final export

```bash
python3 scripts/validate_production.py PROJECT --stage full-export
```

In addition to the scale gate, require full-film implementation and visual review status plus render preflight.

### Before claiming full visual completion

A technical export, contact sheet, or sampled review is not sufficient. The project record must state what continuous playback was actually reviewed. Never infer full continuous review from static evidence.

## Token-efficiency rule

The purpose of these gates is to stop expensive wrong-path iteration early.

When a P0 failure is detected:

1. do not render another full version;
2. do not patch dozens of shots independently;
3. repair the production mechanism;
4. render the smallest sample that can disprove the failure;
5. scale only after the gate passes.

The expected outcome is fewer revisions, not more process documents.
