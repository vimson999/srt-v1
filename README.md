# srt-visual-director

A reusable agent skill for turning timed narration/SRT into a renderer-agnostic visual-director project: narrative mapping, chapter arcs, visual beats, execution shots, asset procurement, asset audit, executable timeline contracts, subtitle-aware production handoff, and renderer execution guidance.

The core planning chain is:

`SRT → narrative_map.json → chapter_arcs.json → visual_beats.jsonl → storyboard.jsonl → plan review → representative render review`

`storyboard.csv` remains available as a compatibility export, but it is not the
director source of truth. Background coverage is a diagnostic; visual quality is
judged by whether each beat makes the intended information change visible.

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

For non-trivial projects, also read `references/visual-direction.md` and
`references/visual-quality-review.md`. Keep the generic rules here; put company,
report, number, chapter, and asset facts in the project contracts.

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

Phase 2 adds the small semantic registry in `templates/shot-language.yaml`.
Use the shot's `visual_action` to retrieve compatible families, then record one
`shot_language.family` and a shot-specific `selection_reason`. The registry
defines reusable information lifecycles and handoff tendencies; it is not an
effect catalog or a rule that every shot must change layout.
