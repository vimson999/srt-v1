# Execution Handoff

## Renderer boundary

The visual-director output is renderer-agnostic. Remotion, HyperFrames, Premiere, AE, or another engine consumes the same storyboard/timeline/assets contracts.

Do not let the renderer redesign source-of-truth data unless an explicit error is found.

## Recommended persistent engine layout

For repeated programmatic production, prefer one reusable engine and many project folders:

```text
report-video/
  engine/
  asset-library/
  projects/
    project-a/
    project-b/
```

Do not scaffold and reinstall a new Remotion project for every episode when a reusable engine already exists.

Do not copy the shared asset library into an episode. Resolve project
`asset_id` references through the catalog or a documented renderer mount. Keep
project-local media only when it is genuinely owned by that episode.

## Subtitle rule

Any rendered review or final video burns subtitles in by default unless the user opts out.

- SRT is a dedicated caption layer.
- Preserve subtitle timing.
- When rendering an excerpt, apply the correct time offset.
- Keep a subtitle-safe region free from chart labels and critical numbers.
- Do not duplicate full subtitle sentences as foreground explanatory copy.

## First render strategy

1. Validate all JSON and media refs.
2. Render a representative 30–90s section first if the visual system is unproven.
3. After approval, scale the same design system to the full timeline.
4. Use preview quality first (e.g. 720p) for full-length V1; render final 1080p after review.

For high-background finance programs, include a coverage report in the handoff:
target coverage, measured coverage, unique usable footage seconds, semantic
alternates, and any conspicuous reuse. Background visibility/opacity is a
separate visual check from coverage.

For the operational preflight, segmented retry strategy, audio muxing, temp-file
safety, and post-render media verification, read
`references/render-reliability.md`. Keep those mechanics renderer-agnostic so
the same handoff applies when the engine changes.
