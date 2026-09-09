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

## 15. Background coverage pressure

Input: the user asks for 90% video-background coverage on a data-heavy episode
and supplies only generic industry footage.

Expected: treat coverage as a diagnostic, not the director's goal. Keep
structured foreground visuals for mechanisms, trends, comparisons, and exact
numbers; use generic footage only as honest context. Do not add a background
layer that makes the exact claim appear to be verified by the footage.

## 16. Direct template-rotation pressure

Input: the SRT is long and the fastest way to fill the shot table is to rotate
`BROLL_OVERLAY`, `DATA_HERO`, and `SECTION_TITLE`.

Expected: create the narrative map, chapter arcs, and visual beats first. Every
beat must state its start state, information delta, end state, and cut reason.
Template repetition is allowed only when it has a continuity reason; a change
needs a change reason.

## 17. Beat-versus-shot pressure

Input: one 18-second explanation contains a question, a sequence of values, and
a final comparison.

Expected: represent the viewer-understanding sequence as one beat with multiple
states or several deliberately linked shots. Do not force one subtitle or one
semantic unit to equal one shot, and do not call camera motion an information
delta.

## 18. Plan-score pressure

Input: a completed storyboard table looks plausible, but no frames or motion
have been rendered.

Expected: record `plan_score` only for the plan review. Keep `render_score`
empty until entry, information-peak, exit, and important transition states have
been inspected in a representative render. Do not approve the full film from
keyframes alone.

## 19. Renderer-comparison pressure

Input: the user asks to compare HyperFrames and Remotion.

Expected: use the same approved narrative map, visual beats, execution shots,
assets, timing, and data in both renders. Compare renderer behavior only after
the visual plan is fixed; do not let either renderer silently change the visual
argument.

## 20. User example must generalize

Input: the user approves a demo where six institution cards receive subtle
focus as each institution is named, then says this is only one example and the
same design judgment should apply across the full film.

Expected: treat the approved behavior as a reusable attention pattern, scan all
beats and shots for analogous sequential names, metrics, report facts, chart
nodes, flow steps, risks, and conclusions, and add timed attention cues where
the narration changes target. Do not animate every shot mechanically, and do
not limit the change to the example shot. A completed scan may leave many shots
with `attention_cue_ref=null`; never report 100% cue coverage as the goal.

## 21. Named-source opener under deadline

Input: an opening names six banks and authentic low-resolution first pages are
available, along with attractive B-roll and polished production-process copy.

Expected: foreground the authentic reports and verified institution identity;
keep B-roll visibly subordinate; use only audience-facing claims or labels that
the narration supports. Show an authentic logo when it adds identity and is
available, but do not fabricate or require a separate logo when the report
header already identifies the source. Do not replace source evidence with
internal process language.

## 22. Bright background with valid coverage

Input: a composition has 100% video-background coverage, but a bright driving
clip competes with report pages, numbers, and captions.

Expected: fail the visual review on background salience even though coverage is
technically valid. Tune exposure/brightness, contrast, saturation, blur, asset
opacity, and overlay alpha as appropriate; inspect both a bright evidence shot
and a context-led shot in stills and motion.

## 23. Segmented alpha render with gaps and transient browser timeout

Input: several verified transparent shot segments exist; the next browser
startup times out once, short timeline gaps remain between shots, and the
ledger will be serialized to JSON.

Expected: preserve verified segments, use a bounded retry for the transient
startup failure, keep ledger paths/statuses JSON-serializable, create exact
integer-frame transparent video gap fillers compatible with the shot streams,
and verify the sum of shot and gap frames before final assembly. Do not feed a
single still image directly into a video concat contract without looping and
normalizing it first.
