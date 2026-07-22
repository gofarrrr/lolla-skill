# Lolla Published Knowledge-Substrate Read Boundary Result

Date: 2026-07-22
Status: Phase 3 complete provider-free
Provider calls: 0
Runtime graph generation or repair: none
Ranking, active/reserve, prompt, and published-artifact changes: none

## Outcome in plain language

Lolla now has one front door for reading the published graph.

Previously, several parts of the system opened `knowledge_graph.json` or
`relationship_graph.json` independently. Each reader could make its own quiet
assumptions about missing files, identity, direction, and list order. That did
not mean the graph was broken, but it made the system harder to reason about
and easier to drift.

The new boundary reads and validates the publication once, then gives
consumers an immutable snapshot. The snapshot says:

- which exact release is being read;
- whether each required layer is complete, completed-zero, partial, failed, or
  missing;
- which canonical models and directed relations exist;
- the authored source and target of every relation;
- where every model and relation sits in the published files;
- where available authoring and Markdown custody lives;
- which queries are outgoing, incoming-reference, or incident.

It does **not** decide which model is useful, rank a lane, allocate active and
reserve pressure, compile the graph, repair aliases, or call a provider.

## The boundary

The owner is
`engine/system_b/published_knowledge_substrate.py`.

Its shape is deliberately small:

```text
PublishedKnowledgeSubstrate.open(root)
        ↓
load result
  status: complete | completed_zero | partial | failed | missing
  coverage: one state per layer
  issues: exact structural/custody problems
        ↓
immutable PublishedKnowledgeSnapshot
  exact models
  exact directed relations
  release identity
  source and authoring custody
  outgoing / incoming-reference / incident indexes
```

Runtime loading has no path to the compiler, candidate publication, embedding
builder, provider client, alias migration, or semantic repair code.

## Exact publication identity

The checked-in release register is
`data/curation/published_substrate_release.json`.

It names release `lolla-graph-2026-04-21-v1` and validates the exact compact
and rich graph files plus the reconstructed custody inputs. Current load status
is `complete` across all declared layers:

```text
knowledge graph                 complete
relationship graph              complete
model registry                  complete
tendency registry               complete
relation registry               complete
published release identity      complete
release custody inputs          complete
model source custody            complete
relation source custody         complete
```

Hash drift in a published graph artifact is a failed release load. Missing or
invalid supporting custody remains visible as partial or missing; it is not
silently converted into a clean publication.

## Direction is preserved

For a relation authored as:

```text
A → ally → B
```

the boundary exposes:

- `outgoing(A)`: the authored relation;
- `incoming_references(B)`: the same relation, still authored from A to B;
- `incident(A or B)`: a navigation view that retains the original source and
  target.

It never creates `B → ally → A`. An incident consumer may choose to show “the
other endpoint,” but that is its own presentation or ranking policy, not a new
authored edge.

## Stable relation and source custody

Every current relation has:

- a stable ID made from its exact directed triple;
- its source and target canonical IDs;
- its rich-graph source order;
- an exact compiled pointer such as
  `data/relationship_graph.json#/0`;
- its immutable compiled payload;
- an authoring record, family, and item pointer;
- a Markdown source path, SHA-256, and byte count;
- its truthful source-anchor state and exact character span when available.

Exact model lookup does no display-name or slug repair. For example,
`commitment-bias` resolves and `Commitment Bias` does not. Historical identity
migrations stay in the authoring lifecycle register rather than becoming
silent runtime aliases.

## Consumers migrated

The live pipeline opens one snapshot and shares it with consumers. The
following paths no longer parse the graph publication independently:

| Consumer | What the boundary owns | What the consumer still owns |
| --- | --- | --- |
| Live pipeline | One validated snapshot and exact legacy payload copies | Lane orchestration and existing runtime policy |
| `RelationGraph` | Directed rich relations and canonical identity | Existing affinity, fan correction, caps, and activation tiebreaker |
| `TendencyCatalog` | Published tendency records | Existing alias lookup and routing-overlay disagreement behavior |
| `PressureRouter` | One shared snapshot | Existing route assembly |
| V60 display-name join | Exact canonical model records | Existing V60 selection and transaction policy |
| Authority/stress workspace builders | Validated publication payload and artifact paths | Their existing default-off experimental workspace output |
| `run_route.py`, `run_triage.py`, `run_companion.py` | Validated publication payload | Their existing legacy standalone output policies |

The three standalone helpers remain time-bounded legacy adapters and will be
reviewed during the Phase 6 skill-entrypoint consolidation. Their current
ranking and incident behavior was preserved rather than redesigned inside a
reader migration.

## Direct graph references that remain

Not every filename reference should be deleted. The machine consumer register
at `docs/evals/lolla-published-substrate-consumer-register-v1.json` classifies
all remaining engine references:

- the one published reader;
- the candidate compiler and compiler-side authoring validators;
- provider-free custody and research-packet evaluators that intentionally
  accept explicit fixture paths;
- the parked Teacher product projection;
- generated workspace output names;
- source-reference strings emitted by the current pressure planner.

These are not hidden alternate live readers. A regression test fails if a new
engine graph filename reference appears without a declared disposition.

## Object-equivalence result

The first migrated consumer was `RelationGraph`. A provider-free equivalence
test reconstructs its former adjacency map directly from the published rich
graph, then compares that with the boundary-backed loader.

Result:

```text
relation neighbor records: exact object equality
source and neighbor order:  unchanged
degree counts:               unchanged
ranking constants:           unchanged
activation tiebreaker:       unchanged
```

The live pipeline also loads the complete 222-model / 1,358-relation snapshot
with a boundary object that raises if any provider method is called. Loading
succeeds without invoking it.

## Verification

Provider-free checks completed successfully:

```text
boundary status/direction/custody/state tests: pass
RelationGraph exact object-equivalence test:  pass
live pipeline no-provider load test:           pass
consumer disposition register tests:           pass
lane/routing/activation regression group:      79 passed, 93 subtests passed
pipeline/skill contract smoke group:           50 passed
```

The full repository suite remains the final handoff gate after Phases 4–6.

## What this result does not prove

- A valid relationship is not necessarily semantically correct.
- An incoming reference is not a reciprocal relation.
- An incident view is not permission to traverse bidirectionally in the live
  pressure policy.
- Shared loading is not shared ranking.
- Complete custody is not evidence of real-user usefulness.
- No two-hop, global, graph-database, Atlas, Teacher, or interface opportunity
  has been activated.

## Next causal step

Extract the exact current constitutional pressure allocation into one named,
versioned planner that consumes this snapshot. The Phase 4 proof must show that
active and reserve identities, order, admission edges, bounds, source refs,
hashes, and pre-verifier survival remain exactly unchanged.
