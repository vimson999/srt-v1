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

## 15. Beat progression for accumulating evidence

Input: six institutional reports are introduced one at a time and should end
as a visible consensus before the target-price comparison.

Expected: keep one Visual Beat with contiguous shot positions and roles such as
`establish`, `develop`, `emphasize`, and `resolve` or `bridge`; do not create a
new Shot Group layer or render six unrelated cards.

## 16. Shot information peak and reading hold

Input: a data-heavy shot reveals a margin bridge and the narration states its
conclusion near the end of the interval.

Expected: record ordered `development_states`, identify one
`information_peak`, and add a justified `reading_hold`; do not assume every
shot uses the same fixed duration or generic scale animation.

## 17. Intentional contrast cut

Input: the film moves from a dense report evidence page to a clean full-screen
judgment with no visual object that should continue across the cut.

Expected: use `continuity_axis=none` and explain the editorial turn in
`contrast_reason`; a decorative dissolve is not required to make the contract
valid.

## 18. Broken interior handoff

Input: an interior shot has no entry anchor and declares a non-`none`
continuity axis, or declares a contrast cut without a reason.

Expected: `scripts/validate_storyboard.py` fails with the shot context and the
missing handoff field; the renderer is not asked to invent continuity.

## 19. Semantic Shot Language selection

Input: one Beat verifies an authentic report, accumulates six institutions into
a consensus, and then compares their target prices.

Expected: retrieve Shot Language candidates from each shot's primary
`visual_action`; use families such as `report_reveal`,
`sequential_card_build`, and `aligned_comparison` only where their fit and
lifecycle apply. Record one selected family and a shot-specific
`selection_reason`; do not turn the sequence into unrelated card layouts.

## 20. Effect-count and layout-quota pressure

Input: a style request asks for more visual variety by requiring several
effects in every shot or a layout change after a fixed number of shots.

Expected: preserve the semantic action, information peak, reading hold, motion
budget, and handoff as the selection criteria. Do not encode effect counts,
fixed layout quotas, mandatory 3D, or animation in every shot as Shot Language
rules.

## 21. Renderer-first recipe pressure

Input: an implementation has an attractive renderer component, but its pattern
does not match the shot's selected Shot Language or declared information peak.

Expected: preserve the shot contract and record a recipe gap or choose another
compatible recipe. Do not change `visual_action`, evidence, state order,
reading hold, motion budget, or handoff merely to reuse the component.

## 22. Repetition warning without aesthetic auto-fix

Input: three consecutive shots intentionally use the same comparison mode and
semantic action because the narration develops one shared scale.

Expected: sequence review emits a structured warning and energy annotations,
but does not fail the contract or automatically force a layout change. Review
the rendered sequence and keep the repetition when it serves comprehension.
