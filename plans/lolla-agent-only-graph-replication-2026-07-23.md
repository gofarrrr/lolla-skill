# Agent-only graph replication plan

Date: 2026-07-23

Status: prospective contract and packets frozen; semantic execution not yet
started

Owner: existing offline Product Delta evaluation

Machine contract:
[`lolla-agent-only-graph-replication-contract-v1.json`](../docs/evals/lolla-agent-only-graph-replication-contract-v1.json)

Generated pre-output packet:
[`generation-packets.json`](../research/agent-only-graph-replication-2026-07-23/generation-packets.json)

Sealed lineage:
[`sealed-manifest.json`](../research/agent-only-graph-replication-2026-07-23/sealed-manifest.json)

Repository provider/API calls authorized: 0

Repository provider/API cost authorized: `$0.00`

Maximum Codex development contexts: 12—eight generation, two blind review,
and two conditional post-reveal interpretation contexts

Graph, source, relation, planner, compiler, runtime, live skill, Decision Work,
Atlas, Observatory, interface, and traversal changes authorized: none

## Plain-language purpose

The previous calibration failed to answer its question for an honest reason:
one of four generation attempts did not leave a recoverable final answer. That
single missing answer removed the only direct-versus-direct baseline and one
direct-versus-graph comparison. The experiment correctly stopped instead of
quietly replacing the missing answer.

The new design does not loosen that rule. It changes the experiment before
execution so one failure no longer destroys the whole comparison:

```text
four new direct outputs:  D3 D4 D5 D6
four new graph outputs:   G3 G4 G5 G6

within direct: D3-D4 and D5-D6
within graph:  G3-G4 and G5-G6
cross:         D3-G3, D4-G4, D5-G5, D6-G6
```

If any one output fails, one within pair and one cross pair disappear. One
within baseline for each condition and three cross pairs still remain. The
failed output remains failed; it is never retried, healed, reconstructed, or
replaced.

This is the smallest disjoint design with that one-failure property. Three
draws per condition would leave one condition without a full independent
within pair after some single failures. Five or more draws would add cost
without being required for the declared resilience.

## Falsifiable question

> On the one checked-in case with exact current direct-only and
> direct-plus-current-one-hop packets, do source-reviewable cross-condition
> differences recur more consistently than source-reviewable differences
> between independent outputs from the same condition, under a design that
> remains evaluable after any one generation attempt fails?

Allowed result states are:

- `cross_condition_difference_more_consistent_than_observed_within_condition_variation`;
- `cross_condition_difference_not_distinguishable_from_observed_within_condition_variation`;
- `mixed_or_reviewer_disagreement`;
- `not_evaluable`.

None of these states selects a winning answer or changes the graph.

## Why there is still one case

The repository contains other conversations and older answer bundles, but no
second checked-in-safe case has the exact current direct-only and
direct-plus-current-one-hop request envelopes. Adding an older pipeline would
change both the case and the mechanism. That would create a larger but less
interpretable experiment.

This replication can examine repeatability on one case. It cannot establish
general expected behavior across decisions, users, models, or providers.

## Reused owners

No parallel graph, compiler, reader, planner, semantic supplier, or answer
grader is introduced.

| Responsibility | Existing owner reused |
| --- | --- |
| Authoritative conversation | checked-in retailer-pilot source |
| Exact direct and graph requests | completed variance-calibration packets |
| Candidate allocation and one-hop increment | frozen graph-increment rehearsal |
| Response schema and generation wrapper | completed variance-calibration packet |
| Candidate accounting and admission | existing pressure compiler |
| Atomic answer comparison | Product Delta paired-screen grammar |
| Qualification, null, and stand-down controls | existing Product Delta screen |
| Lineage reveal and fan-in | deterministic Product Delta custody |

The new provider-free code only freezes, aliases, validates, and later
consolidates these existing artifacts.

## Phase 1 — publish the contract before semantic output

The first PR contains only:

- this plan and the machine contract;
- eight neutral generation packets;
- a separately sealed condition/draw map;
- the eight-pair comparison plan;
- the mechanical missingness gate;
- the blind-review and post-reveal interpretation boundaries;
- deterministic validation and tests;
- current handoff documentation.

No answer is generated on the contract branch. The PR must merge before any of
the eight semantic contexts start, so outputs cannot change their own contract.

## Phase 2 — eight isolated generation attempts

Every generation context:

1. starts in a separate temporary working directory;
2. receives exactly one checked-in neutral packet;
3. has read-only repository visibility;
4. receives no sibling packet, output, review, lineage, or previous result;
5. uses the exact inherited request, schema, wrapper, and settings;
6. writes its final assistant message directly to a predeclared external file;
7. stops at the first terminal result;
8. receives no retry, fallback, healing, or replacement.

All eight attempts run even if an earlier one fails. This prevents later
execution count or allocation from adapting to observed output.

Each imported terminal state remains one of:

- `complete`;
- `partial`;
- `failed`;
- `missing`.

`completed_zero` remains part of Lolla's general state vocabulary but is not a
valid generation outcome for this response contract.

## Phase 3 — deterministic admission and pair availability

A complete output must pass:

- inherited response-schema shape and length bounds;
- exact candidate identity and one-to-one candidate accounting;
- the existing deterministic pressure compiler;
- declared high-stakes fact and causation safety checks.

Each pair is available only when both of its frozen endpoints are complete.
The overall interpretation gate requires:

- at least one available direct-versus-direct pair;
- at least one available graph-versus-graph pair;
- at least three available direct-versus-graph pairs;
- both blind reviews complete.

This gate measures missingness only. It does not decide whether a difference
is large, meaningful, useful, or caused by the graph.

## Phase 4 — two blind non-scalar reviews

Two isolated reviewers receive:

- the complete checked-in source;
- eight neutrally named pairs or explicit unavailable-pair records;
- the existing ten qualification traps;
- the exact-duplicate null;
- the legitimate stand-down;
- the existing atomic Product Delta review grammar.

Before both reviews freeze, they do not receive:

- condition or draw lineage;
- within/cross pair role;
- candidate origin or disposition ledgers;
- previous variance judgments;
- source-proxy reads;
- the sibling review.

They record atomic reasoning moves, source grounding, answer-level preservation
and loss, unsupported additions, burden, uncertainty, and whether a material
decision difference is present, absent, or uncertain. They do not score, rank,
vote, or choose an answer.

## Phase 5 — bounded post-reveal interpretation

The original blind reviewers cannot compare “within” and “cross” recurrence
while lineage remains hidden. Deterministic counts alone cannot determine
whether the same source-grounded reasoning operation recurred rather than
style, length, or polish. Therefore, only if the mechanical availability gate
passes, two additional contexts interpret the pattern.

Each context receives exactly one frozen blind review plus deterministic
lineage reveal. It does not receive the sibling review. It may cite existing
pair IDs, atomic move IDs, and answer-level observations, but it may not add or
revise answer judgments.

This is not identity continuity with the original reviewer and is not a new
general evaluator. It is a review-specific, post-reveal interpretation inside
the existing Product Delta owner. Its only job is to classify that frozen
review's recurrence pattern under the three declared reviewer-specific states.

If the availability gate fails, these two contexts do not start and the result
is `not_evaluable`.

## Phase 6 — deterministic consolidation

The fan-in preserves:

- every terminal state;
- every available and unavailable pair;
- both blind reviews side by side;
- both review-specific post-reveal interpretations side by side;
- every disagreement, uncertainty, burden, unsupported addition, and lost
  value;
- exact request, output, review, lineage, and contract hashes;
- provider and Codex custody limitations.

If both post-reveal interpretations independently return the same non-mixed
state, the consolidation records that aligned state while retaining the whole
evidence vector. Otherwise it records `mixed_or_reviewer_disagreement`. It does
not compute a score, majority vote, significance test, effect size, winner, or
automatic graph decision.

## Execution and publication sequence

1. Validate and merge the contract PR.
2. Run all eight isolated generation attempts with direct terminal capture.
3. Import and validate the eight first-terminal states without repair.
4. Build the blind packet and sealed execution map.
5. Run and freeze two isolated blind reviews.
6. Evaluate the mechanical availability gate.
7. If the gate passes, run and freeze the two review-specific post-reveal
   interpretations; otherwise preserve `not_evaluable`.
8. Build deterministic consolidation and the bounded result note.
9. Run focused and full repository verification.
10. Publish and merge a separate result PR.

The result PR may report only what occurred under this exact contract. It may
not alter the prospective contract to fit the outputs.

## Stop rules

Stop or preserve failure at:

- drift in any locked predecessor artifact;
- drift in inherited messages, schema, wrapper, generation settings, direct
  content, current one-hop increment, or candidate identities;
- allocation other than four new draws per condition;
- generation exposure to sibling material or lineage;
- the first terminal generation failure, without retry or replacement;
- response-shape, compiler, candidate-custody, or high-stakes-integrity
  failure;
- blind-review exposure to lineage or sibling review;
- unavailable overall missingness gate;
- post-reveal addition of new answer-level semantic judgments;
- any score, ranking, vote, winner, significance, or automatic graph decision;
- any claim that unavailable Codex route, token, or platform cost is known or
  zero;
- any provider API call, private archive read, principal-human-field edit,
  graph/planner/compiler/runtime/skill change, or interface work.

## What this cannot decide

This experiment is not:

- principal-human review;
- F2 or F3 completion;
- provider execution;
- a statistically powered estimate;
- expected model behavior;
- proof that a relation is relevant or correct;
- graph causation or graph usefulness;
- proof that an answer is better, safer, or more useful;
- permission for incoming edges, direct-reserve expansion, a second hop,
  community search, embeddings, a graph database, or runtime promotion.

The contract earns only a more reliable look at one narrow automated question.
The graph remains unchanged whatever the result.
