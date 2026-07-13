# Reasoning-process contract v0

Status: Phase 0 complete; provider-free research only  
Date: 2026-07-11  
Governing plan:
`plans/reasoning-process-ledger-and-bounded-views-2026-07-11.md`

## Purpose

This contract defines the technical boundary for interpreting and evaluating
the reasoning process in a multi-turn conversation. It does not evaluate the
final memo, recommendation, or deliverable.

The product distinction is binding:

```text
authoritative conversation
  -> broad source-linked process ledger
  -> bounded question-specific process views
  -> evidence-vector assessment of the process

final memo/output: separate evaluation object
reasoning abstraction and graph pressure: later blocked stage
```

A final recommendation can be attractive while its process is weak. A strong
process can still produce a wrong or uncertain recommendation. The process
record therefore provides inspectable evidence, not certification.

## Contracted artifacts

### 1. Authoritative conversation

The one-to-one conversation remains the source of truth. Stable turn and span
IDs, exact text, message order, and a source hash must remain available. No
summary or process view may replace it.

### 2. Canonical reasoning-process ledger

Schema: `lolla.reasoning_process_ledger.v0`

The ledger is broad and append-only. It records every proposed observation and
failure with:

- stable observation and source identities;
- exact source references;
- semantic status and interpretation provenance;
- complete state history and terminal custody;
- explicit ambiguity and operational failure;
- probabilistically assigned relations to earlier observations;
- a permanently false direct-graph-routing flag.

An item may be admitted, preserved as ambiguous, quarantined for invalid source
or schema, or preserved as an operational failure. Presence in the ledger does
not prove that the interpretation is correct or important.

Deterministic code may validate identity, exact source, shape, references,
hashes, budgets, state custody, and product boundaries. It may not infer that
an item is relevant, accepted, equivalent, resolved, contradictory, or
superseded.

### 3. Bounded process view

Schema: `lolla.reasoning_process_bounded_view.v0`

A view answers exactly one process question:

1. position and decision trajectory;
2. exploration and alternatives;
3. evidence and assumption discipline;
4. uncertainty and unresolved state;
5. challenge and revision response.

Each input ledger observation receives exactly one view disposition. Semantic
dispositions—include, park as not applicable, park as redundant, or park as
unclear—must come from a probabilistic reader or source reviewer. Deterministic
code may only exclude mechanically invalid input or mark an item not evaluated
because a prospectively frozen budget was reached.

Every included view item carries both ledger-observation and exact-span
lineage. Every omission remains recoverable from the authoritative ledger. A
view is never the authoritative source.

Frozen model-facing schema:
`docs/evals/reasoning-process-bounded-view-provider-schema-v0.json`.

### 4. Process assessment

Schema: `lolla.reasoning_process_assessment.v0`

The assessment is a vector of evidence-linked observations across:

- exploration and alternative coverage;
- evidence-versus-assumption discipline;
- position and decision trajectory;
- response to challenge and revision;
- uncertainty and reopen conditions;
- Lolla-pressure disposition when present;
- limits of the assessment.

Each observation is `supported`, `mixed`, `unclear`, or `not_observed`.
Supported, mixed, and unclear observations require lineage through both the
bounded view and ledger. `Not observed` must not invent item-level evidence and
must explicitly say that absence from the captured process is not proof of
absence elsewhere.

The assessment cannot include a scalar quality, effort, depth, trust, or
correctness score. Calls, tokens, latency, and event counts remain telemetry and
cannot be treated as quality evidence.

Frozen model-facing schema:
`docs/evals/reasoning-process-assessment-provider-schema-v0.json`.

## Frozen evidence gates

The authoritative machine-readable contract is
`docs/evals/reasoning-process-phase0-contract-v0.json`.

Load-bearing gates include:

- 100% authoritative-message, exact-source, and terminal-candidate custody;
- 100% reviewed material present or explicitly disputed;
- 100% protected-item accounting and visible survival;
- zero invalid admitted items;
- zero source-strength inflation;
- zero context-invisible labels;
- zero direct graph seeds;
- no process-evaluation dimension at zero;
- at most 32 observations, 24,000 UTF-8 input bytes, and 12 output items per
  bounded view;
- provider schemas no deeper than 8 and no larger than 12,000 bytes.

The view budgets are attention and operability boundaries, not semantic
relevance rules. If legitimate source material cannot fit, the representation
must be redesigned before any call rather than silently pruning it.

## Provider envelope

Phases 0–2 permit zero provider calls. The later hard ceiling is 30 calls and
$0.30, divided prospectively across one development baseline, one possible
generic repair, two transfer cases, and conditional stability work. This is a
maximum envelope, not current authorization.

All later calls require:

- an explicit provider/model compatibility preflight;
- temperature zero and reasoning disabled;
- no fallback, automatic retry, response healing, or evaluator call;
- complete raw attempt, terminal state, usage, cost, and failure custody;
- source-first review before narrative polish is considered.

Provider transport enforcement never replaces local typed and semantic
validation. A schema-valid response remains an untrusted semantic proposal.

## Failure taxonomy

The frozen taxonomy is `RP0`–`RP15` in the machine-readable contract. It keeps
contract/hash, source custody, candidate custody, concept omission, semantic
placement, trajectory, source strength, context visibility, fan-in,
minority-signal loss, provider transport, stability, scorer mismatch,
assessment overclaim, deterministic semantic gating, and forbidden product
boundary breaches distinct.

The same load-bearing semantic failure surviving the one allowed generic
repair on two cases closes the design for material redesign. Stable wrong
output is failure. Schema validity is not semantic correctness.

## Non-claims

Passing this contract does not establish:

- final-memo quality or correctness;
- reasoning quality, effort, depth, or trust;
- graph value or graph integration authority;
- runtime readiness;
- usefulness to a human reader;
- downstream reconsideration improvement.

It establishes only that the artifacts obey the frozen structural, custody,
lineage, budget, and product boundaries required before provider-free replay.

## Phase 0 verification

- 19 focused adversarial contract tests passed;
- 47 tests passed across the new contracts and neighboring conversation-state,
  turn-record, hybrid-boundary, constitution, and measurement controls;
- both checked-in provider schemas match their generated source exactly;
- schema sizes and depth remain inside the frozen limits;
- provider, evaluator, graph, runtime, and embedding calls: zero;
- paid cost: $0.00.
