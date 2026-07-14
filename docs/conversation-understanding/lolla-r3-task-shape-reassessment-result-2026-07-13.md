# Lolla R3 final-consumer task-shape reassessment

Status: provider-free reassessment complete; one-pass wire redesign selected

Date: 2026-07-13

Provider calls: zero

Runtime changes: none

## Plain-language outcome

The R3 failure does not currently justify splitting the final consumer into
multiple LLM calls or buying a stronger model.

Gemini returned all nine required pressure judgments. Eight rows had no
mechanical finding. The only failure was one row that said both:

```text
disposition = park
effect = uncertainty_change
```

Those labels contradict each other under Lolla's contract. `park` means that
the pressure does not earn a material effect now and has a condition for later
reopening. The model was asked to express that decision twice—once as a
disposition and once as an effect—and the two fields diverged.

That is direct evidence of redundant wire coordination. It is not proof that
the complete task exceeded the model's reasoning capacity. The preserved
response cannot be repaired losslessly: keeping `park` would require changing
the effect, while keeping `uncertainty_change` would require changing the
disposition and adding missing effect custody. Deterministic code is not
allowed to make either semantic choice.

## Alternatives compared

| Design | Calls | Serial depth | Transfer boundaries | Schema properties | Maximum estimated cost | Evidence status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Current one pass | 1 | 1 | 0 | 14 | `$0.0081855` | accepted once; response failed one cross-field rule |
| Collapsed-outcome one pass | 1 | 1 | 0 | 13 | `$0.00816725` | provider-free only |
| Disposition then synthesis | 2 | 2 | 1 | 13 across two schemas | `$0.01180325` worst-case | provider-free only |

The split design gives the first stage seven semantic responsibilities and the
second stage three. It does not eliminate work; it redistributes it, introduces
a serial call and a disposition-ledger transfer, and can fan a maximum-size
28,251-byte ledger into synthesis. Research suggests delayed formatting can
help when a model is near capacity, but R3 has not established that capacity is
the causal problem.

## Selected design

The smallest evidence-backed redesign keeps one fresh-consumer call and
collapses disposition plus effect into one controlled outcome:

```text
reject
park
apply_reframe
apply_new_condition
apply_new_alternative
apply_uncertainty_change
apply_reversal_rule
apply_reinforces_existing
```

This preserves the constitutional boundary:

- the LLM still decides whether each pressure applies, should be rejected, or
  should be parked;
- the LLM still selects the material effect when it applies;
- deterministic code maps the explicit controlled label to the canonical
  disposition/effect pair;
- code continues to validate pressure identity, source turns, public/private
  effect custody, boundary roles, text bounds, hashes, and budgets;
- code does not infer relevance, choose between ambiguous labels, delete
  candidates, or heal a response;
- all six direct and three graph pressures remain inspectable;
- rejection and parking remain valid outcomes;
- the full conversation and original answer remain authoritative.

The combined label prevents the exact observed disposition/effect
contradiction. It does not guarantee semantic correctness. A model can still
choose the wrong combined label, cite weak evidence, force pressure, or draft a
bad answer. Those remain source-first evaluation questions.

## Why conditional JSON Schema was not selected

Google's documentation updated on 2026-07-07 demonstrates `anyOf` for a Gemini
3.5 Interactions API moderation example. The full JSON Schema standard also
supports conditional validation. Neither proves that OpenRouter's Chat
Completions translation to the pinned Gemini 3.1 Flash-Lite Google Vertex route
will accept the same branch shape.

The collapsed enum uses only the already proven, documented subset and is
smaller. A union would add a provider-specific dependency without adding
semantic freedom.

## What local evidence establishes

- the exact R3 call and failure hashes remain unchanged;
- one and only one mechanical finding reproduces;
- overload, ontology ambiguity, and model capacity remain possible but
  unproven explanations;
- the preserved conflicting row has no lossless combined-label mapping;
- all three prospective schemas pass the documented-subset lint;
- the collapsed compiler covers apply, reject, and park across all nine exact
  pressure IDs;
- identity, order, source-turn, effect-custody, outcome, and ledger tampering
  fail closed;
- separated synthesis cannot mutate its frozen disposition ledger;
- fan-in, schema size, prompt size, serial depth, calls, and maximum cost are
  measured separately;
- every artifact is self-hashed and linked to frozen inputs;
- no provider call, semantic repair, judge, model comparison, or runtime
  integration occurred.

## Decision

R3 is redesigned at the provider-wire boundary, not split into a new agent
pipeline. The selected collapsed-outcome contract is ready for a future
prospective empirical test but has no model-backed evidence yet.

The future hypothesis is:

> On a newly frozen ambiguous multi-turn reliability case, the collapsed
> one-pass contract returns all pressure outcomes under mechanical custody and
> produces a source-reviewable answer without the disposition/effect
> contradiction.

A future test must use a safe case frozen before execution and not used to
change this contract. It may make at most one cheap-model call if separately
authorized, with no retry, fallback, healing, premium model, or evaluator. A
mechanical pass must then undergo the existing source-first vector review.

No call is authorized by this result. A first failure must be preserved and
reclassified provider-free; it does not automatically authorize the split
design.

## Current-practice record

The dated research maps official Gemini and OpenRouter guidance, recent
structured-output research, full JSON Schema conditionals, JSONSchemaBench,
Pydantic AI, and Instructor to the exact local failure. See
`lolla-r3-task-shape-current-practice-2026-07-13.md`.

## Evidence

- Current-practice check:
  `docs/conversation-understanding/lolla-r3-task-shape-current-practice-2026-07-13.md`
- Counterfactual implementation:
  `engine/system_b/r3_task_shape_counterfactual.py`
- Provider-free builder:
  `scripts/evals/build_r3_task_shape_reassessment.py`
- Responsibility map:
  `research/lolla-r3-task-shape-reassessment-2026-07-13/responsibility-map.json`
- Causal failure audit:
  `research/lolla-r3-task-shape-reassessment-2026-07-13/failure-causal-audit.json`
- Frozen counterfactual contracts:
  `research/lolla-r3-task-shape-reassessment-2026-07-13/counterfactual-contracts.json`
- Comparison vector:
  `research/lolla-r3-task-shape-reassessment-2026-07-13/comparison-vector.json`
- Decision:
  `research/lolla-r3-task-shape-reassessment-2026-07-13/decision.json`
- Hash-custody summary:
  `research/lolla-r3-task-shape-reassessment-2026-07-13/summary.json`
- Tests: `tests/test_r3_task_shape_counterfactual.py`
