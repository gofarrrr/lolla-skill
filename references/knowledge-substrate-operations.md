# Knowledge-substrate operations

Load this reference only when maintaining, validating, or proposing changes to
Lolla's 222-model source, relationship graph, compiler, published read boundary,
constitutional pressure planner, or prospective portfolio custody. It is not an
extra runtime step and does not authorize provider calls or graph expansion.

## The ownership chain

```text
222 canonical Markdown files
  + reviewed model and relationship curation
  + explicit source-anchor and compiler-input manifests
  -> deterministic candidate compiler
  -> published knowledge_graph.json + relationship_graph.json
  -> one immutable published-substrate snapshot
  -> one versioned constitutional pressure planner
  -> active pressure + reserve
  -> reasoner applies, rejects, or parks active pressure
```

Each layer has one job:

- Markdown owns the available source prose for a mental model.
- Reviewed curation owns authored operational and relationship meaning.
- Manifests own file identity, hashes, coverage, and release custody.
- The compiler owns deterministic projection into candidate graph files. It may
  not promote or overwrite the published files.
- The published-substrate reader owns exact canonical identity, authored edge
  direction, immutable indexes, and load-state reporting. It does not compile,
  repair aliases, rank, or call a provider.
- The constitutional planner owns the existing direct cap, outgoing one-hop
  expansion, relationship slots, ordering, deduplication, and reserve policy.
- The reconsidering reasoner owns apply/reject/park. The human owns the
  decision.

## What the current graph does

The published substrate contains 222 canonical models and 1,358 rich directed
relations. A relation is read in its authored direction. Incoming-reference
queries may show an edge that points at a model, but they do not reverse it.

The live constitutional planner is deliberately bounded:

- up to six direct active candidates;
- only direct-active seeds are expanded;
- only authored outgoing relations are traversed;
- traversal depth is exactly one hop;
- graph slots are considered in antagonist, tension, then ally order;
- deterministic ordering and deduplication select active items and preserve the
  rest as reserve;
- no affinity score or probabilistic applicability filter may silently remove
  graph pressure before the reconsidering reasoner sees the active set.

This is not GraphRAG over arbitrary documents. The nodes are curated reasoning
lenses and the edges are pressure relationships, not extracted real-world
entities and causal facts. A reachable path is a reason to inspect a possible
connection, not proof that the connection is relevant or true in the user's
situation.

## Provider-free validation

From the repository root, run the complete packaged-readiness check:

```bash
PYTHONPATH=. python3 scripts/evals/validate_self_contained_skill.py --validate-only
```

That command performs no provider or embedding calls. It checks the skill
structure and its named runtime files, repository-local source custody, relation
and compiler-input manifests, the strict published snapshot, byte-equivalent
candidate compilation in a temporary directory, and exact replay of the
checked-in constitutional pressure baseline.

For a narrower compiler check:

```bash
candidate_dir="$(mktemp -d)"
PYTHONPATH=. python3 scripts/product/build_graph_substrate_candidate.py \
  --output-dir "$candidate_dir"
PYTHONPATH=. python3 scripts/product/build_graph_substrate_candidate.py \
  --output-dir "$candidate_dir" --validate-only
```

The candidate directory is disposable. Successful equivalence does not promote
it and does not authorize replacement of either published graph file.

The source and compiler manifests can also be checked independently:

```bash
PYTHONPATH=. python3 scripts/product/adopt_relation_semantics_authoring.py --validate-only
PYTHONPATH=. python3 scripts/product/adopt_graph_compiler_inputs.py --validate-only
PYTHONPATH=. python3 scripts/evals/validate_repository_local_authority.py --validate-only
```

## Published versus prospective behavior

The current live policy is frozen in
`data/curation/constitutional_pressure_policy_v1.json`. The richer complete-path
custody implementation in `engine/system_b/prospective_portfolio_custody.py`
is candidate-only. It proves that every exact bounded one-hop path can be
serialized while preserving current active identities and order. It is not
imported by the live runtime, reasoner, receipt, Decision Trail, Atlas, or
Observatory.

The following remain separate experiments and require their own falsifiable
contract and authorization:

- expanding direct-reserve candidates;
- incoming-reference or multi-hop pressure;
- new ranking, rotation, or graph-slot rules;
- community detection, global graph summaries, or a graph database;
- automatic semantic graph mutation;
- wiring prospective complete-path custody into the live reasoner or receipt;
- provider calls, embedding rebuilds, and usefulness or accuracy claims.

## Change discipline

Start from one question and change one causal boundary at a time. Never compile
at runtime, infer missing source meaning, normalize an exact relation silently,
or let a clean schema stand in for semantic review. Preserve `complete`,
`completed_zero`, `partial`, `failed`, and `missing` as different states.

Historical artifacts can contain inert provenance from an earlier machine or
project. They are not active dependencies. Do not rewrite hash-locked evidence
to make it look newer; keep current instructions, manifests, setup paths, and
readiness checks repository-local, and introduce a prospective version if a
historical artifact must eventually be replaced.
