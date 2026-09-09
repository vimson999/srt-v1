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

#### `storyboard.jsonl`

Required fields:

`shot_id,beat_ids,chapter_id,source_start,source_end,local_start,local_end,shot_function,claim_type,start_state,information_delta,end_state,attention_target,visual_grammar,visual_design,programmatic_visual,assets,asset_role,motion_arc,motion_reason,cut_reason,transition_out,caption_policy,source_status,plan_score,render_score,status`

`plan_score` and `render_score` begin as `null` until their respective reviews.
`assets` must identify stable asset IDs or explicit programmatic/data refs, not
only filenames. `status` should distinguish planned, reviewed, approved, and
needs_revision.

#### `shot_review.jsonl`

Required fields:

`shot_id,beat_id,hard_gate_status,source_gate,plan_score,render_score,plan_notes,render_notes,review_status,revision_id`

This contract records review evidence; it does not replace the shot plan.

### `storyboard.csv`

Required compatibility columns:

`shot_id,start,end,chapter,narration_focus,visual_mode,visual_design,on_screen_text,motion,asset_need`

The CSV may be generated for legacy tools, but it is not a substitute for the
narrative map, chapter arcs, visual beats, or JSONL execution contract. If the
CSV is the only downstream format available, preserve the new fields in a
sidecar JSONL file and keep the join key `shot_id` stable.

### `director_summary.md`

Contains duration, subtitle count, chapter count, visual-unit count, visual-mode mix, terminology warnings, and next action.

## Phase 2

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

## Phase 4

### `timeline.json`

Each shot should include:

`shot_id,beat_id,source_start,source_end,local_start,local_end,duration,shot_function,visual_type,visual_id,chart_ref,data_ref,primary_asset,secondary_assets,transition_out`

For excerpts, preserve both source time and local composition time.

## Design artifact

When production is imminent, produce `DESIGN.md` defining canvas, typography, spacing, safe area, number hierarchy, card/overlay treatment, chart style, motion rules, subtitle safe zone, transitions, and anti-patterns. For high-background profiles, also record `asset_opacity`, `overlay_alpha`, the representative shots used for the visibility check, and any mobile-legibility decision. These fields make background visibility reproducible instead of treating it as an untracked visual impression.

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
