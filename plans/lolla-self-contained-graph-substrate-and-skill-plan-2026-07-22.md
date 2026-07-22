# Plan: Self-Contained Graph Substrate, Pressure Portfolio, and Lolla Skill

> Source PRDs: `docs/conversation-understanding/lolla-graph-substrate-custody-and-reproducibility-prd-v0.md` and `docs/conversation-understanding/lolla-constitutional-pressure-portfolio-custody-prd-v0.md`

Date: 2026-07-22
Status: approved for provider-free execution through Phase 6
Runtime semantic changes authorized: none
Provider and embedding calls authorized: zero

Execution update: Phases 0–6 completed provider-free on 2026-07-22. The
source/compiler result is
`docs/conversation-understanding/lolla-graph-substrate-source-and-compiler-reconstruction-result-2026-07-22.md`.
The reader result is
`docs/conversation-understanding/lolla-published-knowledge-substrate-read-boundary-result-2026-07-22.md`.
The frozen planner result is
`docs/conversation-understanding/lolla-constitutional-pressure-planner-v1-result-2026-07-22.md`.
The candidate custody result is
`docs/conversation-understanding/lolla-prospective-complete-portfolio-custody-result-2026-07-22.md`.
The consolidated skill and verification result is
`docs/conversation-understanding/lolla-self-contained-graph-substrate-and-skill-result-2026-07-22.md`.
The implementation boundary is complete without a provider, embedding rebuild,
published-graph change, live portfolio change, or Atlas interface change.

## Architectural decisions

- **Sole project authority**: this repository owns the canonical Markdown,
  reviewed curation, compiler, published substrate, runtime readers, pressure
  planner, skill instructions, and open-source handoff.
- **Retired workspace boundary**: no active code, test, manifest, current
  documentation, or skill instruction may require or advertise another local
  repository or machine-specific source path. Recoverable historical material
  may be used only after exact reconciliation and then becomes repository-local
  source with repository-local custody.
- **One-way recovery, no ongoing source**: any still-accessible recovery snapshot
  is a temporary read-only recovery input, never an installed dependency or a
  second authority. The completed repository must validate without it.
- **Source and projections**: reviewed authoring records are the semantic
  source. The compact and rich graph files are deterministic projections, not
  substitute authoring inputs.
- **Candidate-first publication**: compilation writes candidate output and a
  comparison report by default. No phase silently overwrites the published
  runtime artifacts.
- **Runtime read boundary**: consumers share immutable canonical identity,
  direction, lineage, missingness, and indexes through one published-substrate
  interface. They retain separate ranking and admission policies.
- **Direction**: outgoing, incoming-reference, and incident navigation remain
  distinct. Incoming references never become reverse authored relations.
- **Current pressure policy**: preserve the active and reserve identities,
  order, bounds, one-hop outgoing traversal, and pre-verifier graph-survival
  behavior of the existing constitutional policy.
- **Prospective custody**: complete seed-scope and convergent-path custody is
  built as a candidate schema before any live adoption.
- **Skill topology**: update the existing `lolla` skill as the distributable
  skill surface. Do not create a parallel graph skill or a second runtime.
- **Open-source test**: a clean-clone simulation with only documented
  environment inputs is the final portability gate.
- **Roadmap boundary**: this plan does not reopen retired semantic-reader
  programs, activate Atlas/Teacher work, call providers, change prompts, or
  claim real-user usefulness.

---

## Phase 0: Freeze Evidence and Remove Active External-Workspace Assumptions

**User stories**: A maintainer can see exactly what current graph and pressure
behavior exists; an open-source user is not pointed at a private machine path;
an evaluator can reproduce the baseline before implementation changes.

### What to build

Create one repository-local baseline contract that records current graph
identities, source custody, compiled hashes, current pressure-policy behavior,
and the disposition of every active external-workspace reference. Replace
machine-specific defaults in active provider-free custody tools with explicit
repository-local inputs. Add a guard that distinguishes prohibited current
dependencies from immutable historical evidence without rewriting frozen
artifacts.

### Acceptance criteria

- [x] Current 222-model, 1,358-relation, relation-type, source-manifest, and
      published-artifact identities are reproducible locally.
- [x] The current constitutional portfolio baseline records active/reserve
      identities, ordering, seed scope, admission paths, and convergent-path
      loss for deterministic fixtures and the agreed corpus sweep.
- [x] Active code and current handoff documentation contain no absolute source
      path or dependency on another repository.
- [x] Every remaining retired-workspace mention is classified as immutable
      historical evidence or removed from the current product surface.
- [x] The baseline and guards make zero provider or embedding calls.
- [x] Existing runtime behavior and published graph bytes are unchanged.

---

## Phase 1: Recover Complete Relation Authorship Into This Repository

**User stories**: A maintainer can inspect and validate every current relation
from this checkout; a human reviewer can distinguish active, superseded,
historical, and unresolved authoring states.

### What to build

Recover the exact current 222-record relation-authoring set into the canonical
repository-local curation boundary. Preserve exact file and aggregate hashes,
reconcile every record to the published 1,358 directed relations, and declare
all canonical-ID migrations and historical-record lifecycle states. Introduce
truthful source-anchor states without inventing or rewriting semantic meaning.

### Acceptance criteria

- [x] All 222 active relation-authoring records exist in this repository.
- [x] Their exact recovery manifest reconciles to the frozen recovery identity
      and the current rich graph projection.
- [x] Every published relation resolves to exactly one active authoring record.
- [x] Both known canonical-ID migrations and every legacy record disposition
      are explicit and mechanically validated.
- [x] Exact, normalized, synthesized/multi-span, unresolved, and missing
      source-anchor states remain distinguishable.
- [x] No compiler or runtime change is required to read the current published
      graph in this phase.
- [x] The phase completes successfully after the retired workspace is made
      unavailable.

---

## Phase 2: Compile a Deterministic Candidate Substrate

**User stories**: A fresh-clone maintainer can reconstruct the graph from
declared inputs; an evaluator can compare candidate and published releases
without changing runtime.

### What to build

Deepen the existing compiler into the sole repository-local compiler. Compile
the compact and rich relationship projections from one active relation
registry, produce an input/output release manifest and coverage vector, reject
missing authoring inputs instead of compiling from existing output, and report
local embedding staleness without attempting a rebuild.

### Acceptance criteria

- [x] Compilation begins only from declared repository-local authoring inputs.
- [x] Compile-from-output or silent output-reuse fallback is impossible.
- [x] Two clean candidate builds from the same inputs are byte-identical.
- [x] Candidate relation identities and fields reconcile with the frozen
      published release or every divergence is explicitly classified.
- [x] Compact and rich relation projections derive from the same canonical
      relation record and stable directed identity.
- [x] Release coverage distinguishes complete, completed-zero, partial, failed,
      and missing per relevant layer.
- [x] Candidate output cannot overwrite published artifacts by default.
- [x] Embedding validation is local and reports `current`, `stale`, `missing`,
      or `failed` without a provider call.

---

## Phase 3: Introduce One Published-Substrate Read Boundary

**User stories**: A runtime consumer receives validated identities, direction,
lineage, and availability without parsing repository files; a maintainer can
remove duplicate readers rather than adding another permanent layer.

### What to build

Provide an immutable repository-local substrate snapshot with explicit model,
relation, routing, source, release, and coverage interfaces. Migrate one real
provider-free consumer end to end while preserving its output, then migrate
the remaining live graph consumers by replacement. Give any temporary adapter
one owner and a deletion milestone.

### Acceptance criteria

- [x] Runtime loading never compiles, generates, repairs, or calls a provider.
- [x] Exact canonical lookup performs no silent alias or slug repair.
- [x] Outgoing, incoming-reference, and incident queries preserve original
      authored direction.
- [x] Every returned relation retains a stable relation ID, source order,
      compiled pointer, and available authoring/source custody.
- [x] Missing, failed, partial, and completed-zero loads remain different.
- [x] The first migrated consumer has byte- or object-equivalent behavior.
- [x] Every remaining live direct graph reader is migrated, explicitly
      time-bounded, or demonstrated to belong to immutable historical tooling.
- [x] No ranking, portfolio, prompt, or active/reserve semantics change.

---

## Phase 4: Extract and Version the Existing Pressure Planner

**User stories**: A reviewer can replay the exact current constitutional
pressure policy; a maintainer can change substrate plumbing without changing
which pressure reaches the reasoner.

### What to build

Extract the existing constitutional direct and graph allocation into one named,
versioned planner that consumes the published substrate snapshot. Freeze the
current direct-active cap, source-seed scope, outgoing one-hop traversal,
relation slots, deterministic ordering, reserve behavior, bounded handoff, and
pre-verifier graph survival.

### Acceptance criteria

- [x] The policy declares its identity, version, caps, direction, hop depth,
      seed rule, ordering, and deduplication rule.
- [x] Frozen fixtures preserve exact active and reserve identities, order,
      admission edges, serialized bounds, and current hashes.
- [x] Graph pressure still survives before probabilistic applicability logic.
- [x] The planner performs no graph-file loading, compilation, semantic merge,
      embedding generation, or provider call.
- [x] Apply/reject/park custody still links to the same active pressure items.
- [x] Duplicate or obsolete planner paths are removed or given a tested
      deletion milestone.

---

## Phase 5: Add Prospective Complete Portfolio Custody

**User stories**: A reasoner and human reviewer can inspect exactly which seeds
were expanded, which were not, and every exact bounded graph path that reached
an active or reserve target.

### What to build

Produce a candidate-only portfolio schema that declares expansion scope,
expanded direct-active seeds, unexpanded direct reserve, admission path,
complete exact provenance paths within the bounded one-hop scope, policy and
substrate identities, and a per-layer coverage vector. Keep the current active
identities and order unchanged.

### Acceptance criteria

- [x] `direct_active_only`, `outgoing`, and one-hop scope are explicit.
- [x] Unexpanded direct reserve is not represented as an empty neighborhood.
- [x] Every enumerated target has active or reserve disposition.
- [x] Every distinct exact path in scope survives serialization.
- [x] The winning admission path remains distinguishable from all provenance
      paths.
- [x] The deterministic corpus sweep accounts for all previously lost outer
      convergent paths.
- [x] Any safety-bound truncation produces `partial` with exact counts and
      reason rather than clean completion.
- [x] Active identities and order equal the current policy baseline.
- [x] The prospective schema is not connected to the live reasoner, receipt,
      or Decision Trail in this phase.

---

## Phase 6: Make the Existing Lolla Skill Self-Contained and Distributable

**User stories**: A GitHub user can clone the repository, install the existing
Lolla skill, understand its authority boundaries, validate its packaged
substrate, and run its documented provider-free checks without access to the
founder's machine or retired workspaces.

### What to build

Update the existing `lolla` skill surface and its progressively disclosed
references so it points only to repository-contained scripts, sources,
artifacts, and current documentation. Keep the skill conductor concise, move
detailed graph/substrate operating knowledge into directly linked references,
generate or validate Codex-facing skill metadata where appropriate, and add a
clean-clone installation and provider-free readiness check. Do not create a
second Lolla or graph skill.

### Acceptance criteria

- [x] The skill has one clear trigger description and one canonical runtime
      workflow.
- [x] Skill instructions are concise and link detailed graph/substrate
      contracts through one-level progressive disclosure.
- [x] All invoked scripts and referenced required files are present in the
      repository or created by documented setup.
- [x] No skill path, setup path, current reference, manifest, or readiness
      check depends on another repository or machine-specific project path.
- [x] A clean-clone simulation validates source custody, compiled substrate,
      current pressure-policy baseline, and skill structure without provider
      calls.
- [x] Skill validation and representative helper tests pass.
- [x] Claude Code and Codex installation surfaces do not contradict each other.
- [x] Existing live semantic behavior remains unchanged unless a separately
      reviewed runtime-promotion decision is made.

---

## Separately authorized work after this plan

The following remain outside Phases 0-6:

- publishing changed graph bytes to the live runtime;
- wiring the prospective portfolio-custody schema into the live reasoner,
  receipt, or Decision Trail;
- expanding direct-reserve neighborhoods;
- incoming-reference or two-hop pressure;
- alternative graph-slot ranking or rotation;
- graph-only candidate/V60 paired enrichment;
- Atlas interface, Teacher, or Observatory feature work;
- further Atlas data or route changes beyond the separately authorized and
  completed custody V2 migration recorded in
  `docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md`;
- provider calls, embedding rebuilds, prompt changes, or real-run experiments;
- accuracy, cost, or usefulness claims.

Each requires a separate falsifiable contract and any necessary founder
authorization after the self-contained baseline is complete.
