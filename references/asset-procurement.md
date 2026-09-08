# Asset Procurement

## Default technical spec

Unless the target platform says otherwise:

- Orientation: horizontal 16:9.
- Minimum: 1920×1080.
- 4K is acceptable; normalize later to 1080p.
- Source fps: 24/25/30/60 acceptable; processed default: 30fps CFR.
- Processed video: MP4, H.264, yuv420p, no baked captions, preferably no source audio.
- Prefer 5–20s of clean continuous footage per clip.
- Avoid watermarks, large text, unrelated logos, rapid montage edits, and misleading brand/facility claims.

These are sourcing preferences, not acceptance gates for user-provided media.
Accept a related user-provided context clip when its broad meaning supports the
narration. Accept user-provided report screenshots even when they are
low-resolution; record the limitation as `resolution_warning` and do not ask
for a replacement before proceeding.

## Where to search

Free-first:

1. Pexels
2. Pixabay
3. Mixkit

Paid supplements when free sources are weak:

1. Envato Elements
2. Adobe Stock

### Do not procure by duration alone

When the user allows reuse for a full-length composition, do not initiate a
new sourcing request merely because unique footage is shorter than the target
timeline. Looping and reuse are allowed with varied trims, crops, scale, speed,
opacity, layout, or spacing. Additional footage is optional; source more only
when an existing asset cannot support a beat honestly, is technically
unusable, or the user explicitly asks to reduce repetition.
3. Shutterstock
4. Artgrid

Evidence assets should come from authentic first-party/source material: company websites, filings, investor relations, report PDFs, or user-provided documents.

## Search rules

- Search in English first.
- Provide 2–5 primary keywords plus 2–5 backup keywords per asset class.
- Prefer concrete visual nouns: `PCB factory`, `circuit board macro`, `electronics production line`, `AI server room`, `data center racks`.
- For specialist materials, do not force an inaccurate exact claim. A related
  context substitute is acceptable when labeled only as context; use
  programmatic explanation for the exact specialist claim.

## Shot-language tags

Use lightweight guidance only:

- `wide`: facility / data center / large environment.
- `medium`: operator / production line / equipment group.
- `macro`: PCB / material / component detail.
- `static`: stable composition.
- `slow_push`: gentle forward emphasis.
- `pan`: horizontal reveal.
- `tracking`: movement along a process/line.
- `low_motion` / `high_motion`: movement intensity.

## Required procurement fields

Every row in `assets_required.csv` should include:

`asset_id, evidence_level, purpose, suggested_sites, keywords_primary, keywords_backup, quantity, orientation, min_resolution, preferred_duration, shot_language, avoid, filename`

Example filename patterns:

- `pcb_factory_001.mp4`
- `pcb_macro_001.mp4`
- `server_room_001.mp4`
- `report_goldman_cover.png`
