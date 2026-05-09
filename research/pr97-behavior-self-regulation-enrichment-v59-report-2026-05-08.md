# PR97 Behavior Self-Regulation Enrichment v59 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr97-behavior-self-regulation-v59`

## Scope

PR97 continues the dormant reviewed-affordance enrichment track. It does not
wire affordances into `/lolla`, prompts, lane adapters, packet rendering, or
runtime pickup.

The audit target was a behavior and self-regulation ring:

- `goal-setting`
- `input-vs-output-goals`
- `persistence-grit`
- `habit-formation`
- `self-control`
- `flow`

The operating question stayed the PR55 transaction-identity question:

> Would separating this material change downstream use, reject, defer, merge,
> evidence-gate, treatment, misuse-guard, or final-answer behavior?

Two read-only subagent audits were used as pressure checks. Final adjudication
was made locally after reading the full canonical Markdown and current records.

## Source-Read Verdict

Positive affordance split accepted:

- `self-control.deliberate-pause-before-impulse-action`

Absence rails added:

- `goal-setting.premature-solutioning-during-goal-selection`
- `goal-setting.abstract-accurate-goal-without-decision-guidance`
- `input-vs-output-goals.accurate-output-without-actionable-input`
- `persistence-grit.grind-without-recovery-or-load-management`
- `persistence-grit.exhaustive-effort-without-leverage`
- `habit-formation.cue-craving-diagnosis-as-standalone-card`
- `habit-formation.ai-persona-consistency-as-habit-affordance`
- `habit-formation.professional-consistency-as-habit-split`
- `self-control.self-control-as-infinite-resource`
- `self-control.eisenhower-matrix-as-self-control-split`
- `self-control.ai-tendency-encoding-as-self-control-affordance`
- `self-control.self-control-as-more-deliberation`
- `flow.felt-focus-as-problem-fit`
- `flow.flow-without-feedback-or-coordination`
- `flow.job-redesign-for-flow-as-standalone-affordance`

No positive splits were accepted for `goal-setting`,
`input-vs-output-goals`, `persistence-grit`, `habit-formation`, or `flow`.

## Accepted Split

### `self-control.deliberate-pause-before-impulse-action`

The existing Self Control affordance owns chronic follow-through system design:
when the right move is known but not executed under stress, temptation, or
distraction, redesign conditions around the behavior.

The source also supports a distinct acute transaction: when a person or team is
about to react under pressure, insert a deliberate pause, ask what is happening,
decide whether more time is needed, and disclose skipped checks if action must
still be rushed.

Why this passes:

- Activation is immediate impulse, urgency, hostility, temptation, or hot
  cognition, not repeated follow-through failure.
- Evidence requires the imminent action, pressure, skipped-step risk, and
  acting-now versus delaying threshold.
- Treatment is pause, name pressure, act or delay, and disclose skipped checks.
- The receiver can decide to delay, act with a threshold, or proceed with
  monitoring; this is different from redesigning environment, habit, rest, or
  prompts.

This split is intentionally narrow. It blocks rushed advice without converting
ordinary execution into endless deliberation.

## Rejected Positive Splits

### `goal-setting` expansion

Rejected as positive split.

SMART goals, goal hierarchy, hypothesis-driven goal setting, interrogative
self-talk, anti-goals, and process-focus material are useful, but they do not
change the current card's receiver transaction. The current card already owns
explicit outcome, larger purpose, trade-offs, ownership, thresholds, cadence,
and stale-goal review.

PR97 added two rails:

- do not call it goal-setting if the answer jumps into solutioning before the
  outcome is clear;
- do not treat abstractly accurate goals as useful when they do not guide
  daily or frontline decisions.

### `input-vs-output-goals` expansion

Rejected as positive split.

SMART bridge, end-product orientation, habit/self-control input design,
cognitive-load/scaffolding examples, sales outcome framing, and Pareto/vital-few
language are better understood as owner-boundary material. The current card
already owns the end-state versus controllable-action distinction.

PR97 added one rail:

- an accurate output statement is not enough if it does not identify actionable
  inputs.

### `persistence-grit` expansion

Rejected as positive split.

Mastery loops, resilience, hypothesis-driven problem solving, deep work,
walk-away rules, and "do not boil the ocean" material are real source elements,
but they do not require a new Grit card. The current card already owns
sustained effort with practice loops, progress evidence, recovery routines, and
stop or pivot criteria.

PR97 added two rails:

- do not turn grit into nonstop grind without recovery or load management;
- do not promote exhaustive, low-leverage effort when the source calls for
  enough facts, action thresholds, and thoughtful action.

### `habit-formation` expansion

Rejected as positive split.

Cue/craving diagnosis, response simplification, professional consistency, AI
persona consistency, and low-level goal alignment are either substeps of the
existing habit loop or owned by adjacent records.

PR97 also corrected one boundary:

- inert strategy is a reason to design repeated behavior, not a broad
  `do_not_use_when` condition for habit formation.

The `strategy-document-as-execution` absence remains first-class: a plan
artifact is not execution.

### `flow` expansion

Rejected as positive split.

Immediate feedback, challenge recalibration, deep-work cycle, group flow,
motivation/fulfillment, zone-of-genius language, and job redesign are all
captured as evidence, treatment detail, or absence material inside the current
calibrated-immersion card.

PR97 added rails against:

- treating felt focus as problem-fit;
- using flow without feedback, stakeholder coordination, or environmental
  signals;
- promoting job redesign for flow as a standalone affordance from a thin source
  example.

## Quality Interpretation

PR97 continues the same middle path as PR96:

- accept one positive split where pooled material would change receiver action;
- reject rich examples that would inflate the substrate without new transaction
  identity;
- promote anti-overclaim boundaries as absence rails.

The important correction is that behavior/self-regulation cards can sound like
generic productivity advice if they are not evidence-gated. v59 keeps them
operational: outcome, input, loop, pause, recovery, feedback, and stop-rule
evidence must be visible.

## v59 Compile Result

Artifact: `model_affordances_v59`

- Status: `draft_review_only`
- Records: `222`
- Affordances: `306`
- Absence records: `679`
- Schema-validation failures: `0`
- Source-quote rejections: `0`

Delta from v58:

- Affordances: `+1`
- Absence records: `+15`
- Runtime references: none

## Runtime Boundary

The v59 artifact remains dormant. PR97 does not:

- import v59 from live runtime paths;
- change packet producer defaults;
- add lane-to-nomination logic;
- change prompts;
- change `/lolla`;
- promote reviewed cards into automatic reasoning instructions.

The runtime question remains later work:

> Can reviewed cards survive pickup, compression, display, and LLM use without
> losing their epistemic shape?

PR97 improves the reviewed substrate that a future answer to that question
would use. It does not answer the runtime pickup question by itself.

## Verification Commands

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v59.json --quality-report-filename quality_report_v59.md --artifact-id model_affordances_v59 --report-title "Model Affordance Quality Report v59"
PYTHONPATH=. pytest tests/test_pr97_v59_behavior_self_regulation_enrichment.py tests/test_pr96_v58_communication_adoption_enrichment.py tests/test_model_affordance_compiler.py
rg -n "affordances_v59|model_affordances_v59" engine scripts -g '*.py'
git diff --check
```
