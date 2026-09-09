---
name: srt-visual-director
description: Use when a user provides an SRT, timed narration, or finalized voice script and wants visual direction, storyboarding, asset planning, or a production-ready handoff for a non-face video.
---

# SRT Visual Director

## Core principle

Turn timed narration into a visual argument, not a slideshow. **Evidence in the foreground; context in the background.** Exact claims, numbers, institutions, report facts, and labels must be accurate; background B-roll only needs to be semantically appropriate and non-misleading.

For any non-trivial SRT project, do not jump directly from subtitle units to a visual mode. Pass through a renderer-agnostic director middle layer:

1. **Narrative map** — claims, evidence, questions, turns, risks, and conclusions, including how they relate.
2. **Chapter arcs and visual beats** — what the viewer should understand at the start and end of each beat, and what information changes.
3. **Execution shots** — timecodes, visual grammar, assets, layout, motion, captions, and transitions.

The resulting flow is:

`SRT → narrative map → chapter arcs → visual beats → execution shots → assets → plan review → representative render review → full render`

Keep these source contracts in the project while managing reusable media in one shared asset library beside `projects/`.

### Visual responsibility

Use the least specific visual that can honestly perform the job, but no less specific than the claim requires:

- **Context / atmosphere / place** — semantically related B-roll may be sufficient.
- **Mechanism / trend / cause / flow** — B-roll may establish context, but the structured foreground must add an explanation such as a flow, chart, comparison, or labeled process.
- **Numbers / ratings / targets / report conclusions** — use readable evidence or structured data. B-roll cannot substitute for the exact claim.

Background coverage is a technical statistic, not the director's success criterion. A valid video layer does not prove that the visual argument is complete.

### Beat and shot distinction

A **visual beat** is a unit of viewer understanding; a **shot** is an executable visual interval. One beat may contain one shot or several states inside one shot. Every beat should expose `start_state`, `information_delta`, and `end_state`. Every shot should explain its `shot_function` and `cut_reason`. A static hold is valid when it protects reading time or gives a conclusion weight; motion is not progress by itself.

## Scope boundary

This skill stores **repeatable rules that survive a change of company, topic, asset set, or project path**. Keep episode-specific facts—company names, prices, institution names, Shot IDs, source timestamps, asset filenames, and absolute paths—in the project's SRT, storyboard, data, manifest, and configuration files. Keep reusable renderer implementation and export helpers in the engine. A profile default such as 90% background coverage is configurable guidance, not a universal requirement for every video genre.

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
- Default long-form finance output is 16:9, 1920×1080; accept 4K sources; production normalization is H.264 MP4, 30fps.
- Final rendered previews and finals **burn subtitles into the video by default** unless the user explicitly opts out. Keep captions in an independent layer and protect a subtitle safe zone.
- For a recurring video factory, initialize or reuse `<factory_root>/asset-library/` beside `projects/`. Projects reference stable `asset_id` values; they do not copy shared media into every project.
- Give each project one drop zone at `asset-library/inbox/<project_id>/`. The user supplies files there and reports “素材已准备好，继续”; catalog maintenance is agent-owned.
- Keep generated inventory in `catalog/assets.json`, durable reviewed descriptions in `catalog/metadata.json`, usage in `catalog/usage.json`, and unresolved review work in `catalog/review_queue.json`.
- For the high-background finance-podcast profile, treat 90% video-layer coverage as a configurable diagnostic inherited from the profile, never as a director goal, quality score, or pass condition. Keep evidence and readable data on screen when they need a holdout from background video.
- Treat background coverage and perceived background visibility as separate acceptance checks. Coverage counts frames with a valid video layer; visibility is the result after the asset opacity and every dark gradient, mask, or overlay are composited.
- Treat background salience as a separate visual gate: a technically visible background still fails when its highlights, motion, or local contrast compete with evidence, numbers, or captions.
- For a high-background finance profile, expose two independent controls in the design handoff: `asset_opacity` and `overlay_alpha`. If the user asks for a more visible background, adjust both and preview representative context and evidence shots. A useful starting preset is `0.42–0.50` for the asset layer (ordinary context around `0.46`, evidence around `0.50`), while reducing overly opaque masks. These are tunable profile defaults, not universal aesthetic requirements.
- Before storyboarding a long piece, estimate usable source duration and alternates. As a planning heuristic, a 2.5-minute test needs about 4–8 minutes of usable footage across 4–6 semantic categories; a 10-minute-plus program usually needs about 20–30 minutes. Adjust for the requested repetition tolerance.
- Before any renderer export, read `references/render-reliability.md`, run a preflight and a representative smoke render, and choose a resumable render plan proportional to duration and scene complexity.
- Before scaling a new visual system to a full piece, review the plan and render a representative 30–90s section. Keep `plan_score` (design review) separate from `render_score` (actual frame/motion review).
- When narration changes the attention target inside one shot, create timed attention cues that map the spoken window to a stable visible target. If the user approves one such behavior as an example and asks for the same judgment throughout, scan the complete plan for analogous names, metrics, report facts, chart nodes, flow steps, risks, and conclusions. Apply the pattern where the attention condition recurs; do not animate unrelated shots mechanically.
- Complete scan coverage is not cue coverage. Record the decision across the full plan, but let shots without a narrated attention-target change stay uncued; never use “every shot has motion” as evidence that the generalization is complete.
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

For finance / research-report content, also read `references/finance-profile.md`.

For any non-trivial visual plan, also read `references/visual-direction.md` and
`references/visual-quality-review.md`.

When real media must be sourced, read `references/asset-procurement.md`.

When a shared media library is available or should be created, read `references/asset-library.md`.

Before handing to Remotion, HyperFrames, or another renderer, read `references/execution-handoff.md`.

Before previewing or exporting a long composition, read `references/render-reliability.md`.

Use `references/output-contracts.md` for schemas and expected artifacts.

For SRT-only new projects, use `scripts/init_project.py` or reproduce its contract exactly. Never overwrite an existing project automatically.

## Non-negotiables

- Never fabricate a report page, source screenshot, company facility, or exact event and present it as real.
- Never assign a visual mode directly from a subtitle unit before the narrative map, chapter arc, and visual beat have been resolved.
- Every beat must state what changes in viewer understanding; `motion_arc` alone is not an information plan.
- On-screen explanatory copy must be audience-facing and supported by the narration or evidence. Internal production rationale, workflow labels, and prompts are not substitutes for source evidence.
- Repetition is acceptable when it has a continuity reason; variation is required when it has a change reason. Do not rotate templates mechanically.
- Background B-roll may support context, but it may not be the sole explanation of a mechanism, causal relationship, trend, financial number, rating, target, or report conclusion.
- Review hard gates separately from function-weighted soft scores. At minimum, check truthfulness, source status, readability, subtitle safe zone, valid references, and technical executability.
- Review a key shot at entry, information peak, and exit; review important transitions dynamically before approving the full render.
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
