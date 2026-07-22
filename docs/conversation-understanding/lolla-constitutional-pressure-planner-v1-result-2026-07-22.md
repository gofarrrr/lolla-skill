# Lolla Constitutional Pressure Planner V1 Result

Date: 2026-07-22
Status: Phase 4 complete provider-free
Provider calls: 0
Live portfolio output change: none
Published graph, prompts, ranking, and disposition semantics: unchanged

## Outcome in plain language

The policy that decides which recalled mental models become active pressure is
now one named component instead of behavior spread between the live wrapper and
an older research ledger module.

The new component does not make the graph “smarter.” It makes the current rule
inspectable and replayable:

```text
Lane 2 recalled candidates
        ↓
keep the first canonical occurrence of each candidate
        ↓
first six become direct-active; overflow remains direct reserve
        ↓
expand outgoing relations from those six seeds only, one hop
        ↓
admit at most one antagonist, one tension, and one ally
        ↓
preserve every other enumerated target in graph reserve
        ↓
send active pressure to reconsideration before verifier interpretation
```

This is the policy Lolla already used. The change gives it an owner, version,
checked-in contract, typed substrate input, and exhaustive replay test.

## Named policy

Owner:
`engine/system_b/constitutional_pressure_planner.py`

Checked-in contract:
`data/curation/constitutional_pressure_policy_v1.json`

Identity:

```text
policy_id:      lolla.constitutional_pressure_planner
version:        1.0.0
contract hash:  sha256:829bd0c086610dafabb09b5c941580efcc511396a3ed8c5d3ea3673e17031b10
```

## Frozen policy, exactly

| Property | V1 value |
| --- | --- |
| Direct-active cap | 6 |
| Expansion seeds | Direct-active only |
| Direction | Authored outgoing relations |
| Hop depth | 1 |
| Graph slots | antagonist, tension, ally |
| Direct ordering | Input recall order represented by zero-padded rank mechanisms |
| Within graph slot | source model ID, then target model ID, ascending |
| Direct deduplication | First canonical input occurrence |
| Graph deduplication | One active target across relation slots |
| Affinity used for admission | No |
| Conversation text used for graph admission | No |
| Probabilistic prefilter | No |
| Provider calls | 0 |

Direct candidates beyond the cap are capacity reserve, not semantic rejects.
Graph targets not selected for one of the three active slots remain graph
reserve. Targets already present in direct-active are recorded as graph/direct
duplicates rather than deleted.

## Inside-out ownership

The boundaries are now explicit:

- the **published substrate** owns exact models, directed relations, release
  identity, and custody;
- the **planner** owns seed scope, caps, order, one-hop traversal, and
  active/reserve allocation;
- the **constitutional survival serializer** owns the existing pressure item,
  source-ref, bounded reserve, portfolio hash, and disposition-skeleton shape;
- the **reasoner** still owns apply, reject, or park;
- the **human** still owns the decision.

The planner does not load a file, compile, access embeddings, call a provider,
merge semantic records, or evaluate whether a candidate applies.

The older `build_direct_ledger()` and `build_graph_ledger()` functions remain
as deterministic low-level ledger primitives used by frozen research tests.
They no longer own the live policy parameters or publication loading, so they
are not a second live planner.

## Canonical live path

The live pipeline now retains the immutable publication snapshot from startup
and calls:

```text
build_constitutional_graph_survival_from_snapshot(...)
```

The older raw-dict entrypoint remains a compatibility adapter for existing
provider-free evaluations and frozen fixtures. Both entrypoints use the same
planner and serializer. A test proves that their complete output objects and
portfolio hashes are equal.

## Pre-verifier survival remains intact

The companion sequence remains:

```text
recall candidates
        ↓
build deterministic constitutional pressure portfolio
        ↓
run probabilistic verification as interpretation telemetry
```

The verifier still cannot delete, reorder, or rank which candidates survive
into the constitutional active/reserve portfolio. The live source-order test
locks this call order, and the portfolio itself continues to declare:

```text
probabilistic_applicability_gate: false
verifier_fields_used_for_survival: []
candidate_deletion: false
```

## Exhaustive replay result

The Phase 0 baseline contains all 163 contiguous sorted 60-model windows over
the canonical 222-model registry. The snapshot-backed V1 planner replayed every
window and matched the frozen current policy for:

- full portfolio SHA-256;
- direct-active IDs and order;
- direct-reserve count and ID-set hash;
- graph-active IDs, order, selected relation slots, and admission edges;
- graph-reserve count and ID-set hash;
- source-reference and serialized bounds indirectly covered by the full
  portfolio hash.

Result:

```text
windows replayed:             163
portfolio hash mismatches:    0
direct active/order mismatch: 0
graph active/path mismatch:   0
reserve identity mismatch:    0
```

Because the entire existing portfolio object is equal, the disposition ledger
skeleton still links apply/reject/park to the same pressure IDs in the same
order.

## Verification

Provider-free checks completed successfully:

```text
policy contract and identity tests:          pass
no-loader/compiler/embedding/provider test: pass
snapshot vs raw adapter full equality:       pass
163-window frozen policy replay:             pass
pre-verifier call-order lock:                pass
planner-specific suite:                      5 passed
constitutional/pipeline regression group:   39 passed
```

## What this does not prove or authorize

- The six direct-active candidates are not necessarily the best six.
- One active relation per type is not a semantic optimality claim.
- An outgoing one-hop path is not evidence of relevance, correctness, or
  causation.
- Direct reserve remains unexpanded in V1.
- Active graph items still carry one admission path rather than every
  convergent exact path.
- Incoming-reference, two-hop, graph-global, Atlas, interface, provider, and
  real-user experiments remain outside this phase.

## Next causal step

Phase 5 can now improve **custody without changing policy**. It will build a
candidate-only portfolio view that explicitly records direct-active seed scope,
unexpanded direct reserve, the admission path, and every exact one-hop path
from an expanded seed to each graph target. The live portfolio and reasoner
input remain unchanged.
