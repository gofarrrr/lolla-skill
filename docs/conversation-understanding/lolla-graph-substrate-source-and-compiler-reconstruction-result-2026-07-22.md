# Lolla Graph Substrate Source and Compiler Reconstruction Result

Date: 2026-07-22
Status: Phases 0–2 complete provider-free; published runtime artifacts unchanged
Provider calls: 0
Embedding calls or rebuilds: 0
Runtime, prompt, ranking, portfolio, Atlas, and interface changes: none

## Outcome in plain language

This repository can now explain where the current graph came from and rebuild
it without the retired worktree.

Before this work, Lolla had two healthy published graph files, but part of the
reviewed material and compiler inputs behind them existed only in an old local
working snapshot. That made the graph usable but not independently
reconstructable from a clean clone.

The repair did not invent new relationships, expand traversal, or replace the
existing graph system. It recovered the exact reviewed inputs into their
existing repository locations, deepened the existing compiler, and made that
compiler write only to an explicit candidate directory. A candidate build now
reconstructs both published graph files byte-for-byte.

The simple ownership chain is now:

```text
222 repository Markdown sources
        ↓
repository-local reviewed curation and overlays
        ↓
one deterministic candidate compiler
        ↓
compact knowledge graph + rich relationship graph
        ↓
exact comparison with the published runtime files
```

The next problem is different: live consumers still need one strict read
boundary, and the constitutional pressure planner still needs to be separated
from file loading without changing its policy. Those are Phases 3–5.

## Falsifiable question and result

> Can a checkout with no access to another worktree validate the current
> authoring set and deterministically reconstruct candidate graph artifacts
> without reading the published artifacts as compiler input?

**Result: yes.** Repository-local validation succeeds after the recovery input
is removed. The compiler refuses absent inputs, refuses an implicit output
directory, refuses the published data directory, makes no provider call, and
produces byte-identical candidate graph artifacts on repeated builds.

This result establishes custody and reproducibility. It does not establish
that every curated relation is semantically correct or useful.

## Phase 0 — repository authority and frozen baseline

The active repository no longer points to another project or machine-specific
source directory:

- canonical mental-model Markdown defaults to `data/model_sources/`;
- source and affordance manifests record repository-relative provenance;
- extraction-packet assembly requires the repository source rather than
  copying from a private location;
- current Observatory ownership text and tests use repository-local language;
- a repository-authority validator scans active files for retired-workspace
  dependencies and records any explicitly frozen exception;
- a deterministic baseline records graph counts, artifact identities, current
  pressure selection, seed scope, and convergent-path loss.

The baseline records:

| Measure | Result |
| --- | ---: |
| Canonical models | 222 |
| Rich directed relations | 1,358 |
| Allies | 523 |
| Antagonists | 344 |
| Tensions | 491 |
| Compact graph edges, including tendency links | 1,742 |
| Deterministic 60-model portfolio windows | 163 |
| Graph-active selections | 489 |
| Active selections with multiple exact seed paths | 265 |
| Additional exact paths absent from the outer active item | 808 |

One old absolute-path metadata value remains only inside the immutable V60
compiled artifact `data/compiled/model_affordances/affordances_v60.json`, whose
SHA-256 is locked as
`4dea740ecf71894a8b56146502983c4d3e448f24a6628a8430a445b3c47bedc8`.
It is classified as inactive historical evidence, not an active dependency.
Its prospective retirement belongs to the final packaging phase so historical
evidence is not silently rewritten.

## Phase 1 — exact relation authorship and source-anchor truthfulness

The exact recovered authoring identity is now repository-local:

```text
active records:       222
active record bytes:  1,243,714
record-set SHA-256:   a779626577a3f373a6882b68f5c0621e3cc2fb62935c13b3421ca2b2ca2ca3cd
authored relations:   1,358
```

Every published rich relation resolves to exactly one active authored record.
The active relation directory is still
`data/curation/relation_semantics/`; no second relation registry was created.

The two legacy identity records are preserved but mechanically excluded:

| Historical identity | Current canonical identity | Runtime aliasing |
| --- | --- | --- |
| `commitment-and-consistency-bias` | `commitment-bias` | forbidden |
| `representativeness-bias` | `representativeness-heuristic` | forbidden |

The new source-anchor register does not pretend that every `source_quote` is a
literal source location. It classifies all 1,358 relations mechanically:

| Source-anchor state | Count | Meaning |
| --- | ---: | --- |
| `exact_span` | 605 | The excerpt is an exact character span in the declared Markdown source |
| `normalized_excerpt` | 14 | It matches only after whitespace collapse and case-folding |
| `synthesized_or_multi_span` | 0 | Reserved for an explicit future human declaration; never guessed by code |
| `unresolved` | 739 | Source and excerpt exist, but no mechanical match was found |
| `missing` | 0 | Source or excerpt is unavailable |

Each row retains a stable directed relation identity, authoring-file and item
pointer, compiled rich-graph index, source-file identity, source order, and any
exact character span. An unresolved anchor is a review state, not evidence that
the relationship is false. An exact span is provenance, not proof that the
relationship is wise.

## Phase 2 — one candidate compiler

The existing `KnowledgeCompiler` is now the single repository-local compiler.
The repair supplied its previously absent declared inputs instead of building a
parallel compiler:

- 222 active operational-curation records;
- 222 active intervention-semantic records;
- 222 active relation-semantic records;
- 51 reframing files;
- 14 prerequisite files;
- 16 structural-coverage files;
- the two tendency-semantic source files;
- explicit identity migrations and inactive-record dispositions.

One historical custody defect was found while comparing candidate and
published bytes. A later reviewed wording change for the `checklists` model had
been applied directly to the compiled graph but not carried back to its
curation record. Git history identified the exact reviewed sentence, which was
restored to the repository-local curation input. No new wording was generated.

The compiler contract now requires:

- an explicit candidate output directory;
- complete repository-local authoring inputs;
- no compile-from-published-output fallback;
- no write to `data/knowledge_graph.json` or
  `data/relationship_graph.json`;
- no automatic promotion;
- a deterministic compilation date and mode from the checked-in contract;
- input and output identities, counts, coverage, and published comparisons in
  the candidate manifest.

Two independent candidate builds are byte-identical. They reconstruct:

| Artifact | Bytes | SHA-256 | Published comparison |
| --- | ---: | --- | --- |
| `knowledge_graph.json` | 2,129,575 | `5689b79868339ce9221b799eac88870a6053b69a67ba3aaef3f2ba5cd62efdae` | byte-identical |
| `relationship_graph.json` | 1,263,715 | `89808c4585498f3880b4d7fa0110d64cd46f7acff312c0870fc6cb9a97e752cf` | byte-identical |

The candidate manifest defines `complete`, `completed_zero`, `partial`,
`failed`, and `missing` separately. Current declared compiler layers are
complete.

The local activation-embedding check opens `data/embeddings.db` read-only and
compares every activation-condition identity, text, and content hash:

```text
status:                 current
expected records:       867
observed records:       867
current records:        867
missing / extra / stale: 0 / 0 / 0
automatic rebuild:      false
provider calls:         0
```

Tests also preserve `missing`, `stale`, and `failed` as distinct outcomes. No
embedding was generated or updated.

## What did not change

- Published graph bytes did not change.
- The runtime does not use candidate output.
- The active/reserve pressure portfolio did not change.
- Lane ranking, one-hop direction, caps, prompts, and apply/reject/park did not
  change.
- No graph database, MCP layer, community detection, global GraphRAG search,
  incoming-edge expansion, or multi-hop traversal was added.
- V60 remains a separate semantic layer.
- Atlas, frontend, Teacher, Observatory features, and product claims remain
  outside this work.

## Verification

Representative provider-free checks completed successfully:

```text
relation authoring and source-anchor validation: pass
compiler-input manifest validation:              pass
two candidate builds and published comparison:   pass
embedding current/stale/missing/failed tests:     pass
graph baseline and repository-authority tests:    pass
targeted graph reconstruction suite:              19 passed
```

The full repository suite remains a handoff gate after all planned phases, not
evidence claimed by this intermediate result.

## Next causal step

Build one immutable **published-substrate read boundary** and migrate existing
live consumers to it by replacement. That boundary will own file validation,
canonical identity, authored direction, exact relation IDs, source and
authoring pointers, release identity, and availability states. Lane selectors
and the pressure planner will keep their own ranking and admission policies.

The falsifiable Phase 3 question is:

> Can a real provider-free graph consumer stop parsing graph files directly
> and produce exactly the same result through one strict substrate snapshot?
