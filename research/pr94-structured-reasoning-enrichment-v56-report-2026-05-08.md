# PR94 Structured Reasoning Enrichment v56 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr94-structured-reasoning-v56`

## Scope

PR94 continues the dormant reviewed-affordance enrichment track. It does not
wire affordances into `/lolla`, prompts, lane adapters, packet rendering, or
runtime pickup.

The audit target was a structured-reasoning and meta-boundary ring:

- `category-decisions`
- `critical-thinking`
- `conjunction-fallacy`
- `mental-models-of-reality`
- `evolutionary-pressure`
- `international-negotiation-and-diplomacy-models`

The operating question stayed the PR55 question:

> Would separating this material change downstream use, reject, defer, merge,
> evidence-gate, treatment, misuse-guard, or final-answer behavior?

PR94 used two read-only subagent audits as pressure checks, then made final
adjudication locally against the source files and current records.

## Source-Read Verdict

Positive affordance splits accepted:

- `category-decisions.category-of-one-positioning-frame`
- `critical-thinking.framework-fit-stress-fracture-check`
- `critical-thinking.personal-data-action-threshold-check`

Absence rails added:

- `category-decisions.category-lock-in-after-causal-shift`
- `category-decisions.universal-playbook-before-taxonomy-validation`
- `critical-thinking.academic-selfie-as-standalone-affordance`
- `conjunction-fallacy.group-smoothed-step-probabilities-as-rigor`
- `mental-models-of-reality.model-name-collection-without-decision-pressure`
- `evolutionary-pressure.accessibility-over-accuracy-as-evolutionary-pressure`
- `evolutionary-pressure.evolutionary-logic-as-fatalism`
- `evolutionary-pressure.adaptation-loop-without-selection-evidence`
- `international-negotiation-and-diplomacy-models.standalone-cwd-agent-orchestration`
- `international-negotiation-and-diplomacy-models.fud-tactic-as-diplomacy`

No positive splits were accepted for `conjunction-fallacy`,
`mental-models-of-reality`, `evolutionary-pressure`, or
`international-negotiation-and-diplomacy-models`.

## Accepted Splits

### `category-decisions.category-of-one-positioning-frame`

The existing category-decisions card owns repeat-choice precommitment and
taxonomy validation. The source also contains a different transaction:
category-of-one positioning.

Why this passes:

- Activation is market, offer, or strategic positioning, not repeated operational
  classification.
- Evidence requires `1 Specific Problem, 1 Specific Person, 1 Specific Way`.
- The receiver should reject category language that is only label theater.
- The card must defer to `jobs-to-be-done` when customer-progress evidence is
  missing.

This split is deliberately narrow. It does not make category labels into
strategy, and it does not create deterministic routing.

### `critical-thinking.framework-fit-stress-fracture-check`

The existing critical-thinking card was doing too much. It checked claims,
evidence, assumptions, personal data, and framework fit inside one broad card.
The source supports making framework-fit inspection first-class when a named
framework, process, analogy, or mental model is carrying the recommendation.

Why this passes:

- Activation is a named framework doing causal work in the answer.
- Evidence is the imported assumption and context mismatch.
- Treatment is to identify the stress fracture before the recommendation earns
  weight.
- The receiver behavior differs from generic claim/evidence checking: use only
  when the framework itself is carrying the conclusion; reject when this is
  generic issue-tree work better owned by `decomposition`.

This split is especially relevant to the larger Lolla goal: a mental-model card
should not become authority merely because its vocabulary sounds strategic.

### `critical-thinking.personal-data-action-threshold-check`

The source explicitly warns that critical thinking can fail when it filters out
emotional or personal data in high-stakes human situations. That is not the same
transaction as generic empathy. It is evidence hygiene inside a critical-thinking
frame.

Why this passes:

- Activation is false rationality: relevant human data is being removed as if it
  were noise.
- Evidence requires emotional, relational, or personal data plus validation
  status.
- Treatment preserves the data but still requires a one-day answer or action
  threshold so critique does not become detachment theater.
- The receiver should reject unvalidated emotional interpretation as proof and
  route pure perspective-taking to empathy or emotional-intelligence records.

## Rejected Positive Splits

### `conjunction-fallacy.disjunctive-failure-analysis`

Rejected as a positive split.

The source mentions disjunctive structures, but the current corpus already gives
that transaction to `risk-assessment.thresholded-downside-governance`, which
explicitly covers disjunctive component failures, hidden failure paths,
thresholds, monitoring, and safeguards.

PR94 kept `conjunction-fallacy` focused on sequential success-gate fragility and
added `group-smoothed-step-probabilities-as-rigor` as a guard.

### `mental-models-of-reality` expansion

Rejected as positive split.

The source contains latticework, decomposition, inverse thinking, Feynman,
persona, prospect, and AI twin material. Those are real, but better owned by
existing adjacent records:

- `latticework-of-mental-models`
- `decomposition`
- `inversion`
- `feynman-technique`
- `analogies-and-metaphors`
- `mental-simulation.persona-fidelity-role-play`
- `empathy`
- `understanding-motivations`
- `user-experience-research-methods`
- `persuasion-principles`

PR94 added `model-name-collection-without-decision-pressure` because the main
runtime danger is not under-extraction; it is impressive model-name accumulation
without prediction, mechanism, threshold, protocol, test, or decision pressure.

### `evolutionary-pressure` expansion

Rejected as positive split.

The source contains croc-brain communication, commitment-consistency,
organizational adaptation loops, emotional drivers, and EQ. The current record
correctly owns selection-environment diagnosis: what the system rewards, selects
against, and makes likely to survive.

The rejected material is better owned by:

- `persuasion-principles`
- `pre-suasion`
- `simplification`
- `signaling`
- `commitment-bias`
- `adaptation`
- `systems-thinking`
- `resilience`
- `emotional-intelligence`

PR94 added rails for accessibility-over-accuracy, evolutionary fatalism, and
generic adaptation without selection evidence.

### `international-negotiation-and-diplomacy-models` expansion

Rejected as positive split.

The current card correctly owns substance, signaling, stakeholder
interpretation, sequencing, credibility, relationship, and durable settlement.
Tempting source examples like game theory simulation, CWD agent orchestration,
FUD, persuasion packaging, buying-committee personas, and perspective taking do
not justify standalone negotiation affordances unless they serve the durable
settlement transaction.

PR94 added absence rails for standalone CWD orchestration and FUD-as-diplomacy.

## Quality Interpretation

PR94 is a mixed enrichment pass:

- it accepts three positive splits where current one-card compression could hide
  distinct receiver actions;
- it rejects richer-looking source clusters when adjacent records already own
  the cleaner transaction;
- it adds absence rails where seductive examples could otherwise be mistaken for
  source permission.

This is the intended middle path between leaving cognition on the table and
turning the corpus into a massive dump.

## v56 Compile Result

Artifact: `model_affordances_v56`

- Status: `draft_review_only`
- Records: `222`
- Affordances: `303`
- Absence records: `624`
- Schema-validation failures: `0`
- Source-quote rejections: `0`

Delta from v55:

- Affordances: `+3`
- Absence records: `+10`
- Runtime references: none

## Runtime Boundary

The v56 artifact remains dormant. PR94 does not:

- change packet producer defaults;
- add a lane-to-nomination adapter;
- import v56 from engine or scripts;
- change prompts or receiver rubrics;
- alter `/lolla` behavior.

Before runtime pickup, the PR55 blockers still stand:

- explicit artifact selection;
- confidence visibility;
- absence visibility;
- grouped affordance identity;
- lane provenance mapping;
- broad-card cap behavior;
- receiver freedom to reject or defer cards.

## Validation

Focused validation should cover:

- edited records validate against schema and exact source quotes;
- v56 preserves all 222 model IDs from v55;
- v56 adds only the three accepted positive affordance IDs;
- v56 adds only the ten expected absence rails;
- rejected source clusters remain compressed or route to adjacent owners;
- v56 is not referenced by live runtime paths.

Focused command:

```bash
PYTHONPATH=. pytest tests/test_pr94_v56_structured_reasoning_enrichment.py tests/test_pr93_v55_implementation_feedback_enrichment.py tests/test_model_affordance_compiler.py
```

## Bottom Line

PR94 enriches the corpus where compression was hiding receiver action:
category-of-one positioning, framework-fit stress fractures, and human-data
evidence hygiene inside critical thinking.

It also refuses several tempting expansions. That refusal is part of quality.
The corpus should preserve the source's cognition, but it should not turn every
example into an affordance when another record already owns the action.
