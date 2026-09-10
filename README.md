# srt-visual-director

A reusable agent skill for turning timed narration/SRT into a renderer-agnostic visual-director project: initialization, visual direction, asset procurement, asset audit, executable timeline contracts, subtitle-aware production handoff, and renderer execution guidance.

## Install in Codex / compatible agents

Copy this folder to:

```bash
~/.agents/skills/srt-visual-director/
```

or the runtime-specific personal skills directory.

## Minimal use

Provide a final SRT and ask the agent to use `srt-visual-director`.

For a new project, the skill should first initialize `projects/<project_id>/`, copy the SRT to `input/subtitles.srt`, extract `input/script.txt`, write `project.json`, and create the standard project skeleton before storyboarding.

For finance content, the skill defaults to horizontal 16:9, 1920×1080, 30fps, and burned-in subtitles unless instructed otherwise. For recurring finance
video production, it also uses a shared `asset-library/` beside `projects/`;
asset IDs are shared while audio and subtitles remain project-owned.

After the user supplies requested media, they only need to place it in
`asset-library/inbox/<project_id>/` and say “素材已准备好，继续”. The agent
intakes, deduplicates, describes, indexes, and binds the files; the user does
not need to run catalog commands.

## Optional initialization utility

```bash
python3 scripts/init_project.py /path/to/final.srt \
  --factory-root /path/to/report-video \
  --project-id my_project
```

The utility refuses to overwrite an existing project.

## Internal asset intake

The agent can run `scripts/intake_assets.py` for a project drop zone. It copies
new media by content hash, leaves the source untouched, refreshes the shared
catalog, and leaves new items in `catalog/review_queue.json` until visual and
provenance review is complete.

## V2 storyboard contract

Phase 1 storyboards use `storyboard/storyboard.jsonl` as the canonical rich
shot contract. Each line describes Beat position, the shot information state,
one semantic visual action, a motion budget, and the handoff to the next shot.
`storyboard/storyboard.csv` remains a compact review projection.

Validate a completed storyboard with:

```bash
python3 scripts/validate_storyboard.py projects/<project_id>/storyboard/storyboard.jsonl
```

The validator checks structure and sequence continuity. Evidence authenticity,
Timed Attention Cue timing, rendered visual quality, and render reliability
remain separate review responsibilities.
