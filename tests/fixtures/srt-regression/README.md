# SRT Regression Case Library

This directory is a growing regression-case library built from short, rebased excerpts of real long-form projects. The goal is not to preserve entire historical projects. Each case preserves the smallest realistic SRT structure that can expose an expensive directing or production failure before a full-length film is attempted.

`cases.json` is the machine-readable registry. The `.srt` files are the actual source fixtures.

## Library rules

- Preserve source wording. Do not silently fact-correct or rewrite a fixture.
- Rebase fixture time to `00:00:00` so the case is cheap and repeatable.
- Exercise the production path, not only parsing: `SRT -> narrative map -> visual beats -> shots -> representative render -> self-review -> production gate`.
- A successful parse, schema validation, or render is not a visual-regression pass.
- Do not treat a successful case's layout, colors, component count, or shot count as a universal style.
- Record the failure class that justified each case so future Skill changes can select the relevant subset.
- When a new real project exposes a systemic failure that existing cases do not exercise well, add the smallest representative case here instead of waiting for another full-length failure.

## Current cases

| Fixture | Duration | Source window | Why it is useful | Primary regression risks |
|---|---:|---|---|---|
| `honghao-0914-argument-turn.srt` | 01:29.300 | 00:00:42.166–00:02:11.466 | Multiple named AI actors and public-statement evidence followed by a clear argumentative turn from the surface safety explanation to a shared constraint. | planning-text leak; example-only fix; state-without-visual-change; template collapse; repeated patch loop |
| `baiyi-macro-to-ai.srt` | 01:11.533 | 00:00:57.133–00:02:08.666 | Macro evidence moves through rate expectations, oil, valuation pressure, A-share turnover and barbell structure, then resolves into an asset-selection principle and hands off to AI. | template collapse; background-as-decoration; weak beat transition |
| `catl-contrarian-share.srt` | 01:26.833 | 00:00:31.133–00:01:57.966 | Negative market narrative is contradicted by three investment banks and three target prices, then tested against market-share data. | generic report cards; attention-cue failure; state-only card reveals; sample/full degradation |
| `xiaomi-demand-vs-pricing.srt` | 01:28.333 | 00:00:20.600–00:01:48.933 | The same event receives a different interpretation; narration branches into two competing explanations, then introduces price cuts, launch incentives and order evidence. | template collapse; evidence/background separation; binary comparison reduced to text panels; motion without information progress |

## Minimum regression checks

For each applicable fixture confirm:

1. No planning or internal-production language appears as audience-facing copy.
2. The argument is represented by actual visual relationships, not only title + narration paragraph + small image.
3. Different information responsibilities do not collapse into one repeated card shell.
4. Named institutions, actors and exact numbers receive timed attention when spoken.
5. Entry -> development -> peak -> hold -> exit creates real information progress.
6. Representative render and expansion probe use the canonical production path and active content revision.
7. Technical success is recorded separately from visual review.
8. A failed self-review is repaired by the production system; it is not converted into a user question asking whether a known regression is acceptable.
9. The second occurrence of the same P0/P1 class escalates to a mechanism-level repair instead of another broad revision.

## Test tiers

Use `cases.json` to select the smallest useful regression set:

- **Smoke:** one case that directly overlaps the changed failure class.
- **Director change:** all cases whose structure/failure classes overlap the changed directing behavior.
- **Production-gate change:** all SRT cases plus control-plane regression tests.
- **Release candidate:** the complete case library. Any claim about visual quality still requires rendered review rather than JSON-only success.

## Adding a case

When a real production exposes a new systemic failure:

1. identify the failure class and the smallest continuous SRT window that can reproduce it;
2. keep enough context to contain a real claim/evidence/turn/attention problem rather than an artificial one-line fixture;
3. rebase time to zero without rewriting the wording;
4. add the `.srt` and a `cases.json` entry with structure tags, failure classes, and concrete `must_demonstrate` expectations;
5. run the relevant existing cases as well, because a fix for one failure must not reintroduce another.

These SRT cases complement JSON/control-plane regression fixtures for path divergence, repeated-patch escalation, render preflight and review-state integrity.
