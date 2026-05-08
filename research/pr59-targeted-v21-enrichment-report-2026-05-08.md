# PR59 Targeted v21 Enrichment Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr59-targeted-v21-enrichment`

Status: dormant reviewed substrate only; no runtime pickup

## Purpose

PR59 continues the post-v18 source-adequacy work after v19 and v20. The goal is not to maximize affordance count. The goal is to preserve source-backed cognition that changes downstream receiver action while rejecting source-real but duplicate material that belongs to a better existing owner.

This PR uses the PR56 split rule:

- a new affordance must change activation conditions;
- it must require different case evidence;
- it must have its own do-not-use boundaries;
- it must change treatment requirements or misuse guards;
- it must let a future receiver make a cleaner use/reject/defer/merge decision;
- it must not become a broad duplicate under a less precise model name.

## Artifact

- Previous artifact: `model_affordances_v20`
- New artifact: `model_affordances_v21`
- Path: `data/compiled/model_affordances/affordances_v21.json`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `268`
- Absence records: `429`
- Schema validation failures: `0`
- Source quote rejections: `0`

Delta from v20:

- `+2` affordances
- `+0` records
- `+0` absence records
- no live runtime import

## Accepted Positive Splits

### `emotional-intelligence.self-regulation-under-emotional-activation`

Accepted because the existing Emotional Intelligence card handled stakeholder emotion, trust, morale, fairness, and adoption: the technical answer may not land socially. The source also supports a separate self-regulation transaction where the user's or advisor's own emotional activation is the decision hazard.

The new card activates when stress, conflict, disappointment, hostility, shame, anger, fear, or urgency may distort action. It requires the receiver to pause the hot response, name the likely emotion, preserve the relevant standard or boundary, and choose a regulated action or message.

Why it is not duplicate:

- It is not `empathy` because the case evidence is not another person's experience; it is the actor's own activated emotional state.
- It is not `active-listening` because the main move is not diagnosis-before-advice in another person's speech.
- It is not the existing EI landing check because that card asks whether emotions outside the answer will shape adoption.

Source basis:

- `Managing feelings (Self-Management)`
- `remain calm, steady, and effective during stressful or hostile situations`
- `Emotional Hijacking and Impulsive Action`

### `metacognitive-questioning.expert-process-elicitation`

Accepted because the existing Metacognitive Questioning card handled next-question gating during ongoing work: inspect the current reasoning path and name the next discriminating question. The source also supports a distinct expert-elicitation transaction: when asking an expert, advisor, or model for an answer, ask how they judge, which skills matter, which variables matter, and how those skills should be tested.

The new card activates when a user is tempted to ask for a final answer but would gain more by learning the transferable process behind the answer. It is especially relevant for hiring, vendor selection, specialist advice, and domain-expert evaluation.

Why it is not duplicate:

- It is not generic consulting methodology because it does not structure a whole problem into TOSCA, hypotheses, and make-or-break analyses.
- It is not the existing MCQ next-question gate because the receiver action is to transform a direct answer request into process, criteria, skills, variables, and tests.
- It is not prompt engineering because the card remains about source-backed reasoning transfer, not runtime prompt behavior.

Source basis:

- `The "Ask How, Not What" Heuristic (Expert Elicitation)`
- `What skills matter and which ones can be learned on the job? Why? Where do I find the best people? How do I test these skills?`
- `This focuses the conversation on the expert's thought chain and reasoning steps`

## Rejected Or Deferred Candidates

### `critical-thinking.problem-structure-discipline`

Verdict: reject duplicate.

The source clearly contains disaggregation, hypothesis-driven work, What You Have To Believe, and MECE. But the downstream transaction is already owned more precisely by:

- `decomposition.mece-key-driver-action-map`
- `decomposition.test-cuts-and-assumptions`
- `consulting-firms-methodology.structure-uncertainty-into-testable-questions`
- `scientific-method-evidence-testing.falsifiable-hypothesis-threshold-test`

Adding the same move under `critical-thinking` would turn a source-real cluster into duplicate card vocabulary.

### `conjunction-fallacy.disjunctive-failure-risk-check`

Verdict: reject positive split for PR59; keep as route/guard concern.

The source names the disjunctive opposite error, where failure can occur if any one component fails. But the current conjunction card already has a do-not-use boundary for disjunctive risk, and the positive governance transaction is better owned by risk-oriented cards such as `risk-assessment` and `risk-vs-uncertainty`.

The useful future behavior is route/defer/merge, not a second conjunction card.

### `evolutionary-pressure.threat-filter-communication-packaging`

Verdict: reject duplicate.

The source supports communication packaging for the "croc brain": simple, clear, visual, novel, and non-threatening. But the downstream receiver action is message adoption and persuasion packaging, already owned more cleanly by `persuasion-principles` and sometimes by Emotional Intelligence or cross-cultural communication cards.

Keeping this out prevents evolutionary-pressure from becoming a broad container for every biologically flavored communication move.

### `international-negotiation-and-diplomacy-models.adversarial-countermove-simulation`

Verdict: reject duplicate.

The source supports game theory simulation, attack/defense teams, minmax, and maxmin. But those moves are already owned by:

- `game-theory-payoffs.counterparty-response-payoff-map`
- `mental-simulation.assumption-bound-scenario-rehearsal`
- `batna.credible-walk-away-alternative-test`

The existing diplomacy card should stay focused on substance, signaling, stakeholder interpretation, and durable settlement. Countermove simulation should be a merge/reroute behavior when adjacent cards are nominated.

### `mental-models-of-reality.actor-mental-model-inference`

Verdict: needs rewrite, not added.

The source supports actor mental models, prospect beliefs, and AI persona-style psychological fingerprints. But a broad "infer/adapt to another actor's mental model" affordance collides heavily with `empathy`, especially stakeholder-evidence, confirmable reflection, and strategic perspective-taking.

A future pass may succeed only if it is rewritten narrowly around predictive actor-map simulation or strategy validation, with explicit route-to-empathy boundaries for emotional support, stakeholder reframing, adoption evidence, and negotiation self-interest cases.

## Why This PR Is Small

PR59 deliberately adds only two cards from a larger reviewed candidate set. That is not under-extraction; it is the point of this stage.

The v18 completion risk was that source-real material could be compressed too aggressively. The opposite risk is now just as important: once reviewers start looking for richness, every rich source paragraph can look like a new card.

This PR preserves the strict rule:

> Source-real is not enough. Transaction-distinct is the bar.

## Runtime Safety

No runtime, prompt, packet, lane, Observatory, or product path was changed.

The v21 artifact remains dormant and review-only. Live paths must still pass an explicit artifact path in any future experiment; no latest-file behavior is introduced here.

## Validation

Target validation:

```bash
python3 -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('engine').resolve())); from system_b.model_affordance_validation import validate_model_affordance_file; files=[Path('data/model_affordances/batch_7/emotional-intelligence.json'), Path('data/model_affordances/batch_10/metacognitive-questioning.json')]; [validate_model_affordance_file(f, source_roots=(Path('data/model_sources'),)) for f in files]; print('validation_ok', len(files))"
```

Compile:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v21.json --quality-report-filename quality_report_v21.md --artifact-id model_affordances_v21 --report-title "Model Affordance Quality Report v21"
```

Expected focused test set:

```bash
pytest tests/test_pr59_v21_targeted_enrichment.py tests/test_pr58_v20_targeted_enrichment.py tests/test_pr57_v19_targeted_enrichment.py tests/test_pr36_batch7_records.py tests/test_pr45_batch10_records.py tests/test_pr50_batch13_records.py tests/test_pr53_batch16_records.py tests/test_pr54_batch17_records.py
```

## Bottom Line

PR59 enriches the full-corpus substrate in the manner we want:

- it reads the source material directly;
- it keeps the additions dormant;
- it adds only transaction-distinct cognition;
- it records duplicate-owner rejections;
- it protects v21 from becoming a larger but blurrier vocabulary pile.
