# Batch 3 result — fact/reasoning boundary shadow

Status: **failed as frozen; informative, not retried**

## What this batch asked

Can a small LLM job convert a complete conversation into a fact-free reasoning
projection that stays the same when only facts change, but changes when the
reasoning itself changes?

If yes, deterministic code could safely validate and route that projection
without pretending to understand messy language. If no, the projection is not
ready to control graph routing.

## What worked

- All three model responses passed the exact typed contract.
- Every source-turn reference was valid.
- The deterministic sealer excluded raw text, quotes, entities, quantities,
  dates, desired outcomes, and topic labels from the routing projection.
- Deterministic seed routing was reproducible and used only declared V60 model
  IDs.
- No retry, evaluator call, or runtime modification occurred.
- Three calls used 2,222 tokens and an estimated `$0.0011605`.

This is evidence that the custody boundary can be implemented simply. It is
not evidence that the semantic abstraction is reliable.

## What failed

The two fact variants used the same sentence-level reasoning structure, but
the interpreter returned different labels and therefore different graph seeds:

- both returned `counterpressure_acknowledged_not_integrated` and
  `missing_reversal_condition`;
- only `facts_a` returned `criteria_defined_after_commitment`;
- only `facts_b` returned `status_signal_used_as_evidence`.

The changed-reasoning fixture did produce different labels and candidates, so
there is directional sensitivity to reasoning. But the base output missed the
two labels prospectively required by the contract, and the improved
conversation still received missing/asymmetric pattern labels at the user
scope. That exposes an unresolved target question: are we classifying the
user, the assistant, or the joint reasoning trajectory?

## Meaning for the product

The experiment supports the architectural division of labor but not the
current semantic projection:

```text
LLM interpretation: necessary, not stable enough yet
Deterministic custody/routing: narrow, reproducible, and fact-free
Live graph integration: not authorized
```

We must not respond by adding keyword rules or layered Python gates. The miss
belongs to the semantic target and ontology. This frozen case will not be
retried or repaired post hoc.

Batch 4 must now decide what to retain as product, what to simplify, and what
must remain a research surface.
