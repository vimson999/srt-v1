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

## Phase 1 — Direct from SRT

1. Parse total duration, subtitle count, sections, topic shifts, data-heavy passages, arguments, risks, comparisons, and conclusions.
2. Merge subtitles into semantic visual units. Typical range: 5–15s. Openers may be 2–5s; complex explainers may be 10–20s.
3. Build the Beat progression inside existing Visual Beats and assign each shot a Beat position and role (`establish`, `develop`, `emphasize`, `resolve`, or `bridge`). Do not create a separate Shot Group layer.
4. For each shot, write the information state: `start_state` → ordered `development_states` → `information_peak` → optional protected `reading_hold` → `end_state`, with `information_delta` explaining the change in understanding.
5. Choose one primary semantic action (`visual_action`) such as `verify`, `accumulate`, `causal`, `compare`, `conclude`, or `pause`; record a `motion_budget` with one primary motion responsibility, at most one supporting responsibility, and an ambient background policy.
6. Retrieve compatible families from `templates/shot-language.yaml`, select one against the information lifecycle and handoff, and record `shot_language.family` plus a shot-specific `selection_reason`. Do not select by effect novelty or layout quotas.
7. When a matching canonical recipe exists in `templates/shot-recipe.json`, select it as the renderer-neutral implementation plan. Record a recipe gap instead of changing the action or forcing an unrelated recipe.
8. Write the attention handoff: why the transition happens, what `exit_anchor` remains, what `entry_anchor` is inherited, which `continuity_axis` carries attention, or why a deliberate contrast cut needs `contrast_reason`.
9. Assign each unit a visual mode:
   - `BROLL_OVERLAY`
   - `REPORT_EVIDENCE`
   - `DATA_HERO`
   - `CHART`
   - `PROCESS_FLOW`
   - `COMPARISON`
   - `SECTION_TITLE`
   - `FULL_BROLL`
   - `RISK_MATRIX`
   - `TIMELINE`
   - `MAP`
10. Produce canonical `storyboard/storyboard.jsonl`, the compact `storyboard/storyboard.csv` projection, and a concise director summary. Run `scripts/validate_storyboard.py` before handing the storyboard to a renderer.
11. Identify terminology that needs confirmation. Do not put uncertain ASR text on screen.

The Phase 1 middle layer describes information and attention flow; it does not
replace Evidence records, Timed Attention Cues, Render Review, or Render
Reliability checks. Those remain the source and QA gates for exact claims,
timing, pixels, and export behavior.

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
3. Avoid black gaps: a visual unit may extend through small speech pauses until the next unit begins.
4. Data claims must resolve to structured data or exact source text; do not hardcode facts inside animation components when a data file exists.
5. Calculate and record video-background coverage separately from unique footage
   duration and reuse. A 90% coverage target is not permission to use an
   identical immediate loop conspicuously; it is also not a reason to block a
   full-length composition when varied reuse is acceptable.
6. Validate shot continuity, asset refs, chart refs, data refs, media paths,
   subtitle timing, asset-library paths, background visibility, and project
   status before handoff.
7. Run `scripts/review_sequence.py` on the ordered storyboard. Resolve
   structural and reference errors; inspect repetition, cognitive-release,
   motion-balance, and energy-curve warnings without treating them as automatic
   aesthetic failures.

## Phase 5 — Production handoff

Hand off renderer-agnostic artifacts first. Then adapt to the chosen engine.

For test renders and final renders, subtitles are burned in by default. Use the SRT as a dedicated caption layer with safe-zone collision avoidance.

For a first test, prefer one representative 30–90s section when the visual language is unproven. Once accepted, scale to the full piece. If the visual system is already validated, a low-resolution full-length V1 is appropriate.

For Remotion, also inspect representative stills at an opening, a data-heavy
shot, an evidence shot, and a context-B-roll shot before exporting MP4. If the
local Chrome and Remotion browser versions differ, use an explicitly configured
local browser or fix the environment; do not repeatedly download a browser
binary without user approval.
