# Output Contracts

## Phase 0

### `project.json`

Recommended fields:

`schema_version,project_id,profile,source,status,aspect_ratio,width,height,fps,subtitle_burn_in,renderer`

For a shared-media factory, also include:

`asset_library.root,asset_library.catalog,asset_library.resolution,asset_library.remotion_mount`

When the project accepts new media, also include `asset_library.drop_zone`.

Defaults for finance: `profile=finance`, `1920x1080`, `30fps`, `subtitle_burn_in=true`, `renderer=null`.

### `input/subtitles.srt`

An exact project copy of the supplied final SRT. Do not rewrite timestamps during initialization.

### `input/script.txt`

Ordered narration text extracted from SRT entries. Extraction removes sequence numbers/timestamps and basic formatting tags only; it does not fact-correct or creatively rewrite the source.

### Standard directories

Project directories are:
`input,storyboard,data,manifest,output/{preview,final},scripts`

The factory-level shared directories are:
`asset-library/inbox/<project_id>,asset-library/raw/{video,images,reports,logos},asset-library/processed/{video,images,thumbnails},asset-library/catalog/{assets.json,metadata.json,usage.json,review_queue.json,intake_log.json}`.

Project-local `assets/` overrides are optional and must not be mistaken for the
shared library.

Initialization may create valid empty JSON objects/arrays for later contracts, but must not guess facts to populate them.

## Phase 1

### Director middle-layer contracts

For a non-trivial project, these contracts are the source of truth between SRT
parsing and renderer execution. JSONL records are one object per line.

#### `narrative_map.json`

Required top-level fields:

`schema_version,project_id,timing_source,source_status,segments`

Each `segments` item should include:

`segment_id,source_start,source_end,question,claim_chain,evidence_policy,background_policy,turn,conclusion`

`claim_chain` records the claims and their relationships, for example
`supports`, `contrasts`, `qualifies`, `causes`, `risks`, or `concludes`. Keep
exact values and source requirements in the segment or its linked data contract;
do not hide them in a prose note.

#### `chapter_arcs.json`

Required top-level fields:

`schema_version,project_id,arcs`

Each arc should include:

`chapter_id,segment_ids,opening_question,development,turn,closing_takeaway,dominant_visual_grammar,anti_patterns,source_gate`

#### `visual_beats.jsonl`

Required fields:

`beat_id,chapter_id,source_start,source_end,shot_ids,shot_function,start_state,information_delta,end_state,attention_target,visual_responsibility,background_role,cut_reason,source_status`

Use `background_role=none_required|context_only|evidence_backing` and keep it
separate from the measured video-layer coverage.

#### `storyboard/storyboard.jsonl`

This is the canonical rich, renderer-agnostic execution contract. Each
non-empty line is one shot. It extends the existing Narrative Map and Visual
Beat layers; it does not create a parallel Shot Group layer.

Required editorial, timing, and review fields:

`shot_id,beat_id,beat_ids,beat_position,role_in_beat,chapter,chapter_id,start,end,source_start,source_end,local_start,local_end,narration_focus,shot_function,claim_type,visual_mode,visual_grammar,visual_design,programmatic_visual,assets,asset_role,on_screen_text,motion,asset_need,caption_policy,source_status,plan_score,render_score,status`

Required V2 directing fields:

`schema_version,start_state,development_states,information_peak,reading_hold,information_delta,end_state,attention_target,motion_arc,motion_reason,visual_action,motion_budget,transition_reason,cut_reason,transition_out,exit_anchor,entry_anchor,continuity_axis,contrast_reason`

`beat_id` is the shot's primary Beat and must also appear in `beat_ids`, which
supports an intentional multi-Beat bridge. `start`/`end` remain the legacy
seconds projection; `source_start`/`source_end` preserve source time and
`local_start`/`local_end` preserve composition time. Likewise,
`transition_reason` is the V2 attention-handoff reason while `cut_reason` and
`transition_out` preserve the established editorial and downstream fields.

`role_in_beat` is one of `establish,develop,emphasize,resolve,bridge`.
`visual_action` is one of `establish,focus,compare,accumulate,causal,verify,turn,conclude,pause`.
`development_states` is an ordered array of objects with
`state_id,relative_start,description,attention_target`. `reading_hold` records
`required`, an optional `min_seconds`, and a reason; the duration is guidance,
not a global fixed rule.

`motion_budget` contains one `primary` motion object, an optional single
`supporting` motion object, and `background_policy`. `exit_anchor` and
`entry_anchor` are either null at a sequence boundary or objects with
`anchor_id,kind,description`. `continuity_axis` is one of
`position,direction,color,shape,scale,data_scale,none`. An interior
`continuity_axis=none` requires a non-empty `contrast_reason`.

`plan_score` and `render_score` begin as `null` until their respective reviews.
`assets` must identify stable asset IDs or explicit programmatic/data refs, not
only filenames. `status` should distinguish planned, reviewed, approved, and
needs_revision.

Validate the JSONL with `scripts/validate_storyboard.py`. The validator checks
contract shape and sequence continuity; it does not replace Evidence, Timed
Attention Cue, Render Review, or Render Reliability review.

#### `shot_review.jsonl`

Required fields:

`shot_id,beat_id,hard_gate_status,source_gate,plan_score,render_score,plan_notes,render_notes,review_status,revision_id`

This contract records review evidence; it does not replace the shot plan.

### `storyboard/storyboard.csv`

This is a compact, human-readable compatibility projection of the JSONL
contract. Required columns:

`shot_id,start,end,beat_id,beat_position,role_in_beat,chapter,narration_focus,visual_mode,visual_action,visual_design,on_screen_text,motion,motion_budget,asset_need,transition_reason,continuity_axis`

The CSV must not encode nested state arrays or anchors as a second source of
truth. It is not a substitute for the narrative map, chapter arcs, visual
beats, or JSONL execution contract; keep `shot_id` stable for downstream joins.

### `director_summary.md`

Contains duration, subtitle count, chapter count, visual-unit count, visual-mode mix, terminology warnings, Beat count, Beat role progression, visual-action mix, required reading-hold count, unresolved handoffs, and next action.

## Phase 2

### Shot Language enrichment

Phase 1 `storyboard/storyboard.jsonl` records remain valid before semantic Shot
Language selection. When a shot advances to the Shot Language or Shot Recipe
stage, add:

```json
{
  "shot_language": {
    "family": "report_reveal",
    "selection_reason": "The authentic source region must be located before its value becomes a chart anchor"
  }
}
```

`family` must be a stable ID from `templates/shot-language.yaml`, and the
family's `visual_actions` must contain the shot's `visual_action`.
`selection_reason` is required for a selected family and explains the
shot-specific information or handoff problem. Keep alternate candidates out of
the canonical shot record.

The shared registry is JSON-compatible YAML with:

`schema_version,registry_id,selection_input,shot_record_contract,families`

Each family contains:

`id,visual_actions,use_when,avoid_when,entry,development,peak,hold,exit,motion_personality,handoff,renderer_neutral`

This registry is a renderer-neutral policy artifact, not a component catalog.

### Shot Recipe enrichment

After selecting a compatible canonical recipe from `templates/shot-recipe.json`,
record:

```json
{
  "shot_recipe": {
    "id": "aligned_value_comparison",
    "selection_reason": "The selected comparison family needs one shared data scale"
  },
  "recipe_gap": null
}
```

The recipe's `shot_language` must equal `shot_language.family`, and its
`visual_actions` must contain the shot's `visual_action`. When no canonical
recipe fits, use `shot_recipe=null` and a non-empty `recipe_gap`; do not mutate
the shot contract to manufacture compatibility.

### `assets_required.csv`

Required columns:

`asset_id,evidence_level,purpose,suggested_sites,keywords_primary,keywords_backup,quantity,orientation,min_resolution,preferred_duration,shot_language,avoid,filename`

`min_resolution` is a sourcing preference for newly procured media. It is not an
acceptance gate for user-provided context footage or authentic low-resolution
report screenshots. Preserve those assets and record the limitation in
`resolution_warning`.

## Phase 3

### `assets.json`

Recommended project-snapshot fields:

`asset_id,type,category,path,raw_path,thumbnail,description,tags,duration,width,height,fps,codec,usage,status,warnings`

The shared catalog should additionally include:

`sha256,ownership,source_projects,provenance_status,license_status,resolution_warning,acceptance_basis,use_as,do_not_claim_as,file_exists,file_size_bytes,search_text`

`assets.json` is generated. Durable reviewed descriptions, tags, selection
status, and provenance notes belong in `catalog/metadata.json`; new or
incomplete records are surfaced in `catalog/review_queue.json`.

### `shot_assets.json`

Recommended fields:

`shot_id,beat_id,start,end,visual_type,generated_visual,primary_asset,secondary_assets,fallback_assets,asset_role,source_status`

### `missing_assets.json`

Each item: `shot_id,need,reason,keywords,suggested_sites,priority`.

### `manifest/asset-reuse-plan.json`

Generated by `scripts/plan_asset_reuse.py` from shot needs, the shared catalog,
durable metadata, and usage history. Required top-level fields:

`schema_version,candidates_by_shot,assignments,gaps,summary`

Candidate cards contain:

`asset_id,shot_id,visual_action,shot_language,decision,semantic_fit,intended_use,prohibited_interpretation,publication_gate,prior_usage,selection_status,provenance_status,license_status,resolution_warning,warnings`

`semantic_fit` records `score,matched_terms,role_compatible,basis`; exact
evidence needs cannot be satisfied by context-only assets.

Assignments contain:

`shot_id,visual_action,shot_language,selected_asset_id,decision,semantic_fit,publication_gate,prohibited_interpretation,prior_usage,treatment,treatment_variation,repetition_warning,resolution_warning`

Gaps contain `shot_id,need,reason,genuine`. A publication gate, low-resolution
warning, or prior use is not by itself a genuine gap. The plan is read-only
with respect to `raw/`, `assets.json`, `metadata.json`, and `usage.json`;
accepted bindings update usage in a later explicit step.

## Phase 4

### `storyboard/sequence-review.json`

Generated by `scripts/review_sequence.py` from the ordered canonical
storyboard. Required top-level fields:

`schema_version,shot_count,findings,energy_curve,inputs,summary`

Each finding contains:

`severity,shot_ids,rule,message`

`severity=error` blocks renderer handoff; `severity=warning` requires
editorial inspection but is not automatically blocking. Each energy annotation
contains:

`shot_id,beat_id,role_in_beat,visual_action,complexity,energy,reading_hold`

The report may record whether `director_summary.md` and rendered-review
metadata were supplied. It does not replace source, pixel, or media-output
verification.

### `timeline.json`

Each shot should include:

`shot_id,beat_id,source_start,source_end,local_start,local_end,duration,shot_function,visual_type,visual_id,chart_ref,data_ref,attention_cue_ref,primary_asset,secondary_assets,transition_out`

For excerpts, preserve both source time and local composition time.

### `motion_cues.json`

Use this sidecar when one or more shots change attention target without a cut.
An empty project contract is:

```json
{"schema_version": 1, "cues": []}
```

Each cue should include:

`cue_id,shot_id,source_start,source_end,local_start,local_end,spoken_trigger,target_id,emphasis,inactive_behavior`

`source_start/source_end` are derived from the SRT timing authority.
`local_start/local_end` preserve excerpt offsets. `target_id` must resolve to
one visible renderer element. Cue windows must stay inside their shot, use
integer-frame rounding only at renderer handoff, and avoid unintended overlap
between mutually exclusive targets.

## Design artifact

When production is imminent, produce `DESIGN.md` defining canvas, typography, spacing, safe area, number hierarchy, card/overlay treatment, chart style, motion rules, subtitle safe zone, transitions, and anti-patterns. For high-background profiles, also record `asset_opacity`, `overlay_alpha`, the representative shots used for the visibility check, and any mobile-legibility decision. These fields make background visibility reproducible instead of treating it as an untracked visual impression.

When `motion_cues.json` is used, `DESIGN.md` should also define the attention
language: target emphasis, inactive-peer behavior, enter/hold/settle timing, and
the representative cue transitions used for review.

### Coverage report

For high-background programs, record:

`target_video_background_coverage,measured_video_background_coverage,unique_keep_video_seconds,semantic_category_count,alternate_count,reused_asset_ids,reuse_count,repetition_notes`

`unique_keep_video_seconds` is informational. It is a quality diagnostic, not a
production gate. Full-length compositions may reuse existing assets when the
reuse is semantically honest and technically valid; report the reuse count and
treatments separately from unique footage.

### `render_manifest.json`

For a preview or final export, record the reproducible render handoff:

`composition_id,width,height,fps,total_frames,expected_duration,actual_duration,mode,segment_frames,segments,audio_source,audio_range,audio_mode,verification,status,warnings`

For versioned preview/final handoffs, also record `preview_revision`,
`rendered_revision`, and `concurrency`. If the preview revision is newer than
the rendered revision, set the render status to `stale` or equivalent and keep
the older output's verified metadata unchanged until a new render succeeds.

Each `segments` item should include:

`index,start_frame,end_frame,frame_count,output_path,status,attempts,log_path`

Use `mode=preview` or `mode=final`. `audio_mode` should distinguish a muted
video render followed by one final mux from an intentionally silent output.
`verification` should state the inspected duration, frame count, resolution,
fps, codec, and audio presence. The manifest is operational evidence; it does
not replace the project timeline or source contracts.
