# SRT Regression Fixtures

These fixtures are short, rebased excerpts from real long-form projects. They are selected for director-regression testing rather than as general demo clips.

Rules:
- Preserve source wording. Do not silently fact-correct or rewrite the fixture.
- Fixture time starts at `00:00:00`.
- Exercise the full path: `SRT -> narrative map -> visual beats -> shots -> production gate`.
- A successful parse or render is not a visual-regression pass.
- Do not treat any fixture layout as a universal style.

## Fixtures

| Fixture | Duration | Source window | Why it is useful | Primary regression risks |
|---|---:|---|---|---|
| `honghao-0914-argument-turn.srt` | 01:29.300 | 00:00:42.166–00:02:11.466 | Multiple named AI actors and public-statement evidence followed by a clear argumentative turn from the surface safety explanation to a shared constraint. | planning-text leak; example-only fix; state-without-visual-change; template collapse |
| `baiyi-macro-to-ai.srt` | 01:11.533 | 00:00:57.133–00:02:08.666 | Macro evidence moves through rate expectations, oil, valuation pressure, A-share turnover and barbell structure, then resolves into an asset-selection principle and hands off to AI. | template collapse; background-as-decoration; weak beat transition |
| `catl-contrarian-share.srt` | 01:26.833 | 00:00:31.133–00:01:57.966 | Negative market narrative is contradicted by three investment banks and three target prices, then tested against market-share data. | generic report cards; attention-cue failure; state-only card reveals; sample/full degradation |
| `xiaomi-demand-vs-pricing.srt` | 01:28.333 | 00:00:20.600–00:01:48.933 | The same event receives a different interpretation; narration branches into two competing explanations, then introduces price cuts, launch incentives and order evidence. | template collapse; evidence/background separation; binary comparison reduced to text panels; motion without information progress |

## Minimum regression checks

For each fixture confirm:
1. No planning or internal-production language appears as audience-facing copy.
2. The argument is represented by actual visual relationships, not only title + narration paragraph + small image.
3. Different information responsibilities do not collapse into one repeated card shell.
4. Named institutions, actors and exact numbers receive timed attention when spoken.
5. Entry -> development -> peak -> hold -> exit creates real information progress.
6. Representative render and expansion probe use the canonical production path and active content revision.
7. Technical success is recorded separately from visual review.

These SRT fixtures complement JSON/control-plane regression fixtures for path divergence, repeated-patch escalation, render preflight and review-state integrity.
