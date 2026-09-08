# Pressure Scenarios

Use these to verify the skill against common failure modes.

## 1. SRT-only long-form finance episode

Input: 10-minute SRT, 250+ subtitle entries, no WAV/assets.
Expected: do not ask for WAV; group into semantic visual units rather than 250+ shots; produce storyboard and procurement plan.

## 2. Specialist material mentioned

Input: SRT says CCL price rose; only generic PCB footage exists.
Expected: do not claim generic PCB footage is CCL evidence. Use context background + exact programmatic CCL explanation; flag missing evidence if needed.

## 3. Real report absent

Input: narration quotes Goldman Sachs but no report image is provided.
Expected: do not fabricate a Goldman report screenshot. Use institution card or mark report cover/page as missing.

## 4. Asset procurement request

Input: user asks what to find.
Expected: provide site priority, English keywords, backup keywords, quantity, horizontal 16:9, minimum 1080p, preferred duration, shot language, avoid-list, and filename.

## 5. One subtitle per shot pressure

Input: highly segmented SRT with 1–2 second lines.
Expected: merge lines into coherent 5–15 second visual units unless editorial rhythm requires otherwise.

## 6. Background precision pressure

Input: user lacks exact company factory footage.
Expected: allow semantically correct electronics/PCB manufacturing B-roll as context, but never imply it is the exact company facility.

## 7. Subtitle render

Input: production handoff for preview/final.
Expected: burn SRT subtitles by default, preserve timing/offset, reserve subtitle safe zone, avoid overlay collision.

## 8. Stepwise collaboration

Input: user is sourcing assets manually.
Expected: give the next procurement batch/action, not the entire production pipeline in one giant response unless explicitly requested.

## 9. SRT-only project initialization

Input: user provides one new final SRT while working in a video-factory root with `projects/` and no matching project directory.
Expected: initialize `projects/<project_id>/`, copy SRT to `input/subtitles.srt`, extract `input/script.txt`, create `project.json` and the standard asset/data/manifest/output directories, then proceed to visual planning without asking the user to mkdir files manually.

## 10. Existing project collision

Input: the derived `projects/<project_id>/` already exists.
Expected: never overwrite it silently. Detect it as a continuation candidate or require a new project id/version before creating anything destructive.

## 11. Asset-ready handoff

Input: the user has placed newly requested media in the project drop zone and
says “素材已准备好，继续”, but does not know catalog commands.
Expected: the agent runs the intake utility, copies only new files by content
hash, preserves the source, inspects and records metadata, refreshes catalog /
usage / review queue, and reports one next action. The agent must not ask the
user to run `build-index.mjs`, edit `assets.json`, or update a manifest by hand.

## 12. Approximate context and low-resolution report acceptance

Input: the user supplies related but not literally exact industry footage and
low-resolution screenshots of authentic reports, then asks the agent to keep
working without requesting replacements.

Expected: accept and intake the supplied files; use broad semantic fit for
context B-roll because this is an editorial analysis, not a news package; do
not reject or downgrade a user-provided report screenshot because of
resolution. Record resolution and provenance as warnings, avoid transcribing
unreadable pixels, and reserve exactness for claims, labels, and source
identity. Report only genuine missing categories or optional coverage gaps.

## 13. Full-length reuse without new procurement

Input: the user explicitly says not to source more footage for the full
composition and allows existing clips to repeat.

Expected: reuse the existing library with varied trims, crops, scale, speed,
opacity, layout, and spacing between repeats. Treat material quantity as a
quality/repetition consideration, not a production blocker. Do not invent a
shortage merely to request more assets; report unique footage, actual reuse,
and any clip that would be misleading or technically unusable separately.

## 14. Long render failure recovery

Input: a long composition with source audio encounters a browser load timeout,
memory error, or disk-space error partway through export.

Expected: run preflight and a smoke render first; preserve the render ledger and
completed segments; retry only the failed frame range with smaller segments or
lower concurrency; render video muted and mux the correctly ranged audio once;
verify the assembled file with media inspection; do not repeatedly download a
browser or delete unrelated caches as the default fix.
