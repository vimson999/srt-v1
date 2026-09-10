# Semantic Shot Language

Shot Language is the reusable visual grammar between a shot's semantic action
and a renderer-specific implementation. It does not add another editorial
level:

```text
Visual Beat → Shot → Shot States → Visual Action → Shot Language → Shot Recipe → Renderer
```

Use `templates/shot-language.yaml` as the canonical registry. The file is
JSON-compatible YAML so it can be parsed with standard JSON tooling while
remaining easy to copy into YAML-aware systems.

## What a family represents

A family describes how one semantic information operation progresses through
entry, development, peak, hold, and exit. It also records when the family fits,
when it should be avoided, its motion personality, and its preferred handoff
behavior.

It is not:

- an animation effect name;
- a mandatory layout or card template;
- a quota for visual variety;
- a replacement for `visual_mode`, evidence verification, or timed attention;
- a renderer component or implementation recipe.

`visual_action` states what the shot must do. `shot_language.family` states the
reusable visual grammar chosen to do it. A later Shot Recipe makes that choice
executable for a concrete shot, and a renderer adapter implements the recipe.
Once the family is selected, read `references/shot-recipes.md` and retrieve a
compatible recipe from `templates/shot-recipe.json`; never select a recipe
first and reverse-engineer the shot's action or state to fit it.

## Selection workflow

1. Start from the shot's single primary `visual_action`.
2. Retrieve registry families whose `visual_actions` include that action.
3. Compare each candidate's `use_when` and `avoid_when` with the shot's
   information states, evidence burden, and handoff.
4. Choose the family whose lifecycle best reaches the declared
   `information_peak` while respecting `reading_hold` and `motion_budget`.
5. Record one selected family and a shot-specific reason. Do not write
   “because it looks good”; name the information or attention problem it
   solves.

The first-pass candidate map is intentionally small:

| Visual action | Candidate families |
| --- | --- |
| `establish` | `context_establish` |
| `focus` | `attention_focus`, `data_hero` |
| `compare` | `aligned_comparison`, `risk_matrix` |
| `accumulate` | `sequential_card_build` |
| `causal` | `causal_flow` |
| `verify` | `report_reveal` |
| `turn` | `clean_cut` |
| `conclude` | `data_hero`, `conclusion_resolve` |
| `pause` | `pause_hold` |

This map is a retrieval aid, not automatic final selection. For example,
`data_hero` fits a verified metric that can carry the conclusion by itself;
`conclusion_resolve` fits several already-established elements converging into
one judgment. `risk_matrix` is valid only when its dimensions are meaningful
and supported, while `aligned_comparison` needs a truthful shared scale.

## Shot record enrichment

Phase 1 storyboard records remain structurally valid before Shot Language is
selected. Once a shot advances through the V2 Shot Language stage, add:

```json
{
  "shot_language": {
    "family": "report_reveal",
    "selection_reason": "The source identity and target-price region must be verified before the comparison"
  }
}
```

The family must exist in the registry and include the shot's `visual_action`.
The reason must be specific to the shot's information state, peak, or handoff.
A production-bound shot should have one selected family; alternate candidates
belong in planning notes, not in the final selection field.

## Continuity and motion

Family guidance does not override the Phase 1 contracts:

- `motion_budget` still limits attention competition to one primary motion
  responsibility and, by default, at most one supporting responsibility.
- `reading_hold` still protects legibility based on information density rather
  than a universal duration.
- `exit_anchor`, `entry_anchor`, and `continuity_axis` still define the actual
  shot-to-shot handoff.
- `clean_cut` is valid only with `continuity_axis=none` and a meaningful
  `contrast_reason` for an interior transition.

The registry's handoff fields are preferences used during selection. The shot
record remains the source of truth for the specific transition.

## Extending the registry

Add a family only when an existing family cannot express a recurring semantic
operation without distorting its fit or lifecycle. Keep IDs stable and
renderer-neutral. Every new family must:

- map to at least one existing `visual_action`;
- include non-empty `use_when` and `avoid_when` guidance;
- define entry, development, peak, hold, and exit;
- describe motion personality and handoff preferences;
- avoid fixed effect counts, fixed layout quotas, and mandatory spectacle.

Run `python3 tests/test_shot_language_policy.py` after editing the registry.
