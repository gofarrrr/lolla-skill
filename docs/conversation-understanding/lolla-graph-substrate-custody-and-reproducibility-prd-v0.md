# Lolla Graph Substrate Custody and Reproducibility PRD v0

Date: 2026-07-22
Status: draft for founder review; planning only
Depends on: Constitution v5, the 2026-07-22 graph audit workbook, and an explicit canonical-authoring-home decision
Provider calls authorized: zero
Runtime, artifact publication, Atlas, frontend, and semantic regeneration authorized by this PRD: none

## Product decision in simple terms

Lolla already has a useful-shaped graph artifact. The first job is not to make
it more intelligent. The first job is to make it honestly ownable:

> A fresh clone should know exactly which Markdown, reviewed curation,
> migrations, compiler rules, and local derived assets produced the graph it
> runs.

Today, the current repository contains the newest runtime and published graph,
but an older relation-curation/compiler path. The complete 1,358-relation
authoring state was located in a temporary local recovery snapshot. The
generated graph was committed; all of its authoring inputs were not.

This PRD establishes one authority chain. It deliberately leaves ranking,
multi-hop traversal, portfolio policy, and interface work alone.

## Falsifiable product question

> Can a fresh clone reconstruct a byte-stable, lineage-declared candidate
> release equivalent to the checked-in 222-model/1,358-relation runtime bundle
> without external absolute paths, provider calls, compile-from-output
> fallback, silent identity repair, or semantic invention?

The PRD is complete only when the answer is mechanically **yes** and every
remaining non-complete lineage state is explicitly dispositioned rather than
hidden.

## Why this is the first graph PRD

Any later graph opportunity depends on knowing what an edge means, which
direction was authored, where it came from, and whether an omission is
intentional. Without that:

- two-hop traversal can amplify an unexplained relation;
- incoming-edge traversal can accidentally reverse meaning;
- Atlas can display a confident source claim it cannot resolve;
- a portfolio can preserve a graph path but not its authoring path;
- a compiler can appear green by reserializing the artifact it was supposed to
  derive;
- a second graph module can quietly become another authority.

Custody is therefore not documentation polish. It is the prerequisite for
trustworthy use of every later graph capability.

## External research fit

The current primary sources do not change that priority:

- Microsoft GraphRAG is an LLM-assisted entity/relationship extraction and
  community-report system for searching document corpora. Lolla is a curated
  graph of reasoning lenses used to introduce inspectable pressure.
- Microsoft describes global community-report search as resource intensive and
  provides several distinct search modes. There is no single graph retrieval
  policy that should be copied into every product.
- the cited ChatP&ID figures compare graph input with raw P&ID images and direct
  smart-file ingestion in one engineering-diagram task; they are not general
  RAG-versus-graph guarantees;
- the cited knowledge-graph scaling paper says size scaling generally applies,
  with local exceptions. It does not say that a smaller model plus a good graph
  wins every time;
- DSPy supports explicit modular pipeline architecture, but its computational
  graph is not a knowledge graph;
- trained relational-memory and KEPLER architectures support the value of
  explicit triples in their evaluated settings, not an automatic benefit for
  Lolla's API-time pressure graph.

The resulting design rule is conservative: adopt explicit identity,
direction, provenance, bounded retrieval modes, and task-specific evaluation;
do not import community detection, a graph database, query-language generation,
or performance claims until Lolla has a matching falsifiable need. The audit
workbook records the dated sources, adopted implications, and rejected
generalizations.

## Constitutional and roadmap boundary

This is a separately reviewed graph-planning lane. It does not silently replace
or authorize the current Constitution roadmap's next eligible Stage 1 Decision
Trail truthfulness review.

No implementation phase begins merely because this PRD exists. The founder
must first approve the canonical authoring home and the implementation plan.
Provider-facing work, runtime integration, publication of new graph bytes, and
future semantic experiments remain separately authorized.

## Current baseline

### What is healthy

- 222 checked-in canonical Markdown sources have a valid source manifest,
  matching hashes and byte counts.
- `data/knowledge_graph.json` has 222 canonical model records, 25 tendencies,
  1,742 edges, 15 prerequisite edges, reframing routing, and structural routing.
- Its 1,358 compact model-relation identities reconcile with the 1,358 rich
  records in `data/relationship_graph.json`.
- The rich graph has unique triples, canonical endpoints, and no self-edges.
- All 523 ally and 344 antagonist edges carry an affinity rationale and
  activation condition. Tensions intentionally do not under the frozen April
  policy.
- The 867 edge-activation embedding records match the 867 enriched activation
  conditions in the current graph.
- V60 demonstrates a stronger local pattern: declared record paths, source
  hashes, exact source-quote validation, deterministic compilation, affordance
  and absence custody.

### What is not healthy

- Local Wave 3 curation is the older 1,302-record snapshot and still says
  preview-only.
- The exact 1,358-record enriched authoring set is uncommitted in another
  repository.
- The two repositories contain divergent compiler/loader implementations.
- The local compiler expects historical root paths rather than the current
  `data/` layout and does not reproduce current enriched relation fields.
- The compiler may use already-compiled output when authoring assets are
  absent; that is validation/reserialization, not reconstruction.
- the local lifecycle register omits the known
  `representativeness-bias -> representativeness-heuristic` migration;
- historical and active identity records are mixed in curation discovery;
- complete current authoring inputs for tendencies, reframing, prerequisites,
  and structural routing are not all evident in this checkout;
- Wave 3 `source_quote` does not function as an exact source locator for much
  of the corpus;
- the live and standalone callers load and interpret raw graph artifacts in
  several ways;
- missing, malformed, intentionally empty, and unavailable graph states can be
  collapsed by some callers into an empty container.

## Desired outcome

At the end of the approved implementation sequence:

1. one repository or one strictly one-way release process owns authoring;
2. the 222 active Wave 3 records are durably present and hash-locked;
3. every historical identity record has an explicit lifecycle disposition;
4. every current relation has one stable directed identity;
5. compiled relation fields resolve to exact authoring records and honest
   source-anchor states;
6. one compiler derives both the compact and rich relation projections from
   the same authoring record;
7. a candidate build never overwrites the published graph by default;
8. two builds from the same frozen inputs are byte-identical;
9. one read-only snapshot boundary validates and indexes the published release;
10. consumers declare outgoing, incoming-reference, or incident-navigation
    semantics explicitly;
11. embedding drift is detected locally and produces `stale`, never an
    automatic provider call;
12. the current graph remains usable without being described as semantic truth
    or complete evidence of usefulness.

## Users and jobs

### Maintainer or coding agent

“When I change or inspect graph data, show me the single source of authority,
the exact inputs, the candidate output, every mismatch, and which actions are
forbidden without new authorization.”

### Runtime consumer

“Give me an immutable, validated snapshot with exact canonical identities,
source-authored direction, stable relation IDs, and missingness states. Do not
make me understand repository layout or parse raw JSON.”

### Evaluator or researcher

“Let me compare bounded graph policies against a frozen snapshot without
rebuilding semantics, changing runtime, or inventing reverse/transitive
relations.”

### Human reviewer

“Let me see whether an edge has exact source custody, normalized/synthesized
support, or an unresolved source-anchor review. Do not call all three
‘source-backed’ without qualification.”

## Product principles

1. **One authoring authority.** Two runtime projections are acceptable; two
   editable semantic authorities are not.
2. **Recover, do not re-invent.** The exact uncommitted authoring state is the
   recovery source. Compiled output is never promoted backward into fake
   authorship without a declared reviewed disposition.
3. **Direction is meaning.** Incoming reference is not a reverse relation.
4. **Paths are chains, not new edges.** No endpoint relation is inferred.
5. **State is a vector.** `complete`, `completed_zero`, `partial`, `failed`, and
   `missing` remain distinct per layer and, where necessary, per field.
6. **Compilation is not runtime.** Runtime load can never trigger generation or
   compilation.
7. **Candidate first, promotion later.** Compilation writes to a prospective
   output directory and compares against the published release.
8. **No semantic healing.** Code can reject malformed identity or custody; it
   cannot repair meaning.
9. **No scalar quality badge.** Clean lineage proves traceability, not wisdom.
10. **Deepen existing boundaries.** Reuse the current compiler, validation,
    source-custody, and V60 patterns behind one owner; do not build a second
    graph stack beside them.

## Required architecture

```text
AuthoringWorkspace
  model sources + manifest
  Wave 1 operational records
  Wave 2 intervention records
  Wave 3 relation records
  canonical-ID migrations and lifecycle inclusion manifest
  tendency/reframing/prerequisite/structural registries
        |
        v
compile_knowledge_substrate(...)
        |
        +-- candidate knowledge_graph.json
        +-- candidate relationship_graph.json
        +-- release manifest + coverage vector
        +-- comparison to current published release
        +-- embedding-staleness report
        |
        v
PublishedKnowledgeSubstrate.open(...)
        |
        +-- models
        +-- tendencies
        +-- relations
        +-- reframing routes
        +-- prerequisites
        +-- structural routes
        +-- source/lineage custody
```

The compiler and loader share schemas, relation identity, migration rules, and
manifest validation. They remain separate entrypoints so a runtime read can
never compile.

### Illustrative read interface

Names are provisional; responsibilities are binding.

```python
opened = PublishedKnowledgeSubstrate.open(repo_root)
snapshot = opened.require_artifact_complete()

model = snapshot.models.require_exact("premortem")
outgoing = snapshot.relations.outgoing(("premortem",))
incoming = snapshot.relations.incoming(("premortem",))
incident = snapshot.relations.incident(("premortem",))
```

Rules:

- `require_exact()` performs no runtime slug repair or alias normalization.
- `outgoing`, `incoming`, and `incident` are separate methods.
- an incident record states whether it is outgoing from or incoming to the
  focus model;
- every relation retains original source, target, type, source record order,
  and compiled record pointer;
- a valid published artifact may load with partial authoring lineage, but the
  partial state remains visible.

### Illustrative relation contract

```python
@dataclass(frozen=True)
class PublishedRelation:
    relation_id: RelationId
    source_model_id: CanonicalModelId
    target_model_id: CanonicalModelId
    relation_type: RelationType
    source_record_index: int

    source_description: str
    composition_affinity: float | None
    affinity_rationale: str | None
    activation_condition: str | None
    source_quote: str | None
    extraction_type: str | None
    confidence: str | None

    compiled_record_ref: ArtifactRef
    relation_curation_ref: ArtifactRef | None
    markdown_source_ref: ArtifactRef | None
    lineage: RelationLineage
```

The stable identity may be derived from the unique directed triple:

```text
mmr::<source_model_id>::<relation_type>::<target_model_id>
```

The compiled array pointer remains separate: position is custody, not identity.

## Functional requirements

### R-1 — Freeze and recover the temporary authoring snapshot

Before copying any relation record:

- produce a checked-in recovery manifest with an opaque recovery ID, each file
  path/hash/bytes, aggregate hash, schema hash, and matching compiled artifact
  hash;
- verify the recovered state still totals 222 active source records and 1,358
  unique canonical relation triples;
- compare every mapped field against the frozen current graph;
- record the recovery as one-time machine-local input, not a path dependency;
- stop if the snapshot changes before the manifest is approved.

No PR may depend on `/Users/marcin/...` at runtime, validation time, or ordinary
fresh-clone compilation.

### R-2 — Choose and enforce one canonical authoring home

```text
this repository = authoring + compiler + published runtime + skill authority
temporary recovery snapshot = one-time read-only input, then unsupported
```

In this topology:

- only the repository curation/compiler copy may be edited as authority;
- the temporary recovery location is never a supported project path;
- transitional adapters have a deletion milestone;
- current runtime never consults a recovery location.

### R-3 — Add an explicit active-input and migration lifecycle manifest

Compiler discovery must not mean globbing every JSON file.

The manifest must declare:

- the 222 active canonical records;
- both known historical migrations;
- historical record lifecycle states;
- whether an old record is superseded, excluded, retained as immutable
  evidence, or intentionally merged under a reviewed migration;
- migration IDs, source and target identities, affected fields, and rationale;
- no cycles and canonical targets;
- no runtime aliasing.

### R-4 — Make enriched relation authorship explicit

Active Wave 3 curation must own the fields already used by runtime:

- directed relation family;
- target model ID;
- authored rationale/tension text;
- affinity tier or existing numeric affinity plus its declared rubric;
- affinity rationale for ally/antagonist edges;
- activation condition for ally/antagonist edges;
- source evidence and extraction status;
- review/lifecycle status.

The frozen tension policy is preserved honestly: the 491 tensions do not gain
synthetic affinity rationales or activation conditions merely for symmetry.
Their one-sentence authored tension remains its own complete or partial source
state under the declared contract.

### R-5 — Add exact source-anchor states without rewriting meaning

Every relation source link must be classified as one of:

- exact source span;
- declared normalized excerpt with named normalization;
- multi-span source synthesis with all supporting spans;
- source-anchor review required;
- source missing/failed;
- completed review with intentionally no exact quote, if the schema permits
  that state.

A prospective exact anchor should include source path, source-file hash, block
or span hash, occurrence identity, and normalization version. Line numbers are
convenience only.

The system must not fuzzy-match a quote and silently mark it exact. Mechanical
validation may identify candidates for human review but may not decide semantic
support.

### R-6 — Replace compile-from-output fallback with truthful blocking

The prospective compiler must refuse to call a copied or reserialized current
artifact a source build.

If any required authoring domain is missing, compilation returns a coverage
vector and a blocked status such as `blocked_incomplete_authoring_inputs`.

Validation of an existing published artifact remains a separate operation and
may succeed independently.

### R-7 — Compile both relation projections from one registry

One active relation record must deterministically produce:

- its compact `knowledge_graph.json` model-relation edge;
- its rich `relationship_graph.json` record.

The compiler must verify exact identity reconciliation between projections,
with explicit type-name mapping for tension records. It must reject duplicates,
noncanonical endpoints, silent drops, and undeclared migrations.

### R-8 — Produce deterministic release and coverage manifests

The candidate release manifest must include:

- frozen release/schema identity;
- all authoring input paths and hashes;
- applied migration ledger;
- record and field coverage vector;
- source-anchor states;
- input and output artifact hashes;
- compiler implementation identity;
- semantic equality/difference report against the current release;
- separate volatile build receipt if a timestamp is needed.

Wall-clock time must not change semantic artifact bytes.

### R-9 — Candidate output is safe by default

- The compiler writes only to an explicit prospective output directory.
- It writes atomically inside that directory.
- It never overwrites `data/*.json` by default.
- Publication is a separate, explicit, reviewed operation and is outside the
  initial PR sequence.
- A candidate mismatch never triggers semantic auto-repair.

### R-10 — Validate activation embeddings locally

For every nonempty activation condition:

- verify a corresponding local edge-activation row exists;
- verify edge identity and stored activation text/content hash;
- identify missing and extra rows;
- mark changed text as `stale`;
- degrade the optional tiebreaker explicitly when stale/missing;
- never call an embedding provider automatically.

### R-11 — Provide one immutable published snapshot boundary

The read boundary owns:

- current `data/` layout resolution;
- strict JSON shape validation;
- canonical endpoint and duplicate validation;
- source order and stable relation identities;
- outgoing, incoming, and incident indexes;
- compact/rich graph reconciliation;
- source-manifest validation;
- authoring-lineage and missingness states;
- artifact and snapshot hashes.

It does not own lane ranking, embeddings, portfolio admission, V60 selection,
interface projection, or semantic applicability.

### R-12 — Migrate consumers by replacement, not permanent layering

Consumers migrate one at a time behind characterization tests.

The migration sequence must:

- open the snapshot once in ordinary runtime;
- adapt the snapshot into a legacy mapping only temporarily;
- remove the direct reader each adapter replaces;
- eliminate the `build -> data` path workaround when no current caller needs
  it;
- preserve relation order and frozen artifact pointers;
- expose missing/failed status through existing run-health/degraded behavior;
- park Atlas consumers until the frontend goal reopens.

### R-13 — Correct documentation only after contracts are true

Current public documentation may describe Wave 3 as fully curated and the
canonical articles as not LLM-generated while also describing LLM-assisted
RAG synthesis. The repaired documentation must distinguish:

- source-book corpus;
- LLM-assisted synthesis;
- human/review status;
- published artifact custody;
- authoring lineage;
- exact versus normalized evidence;
- graph path versus semantic applicability;
- experimental usefulness versus established mechanics.

Historical notes remain immutable; current entrypoints become truthful.

## Coverage contract

The release exposes at least these independent states:

```text
published_artifact
model_source_custody
operational_curation_lineage
intervention_curation_lineage
relation_curation_lineage
relation_source_anchor_coverage
tendency_authoring_lineage
reframing_authoring_lineage
prerequisite_authoring_lineage
structural_routing_authoring_lineage
activation_embedding_alignment
```

Every field uses the existing state vocabulary:

- `complete`
- `completed_zero`
- `partial`
- `failed`
- `missing`

No aggregate `healthy_graph` Boolean or scalar score replaces the vector.

## Acceptance criteria

### Source custody gate

- exactly 222 canonical source IDs and paths;
- every file exists and matches manifest SHA-256 and byte length;
- every compiled model's source filename matches the source manifest;
- no machine-local recovery path is required for ordinary use;
- missing recovery snapshot does not affect validation or candidate
  compilation after recovery.

### Curation and identity gate

- exactly one active Wave 3 record per canonical model;
- 1,358 unique directed active relations;
- every endpoint is canonical after declared compile-time migration;
- both historical migrations and legacy record lifecycles are declared;
- every active curation item is compiled or has an explicit reviewed
  disposition;
- every compiled relation resolves to one active relation item;
- no runtime alias normalization.

### Source-lineage gate

- every exact anchor resolves against the declared Markdown hash;
- every normalized/multi-span relation declares its transformation;
- unresolved source anchors remain partial/missing and cannot be reported as
  exact;
- zero silent fuzzy healing;
- a valid anchor is explicitly not treated as semantic correctness proof.

### Compiler gate

- a complete minimal authoring fixture compiles and round-trips through the
  same published loader;
- the full current authoring workspace compiles twice to byte-identical
  semantic outputs;
- missing authoring inputs block rather than trigger output fallback;
- candidate model count is 222 and rich relation count is 1,358;
- compact and rich relation identities reconcile exactly;
- every current enrichment field matches the frozen release during parity
  migration;
- candidate writes never modify current published artifacts;
- candidate comparison reports every byte/field mismatch.

### Embedding-alignment gate

- all 867 current nonempty activation conditions have exact local rows;
- there are no extra edge rows;
- current text/hashes match;
- changed text yields `stale`, not provider use;
- tension field absence remains intentional under the frozen policy.

### Snapshot gate

- incoming and outgoing methods preserve original authored direction;
- incident view declares focus perspective;
- unknown endpoint, malformed container, duplicate relation, and noncanonical
  endpoint fail explicitly;
- missing, failed, completed-zero, partial, and complete do not collapse;
- snapshot hash and source order are stable;
- current Lane 1/Lane 2/constitutional behavior can be reproduced through
  temporary adapters before their direct readers are removed.

### Documentation gate

- current docs name the one authority;
- current docs distinguish artifact custody from derivational lineage;
- current docs no longer imply every `source_quote` is an exact pointer;
- current docs preserve the “graph introduces pressure, not relevance” rule;
- this AGENTS handoff and docs index are updated only when implementation
  actually changes the restart boundary.

## PR sequence

### PR 0 — Evidence freeze and authority contract

Type: documentation and machine-register contract only.
Runtime impact: none.
Provider cost: zero.

Deliverables:

- publish the audit workbook and this PRD;
- freeze current artifact hashes and the recovery manifest;
- record the exact field-level reconciliation between recovered curation and
  the current published graph;
- define the machine reconciliation-register schema;
- record current coverage vector and nonclaims;
- obtain the canonical-authoring-home decision.

Exit gate: another fresh agent can reproduce every count and understand why no
semantic or runtime change is authorized.

### PR 1 — Recover authoring custody

Type: provider-free data custody and validation.
Runtime impact: none; current graph bytes untouched.

Deliverables:

- recover the exact 222 active enriched relation records into the chosen
  authority;
- preserve recovery hashes and an opaque recovery identity;
- update the active relation schema to represent existing fields;
- declare both identity migrations and legacy lifecycle states;
- add inclusion manifest and validation;
- compare recovered records with the frozen published graph.

Exit gate: every published relation resolves to one recovered active relation
record with zero unexplained field mismatch.

### PR 2 — Deterministic prospective compiler

Type: provider-free compiler/manifest implementation.
Runtime impact: none; candidate output only.

Deliverables:

- consolidate compiler ownership around explicit current `data/` inputs;
- remove output-as-input fallback from the prospective path;
- compile compact and rich projections from one relation registry;
- emit coverage, migration, input/output hash, and comparison manifests;
- add provider-free embedding-staleness validation;
- run duplicate candidate compiles.

Exit gate: two candidate releases are byte-identical and exactly match or
explicitly disposition every difference from the frozen current release.

### PR 3 — Single read-only substrate boundary

Type: provider-free runtime architecture, behavior-preserving.
Runtime impact: intended byte/semantic parity.

Deliverables:

- implement one immutable published snapshot and explicit directional queries;
- migrate one provider-free validator first so the module is not unused;
- migrate ordinary live callers incrementally behind characterization tests;
- remove each replaced direct reader;
- preserve current artifacts, relation order, hashes, and lane policies;
- eliminate historical path indirection only when parity is proven.

Exit gate: live non-Atlas consumers use the same snapshot digest and current
selection outputs remain unchanged on the frozen characterization corpus.

### PR 4 — Publication decision, only if separately authorized

Type: explicit artifact promotion and handoff update.
Not authorized by this PRD.

Possible deliverables:

- promote the verified candidate release;
- update pinned downstream hashes through their controlled procedures;
- retire obsolete compiler/reader copies;
- update current docs, indexes, and AGENTS handoff;
- preserve historical artifact hashes and replay boundaries.

## Tests to add or deepen

- source-manifest and compiled-source reconciliation;
- active/historical curation inclusion and migrations;
- relation identity uniqueness and exact curation pointers;
- source-anchor state validation;
- field-level lineage state;
- compact/rich graph projection reconciliation;
- deterministic candidate build and compare;
- no compile-from-output fallback;
- local embedding-row drift detection;
- strict published snapshot container validation;
- direction-preserving outgoing/incoming/incident queries;
- missingness-vector behavior;
- runtime consumer parity;
- frozen evidence and Atlas hash preservation.

Existing selection, fan-correction, activation-tiebreaker, graph-survival,
disposition, and frozen experiment tests remain. Shallow direct-file-reader
tests are replaced only when the corresponding reader is removed.

## Risks and mitigations

### Risk: copying the recovery snapshot obscures provenance

Mitigation: hash-lock every file before copy; stop on snapshot drift; retain a
repository-local recovery manifest with an opaque recovery identity.

### Risk: a `KnowledgeSubstrate` class becomes a god object

Mitigation: it owns authoring validation, compilation contracts, snapshot
loading, identity, custody, and queries only. Lane ranking, portfolio admission,
embeddings, V60, reconsideration, and UI remain separate modules.

### Risk: a new reader becomes a permanent parallel reader

Mitigation: migrate a real provider-free caller in the same PR; give every
adapter a deletion milestone; prohibit new direct graph reads.

### Risk: strict loading changes graceful degradation

Mitigation: return explicit missing/failed/partial states into existing run
health rather than crashing or silently substituting an empty graph.

### Risk: source-anchor cleanup becomes semantic rewriting

Mitigation: separate mechanical candidate detection from human source-first
adjudication; preserve unresolved states; never optimize for a coverage score.

### Risk: canonical serialization creates a large artifact diff

Mitigation: preserve current relation order and compatible serialization during
parity work; compare semantic equality separately; publication stays separate.

### Risk: activation text changes invalidate embeddings

Mitigation: current parity phase changes no semantic text; later changes mark
local rows stale and require separate provider authorization for rebuilding.

### Risk: Atlas pinned hashes force frontend work into scope

Mitigation: current artifacts remain unchanged through PR 0-3. Any later
publication follows the downstream hash-update contract without reopening UI.

## Explicit non-goals

- No new mental models or relations.
- No relation deletion based only on a missing exact source span.
- No multi-hop or incoming-edge runtime pressure.
- No reciprocal or transitive inference.
- No graph-wide relevance, centrality, importance, or quality score.
- No change to Lane 1, Lane 2, Lane 3, or Lane 4 semantics.
- No pressure-portfolio active/reserve change.
- No V60 merger or rewrite.
- No Neo4j, Neptune, PostgreSQL graph extension, MCP, Cypher, or SPARQL.
- No factual/entity GraphRAG or causal-world graph.
- No community summaries.
- No provider or embedding calls.
- No prompt changes.
- No Atlas, frontend, Teacher, Observatory, or deployment work.
- No rewrite of frozen evidence.
- No product-usefulness or better-answer claim.

## Authority decision

The founder selected this repository as the sole authoring, compiler,
publication, runtime, and skill authority. The temporary recovery snapshot is
used only to preserve exact already-authored records. It is not named in public
manifests, required by a fresh clone, or supported after recovery.

## Product nonclaims

Completion of this PRD would establish that:

- Lolla can account for and reproduce its published substrate;
- all consumers can share exact identity and direction;
- omissions and failures are visible;
- future graph experiments have a trustworthy base.

It would not establish that:

- the graph is complete or semantically correct;
- an edge is relevant to a particular conversation;
- multi-hop reasoning is useful;
- a revised answer is better;
- Lolla provides unique real-user value.
