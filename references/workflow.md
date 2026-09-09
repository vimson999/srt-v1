# Workflow

## Phase 0 — Project initialization and state detection

First determine whether this is a new project or a continuation.

### New SRT-only project

When the user supplies a new final SRT and no initialized project exists:

1. Resolve the project root. Prefer a user-specified root. Otherwise, if the current workspace already contains `projects/`, use that workspace root; if not, create `projects/` under the current workspace.
2. Derive a filesystem-safe `project_id` from the SRT filename or an unambiguous topic name. Do not invent a topic when the filename/content is ambiguous; use the sanitized filename stem.
3. Create `projects/<project_id>/` with the standard project skeleton shown below.
   Also create or reuse the shared `<factory_root>/asset-library/` sibling. The
   library is initialized once per factory, not once per episode.
4. Copy—not move—the supplied SRT to `input/subtitles.srt`.
5. Extract ordered subtitle text into `input/script.txt`. Do not silently rewrite or fact-correct the wording during extraction.
6. Create `project.json` with profile, status, canvas, fps, source path, and subtitle burn-in default.
7. Create valid empty JSON contracts for later phases; do not populate them with guessed facts.
8. If `projects/<project_id>/` already exists, **do not overwrite it**. Treat it as a continuation candidate or require a different project id/version.
9. Continue immediately to Phase 1 once initialization succeeds.
10. Tell the user where to place requested media: `asset-library/inbox/<project_id>/`. The only follow-up needed from the user is “素材已准备好，继续”.

Recommended helper:

```bash
python3 scripts/init_project.py final.srt --factory-root /path/to/report-video --project-id optional_id
```

Standard skeleton:

```text
projects/<project_id>/
  project.json
  DESIGN.md                    # created when visual system is defined
  input/
    subtitles.srt
    script.txt
    voice.wav                  # optional until supplied
  storyboard/
    storyboard.csv
    timeline.json
  data/
    financials.json
    charts.json
    institutions.json
    motion_cues.json
  manifest/
    assets_required.csv
    assets.json
    shot_assets.json
    missing_assets.json
  output/
    preview/
    final/
  scripts/

<factory_root>/asset-library/
  inbox/<project_id>/           # user drop zone; never treated as the catalog
  raw/{video,images,reports,logos}/
  processed/{video,images,thumbnails}/
  catalog/{assets.json,metadata.json,usage.json,review_queue.json}
```

Project-local `assets/` overrides are optional and should only be created when
the user explicitly wants project-owned media. Shared media belongs in the
factory-level library.

### Existing project detection

Inspect available inputs and resume from the furthest completed phase:

- Initialized project + SRT only → Phase 1.
- SRT + storyboard → Phase 2.
- Raw assets present → Phase 3.
- `assets.json`, `shot_assets.json`, `timeline.json` populated and valid → Phase 5 handoff after Phase 4 validation.

Do not make the user repeat work already present.

## Phase 1 — Narrative map, chapter arcs, and visual beats

Do not convert SRT entries directly into a rotating list of visual modes. First
make the argument legible, then choose how to stage it.

1. Parse total duration, subtitle count, sections, topic shifts, data-heavy passages, arguments, risks, comparisons, and conclusions.
2. Merge subtitles into semantic source units. Typical range: 5–15s. Openers may be 2–5s; complex explainers may be 10–20s. A subtitle boundary is not automatically a shot boundary.
3. Create `narrative_map.json` with the major questions, claims, evidence, turns, risks, conclusions, and source-status requirements.
4. Create `chapter_arcs.json` describing each chapter's opening question, development, turn, closing takeaway, dominant visual grammar, and anti-patterns.
5. Create `visual_beats.jsonl`. For every beat, state:
   - `start_state`: what the viewer sees or understands on entry;
   - `information_delta`: what this beat adds, changes, compares, or resolves;
   - `end_state`: what the viewer should understand on exit;
   - `shot_function`: context, claim, evidence, explanation, comparison, transition, pause, or conclusion;
   - `visual_responsibility`: context, structured explanation, exact evidence, or mixed;
   - `cut_reason`: why this beat begins, ends, or changes.
6. Expand beats into execution shots only when a new layout, asset, information state, or attention target is needed. A single shot may contain several visual states; several shots may serve one beat.
7. When attention changes inside one shot, create timed attention cues that map
   SRT-derived spoken windows to stable visible target IDs. If the user approves
   one cue behavior as an example and asks for the same judgment throughout,
   scan all beats and shots for analogous names, metrics, report facts, chart
   nodes, flow steps, risks, and conclusions. Generalize the decision rule
   without forcing motion onto unrelated holds. Record `attention_cue_ref=null`
   plus the existing motion reason for stable shots so scan completion cannot be
   confused with cue coverage.
8. Use `storyboard.jsonl` as the renderer-agnostic execution contract. Keep the legacy `storyboard.csv` as a compatibility export when a downstream tool requires it.
9. Identify terminology that needs confirmation. Do not put uncertain ASR text on screen.

For short, simple pieces the artifacts may be compact, but the same fields still
need to be represented. The director summary should report the narrative,
chapter, beat, and shot counts—not only a visual-mode mix.

## Phase 2 — Asset planning

1. Separate assets into:
   - `EVIDENCE_ASSET`: report pages, filings, logos, and authentic report screenshots. The source identity must be truthful. Accept user-provided low-resolution report screenshots; they receive a resolution warning rather than being rejected.
   - `CONTEXT_BROLL`: thematic footage. Use semantic fit over literal visual matching; broad meaning is enough for this editorial analysis, not a news package.
   - `PROGRAMMATIC`: charts, numbers, flows, comparisons, timelines, matrices.
2. Generate `assets_required.csv` with sites, search keywords, quantity, orientation, minimum size, preferred duration, shot language, avoid-list, and filename.
3. Do not ask the user to source visuals that should be generated programmatically.
4. Estimate usable `keep` footage before promising a long-form timeline. For a
   high-background finance podcast, compare the requested coverage target with
   unique source seconds and with the number of semantic alternates. Count only
   footage actually selected for a shot; `backup` or `transition_only` footage
   may be selected when its broad meaning is honest, while `reject` and
   `unreviewed` footage do not count. If the user allows reuse, **reuse existing assets**
   across the full composition with varied treatments; **unique footage is a quality diagnostic, not a go/no-go gate**.
   **Material quantity is not a production blocker** and additional footage is
   optional unless no honest visual support exists.
5. Present only the next actionable procurement batch unless the user requests the full list.

Bind assets to the visual responsibility of the beat or shot. A context clip is
not evidence merely because its filename contains the right noun. When one
evidence asset can satisfy a beat, continuation shots may use context or a
programmatic visual without inventing duplicate evidence requirements.

The procurement response must end with one concrete handoff sentence, for
example: “把以上文件放入 `asset-library/inbox/<project_id>/`，然后告诉我
‘素材已准备好，继续’。” Do not make the user remember catalog or renderer commands.

## Phase 3 — Asset audit

When the user says “素材已准备好，继续” or provides an equivalent explicit
completion notice:

1. Run `scripts/intake_assets.py` for the project drop zone (or the explicit
   source path). It copies supported media into shared `raw/`, uses content
   hashes to skip duplicates, and leaves the supplied source untouched.
2. Inspect thumbnails or representative frames; do not trust filenames alone.
3. Mark each asset: `keep`, `backup`, `reject`, or `transition_only`.
4. Write reviewed descriptions/tags/status/source notes to
   `asset-library/catalog/metadata.json`; let the generated index builder merge
   them into `assets.json`. Never put durable manual metadata only in the
   generated index.
5. Refresh `assets.json`, `usage.json`, and `review_queue.json`; update the
   project manifest as an asset-ID snapshot. Do not copy shared files into the
   project. Bind shots in `shot_assets.json`; primary asset first, semantic
   fallbacks second.
6. Record unresolved needs, missing thumbnails, insufficient alternates, and
   unverified sources in `missing_assets.json`.
7. Report imported count, duplicate count, pending review count, coverage/reuse
   implications, and exactly one next action. Do not ask the user to run the
   indexing command themselves.

## Phase 4 — Executable timeline and validation

1. Build `timeline.json` from SRT timing and storyboard units.
2. Preserve original source time and local composition time when rendering excerpts.
3. Build `data/motion_cues.json` for shots with in-shot attention changes.
   Validate cue windows against shot ranges and ensure every `target_id`
   resolves before renderer handoff.
4. Avoid black gaps: a visual unit may extend through small speech pauses until the next unit begins.
5. Data claims must resolve to structured data or exact source text; do not hardcode facts inside animation components when a data file exists.
6. Calculate and record video-background coverage separately from unique footage
   duration and reuse. A configured 90% coverage diagnostic is not permission
   to use an identical immediate loop conspicuously; it is also not a reason to
   block a full-length composition when varied reuse is acceptable.
7. Validate shot continuity, asset refs, chart refs, data refs, cue refs, media paths,
   subtitle timing, asset-library paths, background visibility, and project
   status before handoff. Treat any coverage percentage as a diagnostic rather
   than a substitute for the visual-responsibility and review gates.

### Plan review and render review

Before production handoff, run two distinct reviews:

1. **Plan review** — inspect the narrative map, chapter arcs, beat transitions,
   shot functions, information deltas, asset responsibilities, and source gates.
   Record `plan_score` and hard-gate failures without pretending that a filled
   table proves visual quality.
2. **Representative render review** — render a 30–90s representative section
   or the smallest section that exercises the visual system. For key shots inspect
   entry, information-peak, and exit states. For important transitions inspect a
   2–4s motion sample. For multi-target shots, inspect at least two cue
   activations and the handoff between them. Record `render_score` separately
   from `plan_score`.
3. **Full-film review** — after the representative section is accepted, inspect
   low-resolution full-film rhythm and chapter continuity, then render the final
   export. A background-coverage percentage cannot replace this review.

## Phase 5 — Production handoff

Hand off renderer-agnostic artifacts first. Then adapt to the chosen engine.

For test renders and final renders, subtitles are burned in by default. Use the SRT as a dedicated caption layer with safe-zone collision avoidance.

For a first test, prefer one representative 30–90s section when the visual language is unproven. Once accepted, scale to the full piece. If the visual system is already validated, a low-resolution full-length V1 is appropriate.

For Remotion, also inspect representative stills at an opening, a data-heavy
shot, an evidence shot, and a context-B-roll shot before exporting MP4. If the
local Chrome and Remotion browser versions differ, use an explicitly configured
local browser or fix the environment; do not repeatedly download a browser
binary without user approval.
