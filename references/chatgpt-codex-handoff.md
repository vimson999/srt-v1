# ChatGPT -> Git -> Codex handoff contract

This document defines the persistent collaboration boundary for `srt-v1`.

The goal is to keep high-value reasoning separate from implementation work without losing context between sessions. ChatGPT and Codex may both reason, but they have different authority. Git is the shared system of record.

## 1. Core model

```text
SRT / brief / evidence
        |
        v
ChatGPT: director / reasoning layer
        |
        | commit director revision
        v
Git: versioned system of record
        |
        | exact revision + project handoff
        v
Codex: implementation / engineering layer
        |
        | commit implementation revision
        v
render + tests + regression evidence
```

A new session must recover project state from committed artifacts before relying on remembered conversation context.

## 2. Authority boundary

| Area | ChatGPT director authority | Codex implementation authority |
| --- | --- | --- |
| SRT meaning and argument structure | Primary | Read-only unless a contradiction/blocker is found |
| Claim / evidence responsibility | Primary | Must preserve |
| Chapter / visual beat / shot intent | Primary | Must preserve |
| Visual relationship and information change | Primary | Must realize |
| Renderer/component architecture | May constrain where necessary | Primary |
| Remotion / HyperFrames / ffmpeg implementation | Contract only | Primary |
| Asset trims, crops, technical transforms | May specify semantic requirements | Primary |
| Tests, preflight, resumable rendering | May specify required gates | Primary |
| Public release / paid licensing / destructive changes | Human authorization required | Human authorization required |

Codex may choose a different technical implementation when it preserves the director contract. It must not reinterpret the director contract into a cheaper semantic result merely because implementation is easier.

Examples of prohibited semantic downgrade include replacing a required relationship, evidence composition, source-timed comparison, or state transformation with generic `title + paragraph + cards` unless the director contract itself permits that form.

## 3. Director contract

For a non-trivial project, ChatGPT should persist the useful reasoning into repository artifacts rather than leaving it only in chat.

Expected project artifacts may include:

```text
projects/<project_id>/
  input/subtitles.srt
  input/script.txt
  DESIGN.md
  narrative_map.json
  chapter_arcs.json
  visual_beats.jsonl
  storyboard/storyboard.jsonl
  data/motion_cues.json
  manifest/production_state.json
  handoff/codex-task.md
```

Not every file has to be populated before every handoff. The handoff file must identify which artifacts are authoritative for the current revision and which remain pending.

The director revision should answer the questions that materially affect implementation:

- what the narration is arguing;
- what evidence or exact values are required;
- what the viewer must see change, compare, locate, accumulate, transform, or connect;
- where the attention target changes with the narration;
- which shots require visual-first authoring rather than a generic UI shell;
- which known regression classes are especially relevant;
- what representative range or cases should prove the implementation before broad scaling.

ChatGPT should not over-specify low-level code when several implementations can honestly satisfy the same visual responsibility.

## 4. Codex implementation contract

Codex begins by reading the repository root `AGENTS.md`, this file, and the project's `handoff/codex-task.md`.

Codex owns normal engineering execution inside the authorized scope:

- renderer/component implementation;
- asset ingestion and technical processing;
- source ranges, trims, crops, transforms and caching;
- tests and regression scripts;
- representative rendering and implementation-side fixes;
- render preflight, segmentation, retries and export reliability;
- performance/debugging work that does not change director meaning.

Codex should solve implementation problems autonomously. It should not return to the user or ChatGPT merely because a component is inconvenient to build.

Codex must not silently change director intent. If the required result cannot be implemented honestly with the current inputs, Codex records the blocker and escalates the smallest director-level question rather than inventing a lower-quality substitute.

## 5. Handoff lifecycle

### Director handoff

Before implementation handoff, ChatGPT should update `handoff/codex-task.md` with:

- director revision / commit SHA when available;
- authoritative project files;
- implementation scope;
- relevant regression classes and case IDs;
- representative sample target;
- known blockers or missing inputs;
- explicit read-only director decisions that Codex must not reinterpret.

The repository commit is the handoff boundary. A chat message may summarize the revision, but Git holds the durable state.

### Implementation return

After implementation, Codex should commit the implementation revision and record:

- implementation locations;
- tests run and their results;
- representative render artifact/revision;
- regression results;
- unresolved implementation blockers;
- any request for a director decision.

If the issue is implementation-only, Codex keeps working. If the issue changes the meaning, evidence duty, visual argument, or accepted project standard, it returns to the director layer.

## 6. Conflict and escalation rules

Use the narrowest responsible layer.

**Codex resolves without director escalation:**

- component bugs;
- CSS/layout mechanics that preserve composition intent;
- codec/ffmpeg/render failures;
- performance/concurrency issues;
- equivalent asset processing technique;
- alternate code structure that preserves the same visible behavior.

**Return to ChatGPT director layer when:**

- source evidence contradicts the current argument contract;
- an exact required source/fact is unavailable and substitution would be misleading;
- two materially different visual interpretations remain equally valid and the contract does not choose one;
- implementation would require weakening an explicit director responsibility;
- a repeated regression indicates the director/production contract itself is underspecified or wrong.

**Return to the human only when the human-in-the-loop policy requires it.** Read `references/human-in-loop.md`. Routine QA failure is not a reason to ask the human for acceptance.

## 7. Revision discipline

Use two conceptual revision types:

- **director revision** — changes to meaning, design responsibility, evidence, visual beats, shot intent, or project standard;
- **implementation revision** — code, renderer behavior, asset processing, performance, tests, and render output that realize an unchanged director contract.

A Codex implementation revision must identify which director revision it implements. If director artifacts change, previous implementation evidence may be stale and should be revalidated only where affected.

Do not rely on phrases such as “same as last chat” as a durable dependency. Persist the decision or point to a committed artifact.

## 8. Regression case library relationship

Normal projects live under `projects/<project_id>/`. They do not automatically become regression cases.

When a real project exposes a new systemic failure:

```text
real project failure
    -> classify/generalize
    -> extract smallest realistic SRT window
    -> add to tests/fixtures/srt-regression/
    -> register in cases.json
    -> keep the project-specific details out of the reusable rule where possible
```

The case library is a permanent failure-prevention asset, not a dump of every project.

## 9. New-session recovery

A new ChatGPT session should be able to start with a request such as:

> Open `vimson999/srt-v1`, read `AGENTS.md` and `SKILL.md`, then follow the repository handoff contract for this SRT.

A new Codex session should be able to start with:

> Read root `AGENTS.md` and `projects/<project_id>/handoff/codex-task.md`. Implement the current director revision without redoing or downgrading the director analysis. Run relevant tests/regression before preview.

These prompts are navigation hints, not the source of truth. The repository contract is the durable source of truth.

## 10. Success criterion

The collaboration succeeds when a new session can answer, from Git alone:

1. what has already been decided;
2. which revision is authoritative;
3. what remains to implement;
4. what Codex may change freely;
5. what Codex must not reinterpret;
6. what tests/regressions prove the next milestone;
7. what issue, if any, genuinely requires director or human input.
