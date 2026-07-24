# Agent-only graph reviewer-envelope repair plan

Date: 2026-07-24

Status: provider-free repair and exact v2 execution consumed; final result
honestly `not_evaluable`

Owner: existing offline Product Delta evaluation

Machine contract:
[`lolla-agent-only-graph-review-envelope-repair-contract-v1.json`](../docs/evals/lolla-agent-only-graph-review-envelope-repair-contract-v1.json)

Execution result:
[`lolla-agent-only-graph-review-envelope-v2-result-2026-07-24.md`](../docs/conversation-understanding/lolla-agent-only-graph-review-envelope-v2-result-2026-07-24.md)

Provider/API calls authorized or made: 0

Provider/API cost authorized or incurred: `$0.00`

Graph, source, relation, traversal, planner, compiler, runtime, skill,
Decision Work, Atlas, Observatory, and interface changes: none

## Plain-language purpose

The completed graph replication did not answer its graph question. Its eight
answers were available, but one of two blind reviewers returned arrays where
the validator required one string. The reviewer-facing example had shown the
allowed values as a list, so it was possible to read the field as a
multi-select.

This repair changes only that response boundary:

```text
before
  "cognitive_effect": ["adds_test", "opens_path", ...]
  ambiguous: allowed-values list or response array?

after
  JSON Schema:
    type: string
    enum: [adds_test, opens_path, ...]
  unambiguous: exactly one string
```

Codex receives the checked-in schema through `codex exec --output-schema`.
The captured first-terminal JSON must then pass a local structural validator
and the existing Product Delta exact-case and enum validator. The schema proves
shape, not meaning.

## Falsifiable question and one causal change

Question:

> Can one authoritative structured-output schema remove the known
> scalar-versus-array ambiguity while preserving the exact frozen review
> material and without changing graph behavior?

One allowed causal change:

> Replace the reviewer-facing example shape with one checked-in JSON Schema
> passed to Codex through `--output-schema`, followed by the existing
> deterministic Product Delta admission checks.

The source conversation, eight frozen answers, answer-pair orientation,
qualification traps, exact duplicate, stand-down, review order, graph
increment, graph lineage, and nonclaims do not change.

## Existing owner and authority split

This is not a new evaluator.

| Responsibility | Owner |
| --- | --- |
| Frozen conversation, answers, controls, and blind pair orientation | consumed graph-replication checkpoint |
| Atomic reasoning-move grammar and exact-case validation | existing Product Delta validator |
| Response shape and scalar enum cardinality | prospective JSON Schema plus deterministic local schema check |
| First-terminal custody and missing/failed state | deterministic execution boundary |
| Apply/reject/park meaning in the original answers | frozen reasoner output; not reinterpreted here |
| Review meaning | future provisional reviewer, if separately authorized |
| Usefulness and action authority | human; not supplied by this work |

The new module lives under `engine/system_b/product_delta_*` and delegates the
semantic-shape admission back to the existing Product Delta validator. It does
not create another graph loader, compiler, planner, semantic reader, score, or
runtime edge.

## Provider-free implementation

The provider-free builder creates:

- lane-specific blind-review JSON Schemas;
- lane-specific post-reveal JSON Schemas, frozen before any possible run;
- two blind packets with the exact frozen semantic material and no old
  example-shaped response contract;
- a known-valid scalar fixture derived from the frozen valid review;
- a known-invalid array fixture derived from the untouched failed terminal
  payload;
- two shape-only post-reveal fixtures;
- a deterministic fixture receipt;
- the exact machine contract, paths, context ceiling, command templates,
  retry policy, and authorization shape.

The checked-in fixtures are development shape evidence. The valid fixture does
not become a new semantic review. The invalid fixture is used only to replay
the known envelope defect; none of its observations are salvaged.

## Provider-free exit result

The local gate requires:

- zero validation errors for the valid scalar review fixture;
- exactly 29 `expected string` errors for the 29 historical
  array-shaped `cognitive_effect` fields;
- zero structural errors for both post-reveal fixtures;
- exact byte and SHA-256 locks over the consumed replication contract, blind
  packet, sealed execution manifest, both terminal review payloads, skeptical
  failure receipt, and `not_evaluable` consolidation;
- no new review, failure, post-reveal, consolidation, or result artifact.

Passing those checks establishes only that the known response-cardinality
ambiguity is repaired prospectively.

## Exact run boundary, now consumed

No answer generation is repeated. The eight frozen admitted answers are
reused because the purpose is to isolate the reviewer envelope. New answers
would mix the envelope change with new reasoner variation.

Both blind reviewers must run fresh. Re-running only the skeptical lane would
be a selective correction after observing the valid primary review. Under v2,
neither historical review counts as one of the required pair.

The prospective sequence is:

1. Recheck the installed Codex CLI and current official structured-output
   guidance.
2. Start two isolated blind contexts with lane-specific packets and schemas.
3. Run both once even if the other fails.
4. Preserve each first-terminal result without retry, repair, reformatting,
   replacement, or semantic salvage.
5. Start the two lane-specific post-reveal contexts only if both blind reviews
   pass schema and existing Product Delta admission.
6. Preserve the two interpretation vectors side by side and consolidate under
   the already-declared non-scalar rule.
7. Publish a separate result PR. A shape-valid run may still be semantically
   uncertain or `not_evaluable`.

Maximum new Codex contexts: four—two blind and two conditional post-reveal.

Repository provider/API calls: zero.

Repository provider/API cost ceiling: `$0.00`.

Codex's ambient platform route, tokens, and economic cost remain unavailable
to the repository operator and must not be reported as zero.

## Authorization boundary

The provider-free work in this plan is complete. It did not itself authorize
the four contexts above. The founder later supplied the exact authorization,
and that authorization is now consumed.

The exact separate authorization frozen in the machine contract is:

```text
AUTHORIZE_LOLLA_GRAPH_REVIEW_ENVELOPE_V2: reuse_frozen_generation_outputs=true; blind_review_contexts=2; conditional_post_reveal_contexts=2; maximum_codex_contexts=4; repository_provider_api_calls=0; repository_provider_api_cost_usd=0.00; no_retry=true
```

The run attempted exactly two blind and two conditional post-reveal contexts,
with zero generation contexts, zero retries, zero repository provider calls,
and `$0.00` repository provider cost. Both blind reviews passed. Both post-
reveal payloads failed one exact nonclaim equality check and were preserved
without repair or semantic salvage. The final state is `not_evaluable`.

No reuse, retry, corrected acknowledgment, or additional semantic context is
authorized by the consumed string.

## Stop rules

Stop if:

- any frozen input hash or byte count changes;
- source, answer, control, comparison orientation, or review meaning changes;
- current Codex no longer supports the frozen `--output-schema` boundary;
- a context sees sibling work or sealed lineage before its declared gate;
- a first-terminal payload is invalid;
- anyone proposes retry, healing, reformatting, replacement, or partial
  semantic salvage;
- both new blind reviews are not valid before post-reveal;
- the result is converted into a score, answer winner, graph-value claim, or
  traversal decision;
- work would call a provider API, inspect a private archive, fill a
  principal-human field, or change graph/runtime/interface behavior.

## What remains unknown

This repair does not tell us:

- whether either future review will be semantically good;
- whether reviewers will agree;
- whether a recurring answer difference comes from the graph;
- whether a graph relation is relevant;
- whether either answer is better;
- whether a human experiences an `aha`;
- whether outgoing one-hop should remain, expand, or stop.

It repairs the measuring instrument before another measurement. It does not
supply the measurement.
