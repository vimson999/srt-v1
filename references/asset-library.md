# Shared Asset Library

Use this reference when the factory has more than one video project or when a
project is expected to reuse context footage, report evidence, logos, charts,
or derived media.

## Canonical layout

Keep the library beside `projects/`, not inside an episode folder:

```text
<factory_root>/
  asset-library/
    inbox/
      <project_id>/             # user drop zone for new media
    raw/
      video/
      images/
      reports/
      logos/
    processed/
      video/
      images/
      thumbnails/
    catalog/
      assets.json
      metadata.json              # durable reviewed descriptions and tags
      usage.json
      review_queue.json          # generated unresolved review items
  projects/
    <project_id>/
      input/
      storyboard/
      data/
      manifest/
      output/
```

`input/` remains project-owned for voice, SRT, and script. A report page may
be kept in the shared library when it is reusable evidence, but its project
scope and provenance must be recorded in the catalog.

## Editorial acceptance rule

The shared library supports editorial analysis, not a news package. For context
B-roll, **semantic fit over literal visual matching** is the rule: accept a
related user-provided clip when its broad meaning supports the narration and it
does not make a false exact-company, exact-event, exact-product, or exact-place
claim. Do not make the user replace a usable related clip just to satisfy a
filename or shot-level match.

**Accept user-provided low-resolution report screenshots.** Resolution is a warning, not an acceptance gate. Ingest, catalog, and keep the screenshot
available even if it is compressed or too small for full-screen text reading.
Record `resolution_warning` and provenance/license status separately; if the
pixels are unreadable, do not transcribe or invent them.

## Source-of-truth and references

- `asset-library/raw/` contains the original file and should be treated as immutable.
- `asset-library/processed/` contains reproducible derivatives; never treat a
  thumbnail or proxy as the master asset.
- `catalog/assets.json` is the generated canonical inventory; do not use it as
  the only place for human-reviewed descriptions.
- `catalog/metadata.json` is the durable metadata sidecar. It may contain
  descriptions, semantic tags, evidence/context classification, shot language,
  source URL, provenance/license status, selection status, and notes keyed by
  `asset_id`. The index builder merges these fields without allowing them to
  overwrite computed paths, file existence, file size, or usage.
- A project `manifest/assets.json` is a project snapshot/lock of the asset IDs
  it uses. It may expose a renderer mount path, but the stable join key is
  always `asset_id`.
- `catalog/usage.json` records project and Shot usage so future edits can avoid
  conspicuous repetition.
- `catalog/review_queue.json` is generated from new or incomplete records and
  tells the agent what still needs inspection or confirmation.
- `catalog/search-assets.mjs` is the standard discovery entry point. Use it
  before requesting new media; it returns ranked candidate cards with a
  decision, intended use, prohibited interpretation, and usage history.

Recommended catalog fields:

`asset_id,sha256,type,category,path,raw_path,thumbnail,description,tags,duration,width,height,fps,codec,usage,status,ownership,source_projects,provenance_status,license_status,resolution_warning,acceptance_basis,use_as,do_not_claim_as,warnings`

Use `search_text` or equivalent normalized tags to search by visual meaning,
not only by filename. Include shot language such as `wide`, `macro`, `static`,
`slow_push`, and `low_motion`.

## Intake and audit

### Discovery before procurement

For each visual need, search the catalog first and return a short candidate set.
Do not treat a filename match as sufficient. A candidate card must make four
things visible: what the asset actually shows, what it may be used to express,
what it must not be used to claim, and whether it is a primary, fallback,
transition-only, review-required, or unavailable candidate. Only after this
search returns no honest candidate should the need become a supplement request.
Keep preview eligibility separate from public-release clearance: `keep` may be
usable in a preview while `provenance_status` or `license_status` remains
unverified. The search result should expose this as `publication_gate` rather
than silently upgrading an unverified source.

The user should only need to place files in `inbox/<project_id>/` and say
“素材已准备好，继续”. The agent owns the following operation; do not ask the
user to run it manually:

```bash
python3 scripts/intake_assets.py --factory-root <factory_root> --project-id <project_id>
```

The operation is incremental and safe to repeat. It hashes files, skips exact
duplicates, copies new originals into `raw/`, records an intake log, and then
refreshes the catalog when the factory index builder is available. It never
deletes the drop-zone source automatically.

For every imported asset:

1. Preserve the original file and compute a stable hash when practical.
2. Inspect a representative frame or thumbnail; do not trust the filename.
3. Record type, duration, dimensions, frame rate, semantic tags, source URL,
   provenance status, and license status.
4. Mark selection status independently: `keep`, `backup`, `reject`,
   `transition_only`, or `unreviewed`. New files default to `unreviewed`.
   Never use `reject` or `backup` solely because a user-provided report
   screenshot is low resolution; add a resolution warning instead.
5. Record whether the asset is evidence or context. Context footage must not be
   narrated as a specific company facility, event, date, or product unless it
   is actually verified.
6. Generate a thumbnail for each video and flag missing derivatives.

If an accepted asset's description currently exists only in a project manifest,
promote that stable description into the library metadata sidecar with the
factory's metadata-sync helper. Never promote `unreviewed` or `pending` records
just to make the queue look clean.

Descriptions inferred from a filename or a single frame are drafts. For report
pages, company-specific facilities, events, dates, source URLs, and license
claims, keep the record unverified until the evidence is actually confirmed.
This verification note does not block acceptance of a user-provided screenshot;
it only controls how strongly it may support an exact claim.

## Coverage and repetition planning

Background coverage is a composition-level metric:

```text
video_background_coverage = frames with a valid video background / total composition frames
```

It is not the percentage of unique footage. Report both values:

- target and measured background coverage;
- total usable `keep` footage seconds;
- number of semantic categories and alternates;
- approximate reuse count or reused Shot IDs.

For a high-background finance podcast, 90% may be retained as a configurable
coverage diagnostic when the user has not specified another target. It is not a
director goal or approval gate. Keep pure data or evidence holdouts when
readability or source exactness requires them. If the library is too small,
proceed with semantically honest programmatic visuals and varied reuse when the
user has not requested more sourcing. **Looping and reuse are allowed**
for full-length compositions. **Do not treat additional footage as required**
merely because unique source seconds are shorter than the
composition. Do not disguise repeated footage as new material: record the
reused asset IDs, treatments, and any conspicuous repetition. A related,
lower-resolution, or lower-specificity user-provided asset may still be used
when it is the honest broad context.

Unique footage is a quality diagnostic, not a production gate. If the user
allows reuse, continue the composition with existing assets and vary trim,
crop, scale, speed, opacity, layout, and spacing. Escalate a missing-asset
issue only when the available library cannot support a beat honestly or a
file is technically unusable.

Planning heuristics:

- 2.5-minute test: 4–8 minutes of usable footage, 4–6 semantic categories,
  and 2–4 alternatives for each important chapter.
- 10-minute-plus program: roughly 20–30 minutes of usable footage, with at
  least two distinct options for every recurring semantic category.

These are starting points, not quotas. Content continuity and semantic fit
take priority over filling time.

## Renderer handoff

The renderer should resolve project asset IDs through the shared catalog or a
documented virtual mount. Do not duplicate the library into a Remotion
project. Before rendering:

- validate every referenced file and thumbnail;
- verify that evidence, charts, and subtitles have separate safe zones;
- render representative stills and a 30–90-second section first;
- record the asset-library root and catalog revision in the handoff;
- only render a full-length MP4 after visual approval.
