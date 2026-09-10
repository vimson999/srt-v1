# SRT Visual Director V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Upgrade srt-v1 with a validated, renderer-agnostic middle directing layer for Beat progression, Shot Information State, Visual Action, Motion Budget, and Shot Handoff while preserving the existing narrative, evidence, attention-cue, render-review, and render-reliability responsibilities.

**Architecture:** Keep the existing Narrative Map → Chapter → Visual Beat → Shot editorial hierarchy and treat Visual Beat as the shot-grouping unit. Add one canonical storyboard/storyboard.jsonl shot contract beneath it; keep storyboard.csv as a compact compatibility projection. A dependency-free validator enforces structure and continuity, while aesthetic judgment and rendered-pixel review remain in the existing Evidence, Timed Attention Cue, Render Review, and Render Reliability workflows.

**Tech Stack:** Python 3 standard library, JSONL, CSV, Markdown, Node.js only for the existing hermetic asset-index test fixture, and Git.

**Spec:** docs/superpowers/specs/2026-09-10-srt-v2-director-contract-design.md

## Global Constraints

- storyboard/storyboard.jsonl is the canonical rich Phase 1 contract; storyboard/storyboard.csv is a compact review/export projection and must not become a competing source of truth.
- Preserve start_state, information_delta, end_state, Evidence, Timed Attention Cue, Render Review, and Render Reliability semantics; add missing state fields instead of renaming or duplicating layers.
- Do not introduce a Shot Group layer; Visual Beat already groups executable shots into one editorial unit of understanding.
- Required semantic actions are establish, focus, compare, accumulate, causal, verify, turn, conclude, and pause.
- reading_hold.min_seconds is shot guidance justified by an editorial reason, not a universal fixed-duration rule.
- Motion Budget records one primary motion responsibility, at most one optional supporting responsibility, and an ambient/background policy; it does not require a fixed effect library or animation on every shot.
- Intentional hard cuts are valid when continuity_axis=none and contrast_reason explains the semantic discontinuity.
- Use only Python standard-library production code in Phase 1; do not add renderer-specific dependencies.
- Every implementation phase ends with a focused test run, the full available regression suite, a Git commit, and a push to the requested GitHub remote when network access permits.
- The branch is feat/v2-director-contract; the base branch is the existing main at dd9fcb4.

---

### Task 1: Establish the V2 plan and a hermetic baseline

**Files:**

- Create: docs/superpowers/specs/2026-09-10-srt-v2-director-contract-design.md
- Create: docs/superpowers/plans/2026-09-10-srt-v2-director-contract.md
- Modify: tests/test_asset_acceptance_policy.py
- Modify: tests/test_asset_intake.py
- Create: tests/fixtures/build-index.mjs

**Interfaces:**

- Consumes: the current repository at dd9fcb4 and its existing standard-library tests.
- Produces: an approved V2 design, this task-by-task plan, and a test suite that does not depend on /Users/v9/Downloads/report-video.

- [x] **Step 1: Inspect the current branch and test entry points**

Run:

~~~
git status --short --branch
git log --oneline -1
python3 tests/test_init_project.py
python3 tests/test_reuse_policy.py
python3 tests/test_render_reliability_policy.py
python3 tests/validate_skill.py
~~~

Expected baseline: the four repository-local tests pass; the two asset tests may fail because their hard-coded external index-builder path is absent.

- [x] **Step 2: Write the approved architecture and staged plan**

Record the canonical JSONL contract, compatibility policy, state machine, semantic action vocabulary, motion budget, handoff rules, validator boundary, and Phases 0–5 in the two documentation files listed above.

- [x] **Step 3: Add a local test fixture for metadata merge behavior**

Create tests/fixtures/build-index.mjs as a test-only Node script that reads catalog/assets.json or a project snapshot, merges catalog/metadata.json fields such as description, tags, status, and notes, preserves computed file_exists and file_size_bytes, and writes the catalog. The fixture must contain the literal field names resolution_warning and acceptance_basis so policy tests can assert that the test contract covers them.

- [x] **Step 4: Point asset tests at the fixture**

Replace the absolute Path('/Users/v9/Downloads/report-video/...') references with ROOT / 'tests' / 'fixtures' / 'build-index.mjs'. Keep the existing idempotent intake and metadata-merge assertions unchanged in meaning.

- [x] **Step 5: Verify the hermetic baseline**

Run:

~~~
python3 tests/test_init_project.py
python3 tests/test_reuse_policy.py
python3 tests/test_render_reliability_policy.py
python3 tests/test_asset_acceptance_policy.py
python3 tests/test_asset_intake.py
python3 tests/validate_skill.py
~~~

Expected: six commands exit 0 and print their existing PASS messages.

- [x] **Step 6: Commit the plan and baseline repair**

~~~
git add docs/superpowers/specs/2026-09-10-srt-v2-director-contract-design.md \
  docs/superpowers/plans/2026-09-10-srt-v2-director-contract.md \
  tests/test_asset_acceptance_policy.py tests/test_asset_intake.py \
  tests/fixtures/build-index.mjs
git commit -m "docs: plan srt visual director v2 upgrade"
git push -u origin feat/v2-director-contract
~~~

Expected: the commit is created on feat/v2-director-contract; the push updates the GitHub branch or reports a network/authentication blocker without rewriting history.

### Task 2: Add the Phase 1 storyboard validator with TDD

**Files:**

- Create: tests/test_storyboard_contract.py
- Create: scripts/validate_storyboard.py

**Interfaces:**

- Consumes: one JSON object per non-empty line in storyboard/storyboard.jsonl.
- Produces: validate_record(record: dict, line_number: int = 1) -> list[str], validate_sequence(records: list[dict]) -> list[str], validate_storyboard(path: Path) -> list[str], and a CLI that exits 0 for a valid file and 1 with contextual errors for an invalid file.

- [x] **Step 1: Write the failing contract tests**

Create a test module that imports scripts/validate_storyboard.py by file path and defines a valid VALID_SHOT fixture with all legacy and V2 fields. Add these named checks:

~~~
def test_accepts_complete_shot_contract():
    assert mod.validate_record(VALID_SHOT) == []

def test_requires_information_peak_and_development_states():
    record = dict(VALID_SHOT)
    record.pop("information_peak")
    record["development_states"] = []
    errors = mod.validate_record(record)
    assert any("information_peak" in error for error in errors)
    assert any("development_states" in error for error in errors)

def test_rejects_motion_budget_with_two_supporting_actions():
    record = dict(VALID_SHOT)
    record["motion_budget"] = dict(VALID_SHOT["motion_budget"])
    record["motion_budget"]["supporting"] = [
        {"action": "slow_push", "layer": "background"},
        {"action": "drift", "layer": "decoration"},
    ]
    errors = mod.validate_record(record)
    assert any("supporting" in error for error in errors)

def test_requires_reason_for_interior_contrast_cut():
    first = dict(VALID_SHOT)
    second = dict(VALID_SHOT)
    first["shot_id"], second["shot_id"] = "S01", "S02"
    first["beat_position"], second["beat_position"] = 1, 2
    first["entry_anchor"] = None
    second["continuity_axis"] = "none"
    second["contrast_reason"] = None
    errors = mod.validate_sequence([first, second])
    assert any("contrast_reason" in error for error in errors)

def test_requires_contiguous_positions_inside_each_beat():
    first = dict(VALID_SHOT)
    second = dict(VALID_SHOT)
    first["shot_id"], second["shot_id"] = "S01", "S02"
    first["beat_position"], second["beat_position"] = 1, 3
    errors = mod.validate_sequence([first, second])
    assert any("beat_position" in error for error in errors)
~~~

- [x] **Step 2: Run the focused test to verify the expected red state**

Run:

~~~
python3 tests/test_storyboard_contract.py
~~~

Expected: import failure because scripts/validate_storyboard.py does not exist. If the test errors for another reason, fix the test harness until the missing production module is the only failure.

- [x] **Step 3: Implement the minimal validator**

Implement the dependency-free validator with these exact rules:

~~~
def validate_record(record: dict, line_number: int = 1) -> list[str]: ...
def validate_sequence(records: list[dict]) -> list[str]: ...
def validate_storyboard(path: Path) -> list[str]: ...
~~~

Require schema_version == 2, unique non-empty shot_id fields, start < end, the legacy fields chapter, narration_focus, visual_mode, visual_design, on_screen_text, motion, and asset_need, plus beat_id, integer beat_position >= 1, valid role_in_beat, valid visual_action, start_state, information_delta, non-empty development_states, information_peak, reading_hold, end_state, attention_target, motion_arc, motion_reason, motion_budget, transition_reason, continuity_axis, contrast_reason, exit_anchor, and entry_anchor.

Require every development state to contain state_id, numeric relative_start in the shot duration range, description, and attention_target, in non-decreasing order. Require reading_hold.required to be boolean; when true, require positive numeric min_seconds and a reason. Require motion_budget.primary to be an object with action, layer, and intensity; permit supporting to be null or one object only; require background_policy.

For sequence validation, reject duplicate IDs, negative or overlapping chronology, beat positions that do not start at 1 and increment by 1, an interior transition lacking anchors unless it uses continuity_axis=none with a non-empty contrast_reason, and a non-none axis without an exit or entry anchor. The first shot may have a null entry anchor; the last shot may have a null exit anchor.

- [x] **Step 4: Run the focused tests to verify green**

Run:

~~~
python3 tests/test_storyboard_contract.py
~~~

Expected: all five named checks pass with no traceback.

- [x] **Step 5: Verify the CLI failure and success paths**

Run:

~~~
python3 scripts/validate_storyboard.py --help
tmp_storyboard="$(mktemp)"
cp templates/storyboard.jsonl "$tmp_storyboard"
python3 scripts/validate_storyboard.py "$tmp_storyboard"
~~~

Expected: help exits 0; the canonical template exits 0. Do not leave the temporary file in the repository.

- [x] **Step 6: Commit the validator**

~~~
git add scripts/validate_storyboard.py tests/test_storyboard_contract.py
git commit -m "feat: validate v2 storyboard shot contracts"
git push origin feat/v2-director-contract
~~~

### Task 3: Initialize the V2 storyboard artifacts and templates with TDD

**Files:**

- Modify: scripts/init_project.py
- Modify: tests/test_init_project.py
- Modify: templates/storyboard.csv
- Create: templates/storyboard.jsonl

**Interfaces:**

- Consumes: the existing SRT initialization API initialize_project(...).
- Produces: empty storyboard/storyboard.jsonl, a header-only storyboard/storyboard.csv, and storyboard/director_summary.md in every new project, plus a storyboard_contract entry in project.json that names the canonical contract and validator.

- [x] **Step 1: Extend the initialization test before production changes**

Add assertions to tests/test_init_project.py:

~~~
jsonl_path = project / "storyboard" / "storyboard.jsonl"
csv_path = project / "storyboard" / "storyboard.csv"
summary_path = project / "storyboard" / "director_summary.md"
if not jsonl_path.exists() or jsonl_path.read_text(encoding="utf-8") != "":
    raise SystemExit("FAIL canonical storyboard.jsonl should start empty")
if csv_path.read_text(encoding="utf-8").splitlines()[0] != mod.STORYBOARD_CSV_HEADER:
    raise SystemExit("FAIL storyboard.csv header contract")
if "pending phase 1" not in summary_path.read_text(encoding="utf-8").lower():
    raise SystemExit("FAIL director summary initialization")
if project_json.get("storyboard_contract", {}).get("path") != "storyboard/storyboard.jsonl":
    raise SystemExit("FAIL storyboard contract pointer")
~~~

- [x] **Step 2: Run the initialization test to verify red**

Run:

~~~
python3 tests/test_init_project.py
~~~

Expected: failure stating that the canonical storyboard.jsonl or contract pointer is missing.

- [x] **Step 3: Implement the smallest initialization change**

Add a module constant:

~~~
STORYBOARD_CSV_HEADER = "shot_id,start,end,beat_id,beat_position,role_in_beat,chapter,narration_focus,visual_mode,visual_action,visual_design,on_screen_text,motion,motion_budget,asset_need,transition_reason,continuity_axis"
~~~

Add these non-overwriting initialization payloads:

~~~
"storyboard/storyboard.jsonl": "",
"storyboard/storyboard.csv": STORYBOARD_CSV_HEADER + "\\n",
"storyboard/director_summary.md": "# Director Summary\\n\\nStatus: pending Phase 1.\\n",
~~~

Add this project pointer without changing the existing schema_version:

~~~
"storyboard_contract": {
    "version": 2,
    "path": "storyboard/storyboard.jsonl",
    "summary_path": "storyboard/director_summary.md",
    "csv_projection_path": "storyboard/storyboard.csv",
    "validator": "scripts/validate_storyboard.py",
}
~~~

- [x] **Step 4: Create the canonical JSONL template**

Create templates/storyboard.jsonl with one valid generic record using SHOT_TEMPLATE_001, BEAT_TEMPLATE_001, no episode-specific facts, visual_action=establish, role_in_beat=establish, a reading_hold reason, a primary motion_budget, and a null entry anchor for the first shot. The file must pass scripts/validate_storyboard.py as a one-line JSONL file.

- [x] **Step 5: Update the CSV projection header**

Keep every existing CSV column and add the compact Phase 1 fields beat_id, beat_position, role_in_beat, visual_action, motion_budget, transition_reason, and continuity_axis. Do not put JSON arrays or nested anchors into the CSV source contract.

- [x] **Step 6: Run the focused tests to verify green**

Run:

~~~
python3 tests/test_init_project.py
python3 scripts/validate_storyboard.py templates/storyboard.jsonl
~~~

Expected: both commands exit 0.

- [x] **Step 7: Commit the initialization contract**

~~~
git add scripts/init_project.py tests/test_init_project.py \\
  templates/storyboard.csv templates/storyboard.jsonl
git commit -m "feat: initialize v2 storyboard artifacts"
git push origin feat/v2-director-contract
~~~

### Task 4: Document the Phase 1 director middle layer

**Files:**

- Modify: SKILL.md
- Modify: references/output-contracts.md
- Modify: references/workflow.md
- Modify: references/execution-handoff.md
- Modify: references/finance-profile.md
- Create: references/director-contract.md
- Create: tests/test_v2_policy.py

**Interfaces:**

- Consumes: the canonical contract and validator from Tasks 2–3.
- Produces: runtime-facing guidance that routes agents to one canonical storyboard contract and explains how the new fields coexist with existing evidence, attention, and render QA.

- [x] **Step 1: Write policy tests before documentation changes**

Create tests/test_v2_policy.py with file-level assertions for these exact behaviors:

~~~
assert_contains(ROOT / "SKILL.md", [
    "Visual Beat",
    "storyboard/storyboard.jsonl",
    "do not add a separate Shot Group",
    "visual_action",
    "motion_budget",
    "transition_reason",
])
assert_contains(ROOT / "references/output-contracts.md", [
    "storyboard/storyboard.jsonl",
    "development_states",
    "information_peak",
    "reading_hold",
    "entry_anchor",
    "exit_anchor",
])
assert_contains(ROOT / "references/workflow.md", [
    "beat progression",
    "information state",
    "one primary semantic action",
    "attention handoff",
])
assert_contains(ROOT / "references/execution-handoff.md", [
    "exit_anchor",
    "entry_anchor",
    "continuity_axis",
])
~~~

- [x] **Step 2: Run the policy test to verify red**

Run:

~~~
python3 tests/test_v2_policy.py
~~~

Expected: failure on missing V2 contract wording.

- [x] **Step 3: Add the runtime contract reference**

Write references/director-contract.md with field semantics, the five Beat roles, the nine semantic actions, state-machine guidance, motion-budget guidance, anchor shape, continuity-axis values, boundary exceptions, and a direct statement that visual quality and source fidelity remain downstream of the contract.

- [x] **Step 4: Update the output contract**

Add a Phase 1 section defining storyboard/storyboard.jsonl as canonical, list the complete legacy-plus-V2 fields, define storyboard.csv as a compatibility projection, and point to scripts/validate_storyboard.py. Keep the existing director_summary.md metrics and add the Phase 1 summary requirements: Beat count, role progression, action mix, required reading holds, and unresolved handoffs.

- [x] **Step 5: Update workflow and renderer handoff guidance**

In SKILL.md and references/workflow.md, route Phase 1 through Beat progression → Shot state → Visual Action → Motion Budget → Shot Handoff. State that existing Narrative Map, Visual Beat, Evidence, Timed Attention Cue, Render Review, and Render Reliability responsibilities remain authoritative. In references/execution-handoff.md, require a renderer to consume the state and handoff fields without redesigning source data.

- [x] **Step 6: Add finance-specific pacing guidance**

In references/finance-profile.md, connect evidence-heavy moments to verify and pause, explanatory mechanisms to causal, comparisons to compare, and conclusions to conclude. State that a complex shot should be followed by a readable hold or simpler visual beat; do not prescribe fixed seconds or a mandatory layout rotation.

- [x] **Step 7: Run the policy and regression tests**

Run:

~~~
python3 tests/test_v2_policy.py
python3 tests/test_reuse_policy.py
python3 tests/test_render_reliability_policy.py
python3 tests/validate_skill.py
~~~

Expected: all commands exit 0.

- [x] **Step 8: Commit the Phase 1 documentation**

~~~
git add SKILL.md references/director-contract.md references/output-contracts.md \\
  references/workflow.md references/execution-handoff.md references/finance-profile.md \\
  tests/test_v2_policy.py
git commit -m "docs: define v2 director middle layer"
git push origin feat/v2-director-contract
~~~

### Task 5: Validate the complete Phase 1 slice

**Files:**

- Modify: tests/pressure-scenarios.md
- Modify: README.md

**Interfaces:**

- Consumes: the complete Phase 1 contract, template, validator, and references.
- Produces: user-facing installation/use documentation and pressure scenarios for sequence-aware direction.

- [x] **Step 1: Add Phase 1 pressure scenarios**

Add cases covering: six institutions accumulating into consensus, a required reading hold after a data peak, an intentional hard cut with a contrast reason, and a broken interior handoff that must fail validation. Preserve the existing asset, subtitle, reuse, and render-reliability scenarios.

- [x] **Step 2: Update README usage**

Document that a Phase 1 storyboard writes storyboard/storyboard.jsonl as the canonical rich contract, optionally emits the CSV projection for review, and can be checked with:

~~~
python3 scripts/validate_storyboard.py projects/<project_id>/storyboard/storyboard.jsonl
~~~

- [x] **Step 3: Run the complete available regression suite**

Run:

~~~
for test in tests/test_init_project.py tests/test_reuse_policy.py \\
  tests/test_render_reliability_policy.py tests/test_asset_acceptance_policy.py \\
  tests/test_asset_intake.py tests/test_storyboard_contract.py \\
  tests/test_v2_policy.py tests/validate_skill.py; do
  python3 "$test" || exit 1
done
~~~

Expected: every test exits 0.

- [x] **Step 4: Inspect the final Phase 1 diff**

Run:

~~~
git diff --check
git status --short
git diff --stat main...HEAD
~~~

Expected: no whitespace errors, only the planned files changed, and the diff contains no renderer-specific dependency or unrelated refactor.

- [x] **Step 5: Commit the Phase 1 release note and push**

~~~
git add README.md tests/pressure-scenarios.md
git commit -m "test: cover v2 sequence-aware directing"
git push origin feat/v2-director-contract
~~~

### Task 6: Phase 2 — Add a semantic Shot Language registry

**Files:**

- Create: references/shot-language.md
- Create: templates/shot-language.yaml
- Create: tests/test_shot_language_policy.py
- Modify: SKILL.md
- Modify: README.md
- Modify: references/director-contract.md
- Modify: references/execution-handoff.md
- Modify: references/output-contracts.md
- Modify: references/workflow.md
- Modify: templates/storyboard.jsonl
- Modify: tests/pressure-scenarios.md

**Interfaces:**

- Consumes: visual_action, shot states, and motion budget from the Phase 1 contract.
- Produces: a small, semantic registry that maps actions to candidate language families such as report_reveal, sequential_card_build, aligned_comparison, causal_flow, data_hero, risk_matrix, pause_hold, and clean_cut.

- [x] **Step 1: Write policy tests for action-to-language mapping**

Assert that each required visual_action has at least one language family, each family documents use_when, avoid_when, entry, development, peak, hold, and exit, and no family is defined as a visual effect count or fixed layout quota.

- [x] **Step 2: Add the registry and reference guidance**

Use YAML-like Markdown-safe data with stable names and concise fields; keep the semantic action as the selection input and make the selected language explainable in the shot record.

- [ ] **Step 3: Verify and commit Phase 2**

Run the new policy test and the complete Phase 1 suite, inspect git diff --check, commit with feat: add semantic shot language registry, and push the same branch.

### Task 7: Phase 3 — Add renderer-agnostic Shot Recipes

**Files:**

- Create: references/shot-recipes.md
- Create: templates/shot-recipe.json
- Create: tests/test_shot_recipe_policy.py
- Modify: references/shot-language.md
- Modify: references/execution-handoff.md

**Interfaces:**

- Consumes: one Phase 1 shot contract plus a selected Phase 2 language family.
- Produces: a recipe shape with fit, avoid, entry, development, information_peak, reading_hold, exit, motion_personality, motion_budget, duration_guidance, pitfalls, and reference_implementation.

- [ ] **Step 1: Test recipe completeness before authoring recipes**

Create policy tests that reject a recipe missing lifecycle phases or a reference implementation and accept recipes that leave renderer choice open.

- [ ] **Step 2: Author the first useful recipe set**

Document only evidence verification, sequential accumulation, aligned comparison, causal explanation, data hero, conclusion/pause, and clean hard-cut recipes. Do not copy a large card inventory or add 3D/particle effects as a diversity requirement.

- [ ] **Step 3: Verify and commit Phase 3**

Run all policy and contract tests, review the recipes for semantic fit, commit with feat: add renderer-agnostic shot recipes, and push.

### Task 8: Phase 4 — Add sequence and full-film review checks

**Files:**

- Create: references/sequence-review.md
- Create: scripts/review_sequence.py
- Create: tests/test_sequence_review.py
- Modify: references/output-contracts.md
- Modify: references/render-reliability.md
- Modify: references/execution-handoff.md

**Interfaces:**

- Consumes: an ordered storyboard.jsonl, optional director_summary.md, and optional rendered-review metadata.
- Produces: deterministic structural checks for Beat progression, repeated layout/action patterns, missing reading holds after dense information, unresolved handoffs, unbalanced motion budgets, and energy-curve annotations; it reports warnings separately from blocking contract errors.

- [ ] **Step 1: Write failing sequence-review tests**

Cover three consecutive shots using the same layout, a complex shot followed by no hold, a missing handoff, a clean contrast cut with reason, and a valid sequence with a simpler release shot.

- [ ] **Step 2: Implement warnings without turning taste into hard rules**

Return structured findings with severity, shot_ids, rule, and message. Treat repeated layout, energy imbalance, and effect monotony as review warnings; treat malformed contracts and unsupported references as errors.

- [ ] **Step 3: Verify and commit Phase 4**

Run structural tests plus a fixture sequence, review the warning output, commit with feat: add sequence review checks, and push.

### Task 9: Phase 5 — Connect asset retrieval, reuse, and automation safely

**Files:**

- Create: references/asset-retrieval.md
- Create: scripts/plan_asset_reuse.py
- Create: tests/test_asset_reuse_planning.py
- Modify: references/asset-library.md
- Modify: references/workflow.md
- Modify: references/output-contracts.md

**Interfaces:**

- Consumes: asset_id, shot_id, visual_action, shot_language, catalog metadata, usage history, provenance status, and selection status.
- Produces: ranked candidate cards and a reuse plan that records semantic fit, prohibited interpretation, publication gate, prior usage, treatment variation, and genuine gaps without treating unique footage duration as a production blocker.

- [ ] **Step 1: Write failing reuse-planning tests**

Assert that an honest related context asset can rank as a fallback, an unverified asset remains behind a publication gate, a low-resolution authentic report is retained with a warning, immediate identical reuse is flagged, and varied reuse is allowed.

- [ ] **Step 2: Implement the planner against the existing catalog contracts**

Keep raw files immutable, keep metadata sidecars durable, use stable asset_id joins, and write usage/repetition notes without copying the shared library into project folders.

- [ ] **Step 3: Verify and commit Phase 5**

Run all tests, inspect catalog path handling, commit with feat: add semantic asset reuse planning, and push.

### Task 10: Final branch verification and GitHub handoff

**Files:**

- No additional production files; inspect all planned changes.

**Interfaces:**

- Consumes: the complete V2 branch and its full regression suite.
- Produces: verified branch state and a GitHub handoff for review.

- [ ] **Step 1: Run the complete project test command**

Run the repository's full available suite:

~~~
for test in tests/test_init_project.py tests/test_reuse_policy.py \\
  tests/test_render_reliability_policy.py tests/test_asset_acceptance_policy.py \\
  tests/test_asset_intake.py tests/test_storyboard_contract.py \\
  tests/test_v2_policy.py tests/test_shot_language_policy.py \\
  tests/test_shot_recipe_policy.py tests/test_sequence_review.py \\
  tests/test_asset_reuse_planning.py tests/validate_skill.py; do
  python3 "$test" || exit 1
done
~~~

Expected: every command exits 0 with no traceback.

- [ ] **Step 2: Run repository hygiene checks**

~~~
git diff --check
git status --short --branch
git log --oneline --decorate -12
~~~

Expected: the branch is clean after the final commit and all commits are on feat/v2-director-contract.

- [ ] **Step 3: Push and report the GitHub branch**

~~~
git push -u origin feat/v2-director-contract
~~~

Report the branch name, commit list, verification commands and results, and any limitation such as the inability to create a PR automatically. Do not claim completion until the fresh verification output and Git status support it.
