# Human-in-the-loop policy

Policy version: 1

The user is the product owner, not the production QA loop. Human confirmation must not be used as a substitute for self-review, regression gates, or visual-quality judgment.

## Default mode: autonomous production

Once the user has clearly requested work such as “制作”, “继续”, “按这个标准继续”, or “做完”, treat that as standing authorization for the non-destructive production work inside the requested scope.

Within that scope, continue autonomously through:

- source/SRT parsing and narrative analysis;
- narrative map, chapter arcs, visual beats and storyboard;
- asset audit, catalog lookup, safe reuse planning and programmatic visuals;
- implementation of shots and internal states;
- representative render, visual self-review and regression repair;
- expansion probe and full-plan analogous-shot scan;
- technical validation, render preflight and review renders;
- re-rendering the smallest affected range after a failed self-check.

Do not stop merely to ask whether the user “confirms” an internal artifact. Progress updates may be informative, but they should not become approval rituals.

## Quality is owned by the production system

A user saying “可以”, “就这样”, “继续”, or not objecting is not evidence that a visual defect is acceptable. Likewise, a user approval does not turn a technical pass into a visual pass.

When a self-check fails:

1. classify the failure;
2. repair it autonomously when the requested scope and available evidence are sufficient;
3. rerun the smallest useful regression check;
4. if the same P0/P1 class appears again, stop broad production and repair the responsible mechanism before continuing.

Never ask the user to choose whether to accept a known regression merely because fixing it is inconvenient or the film is long. Never ask the user to lower an already established standard so production can finish faster.

## Stop and ask only when human input is genuinely required

A user-facing stop is justified only for one of these conditions:

1. **Essential missing input** — a required user-owned source, fact, file, credential, or permission is missing and there is no honest fallback.
2. **Material creative fork** — two or more materially different directions remain equally valid, the brief / DESIGN / evidence does not resolve the choice, and choosing one would meaningfully change the downstream work.
3. **Consequential external action** — publication, upload to a public destination, paid purchase/license, destructive deletion/overwrite of user source files, or another irreversible/external action requires explicit authorization.
4. **Explicit review checkpoint** — the user specifically asked to see/approve a sample before further work (for example: “先给我看样片再继续”).
5. **Scope expansion** — the next action is outside what the user originally requested, rather than merely a normal implementation step inside that request.

If none of these conditions applies, continue.

## What is not a human milestone

Do not stop for routine approval of:

- narrative maps or chapter boundaries;
- visual beats, Shot Language or Shot Recipe selection;
- storyboard completion;
- asset matching when an honest in-scope choice exists;
- internal state timing or attention-cue generation;
- plan-score or technical-test results;
- a representative render that passes the defined self-review gates;
- an expansion probe that passes the production gate;
- routine repair after a regression test fails;
- the choice between “keep quality” and “use a cheaper generic template”.

These are production responsibilities, not user decisions.

## Standing authorization and rendering

Interpret the requested deliverable, not isolated verbs:

- If the user asked only for analysis, storyboard, asset plan, or a preview, do not silently expand that into a final render.
- If the user asked to produce/finish the video or explicitly requested an exported video as the deliverable, ordinary non-destructive preview and final rendering are part of that scope and do not require repeated confirmation at each phase.
- A previous authorization does not cover public publishing, paid licensing, destructive source changes, or a materially different deliverable.

## Review milestones are evidence milestones

The production flow should normally be:

`request -> autonomous plan -> representative render -> self-review/fix -> expansion probe -> self-review/fix -> full implementation -> review/export within scope`

Human review is inserted only when one of the genuine stop conditions above is present. The point of a milestone is to obtain information only the human can provide, not to transfer quality responsibility to the human.

## Communication rule

When continuing autonomously, report important findings and state changes without turning every update into a question. If a human stop is necessary, ask one focused question that identifies exactly what decision or missing input blocks further work.
