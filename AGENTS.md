# srt-v1 agent map

This repository uses a **ChatGPT -> Git -> Codex** collaboration model.

- **ChatGPT is the director / reasoning layer.** For a new SRT, use `SKILL.md` plus the relevant references to understand the argument, evidence, visual beats, shot responsibilities, regression risks, and project standard. ChatGPT should persist the resulting director artifacts into the project and commit a director revision.
- **Git is the system of record.** Cross-session collaboration must rely on committed repository artifacts and revision IDs, not on remembered chat context. If an important decision is not committed, do not assume another session or agent knows it.
- **Codex is the implementation layer.** Codex reads the committed director contract and project handoff, then implements, tests, renders, debugs, and optimizes. Codex may change implementation technique, but it must not silently reinterpret or downgrade the director intent for convenience.

Read `references/chatgpt-codex-handoff.md` for the full authority boundary, artifact contract, handoff lifecycle, and escalation rules.

## Entry points

For SRT directing or planning:
1. Read `SKILL.md`.
2. Read `references/chatgpt-codex-handoff.md`.
3. Work inside `projects/<project_id>/` and preserve the SRT as timing truth.
4. Commit the director revision before handing implementation to Codex.

For Codex implementation:
1. Read this file and `references/chatgpt-codex-handoff.md`.
2. Read `projects/<project_id>/handoff/codex-task.md`.
3. Treat committed director artifacts as requirements, not suggestions to replace with an easier generic layout.
4. Run the repository tests and relevant regression cases before claiming completion.

## Persistent collaboration rule

New ChatGPT or Codex sessions should recover state from Git first. Chat memory can help, but repository artifacts are authoritative.
