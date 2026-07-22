# Lolla Prospective Complete Portfolio Custody Result

Date: 2026-07-22
Status: Phase 5 complete provider-free; candidate-only
Provider calls: 0
Live reasoner, receipt, and Decision Trail connections: none
Live active/reserve output change: none

## Outcome in plain language

Lolla can now show every path it actually inspected under the current policy,
without expanding the policy or changing what reaches the reasoner.

The live V1 portfolio already preserved all direct candidates and all graph
targets as active or reserve. Its outer active graph item, however, carried
only the relation that won admission. When several direct-active seeds pointed
to the same target, the other exact paths were counted inside a lower ledger
but disappeared from the outer item.

The candidate-only custody projection separates two ideas that were previously
easy to confuse:

- **admission path** — the one relation that caused a target to win its active
  antagonist, tension, or ally slot;
- **provenance paths** — every exact outgoing one-hop relation from an expanded
  direct-active seed to that target.

It also states that direct-cap reserve was **not expanded**. It never represents
that unperformed work as an empty neighborhood.

## Candidate-only boundary

Owner:
`engine/system_b/prospective_portfolio_custody.py`

Schema:
`docs/evals/lolla-prospective-portfolio-custody-schema-v1.json`

Corpus result:
`docs/evals/lolla-prospective-portfolio-custody-baseline-v1.json`

The output hard-codes these boundaries:

```text
candidate_only:            true
live_reasoner_connected:   false
live_receipt_connected:    false
decision_trail_connected:  false
provider_calls:            0
```

The live pipeline does not import this module.

## Exact declared scope

Every candidate artifact declares:

```text
expansion seed rule:  direct_active_only
expanded seeds:       the exact six direct-active IDs, in order
unexpanded reserve:   every direct-cap reserve ID
direction:            outgoing authored relations
hop depth:            1
relation types:       antagonist, tension, ally
policy identity:      lolla.constitutional_pressure_planner 1.0.0
substrate identity:   lolla-graph-2026-04-21-v1
```

An unexpanded direct-reserve row carries:

```text
disposition:          direct_capacity_reserve_unexpanded
neighborhood_status: not_enumerated_by_current_policy
neighborhood:         null
```

`null` matters here. An empty list would claim that the system looked and found
nothing. The truthful state is that current V1 did not look.

## Every enumerated graph target has a disposition

Each target reached from the six expanded seeds is exactly one of:

- `active_graph_slot`;
- `reserve_graph_capacity`;
- `reserve_duplicate_of_direct_active`.

Reserve is capacity or duplication custody, not semantic rejection. No target
is omitted merely because it did not win an active slot.

Every exact path contains:

- stable directed relation ID;
- source and target canonical model IDs;
- relation type and outgoing direction;
- hop count `1`;
- rich-graph source order and compiled pointer;
- authoring-file, family, and item pointer;
- Markdown source identity and truthful source-anchor state;
- an exact character span when one is mechanically available.

## Admission remains separate from provenance

For an active target, the artifact carries both:

```text
admission_path:    the existing V1 winning relation
provenance_paths:  every exact in-scope relation to the target
```

The admission path must also appear among the provenance paths. Multiple paths
do not increase the target's authority, imply relevance, or create a new
relation between endpoints. They only show the topology the planner actually
encountered.

## Complete and partial remain different

Without a safety cap, every exact path is serialized and the path layer is
`complete`.

The builder also accepts an explicit `max_serialized_paths` safety bound. If
the bound is lower than the exact in-scope count, it does not silently truncate:

```text
status:                partial
exact_path_count:      full mechanically known count
serialized_path_count: paths actually present
omitted_path_count:    exact difference
partial_reason:        max_serialized_paths_safety_bound
```

Active identities and order are still checked against the live V1 output even
in a partial custody artifact.

## Exhaustive corpus result

The same 163 sorted 60-model windows used by the frozen Phase 0 baseline were
rebuilt through the published snapshot, the versioned planner, and the
candidate custody projection.

| Measure across 163 windows | Result |
| --- | ---: |
| Enumerated graph targets | 3,723 |
| Exact in-scope paths | 6,025 |
| Serialized paths | 6,025 |
| Omitted paths | 0 |
| Active graph targets | 489 |
| Active-target additional non-admission paths | 808 |
| Previously unrepresented additional paths from Phase 0 | 808 |
| Active graph-slot dispositions | 489 |
| Direct-active duplicate reserve dispositions | 90 |
| Graph-capacity reserve dispositions | 3,144 |
| Live active identity/order mismatches | 0 |

All 808 paths that the Phase 0 audit identified as lost from outer active items
are now accounted for in the candidate schema. This is a custody result, not a
usefulness result.

## Provider-free inspection command

One candidate artifact can be built from an explicit JSON array of model IDs or
candidate objects:

```bash
PYTHONPATH=. python3 scripts/evals/build_prospective_portfolio_custody_candidate.py \
  --candidate-ids-json /path/to/candidate_ids.json \
  --output /path/to/candidate_custody.json
```

The command requires an explicit output path, writes no live artifact, performs
no provider call, and reports whether active identity/order stayed equal.

The corpus register can be revalidated with:

```bash
PYTHONPATH=. python3 scripts/evals/build_prospective_portfolio_custody_baseline.py \
  --validate-only
```

## Verification

Provider-free checks completed successfully:

```text
complete scope/disposition/path test:       pass
unexpanded reserve truthfulness test:       pass
admission vs all-provenance test:           pass
partial safety-bound accounting test:       pass
tamper-evident candidate hash test:          pass
163-window 808-path corpus reconciliation:  pass
live-pipeline non-import test:               pass
explicit candidate CLI build/revalidate:    pass
Phase 4/5 focused regression group:         18 passed
```

## What did not change or become authorized

- The six direct-active seeds are unchanged.
- Direct reserve remains unexpanded in the live policy.
- Graph direction remains outgoing and hop depth remains one.
- Active relation slots and ordering are unchanged.
- The live reasoner sees the same portfolio as before.
- Apply/reject/park and receipt claims are unchanged.
- Incoming-reference, two-hop, graph-global, motif, V60 graph-active handoff,
  Atlas, interface, Teacher, provider, and real-user experiments remain parked.

## Next causal step

Phase 6 packages what now exists. The existing Lolla skill must point only to
this repository, explain the source → compiler → publication → planner chain in
progressively disclosed references, validate all required files from a clean
checkout, and retain one canonical live workflow. It must not create a second
graph skill or activate this candidate custody schema in live runs.
