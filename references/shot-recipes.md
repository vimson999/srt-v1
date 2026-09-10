# Renderer-Neutral Shot Recipes

A Shot Recipe turns one selected Shot Language family into an executable state
plan without choosing a renderer. It sits downstream of the Phase 1 shot
contract and Phase 2 language selection:

```text
Shot States → Visual Action → Shot Language → Shot Recipe → Renderer Adapter
```

Use `templates/shot-recipe.json` as the canonical first recipe set. A recipe
does not replace the shot record. It explains how an adapter should realize the
record's entry, development, information peak, reading hold, and exit.

## Selection

1. Complete the shot's information state, `visual_action`, `motion_budget`, and
   handoff.
2. Select and explain one compatible `shot_language.family`.
3. Retrieve recipes whose `shot_language` equals that family and whose
   `visual_actions` includes the shot's action.
4. Check `fit` and `avoid` against the actual evidence, data, state, and
   transition burden.
5. Choose one recipe, then let the renderer adapter map its state timeline to
   concrete primitives.

When no recipe fits, keep the shot contract intact and document the recipe gap.
Do not force the nearest recipe or silently change the semantic action.

Record a successful selection in the shot:

```json
{
  "shot_recipe": {
    "id": "evidence_verification",
    "selection_reason": "The verified report region must become the next comparison anchor"
  },
  "recipe_gap": null
}
```

If no canonical recipe fits, set `shot_recipe` to `null` and provide a
non-empty `recipe_gap` describing the missing reusable pattern. A gap is an
explicit handoff state, not an instruction for the renderer to improvise.

## Recipe contract

Each recipe defines:

- `id`, `shot_language`, and compatible `visual_actions`;
- `fit` and `avoid` conditions;
- `entry`, `development`, `information_peak`, `reading_hold`, and `exit`;
- `motion_personality` and a semantic `motion_budget`;
- `duration_guidance` derived from information and narration rather than fixed
  seconds;
- `pitfalls` that would make the implementation misleading or unreadable;
- a `reference_implementation` expressed as an ordered state timeline;
- an `adapter_contract` that protects the source shot contract;
- `renderer_neutral=true`.

The reference implementation is deliberately declarative. It specifies what
each phase consumes and must communicate, not component names, easing APIs, or
software-specific scene graphs.

## First recipe set

| Recipe | Shot Language | Primary use |
| --- | --- | --- |
| `evidence_verification` | `report_reveal` | Attribute an authentic source region before synthesis |
| `sequential_accumulation` | `sequential_card_build` | Build ordered items into consensus or cumulative weight |
| `aligned_value_comparison` | `aligned_comparison` | Compare honest values on one shared scale |
| `causal_explanation` | `causal_flow` | Reveal a supported mechanism in causal order |
| `verified_data_hero` | `data_hero` | Resolve one sourced metric with label and qualification |
| `evidence_to_conclusion` | `conclusion_resolve` | Converge established evidence into a judgment |
| `protected_pause` | `pause_hold` | Protect reading or cognitive release through restraint |
| `clean_contrast_cut` | `clean_cut` | Express an explained turn without decorative interpolation |

This set is intentionally narrow. `context_establish`, `attention_focus`, and
`risk_matrix` remain valid language families even though they do not yet have
a canonical recipe. That is a visible coverage gap, not permission to use an
unrelated recipe.

## Duration and motion

`duration_guidance.fixed_seconds` remains `false`. Derive timing from the
shot's narration span, number of meaningful development states, label or
evidence density, and protected reading requirement. A recipe may guide
deceleration or stillness, but it must not require animation in every phase.

The recipe's semantic motion budget refines the shot's declared budget; it
cannot expand it. If a recipe appears to need several foreground arguments,
simplify the implementation or choose a different recipe instead of adding
untracked motion.

## Renderer adapter boundary

An adapter may choose layout primitives, typography, interpolation, easing,
camera behavior, and technical composition structure. It must preserve:

- source-backed values and evidence references;
- state order and the declared information peak;
- Timed Attention Cues and reading holds;
- primary/supporting/background motion responsibilities;
- entry and exit anchors, continuity axis, and contrast reason;
- subtitles, safe areas, and render-reliability requirements.

Reference implementations are examples of contract realization, not output
claims. Render Review still judges real frames and Render Reliability still
judges the exported media.

## Extending recipes

Add a recipe only for a recurring implementation pattern with a stable
semantic fit. Keep its language family and actions compatible with
`templates/shot-language.yaml`. Do not add a recipe merely to increase effect
count, force periodic layout changes, or introduce 3D, particles, and spectacle
without an information reason.

Run `python3 tests/test_shot_recipe_policy.py` after changing the recipe set.
