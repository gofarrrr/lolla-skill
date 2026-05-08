# PR60 Targeted v22 Guard Enrichment Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr60-targeted-v22-guard-enrichment`

Status: dormant reviewed substrate only; no runtime pickup

## Purpose

PR60 continues the post-v18 enrichment pass after v21. Unlike PR57, PR58, and PR59, this round does not add positive affordances. It adds absence records where the source explicitly warns against a misuse that could make a future packet look more authoritative while becoming less truthful.

This PR treats absence records as first-class context. The question is:

> What should the future receiver be blocked from overclaiming?

## Artifact

- Previous artifact: `model_affordances_v21`
- New artifact: `model_affordances_v22`
- Path: `data/compiled/model_affordances/affordances_v22.json`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `268`
- Absence records: `434`
- Schema validation failures: `0`
- Source quote rejections: `0`

Delta from v21:

- `+0` affordances
- `+5` absence records
- `+0` records
- no live runtime import

## Added Absence Rails

### `chain-of-thought`: `structured-reasoning-without-implementation-path`

Added because the source says Chain of Thought can identify what should be done while neglecting how to translate that answer into action in a living system. The current absences already blocked transcript-as-truth and transcript-without-verification. This new rail is narrower: do not treat clean structured reasoning as implementation readiness.

Source basis:

- `often neglects the complexity of figuring out *how* to translate that answer into action in a living system`
- `Plan for Action, Not Just Analysis`
- `If we acted on this plan today, what holes would be exposed?`

Why absence, not positive affordance:

- The existing CoT affordance already requires verification and an action path.
- This is an overclaim blocker for analysis-as-implementation, not a new reasoning move.

### `game-theory-payoffs`: `commitment-threat-or-promise-without-credibility-device`

Added because the source says commitments, threats, and promises can change the game only when they are credible. The current positive card already maps players, moves, information, and payoff branches. The missing guard is narrower: do not treat a stated threat, promise, or commitment as leverage unless there is a credibility device.

Source basis:

- `Actions intended to change the game (commitments, threats, promises) must be credible.`
- `What specific devices (e.g., contracts, sunk costs, reputation) make our stated threat or promise absolutely credible to our opponent?`

Why absence, not positive affordance:

- Credibility is a blocker on the existing payoff-map treatment, not a separate reasoning move.
- The receiver should defer or weaken the game-theory card if a commitment/threat/promise lacks a credible device.

### `baseline-establishment`: `goal-baseline-with-solution-imported`

Added because the source says goal setting must be separated from solution, diagnosis, and implementation thinking. The existing baseline card already handles starting condition, success criteria, comparison facts, stale baselines, and convenient metrics. The missing guard is that a baseline can be corrupted by importing the execution plan into the goal itself.

Source basis:

- `Goal setting must be done without thinking about solutions`
- `Am I defining the desired outcome, or am I already thinking about the execution steps required to achieve it?`

Why absence, not positive affordance:

- This is not a new baseline transaction.
- It blocks a polluted baseline before the positive baseline gate is trusted.

### `theory-of-constraints`: `bottleneck-claim-without-measurement-loop`

Added because the source repeatedly says constraint language must name the governing metric, current cap, and movement evidence. The existing positive affordance already requires measured constraint-first intervention. This absence makes the overclaim explicit for future packet display.

Source basis:

- `without naming the governing metric, the current cap, and the evidence that the cap actually moved after intervention`
- `ToC language is used, but no current binding constraint is quantified`

Why absence, not positive affordance:

- This blocks bottleneck theater.
- It does not add another ToC move; it prevents the existing move from firing on slogans.

### `theory-of-constraints`: `technical-bottleneck-without-ownership-route`

Added because the source says stakeholder, ownership, authority, incentive, and decision-right constraints can be stronger than the technical bottleneck. A future packet should not treat a technical cap as resolved if the human route to approval, coordination, or completion is missing.

Source basis:

- `Works when stakeholder or decision-right constraints are the real bottleneck`
- `Execution fails because ownership, authority, and incentive constraints are stronger than the technical one`
- `Assign owners, checkpoints, and decision rights for each bottleneck-relief action before execution starts.`

Why absence, not positive affordance:

- The current ToC record already includes stakeholder and decision-right constraints as evidence types.
- The new rail prevents overclaiming a technical fix when the ownership route is absent.

## Runtime Safety

No runtime, prompt, packet, lane, Observatory, or product path was changed.

The v22 artifact remains dormant and review-only. Live paths must still pass an explicit artifact path in any future experiment; no latest-file behavior is introduced here.

## Validation

Target validation:

```bash
python3 -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('engine').resolve())); from system_b.model_affordance_validation import validate_model_affordance_file; files=[Path('data/model_affordances/batch_5/game-theory-payoffs.json'), Path('data/model_affordances/batch_8/baseline-establishment.json'), Path('data/model_affordances/batch_17/chain-of-thought.json'), Path('data/model_affordances/pilot/theory-of-constraints.json')]; [validate_model_affordance_file(f, source_roots=(Path('data/model_sources'),)) for f in files]; print('validation_ok', len(files))"
```

Compile:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v22.json --quality-report-filename quality_report_v22.md --artifact-id model_affordances_v22 --report-title "Model Affordance Quality Report v22"
```

Expected focused test set:

```bash
pytest tests/test_pr60_v22_guard_enrichment.py tests/test_pr59_v21_targeted_enrichment.py tests/test_model_affordance_pilot.py tests/test_model_affordance_compiler.py tests/test_pr32_batch5_records.py tests/test_pr39_batch8_records.py tests/test_pr54_batch17_records.py
```

## Bottom Line

PR60 strengthens the corpus by adding blocking knowledge rather than more positive model language.

The useful change is small but important: future packets should now be more likely to notice when stepwise reasoning lacks implementation path, when game-theory leverage lacks credibility, when baselines smuggle in solutions, and when constraint language lacks measurement or ownership. That is exactly the kind of less-wrong substrate we want before live pickup.
