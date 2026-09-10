---
name: srt-visual-director
description: Use when a user provides an SRT, timed narration, or finalized voice script and wants visual direction, storyboarding, asset planning, or a production-ready handoff for a non-face video.
---

# SRT Visual Director

## Core principle

Turn timed narration into a visual system, not a slideshow. **Evidence in the foreground; context in the background.** Exact claims, numbers, institutions, report facts, and labels must be accurate; background B-roll only needs to be semantically appropriate and non-misleading. For recurring production, keep the visual director's source contracts in the project while managing reusable media in one shared asset library beside `projects/`.

## Scope boundary

This skill stores **repeatable rules that survive a change of company, topic, asset set, or project path**. Keep episode-specific facts—company names, prices, institution names, Shot IDs, source timestamps, asset filenames, and absolute paths—in the project's SRT, storyboard, data, manifest, and configuration files. Keep reusable renderer implementation and export helpers in the engine. A profile default such as 90% background coverage is configurable guidance, not a universal requirement for every video genre.

## V2 directing contract

Keep the existing editorial hierarchy: Narrative Map → Chapter → Visual Beat → Shot. Visual Beat is the unit that groups shots into one understandable visual sentence; **do not add a separate Shot Group**. Phase 1 makes the middle of that hierarchy executable by describing each shot's Beat progression, information state, semantic `visual_action`, `motion_budget`, and attention handoff.

After the semantic action is stable, Phase 2 selects a renderer-neutral Shot
Language family from `templates/shot-language.yaml`. The family must support the
shot's `visual_action`, fit its information lifecycle and handoff, and be
recorded with a shot-specific `selection_reason`. Shot Language is a reusable
grammar, not another hierarchy level, an effect inventory, or a fixed layout
quota.

Phase 3 may then select a compatible renderer-neutral Shot Recipe from
`templates/shot-recipe.json`. A recipe realizes the existing state lifecycle;
it must not rewrite the shot's action, evidence, motion budget, reading hold,
or handoff to fit an implementation.

The canonical rich storyboard is `storyboard/storyboard.jsonl`, one shot per non-empty line. `storyboard/storyboard.csv` is a compact compatibility projection for review, not a second source of truth. Preserve `start_state`, `information_delta`, and `end_state`; add `development_states`, `information_peak`, and `reading_hold` to complete the state machine rather than renaming it.

Existing Narrative Map, Visual Beat, Evidence, Timed Attention Cue, Render Review, and Render Reliability responsibilities remain authoritative. The V2 middle layer records what information changes and how attention moves; it does not replace source verification, cue timing, rendered-pixel review, or render preflight.

## Acceptance standard

This is editorial analysis, not a news package. For context footage, use **semantic fit over literal visual matching**: the broad meaning only needs to support the narration without creating a false company, event, product, or geography claim. Accept related user-provided footage and keep moving; do not block on an exact facility, model, location, or shot match unless that identity is itself the claim.

**Low-resolution report screenshots are accepted.** A user-provided screenshot of an authentic report must be ingested and remain usable even when it is small, compressed, or not suitable for full-screen reading. **Do not reject or downgrade a user-provided screenshot because of resolution.** Record `resolution_warning` and provenance separately. If text cannot be read, use the screenshot as visual report backing and take exact wording or numbers from readable source text; never invent unreadable pixels.

## Full-length reuse policy

For a full-length composition, default to **reuse existing assets for the full-length composition** when the clips are technically playable and broadly relevant. **Material quantity is not a production blocker.** **Looping is allowed**, but vary trims, crops, scale, playback speed, opacity, layout, or spacing so that repetition feels intentional and does not become conspicuous. **Report reuse separately from unique footage** in the coverage and handoff notes. Only report a true asset gap when no existing asset or programmatic visual can support the beat without misleading the viewer.

## Defaults

- A new SRT-only job begins with **automatic project initialization** under `projects/<project_id>/` before visual planning.
- If the SRT is from final audio, treat SRT timestamps as the timing source of truth.
- If a final script also exists, use script text as wording truth and SRT as timing truth.
- Do **not** map one subtitle to one shot. Merge subtitles into semantic visual units, usually 5–15 seconds.
- For every shot, record Beat position/role, the state sequence from entry through information peak to exit, one semantic `visual_action`, a `motion_budget`, and a `transition_reason` with its handoff anchors.
- Before Shot Recipe or renderer handoff, choose one compatible Shot Language family and record why it solves that shot's information or attention problem.
- When a canonical Shot Recipe fits, hand its ordered state timeline to the renderer adapter; record a recipe gap instead of forcing an incompatible pattern.
- Before renderer handoff, generate a sequence review, resolve structural/reference errors, and inspect aesthetic warnings in context instead of treating thresholds as automatic failures.
- Before requesting more media, rank the reviewed shared catalog against shot needs, preserve publication gates and prohibited interpretations, and plan varied reuse by stable `asset_id`; create a gap only when no honest candidate exists.
- Default long-form finance output is 16:9, 1920×1080; accept 4K sources; production normalization is H.264 MP4, 30fps.
- Final rendered previews and finals **burn subtitles into the video by default** unless the user explicitly opts out. Keep captions in an independent layer and protect a subtitle safe zone.
- For a recurring video factory, initialize or reuse `<factory_root>/asset-library/` beside `projects/`. Projects reference stable `asset_id` values; they do not copy shared media into every project.
- Give each project one drop zone at `asset-library/inbox/<project_id>/`. The user supplies files there and reports “素材已准备好，继续”; catalog maintenance is agent-owned.
- Keep generated inventory in `catalog/assets.json`, durable reviewed descriptions in `catalog/metadata.json`, usage in `catalog/usage.json`, and unresolved review work in `catalog/review_queue.json`.
- For the high-background finance-podcast profile, target video-layer coverage of 90% of composition frames unless the user opts out. Coverage is measured separately from unique source duration and background visibility; never use an identical immediate loop merely to satisfy the percentage.
- Treat background coverage and perceived background visibility as separate acceptance checks. Coverage counts frames with a valid video layer; visibility is the result after the asset opacity and every dark gradient, mask, or overlay are composited.
- For a high-background finance profile, expose two independent controls in the design handoff: `asset_opacity` and `overlay_alpha`. If the user asks for a more visible background, adjust both and preview representative context and evidence shots. A useful starting preset is `0.42–0.50` for the asset layer (ordinary context around `0.46`, evidence around `0.50`), while reducing overly opaque masks. These are tunable profile defaults, not universal aesthetic requirements.
- Before storyboarding a long piece, estimate usable source duration and alternates. As a planning heuristic, a 2.5-minute test needs about 4–8 minutes of usable footage across 4–6 semantic categories; a 10-minute-plus program usually needs about 20–30 minutes. Adjust for the requested repetition tolerance.
- Before any renderer export, read `references/render-reliability.md`, run a preflight and a representative smoke render, and choose a resumable render plan proportional to duration and scene complexity.
- Before renderer handoff, validate `storyboard/storyboard.jsonl` with `scripts/validate_storyboard.py`; keep intentional hard cuts explicit with `continuity_axis=none` and a meaningful `contrast_reason`.
- For long or failure-prone renders, prefer checkpointed frame segments, adaptive concurrency, and one final audio mux over one-shot rendering. Reuse valid segments after a retry; never restart the whole export merely because one segment failed.
- Deliver progressively. Do not overwhelm the user with every downstream step at once.

## Human handoff contract

Keep the user-facing workflow to three checkpoints:

1. User provides SRT/audio → initialize the project, parse timing, and provide the next asset batch.
2. User places requested media in the project drop zone and says “素材已准备好，继续” → run `scripts/intake_assets.py`, inspect files, update metadata/catalog/manifests, and report only gaps or the next decision.
3. User asks for preview or approves the picture → validate and open Studio. Treat preview approval and final export as separate checkpoints; start a long MP4 render only after an explicit request such as “导出”“重新导出” or “重新渲染”.

Do not ask the user to run internal indexing commands, create catalog files, rename assets, or manually update manifests. If the user drops files elsewhere, accept an explicit source path and perform the safe copy/scan yourself; never delete the source without explicit authorization.

## Workflow routing

Read `references/workflow.md` and execute only the current phase.

For Phase 1 shot-state and attention-handoff rules, also read `references/director-contract.md` and `scripts/validate_storyboard.py`.

For semantic Shot Language selection or registry changes, also read
`references/shot-language.md` and use `templates/shot-language.yaml` as the
canonical registry.

For Shot Recipe selection or adapter design, also read
`references/shot-recipes.md` and use `templates/shot-recipe.json` as the
renderer-neutral recipe set.

For sequence or full-film planning review, also read
`references/sequence-review.md` and run `scripts/review_sequence.py`.

For catalog retrieval, candidate ranking, or reuse planning, also read
`references/asset-retrieval.md` and run `scripts/plan_asset_reuse.py`.

For finance / research-report content, also read `references/finance-profile.md`.

When real media must be sourced, read `references/asset-procurement.md`.

When a shared media library is available or should be created, read `references/asset-library.md`.

Before handing to Remotion, HyperFrames, or another renderer, read `references/execution-handoff.md`.

Before previewing or exporting a long composition, read `references/render-reliability.md`.

Use `references/output-contracts.md` for schemas and expected artifacts.

For SRT-only new projects, use `scripts/init_project.py` or reproduce its contract exactly. Never overwrite an existing project automatically.

## Non-negotiables

- Never fabricate a report page, source screenshot, company facility, or exact event and present it as real.
- Real report covers/pages may be used as evidence backgrounds; fabricated lookalike reports may not.
- Programmatic visuals are preferred for data, comparisons, valuation, flows, timelines, risk matrices, and exact quantitative claims.
- Context B-roll may be reused with different trims/crops/scale/speed/overlay treatment, but avoid conspicuous immediate repetition.
- For context B-roll, broad semantic meaning is sufficient; do not reject a supplied related clip merely because it is not literally identical to the narrated scene.
- Accept every user-provided report screenshot as a cataloged visual asset regardless of resolution; attach a resolution warning instead of changing its acceptance status.
- Flag suspicious ASR terms before placing them on screen.
- Treat SRT timestamps as timing truth and do not automatically download or run a new ASR model to rewrite supplied wording. Preserve questionable wording, flag it, and only correct it when the user supplies or authorizes a correction.
- Keep video rendering separate from source-audio assembly when segmenting: render segments muted, place the correctly trimmed/source-ranged audio once on the final timeline, and verify that the muxed duration matches the SRT-driven composition.
- If source assets are missing, record the gap instead of substituting an inaccurate asset.
- Keep selection status (`keep`, `backup`, `reject`, `transition_only`) separate from provenance and license status. A preview-usable asset may still be unverified for public release.
- For shared media, intake new files incrementally by content hash, preserve `catalog/metadata.json` across index rebuilds, and update the catalog and usage record after binding assets to shots; record missing thumbnails, missing files, and insufficient semantic alternates explicitly.
- Before rendering, verify writable temporary storage, available disk space and memory, active Studio/Chrome renderer instances, the configured browser, `ffmpeg`/`ffprobe` availability, composition metadata, referenced media, and a short smoke render. For media-heavy 1080p work, test a representative range at concurrency 1 and then a higher value only if memory allows; use the highest setting that completes reliably. A root-load or `delayRender` timeout that appears only with parallel workers is a resource signal to reduce concurrency, not evidence that the composition must be rewritten. Tell the user to close unnecessary browsers or Studio instances before an expensive render when doing so can materially improve available memory.
- After rendering, verify the actual output with media inspection: duration, frame count, resolution, frame rate, audio presence/duration, and readable file size. Record retries, segment ranges, audio source/range, concurrency, browser/memory warnings, and the render revision in the handoff. If preview code changes after the last MP4, mark the final output stale until it is rendered again; do not label it current merely because an older MP4 still exists.
- Project initialization must preserve the supplied SRT, create a clean `script.txt`, create valid empty contracts for later phases, and refuse silent overwrite of an existing project.
