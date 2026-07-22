# Lolla Constitutional Pressure Portfolio Custody PRD v0

Date: 2026-07-22
Status: draft for founder review; planning only
Depends on: Constitution v5, the 2026-07-22 graph audit workbook, and an approved graph-substrate authority boundary
Provider calls authorized: zero
Runtime behavior, prompt, graph artifact, Atlas, frontend, and semantic-regeneration changes authorized by this PRD: none

## Product decision in simple terms

Lolla does not send every retrieved mental model straight to the reasoner. It
first builds a bounded pressure portfolio:

```text
direct lane candidates
        |
        +-- bounded direct active set
        +-- direct reserve
        |
        v
one-hop outgoing graph expansion from direct-active seeds
        |
        +-- one antagonist slot
        +-- one tension slot
        +-- one ally slot
        +-- graph reserve
        |
        v
reconsidering reasoner
        |
        +-- apply
        +-- reject
        +-- park
```

The current mechanism protects an important constitutional property: graph
pressure is admitted before a probabilistic verifier can silently remove it.
It also keeps candidates that do not fit in the active surface in reserve.

The immediate problem is not that this policy is obviously wrong. The problem
is that important facts about what it did are not fully carried to the outer
portfolio and receipt. In particular, the portfolio does not explicitly say
that only direct-active seeds were expanded, and a graph candidate reachable
through several exact paths is presented with only one admission edge even
though the internal ledger found the other paths.

This PRD first makes the present policy named, typed, bounded, and fully
inspectable. It does not choose a more sophisticated traversal policy.

## Falsifiable product question

> Can Lolla preserve the exact current active candidate identities and order
> while exposing the complete bounded expansion scope, every enumerated exact
> provenance path, active/reserve disposition, and all relevant coverage states
> in a replayable portfolio contract?

The first implementation stage succeeds only if the answer is mechanically
**yes**. Any later claim that incoming, two-hop, or alternative allocation is
better requires a separate frozen experiment and separate authorization.

## Why this follows the substrate PRD

The portfolio planner should decide which published graph candidates become
active or reserve. It should not also decide:

- how graph files are discovered;
- which repository owns relation authorship;
- whether an incoming edge should be treated as a reverse edge;
- how legacy model identities are normalized;
- whether a missing graph means an intentionally empty graph;
- whether a compiled field was source-authored or synthesized.

Those are substrate and compiler responsibilities. The planner must consume a
validated, immutable substrate snapshot so that its one job—bounded pressure
allocation—can be tested independently.

## Constitutional and roadmap boundary

This is a prospective pressure-portfolio planning document. It does not
replace the Constitution roadmap's next eligible Stage 1 Decision Trail
truthfulness review and does not authorize runtime integration.

The following remain binding:

- the graph introduces pressure; it does not certify relevance;
- graph candidates cannot be silently deleted by a probabilistic
  applicability pass before reconsideration;
- active, reserve, malformed, duplicate, missing, partial, and failed states
  remain distinguishable;
- distinct provider-authored interpretations are not merged, ranked, or voted
  away merely for presentation cleanliness;
- apply, reject, and park remain legitimate outcomes;
- the receipt proves what process occurred, not that the result was wise;
- the human retains decision authority.

Provider calls, new semantic judgments, live-run evaluation, prompt changes,
and runtime promotion require their own exact authorization.

## Current policy baseline

The current constitutional portfolio behavior is usefully described as
`constitutional_one_hop_relation_slots_v1`.

That name is prospective documentation. It does not rename a checked-in
runtime contract by itself.

### Direct admission

- The planner receives canonical candidates produced by the live four-lane
  pressure engine.
- Malformed and duplicate inputs receive explicit dispositions.
- At most six direct candidates become active through the controlled-mechanism
  round-robin policy.
- Remaining well-formed direct candidates stay in direct reserve.

### Graph enumeration and admission

- Only the six direct-active candidates are graph-expansion seeds.
- Expansion follows source-authored outgoing relations by one hop.
- The active graph surface has at most one antagonist, one tension, and one
  ally target.
- Within a relation slot, current admission is deterministic and
  lexicographic by source and target identity.
- Affinity, activation similarity, conversation similarity, and a
  probabilistic applicability judgment do not control constitutional graph
  admission.
- All other enumerated graph targets remain in graph reserve.

### Reconsideration and custody

- Active graph candidates receive challenge material and source references.
- The reconsidering reasoner may apply, reject, or park them.
- The internal graph ledger can contain more than one exact source edge for a
  target reached from multiple direct-active seeds.
- The outer active portfolio item currently carries one admission edge, not
  the complete enumerated path set.
- Portfolio and Decision Trail machinery preserve bounded token, hash,
  disposition, and artifact custody.

## Evidence baseline

Provider-free enumeration over 163 deterministic windows of 60 canonical model
IDs produced this characterization of the current policy:

| Observation | Count |
| --- | ---: |
| Graph-active admissions | 489 |
| Active targets with more than one exact enumerated source path | 265 |
| Additional exact paths known internally but not preserved on the outer active item | 808 |

This is a structural characterization, not evidence that all paths are
semantically useful or that the current active choices are optimal.

The topology also warns against enabling broader traversal casually:

| Traversal | Median reachable models | 90th percentile | Maximum |
| --- | ---: | ---: | ---: |
| Outgoing, one hop | 5 | 7 | 10 |
| Outgoing, up to two hops | 26 | 32 | 41 |
| Incident/incoming-plus-outgoing, one hop | 6 | 17 | 159 |
| Incident/incoming-plus-outgoing, up to two hops | 189 | 204 | 221 |

One model has 159 incoming references and eight outgoing relations. Treating
incoming references as reverse relations, or combining incident traversal with
two hops, can therefore make almost the full 222-model corpus reachable. That
would be a new policy, not a harmless extension of the present graph.

## Desired outcome

At the end of the approved sequence:

1. the current constitutional graph-allocation policy has one explicit name
   and version;
2. the planner consumes one immutable `PublishedKnowledgeSubstrate` snapshot
   rather than scanning raw graph dictionaries;
3. the current active identities and order can be reproduced exactly;
4. the portfolio declares which direct candidates were expansion seeds;
5. direct-reserve candidates explicitly state that their neighborhoods were
   not enumerated under v1;
6. every active and reserve graph target retains every exact enumerated path
   within the declared one-hop scope;
7. one admission path remains distinguishable from the complete provenance
   path set;
8. source-authored direction is preserved on every path;
9. overflow, truncation, malformed input, duplicate input, partial substrate,
   failed substrate, and missing substrate remain separate states;
10. bounded token and candidate limits remain mechanically enforced;
11. apply/reject/park disposition remains linked to the exact active pressure
    item and policy identity;
12. no probabilistic or semantic gate is introduced before reconsideration;
13. future traversal experiments can run offline against the same frozen
    snapshot without changing runtime.

## Users and jobs

### Reconsidering reasoner

“Show me the bounded pressure that was actually admitted, where it came from,
and whether several independent graph paths converged on it. Do not pretend
that convergence proves relevance.”

### Human reviewer

“Show me which models were considered, which became active, which remained in
reserve, which direct candidates were expanded, and which were not. Let me
trace every presented graph pressure item back to exact directed relations.”

### Evaluator

“Let me replay the same policy against the same substrate, compare prospective
policies offline, and observe a vector of outcomes rather than one graph or
answer score.”

### Maintainer or coding agent

“Give the substrate, planner, and receipt separate responsibilities so a
change to one does not silently redefine the other two.”

## Required architecture

```text
PublishedKnowledgeSubstrate snapshot
        +
canonical direct lane candidates
        +
explicit ConstitutionalPortfolioPolicy
        |
        v
PressurePortfolioPlanner.plan(...)
        |
        +-- active direct items
        +-- reserve direct items
        +-- active graph items
        +-- reserve graph items
        +-- malformed/duplicate dispositions
        +-- expansion-scope record
        +-- coverage vector
        +-- replay identity
        |
        v
bounded reasoner handoff and Decision Trail
        |
        +-- apply/reject/park per active pressure item
        +-- exact portfolio/policy/substrate custody
```

This is deliberately not one “graph system” object. The substrate owns facts,
direction, and lineage. The policy owns allocation rules. The planner applies
the policy. The handoff renders a bounded view. The Decision Trail owns process
and disposition custody.

### Illustrative planner interface

Names are provisional; responsibilities are binding.

```python
result = PressurePortfolioPlanner.plan(
    substrate=snapshot,
    direct_candidates=canonical_candidates,
    policy=ConstitutionalOneHopRelationSlotsV1(),
    bounds=PortfolioBounds(
        direct_active_max=6,
        antagonist_active_max=1,
        tension_active_max=1,
        ally_active_max=1,
    ),
)
```

The planner receives already-canonical IDs. It performs no slug repair,
semantic merge, source discovery, compilation, provider call, or embedding
generation.

### Illustrative graph-item custody

```python
@dataclass(frozen=True)
class GraphPressureItem:
    target_model_id: CanonicalModelId
    disposition: Literal["active", "reserve"]
    admission_path_ref: RelationPathRef | None
    all_exact_provenance_path_refs: tuple[RelationPathRef, ...]
    provenance_path_count: int
    path_coverage_state: CoverageState
    policy_id: str
    policy_version: str
```

An admission path explains which exact relation won a bounded slot. The full
path-reference set explains every exact path enumerated under this policy. The
two concepts must not be collapsed.

### Illustrative expansion-scope custody

```python
@dataclass(frozen=True)
class ExpansionScope:
    traversal_direction: Literal["outgoing"]
    max_hops: Literal[1]
    seed_policy: Literal["direct_active_only"]
    expanded_seed_ids: tuple[CanonicalModelId, ...]
    unexpanded_direct_reserve_ids: tuple[CanonicalModelId, ...]
    unexpanded_reason: str
    enumerated_relation_count: int
    unique_target_count: int
    coverage_state: CoverageState
```

This makes it impossible for a later reader to confuse “not enumerated because
the direct candidate was reserve” with “enumerated and no relation existed.”

## Functional requirements

### P-1 — Named and versioned policy

Every portfolio declares a stable policy ID, policy version, caps, traversal
direction, maximum depth, seed policy, ordering rule, and deduplication rule.

### P-2 — Typed substrate input

The planner consumes the read-only substrate boundary from the graph-substrate
PRD. It does not open graph files or construct a second relation index.

### P-3 — Direct-candidate custody

Every direct input receives one explicit state: active, reserve, duplicate,
malformed, missing source, or another enumerated schema state. Original lane
and provider-authored interpretation provenance remain visible.

### P-4 — Explicit seed scope

The portfolio records that v1 expands direct-active candidates only. It stores
the expanded seed IDs and unexpanded direct-reserve IDs separately.

### P-5 — Directional traversal

V1 uses only source-authored outgoing one-hop relations. Incoming reference is
not a reverse relation. No transitive endpoint edge is created.

### P-6 — Active and reserve graph custody

Every enumerated graph target receives an active or reserve disposition. A
capacity miss must not become absence or semantic rejection.

### P-7 — Convergence preservation

For each graph target, preserve all exact relation paths enumerated inside the
declared scope, including paths that did not win the active slot. Duplicate
path identities may be removed mechanically; distinct relation identities may
not be merged.

### P-8 — Stable references

Portfolio items reference stable directed relation IDs and immutable substrate
release identity. Compiled array offsets may be recorded as diagnostic
pointers, but cannot serve as the sole stable relation identity.

### P-9 — Boundedness

Candidate, path, serialization, and token limits are explicit. If any limit is
reached, the result declares the affected layer `partial` and records the exact
omission reason. Truncation never masquerades as completed-zero.

### P-10 — Reconsideration disposition

Apply, reject, and park link to the exact active portfolio-item identity,
policy version, substrate release, and reasoner handoff. Rejection does not
delete the original pressure or its provenance.

### P-11 — Coverage vector

At minimum, keep separate coverage states for:

- direct input custody;
- substrate load;
- seed expansion;
- relation enumeration;
- active/reserve allocation;
- path aggregation;
- bounded serialization;
- reasoner handoff;
- reconsideration disposition.

Each uses `complete`, `completed_zero`, `partial`, `failed`, or `missing` with
reason and counts where relevant. Do not reduce them to one score.

### P-12 — Preserve the V60 boundary

V60 affordance enrichment and graph portfolio admission remain separate
systems with different evidence and authority. The planner may expose the
canonical IDs needed for a future paired experiment, but this PRD neither
feeds graph-only candidates into V60 nor merges V60 material into graph
relation custody.

### P-13 — Replay and observability

A provider-free replay records substrate release identity, canonical direct
inputs, policy and bounds, deterministic output, and exact divergence from the
frozen v1 characterization. Logs and reports contain hashes and safe metadata,
never secrets or private conversation content by default.

## Non-functional requirements

- Deterministic: identical substrate, candidates, policy, and bounds produce
  byte-identical planner output.
- Provider-free: compilation, planning, replay, and structural validation make
  zero network or model calls.
- Immutable-input: the planner cannot mutate the substrate snapshot or graph
  artifacts.
- Fail-closed on shape: malformed identity, relation type, or direction is
  rejected explicitly.
- Fail-honestly on availability: partial, failed, and missing graph inputs do
  not collapse into empty success.
- Backward-characterizable: the existing v1 output can be frozen before any
  prospective schema addition.
- Frozen-evidence safe: no historical experiment, prompt, runner, output, or
  hash-locked corpus is rewritten.

## Acceptance gates

### Gate A — Frozen v1 characterization

- current implementation has provider-free fixtures covering empty, one-seed,
  duplicate-target, convergent-path, reserve-overflow, malformed, partial, and
  missing substrate cases;
- fixtures freeze exact active identities, order, active/reserve counts,
  admission edges, serialized bounds, and current hashes;
- the 163-window corpus sweep is reproducible and its inventory is stored as
  local structural evidence;
- no runtime code or output schema changes in this gate.

### Gate B — Planner extraction with exact behavior parity

- planning logic consumes the approved substrate snapshot;
- no planner path opens `knowledge_graph.json` or
  `relationship_graph.json` directly;
- all frozen v1 active identities, order, admission edges, reserve identities,
  bounds, serialized output, and current output hashes remain exact;
- existing R2 and constitutional graph-survival tests remain green;
- any temporary adapter has one owner and an explicit deletion milestone.

### Gate C — Prospective custody schema v2

- `expansion_scope` distinguishes expanded active seeds from unexpanded direct
  reserve;
- all enumerated exact provenance paths are preserved for every active and
  reserve graph target;
- the convergent-path fixture retains one admission path and multiple exact
  provenance paths;
- the 163-window sweep accounts for the previously outer-unpreserved 808 exact
  paths;
- active identities and order remain equal to v1 even though the prospective
  schema and hash are intentionally new;
- coverage states distinguish completed-zero, partial, failed, and missing;
- the candidate v2 result is not wired into runtime or published as current.

### Gate D — Promotion authorization

Promotion requires a separate founder approval naming:

- the exact candidate schema and hashes;
- the exact runtime callers to migrate;
- compatibility and rollback strategy;
- the frozen regression set;
- the Decision Trail and receipt claim changes;
- zero or separately bounded provider-call authority;
- stop rules.

Passing structural gates does not prove usefulness and does not authorize
promotion automatically.

## Proposed PR sequence

### PR 0 — Characterize and freeze current v1

Add provider-free policy fixtures, the deterministic corpus sweep, a named
behavior contract, and the coverage/nonclaim note. Change no runtime behavior.

Exit condition: another machine can reproduce exactly what current v1 admits,
reserves, omits from expansion, and drops from outer path custody.

### PR 1 — Extract planner behind the substrate reader

Move existing allocation behavior behind `PressurePortfolioPlanner` and the
approved immutable substrate API. Preserve exact current bytes and hashes.
Remove or time-bound duplicate graph scans used by this policy.

Exit condition: structural refactor with exact behavior parity.

### PR 2 — Add prospective portfolio-custody schema v2

Add explicit seed scope, unexpanded-reserve state, complete convergent-path
references, policy identity, and coverage vector to a candidate-only result.

Exit condition: every bounded one-hop path is traceable; active identities and
order remain unchanged; prospective output is not live.

### PR 3 — Promote only after separate review

If authorized, migrate the bounded reasoner handoff, receipt, and Decision
Trail to the reviewed v2 custody contract with an explicit compatibility
period and rollback path.

Exit condition: live migration is independently reviewed and authorized. This
PRD does not itself authorize PR 3.

## Testing strategy

### Unit tests

- stable policy identity and serialized bounds;
- direct round-robin parity;
- outgoing-only one-hop enumeration;
- relation-type slot allocation parity;
- lexicographic ordering parity;
- duplicate target and duplicate path handling;
- all exact convergence paths preserved;
- direct reserve distinguished from expanded completed-zero;
- malformed, partial, failed, and missing states;
- deterministic portfolio serialization and hash;
- no probabilistic selector, embedding service, or provider route invoked.

### Integration tests

- current pipeline fixtures produce the same v1 active and reserve identities;
- R2 constitutional graph survival stays before verifier gating;
- active graph pressure reaches the bounded reconsidering reasoner;
- apply/reject/park links to exact pressure-item identity;
- current token caps and receipt bounds remain enforced;
- substrate artifact absence and partial authoring lineage are separately
  represented;
- prospective v2 candidate does not alter the live handoff.

### Corpus checks

- replay all deterministic 60-ID windows;
- reconcile every enumerated path to a stable substrate relation ID;
- account for every active and reserve target inside the declared scope;
- report convergence distribution without claiming that higher convergence is
  better;
- report capacity effects separately from semantic or source-anchor coverage.

### Full handoff checks

Run the smallest relevant tests while iterating, then the AGENTS.md full suite,
JSON validation, and `git diff --check` before a PR handoff. Preserve historical
hashes and explain any changed test count.

## Risks and mitigations

### Risk: custody fields are mistaken for a better selector

Mitigation: keep active identities/order unchanged in v2 and state explicitly
that more provenance is not proof of relevance.

### Risk: a refactor accidentally moves graph pressure behind a verifier

Mitigation: retain ordering assertions proving constitutional graph survival
occurs before probabilistic applicability filtering.

### Risk: all-path preservation becomes unbounded

Mitigation: preserve all paths only inside the declared bounded one-hop scope;
record partial state if an explicit safety bound is reached.

### Risk: incoming references are silently reversed

Mitigation: v1 calls only `relations.outgoing()`. Any future incoming view uses
an incident-reference type that preserves authored direction.

### Risk: schema work creates a parallel portfolio system

Mitigation: characterize current code, extract it once, and generate v2 as a
prospective serialization of the same planner result. Do not maintain two
allocation engines.

### Risk: the planner swallows substrate lineage problems

Mitigation: carry the substrate coverage vector by reference and add planner-
specific states rather than rewriting substrate truth.

### Risk: V60 is merged because both layers mention models

Mitigation: keep graph-relation custody and V60 affordance custody separate.
Test any future pairing as a named experiment with its own authority.

## Explicit non-goals

This PRD does not authorize or claim:

- incoming-edge pressure;
- reverse-edge creation;
- two-hop or unrestricted traversal;
- graph-database adoption;
- community detection or Microsoft-style global GraphRAG;
- causal inference from relation paths;
- affinity-based constitutional admission;
- activation-similarity constitutional admission;
- graph-centrality ranking;
- LLM-based relevance or applicability filtering before reconsideration;
- changing the six-direct or three-relation active caps;
- expanding direct-reserve neighborhoods;
- feeding graph-only active models into V60;
- model-source semantic review or relation rewriting;
- Atlas, frontend, Teacher, or Observatory integration;
- provider calls, live-run evaluation, runtime promotion, or usefulness claims.

## Parked research opportunities

These are experiments to design only after custody and replay gates pass. They
are not assumed improvements.

### O-1 — Direct-reserve neighborhood inventory

Measure what relation paths are never enumerated because v1 expands
direct-active seeds only. Keep this offline and distinguish capacity exclusion
from semantic absence.

### O-2 — Incoming-reference view

Test whether showing “models that point to this seed” adds distinct pressure
when direction is preserved. Never present this as the reverse authored
relation.

### O-3 — Bounded two-hop path view

Test explicit paths with per-seed and per-relation caps. Do not synthesize an
edge between the endpoints. Compare novelty, duplication, contradiction,
disposition, and cognitive load as a vector.

### O-4 — Deterministic portfolio rotation or diversity

Test whether the lexicographic v1 allocation repeatedly privileges the same
targets. Any alternative must stay deterministic, capacity-bounded, and free
of silent probabilistic deletion.

### O-5 — Graph-only candidate and V60 paired handoff

Test whether a graph-only active candidate needs its V60 affordance or explicit
absence record to receive fair reconsideration. Preserve the two provenance
chains and do not make V60 a prerequisite for graph survival.

### O-6 — Human-readable graph projection

After the substrate and portfolio contracts are stable, expose exact direction,
path, source-anchor state, active/reserve state, and apply/reject/park custody
to Atlas or another interface. Interface design remains deliberately outside
this goal.

## Dependencies and decisions

This PRD depends on the graph-substrate PRD resolving one canonical authoring
and compiler authority. The recommended topology is:

```text
this repository owns reviewed authoring + compiler + published substrate
                                    |
                                    v
                 one read-only substrate boundary
                                    |
                                    v
                  one pressure portfolio planner
```

The founder resolved the dependency: this repository is the only supported
authoring, compiler, substrate, planner, and skill authority. No outside
release path remains part of the design.

## Claims this PRD permits

After the prospective gates pass, Lolla may claim only that:

- the current bounded constitutional portfolio policy is explicitly versioned
  and replayable;
- its expansion scope and active/reserve decisions are inspectable;
- every graph path enumerated inside that scope has exact directed custody;
- convergence is preserved as evidence of process, not relevance;
- the planner does not use a probabilistic prefilter to delete graph pressure.

It may not claim that the policy chooses the best models, that graph paths are
causal, that multiple paths make a conclusion true, or that the resulting
answer is more accurate or useful without separate evidence.
