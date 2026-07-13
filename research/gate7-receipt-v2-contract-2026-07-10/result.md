# Gate 7 Reasoning Run Receipt v2 contract repair

Status: **complete; first closed-case transfer observed**  
Date: 2026-07-10

## Simple result

We repaired the receipt contract without touching the live system or rerunning
Case 10. Its first real application to closed Case 06 evidence then stopped
before assembly and exposed fields that the synthetic fixture had missed.

The next receipt must now preserve the source-stated final action and deadline
as separate fields, label authorizations as an as-of snapshot, separate case
questions from reader and human-product questions, distinguish four levels of
graph evidence, use bounded custody language, and reject normalized duplicate
claims.

The repaired contract now also carries the exact anonymous outputs and reveal
mapping, expected and observed pressure IDs, semantic-hearing and effect-
consistency states, partial token scope, and an explicit V60 affordance origin.
The failed first application remains preserved rather than silently rewritten.

An empty pressure portfolio remains valid. The deterministic validator cannot
force a mental model into a case or decide whether a strange graph lens is
useful.

## Verification

- JSON Schema Draft 2020-12 contract validated;
- prospective synthetic fixture validated against the schema;
- provider-free cross-field validator returned `cross_field_valid`;
- 17 adversarial tests passed;
- 22 focused Gate 7 tests passed;
- the no-unbudgeted-call repository suite passed 4,025 tests with one skip;
- zero provider calls;
- zero runtime changes;
- frozen Case 10 receipt hashes remain unchanged.

The existing stability-test module was excluded because its current unit path
invokes live OpenAI embeddings. This provider-free repair did not authorize
those calls.

## Boundary

This repairs the receipt structure, not receipt usefulness. It does not
complete Gate 7, prove answer quality, validate the graph, or authorize runtime
integration.

The core holdout inventory later found no safe untouched case. A replacement
Case 06 contract then assembled and validated the receipt from frozen evidence
without rerunning the pipeline. One separately frozen reader call produced a
stronger partial transfer pass: it preserved the central accountability story
but lost deadline state, a material final user inference, exact lineage subtype,
and exact operating figures. Human usefulness is now the next Gate 7 evidence
need; no additional reader call is authorized.
