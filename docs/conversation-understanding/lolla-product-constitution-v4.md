# Lolla Product Constitution v4

Status: binding development house rules  
Date: 2026-07-12

This amendment incorporates `lolla-product-constitution-v3.md` in full. Earlier versions remain immutable because completed evidence packages may hash-lock them. V4 governs future work.

## House rule 16 — Controlled identities, probabilistic applicability

LLMs may interpret messy conversation and select or reject items from an explicitly supplied controlled vocabulary. They must not invent routing mechanism IDs, mental-model IDs, aliases, or graph nodes during a run.

Canonical identity and semantic applicability are separate:

- deterministic code validates canonical IDs, exact source custody, bounds, hashes, and graph provenance;
- an LLM or human judges whether a controlled mechanism or model applies;
- an unknown or historical alias is quarantined, not silently normalized;
- abstention, ambiguity, insufficient evidence, and rejecting every candidate must remain valid outcomes;
- canonical-name compliance does not prove the selection is useful or correct.

The deterministic graph exists to introduce controlled external recall. A direct LLM selection from the complete model corpus may be tested as a comparison, but it must not silently replace graph pressure or collapse interpretation and challenge selection without an explicit evidence-backed architecture decision.

## Product evil — Canonical-looking semantic drift

The system returns valid IDs and therefore appears stable, while it chooses them through title association, factual-topic overlap, or an under-specified menu. Alternatively, runtime alias repair makes inconsistent substrate identities look canonical and hides the custody defect.

## Additional “what good looks like” questions

- Could every emitted mechanism and mental-model ID be resolved against the frozen canonical registry?
- Was applicability decided semantically rather than inferred from canonical spelling?
- Could the selector reject all candidates without being treated as a failure?
- Did deterministic machinery recall candidates without pretending to certify relevance?
- Were unknown aliases exposed and quarantined rather than repaired invisibly?

