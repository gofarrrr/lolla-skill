# Plan: Conversation-First Context Engineering Roadmap

> Source docs: `HOW_IT_WORKS.md`, `research/conversation-first-rearchitecture-handover.md`, `research/full-system-audit-2026-04-23.md`, `research/pipeline-py-structural-map.md`, current branch `feat/conversation-first-phase-2d-lane2-companion`

## Audience

This document is written as a working handover for:

- the project owner making product and architecture decisions
- a junior developer helping implement the next generation of the system

It is intentionally forward-looking, but it builds on the current codebase rather than proposing a clean-sheet rewrite.

## Outcome

Move Lolla from a **conversation-aware pipeline** to a **conversation-native context-engineering system**.

The target is not "better summaries." The target is **reversible entropy reduction on conversations**:

- reduce messy conversational input into lower-entropy, machine-usable structure
- keep enough provenance that every important derived item can be traced back to raw turns
- preserve nuance, ambiguity, and temporal evolution instead of smoothing them away
- assemble narrow, lane-specific context packets instead of one global compressed story

The system should become better at understanding:

- what the user made live
- what the assistant actually claimed
- what changed over time
- what stayed unresolved
- what structural pressure should be applied from the curated substrate

## Why Change Now

The original bottleneck was the legacy contract:

- `CritiqueRequest(query, vanilla_answer)`

That contract flattened a rich conversation into two strings. It was appropriate for the older System B / single-query paradigm, but it became the wrong abstraction once the skill evolved into a conversation-first audit system.

That bottleneck is now mostly removed:

- Phase 1 shipped `ConversationContext`
- Lane 3 migrated to conversation-first input
- Lane 4 migrated to conversation-first input
- Lane 1 migrated to conversation-first input
- Lane 2 is currently being completed on the active branch

This is a major architectural win. The lanes now mostly read the right thing.

But the bottleneck has moved upstream.

The next limiting factors are:

- capture fidelity is still trust-heavy
- extraction is still monolithic and summary-shaped
- extracted context lacks strong provenance
- lane context assembly is still implicit inside prompt builders instead of explicit in a shared context layer
- `pipeline.py` remains too large and mixes responsibilities that should become separate modules

## Durable Architectural Decisions

These decisions should remain stable across all implementation phases.

### 1. Raw transcript is the source of truth

The actual conversation turns are the canonical artifact.

Derived objects may compress, classify, or index the transcript, but they must not silently replace it as the truth source.

### 2. Derived context must carry provenance

Every important derived item should point back to raw turns or spans.

Examples:

- a constraint should know where it came from
- a dropped thread should know where it was raised and where it was abandoned
- a framing claim should know which user words support it
- an assistant stance summary should know which assistant turns it compresses

### 3. Compression should be structural before narrative

Preferred compression:

- typed objects
- event status
- turn and span references
- active / archived state views

Avoid summary-first compression in the critical path.

### 4. Lanes should consume lane-specific context packets

The system should stop thinking in terms of "one extraction payload for everyone."

Instead:

- one shared conversation IR
- multiple narrow lane packets

### 5. Keep probabilistic edges and deterministic middle

This principle from `HOW_IT_WORKS.md` remains correct.

LLMs should do:

- semantic reading
- classification
- candidate generation
- specific reframing

Deterministic code should do:

- routing
- graph traversal
- selection
- packaging
- observability

### 6. Roll out additively and reversibly

No big-bang rewrite.

Each phase should:

- land alongside the current path
- have an equivalence or quality gate
- be independently revertible

### 7. Do not split `pipeline.py` before the new boundaries are real

The file is too large, but premature splitting would preserve the wrong seams.

First establish:

- conversation IR boundary
- lane packet builder boundary
- orchestration boundary

Then split the file according to those boundaries.

### 8. Evaluation is part of the architecture

This system is quality-first. That means:

- every architectural move needs measurement
- synthetic corpus alone is not enough
- real messy conversations must become part of the protected eval surface
- corpus and annotation work should start in parallel with Phase 1, not wait until the end

### 9. Start with a small substrate plus measured promotions

The v1 doctrine is `Option A`:

- small event substrate
- a few promoted semantic objects
- everything else starts as a projection or packet-local view

Do not freeze a wide ontology up front.

Promote a projection into a first-class IR object only when all of these are true:

- at least 2 lanes independently re-derive it
- the re-derivation cost is measurable in compute, latency, or prompt complexity
- the first-class form can carry stable provenance
- promotion improves at least one phase-appropriate metric without breaking the active cost budget

## Current State Snapshot

### What exists now

- `ConversationContext` + loader + pipeline shim
- lane-specific conversation-first entry points
- strong evidence validation in Lane 2 and Lane 3
- richer prompt structure using `CONTEXT` vs `SOURCE`
- observability surfaces such as `run_health`, boundary-call traces, prompt versions

### What still reflects the old paradigm

- `scripts/run_extract.py` is still a single monolithic extraction call
- `ExtractionPayload` still centers summary fields:
  - `decision_situation`
  - `live_constraints`
  - `synthesized_position`
  - `original_framing`
  - `dropped_threads`
- many of those fields are useful, but they remain mostly provenance-light
- `pipeline.py` still mixes:
  - orchestration
  - lane 1 execution
  - lane dispatch
  - audit packing
  - telemetry helpers
  - serialization helpers

### Practical status

- main is already materially conversation-first
- the active branch is ahead of the handover docs because Lane 2 is in progress
- the right next move is not "more extraction fields"
- the right next move is a real context-engineering layer

## Target Architecture

The target architecture has six layers.

### Layer 1: Capture Integrity

Purpose:

- preserve the raw conversation faithfully
- detect broken or degraded captures early

Responsibilities:

- store immutable turn-by-turn transcript
- assign stable turn ids
- validate transcript shape
- mark degraded or truncated capture clearly

Output:

- `ConversationRecord` or equivalent raw transcript object

### Layer 2: Conversation Index / IR

Purpose:

- perform reversible entropy reduction on the raw conversation

This is the most important new layer. It should not be a prose summary. It should be a typed representation of the conversation's decision-relevant structure.

The v1 doctrine here is `Option A`: small substrate plus measured promotions.

Committed v1 substrate:

- `Turn`
- `SpanRef`

Promoted v1 semantic objects should stay intentionally few:

- `FrameAnchor`
- `UserIssueEvent` — one family with `kind` (constraint / concern / open_loop) + lifecycle fields (`introduced_at_turn`, `status`, `resolved_at_turn`, `superseded_by`). Splitting into separate `ConstraintEvent` / `ConcernEvent` / `OpenLoop` top-level families is an Option-B move and premature without annotation evidence that the kinds discriminate reliably.
- `StanceEvent`

Deferred substrate candidates (not in v1 until evidence justifies):

- `ActorRef` — defer until Phase 0.5 annotation work or later lane measurement shows repeated multi-actor ambiguity (user talking about multiple people, assistant reasoning about multiple stakeholders). Promotion at that point is v1.1, not v1.

Projection candidates, not committed v1 ontology:

- `DecisionOption`
- `ReasoningSegment`
- `CoverageTarget`

The pressure to promote any projection should be decided by the promotion rule above, not by upfront ontology enthusiasm.

Common fields across many of these:

- `source_turn_ids` or `source_spans`
- `status`
- `introduced_at_turn`
- `resolved_at_turn`
- `superseded_by`
- `confidence`
- `kind`

Important rule:

- observed facts and inferred judgments must be separable

For example:

- observed: "user said X in turn 3"
- inferred: "this creates a live family-planning concern"

### Layer 3: Lane Packet Builders

Purpose:

- select and compress only what each lane needs

This is where the actual context engineering happens.

Each packet builder should read the shared conversation IR and emit a narrow context view.

A packet does not need to be one flat blob of prompt prose.

In many cases, the better shape will be a small multi-surface bundle, for example:

- structured objects
- compact notes
- lightweight references to transcript turns / spans / artifacts
- token-budget metadata or inclusion manifests

Examples:

- Lane 1 packet:
  - assistant claims under audit
  - active constraints
  - unresolved concerns
  - omitted checks candidate list
- Lane 2 packet:
  - assistant reasoning spans
  - stance shifts
  - evidence-eligible passages only
- Lane 3 packet:
  - first-turn framing anchors
  - later user reframes
  - mutable constraints
- Lane 4 packet:
  - user question topology
  - assistant coverage evidence
  - unresolved structural dimensions

Important rule:

- packets are projections, not sources of truth

### Layer 4: Audit Lanes

The current lane doctrine remains valid, but lanes should consume explicit packets rather than reconstructing context ad hoc from raw `ConversationContext`.

This makes the system:

- easier to reason about
- easier to test
- easier to measure
- less prompt-brittle

### Layer 5: Curated Substrate and Routing

Keep this mostly as-is.

This layer is already one of the system's strengths:

- deterministic routing
- curated mental-model substrate
- graph-aware selection
- anti-echo logic
- auditability

The job here is not a redesign. The job is to feed it cleaner, better-scoped context packets.

### Layer 6: Revision and Observability

The final reconsideration step should consume:

- findings
- structured context
- supporting spans

Observability should answer:

- what context was selected
- what got compacted
- what got dropped
- what was inferred
- what evidence supports each inference

## Context Engineering Lens

The architecture should be understandable through four context-engineering actions:

### Write

Persist useful state outside the immediate prompt window.

In Lolla, this means:

- raw transcript
- conversation IR
- packet manifests
- eval artifacts

### Select

Pull only the right subset of state into the next reasoning step.

In Lolla, this means:

- lane packet builders
- anti-echo filters
- scoped retrieval from the curated substrate

### Compress

Reduce entropy without losing the information needed for the next decision.

In Lolla, good compression means:

- structural views
- active vs archived state
- source spans instead of repeated full text

Not:

- one polished summary replacing the conversation

### Isolate

Split context so each reasoning step sees only the state relevant to its job.

In Lolla, this means:

- lane-specific packets
- isolated lane prompts
- narrow, role-specific revision or sub-agent contexts when used

## What "Reversible Entropy Reduction" Means in Practice

For this project, the phrase should be operationalized as engineering rules.

### A reduction is acceptable only if:

- it lowers token count or ambiguity
- it preserves the information needed by downstream lanes
- it can be traced back to raw turns
- it does not silently merge materially different states

### A reduction is reversible when:

- the derived object references source turns or spans
- archived / superseded state is retained rather than deleted
- a reviewer can reconstruct the reasoning path from packet back to transcript

### A reduction is not acceptable when:

- it rewrites uncertainty as certainty
- it merges timeline changes into one polished statement
- it hides conflict between turns
- it makes a lane depend on summary prose that cannot be verified

## What To Build and In What Order

This roadmap uses thin, additive slices. Each phase should be demoable or verifiable on its own.

Every phase gate should specify four things explicitly:

- structural artifact
- behavioral metric
- cost / latency budget
- kill criteria

## Cross-Phase Execution Guardrails

- `Phase 0.1` and `Phase 0.5` are hard gates before `Phase 1`
- `Phase 5` does not start until `Phases 1-4.5` have shipped and baked for at least one full cycle
- real-case eval corpus and annotation work start in parallel with `Phase 1`; `Phase 8` operationalizes and hardens that track rather than inventing it late
- `Phase 7` is cleanup and hygiene, not a primary architecture move

---

## Phase 0: Stabilize the Current Conversation-First Migration

**Goal:** finish the current lane migration wave cleanly before opening the next architectural front.

### Why

The context-engineering layer should be built on a stable conversation-first baseline, not on partially migrated lanes.

### What to build

- finish Phase 2d measurement and documentation
- merge Lane 2 only after the evidence standard matches 2a / 2b / 2c
- freeze "add more extraction fields" work until the new IR is defined
- capture a clean baseline of current behavior and current failure modes

### Phase gate

- Structural artifact: Lane 2 has the same quality-evidence package as the earlier lane migrations, baseline docs reflect the real current state of all four lanes, and known bottlenecks are recorded as upstream context-engineering problems rather than lane-input problems.
- Behavioral metric: the baseline is decision-grade enough that later architectural work can be compared against it without ambiguity.
- Cost / latency budget: no material increase to steady-state production cost or latency; only measurement runs may add temporary overhead.
- Kill criteria: if Lane 2 cannot meet the evidence standard without changing architecture first, stop and re-scope instead of papering over the gap with more extraction fields.

### Junior-dev-safe tasks

- corpus run automation
- diff scripts
- measurement packaging
- docs cleanup

---

## Phase 0.1: Audit Capture Fidelity Before Provenance

**Goal:** verify that the raw capture path is trustworthy enough to support provenance-bearing architecture.

### Why

If the capture layer is lossy, truncated, or trust-heavy in ways we do not understand, every later provenance claim becomes fragile.

This phase is intentionally before IR work.

### What to build

- audit the current capture path end to end
- document what gets dropped, truncated, normalized, or trusted implicitly
- define the minimum capture contract required for provenance claims
- fix or explicitly flag any degradation severe enough to invalidate downstream provenance

### Phase gate

- Structural artifact: a capture-fidelity audit exists, the minimum capture contract is written down, and any blocking defects are fixed or surfaced as explicit degraded-mode flags.
- Behavioral metric: sampled captures can be reconciled back to the underlying conversation source with acceptable fidelity, and degraded captures are detectable instead of silent.
- Cost / latency budget: capture validation may add lightweight checks, but must not materially slow the normal user path.
- Kill criteria: if raw capture cannot support trustworthy provenance, `Phase 1` is blocked until the capture path is improved or the degraded boundaries are made explicit.

### Junior-dev-safe tasks

- corpus sampling
- capture diff tooling
- truncation detectors
- degraded-mode fixtures
- audit docs cleanup

---

## Phase 0.5: Ground the Design Against Real Systems

**Goal:** reduce speculative architecture by studying strong external implementations before freezing the v1 IR and packet doctrine.

### Why

This roadmap should not invent from scratch where mature patterns already exist.

This phase is a hard gate before `Phase 1`, not optional prep reading.

Before locking the next abstraction layer, we should explicitly compare Lolla's needs against real systems that already grapple with:

- stateful agent context
- append-only history or checkpoints
- provenance and drill-back
- compaction and memory
- multi-view context assembly
- observability and evals

### What to build

- a short comparison memo across a small number of high-signal external systems
- an adoption / rejection table that says which patterns Lolla should copy, adapt, or avoid
- one or two low-cost spikes to test the most important unresolved choices

Recommended study targets:

- `GAIR-NLP/Context-Engineering-2.0` and the linked ecosystem map
- `microsoft/graphrag`
- `langchain-ai/langgraph`
- `OpenHands/OpenHands`
- `666ghj/MiroFish` as a secondary reference for graph-backed memory updates and report-time tool orchestration
- `humanlayer/12-factor-agents`
- Anthropic / Letta / Manus context-engineering writeups
- Phoenix / OpenInference / Promptfoo for tracing and eval patterns

### Questions this phase should answer

- does anything in the external study materially disconfirm `Option A` or require revising the draft IR boundary?
- which kinds of provenance need exact spans versus turn refs versus derivation lineage?
- should packets contain only compacted content, or also lightweight references for lazy loading?
- where should compaction live, and what kinds of compression are truly reversible?
- how should the new conversation IR relate to Lolla's existing curated knowledge graph and relationship graph?
- which observability and eval surfaces should reuse existing conventions instead of inventing new ones?

### Phase gate

- Structural artifact: a comparison memo exists with concrete external references, adopted and rejected patterns are recorded explicitly, and provenance tiers are defined before the v1 IR is frozen.
- Behavioral metric: at least one spike demonstrates packet -> transcript drill-back with token-budget reporting, and the external comparison materially narrows design uncertainty rather than just adding reading notes.
- Cost / latency budget: research and spike work stay lightweight and off the production critical path.
- Kill criteria: if the adoption memo reveals an external pattern that would materially change the IR design, `Phase 1` blocks until the roadmap and IR draft are revised.

### Junior-dev-safe tasks

- source cataloging
- architecture comparison tables
- spike harnesses
- packet-ablation scripts

---

## Phase 1: Introduce a Provenance-Bearing Conversation IR

**Goal:** add a shared intermediate representation alongside `ConversationContext` without changing lane behavior yet.

### Why

This is the missing architectural layer. Without it, the system will keep solving context engineering implicitly inside prompts.

### What to build

- define IR dataclasses / schemas for the first set of stable concepts
- add source span references as a first-class concept
- create a builder that converts current artifacts into the first IR version
- keep the current extraction output and lane behavior intact during this phase

### Scope of the first IR version

Keep the initial object set small and high-value:

- raw turns (`Turn`)
- span references (`SpanRef`)
- framing anchors (`FrameAnchor`)
- user-side issue events (`UserIssueEvent`) — single family with `kind` (constraint / concern / open_loop) + lifecycle fields, **not** separate top-level `ConstraintEvent` / `ConcernEvent` / `OpenLoop` families
- assistant stance events (`StanceEvent`)

Deferred from v1 (promote only if Phase 0.5 annotation or lane measurement shows the pain is clear):

- `ActorRef` — not in v1 substrate until multi-actor ambiguity is evidenced

Do not try to model the entire world in v1.

Prefer a small core plus explicit projections over a large ontology frozen too early.

### Promotion rule for new first-class IR objects

A projection becomes a first-class IR object only when all of these are true:

- at least 2 lanes independently re-derive it
- the re-derivation cost is measurable in compute, latency, or prompt complexity
- the promoted form can carry stable provenance
- the promotion improves at least one phase-appropriate metric without breaking the active cost budget

### Phase gate

- Structural artifact: the repo has a shared conversation IR definition, every v1 object includes provenance fields, provenance distinguishes exact spans vs turn refs vs inference lineage, and existing code can build the IR from current transcript plus current artifacts.
- Behavioral metric: provenance coverage, drill-back speed, and annotation agreement improve enough on the protected cases to justify the IR as a fidelity layer, even though lane behavior does not change yet.
- Cost / latency budget: IR construction may add modest local processing, but must not introduce a material API-cost increase or meaningful steady-state latency regression.
- Kill criteria: if v1 IR objects cannot be built with stable provenance or acceptable annotation agreement, narrow the promoted object set before moving forward.

### Junior-dev-safe tasks

- dataclass/schema implementation
- loaders and converters
- provenance validators
- fixture creation
- shape tests

---

## Phase 2: Index User-Side Context Properly

**Goal:** replace summary-only user-context fields with provenance-bearing user-side events.

### Why

User-side structure drives:

- Lane 3 framing
- Lane 4 question shape
- Lane 1 omissions

This is where nuance is often lost today.

### What to build

Build explicit indexed objects for:

- first-turn framing anchors
- later reframes
- constraints with lifecycle
- concerns / dropped threads / open loops

Every object should know:

- where it came from
- whether it is still live
- whether it was resolved or superseded

### Implementation note

This phase can still use the current extraction prompt as a bootstrap if needed, but the system should start preferring span-backed objects over free-text paraphrases.

### Status note - 2026-04-24

Phase 2 exact-span enrichment was tested as a no-code feasibility gate after
Phase 1 shipped. The first 3-case annotation looked promising, but widening to
the 10-case corpus changed the conclusion: only 8 / 71 user-side objects (11%)
had a useful >=4-word evidence span, and coverage collapsed to 0 on the
complex/high-value cases (`messy_three_problems`, `parenting_teen`,
`startup_pivot`, `whistleblower`).

Decision: do not add dormant `evidence_spans` fields or algorithmic substring
enrichment now. Current extraction is paraphrase-first; user-side context is
recoverable at `turn_ref` / `derivation` granularity, but exact-span enrichment
needs a real semantic quote producer. Revisit this phase when Phase 5
specialist extraction, or a Phase 4 packet builder with a concrete consumer
need, can populate quote-level anchors honestly.

### Phase gate

- Structural artifact: framing, constraints, and concerns exist as provenance-bearing IR objects, with active vs archived vs superseded state explicit.
- Behavioral metric: packet builders and reviewers can recover user-side state with less manual reconciliation than the current summary-first path.
- Cost / latency budget: indexing user-side context should stay within the existing steady-state extraction envelope or trigger an explicit budgeting decision before shipping.
- Kill criteria: if the user-side model becomes too wide, too subjective, or too expensive without improving fidelity, narrow it back to the smallest useful promoted set.

### Junior-dev-safe tasks

- lifecycle helpers
- source-span matching utilities
- corpus annotation helpers
- status-transition tests

---

## Phase 3: Index Assistant-Side Reasoning as a Trajectory

**Goal:** model the assistant's evolving position instead of compressing it into one `synthesized_position`.

### Why

Conversation audits care about:

- what the assistant claimed
- how the assistant's position changed
- when caveats appeared or disappeared
- whether later turns silently dropped earlier caution

That information is structurally important for Lane 1 and Lane 2.

### What to build

Introduce assistant-side objects such as:

- `StanceEvent`
- `ReasoningSegment`
- `ClaimSpan`
- `Caveat`
- `ReversalCondition`

The goal is not to fully formalize reasoning. The goal is to capture enough structure to tell the difference between:

- current position
- prior position
- unresolved ambiguity
- rhetorical confidence vs earned confidence

### Phase gate

- Structural artifact: the system can represent an assistant stance trajectory rather than one final synthesis, and assistant-side segments remain tied to real assistant spans.
- Behavioral metric: protected cases involving dropped caveats, reversals, or shifting confidence become easier to diagnose than under `synthesized_position` alone.
- Cost / latency budget: assistant-side indexing must stay modest enough that it does not crowd out downstream lane budget.
- Kill criteria: if assistant trajectory objects show poor annotation agreement or mostly duplicate packet-level summaries, keep only the minimum stance structure that proves useful.

### Junior-dev-safe tasks

- event schemas
- sequence assembly helpers
- serialization
- comparison tests across turns

---

## Phase 4: Build Explicit Lane Packet Builders

**Goal:** stop assembling lane context implicitly inside prompt-formatting functions.

### Why

This is the actual context-engineering layer. It turns shared IR into narrow, lane-specific working memory.

### What to build

For each lane, add a packet builder that:

- selects relevant objects
- keeps provenance
- compacts structure into a narrow packet
- exposes exactly what the lane needs and nothing more

Recommended order:

1. Lane 3 packet builder
2. Lane 4 packet builder
3. Lane 1 packet builder
4. Lane 2 packet builder

This order mirrors the historical migration risk profile and starts with the simplest user-side packets.

### Phase gate

- Structural artifact: each lane has a named packet shape, packet builders are testable independently of prompts, and packet-to-transcript drill-back remains possible.
- Behavioral metric: packet builders measurably reduce prompt-side context reconstruction and improve packet-level precision on the protected regression cases.
- Cost / latency budget: each lane packet needs an explicit token budget, and packet assembly must stay cheaper than the prompt complexity it replaces.
- Kill criteria: if a packet does not reduce prompt reconstruction or cannot justify its token budget on real cases, do not ship that lane's packet path yet.

### Junior-dev-safe tasks

- packet schemas
- packet builder unit tests
- token-budget reporting
- observability for what each packet included / excluded

---

## Phase 4.5: Define the Conversation IR <-> Curated Graph Join Contract

**Goal:** make the boundary between conversation-state and graph-backed domain knowledge explicit before extraction decomposition.

### Why

The curated graph is one of Lolla's strongest assets, and the join contract is where many of the subtle architecture decisions actually live.

If this boundary stays implicit, later phases will drift.

### What to build

- define which entities and edges in the curated graph remain authoritative
- define which conversation-state objects are authoritative in the IR
- decide whether packets carry graph references directly or receive graph enrichment later
- decide whether packet builders or lane runners own graph joins
- define how provenance works when conversation-derived context is joined to graph-routed knowledge

### Phase gate

- Structural artifact: a written join contract exists that defines authority, data flow, join timing, and provenance semantics between conversation IR and the curated graph.
- Behavioral metric: at least one lane can be traced cleanly from transcript -> packet -> graph-backed routing -> lane output without ambiguity about where each piece of state came from.
- Cost / latency budget: graph joins must stay within the current routing envelope unless an explicit product decision accepts added cost or latency.
- Kill criteria: if the join cannot be made auditable and stable, keep graph access behind the existing routing surfaces rather than widening the boundary prematurely.

### Junior-dev-safe tasks

- join-contract diagrams
- graph-reference manifest fixtures
- provenance trace tests
- route-join comparison harnesses

---

## Phase 5: Decompose Extraction Around the New IR

**Goal:** replace the monolithic extraction call with specialist indexing passes only after the IR exists.

### Why

Decomposing the current monolith before defining the new IR would simply reproduce the old field list in multiple prompts.

That is not enough.

This phase starts only after `Phases 1-4.5` have shipped and baked for at least one full cycle.

### What to build

Split extraction by stable semantic jobs, not by legacy JSON field names.

Candidate passes:

- user framing / reframing indexer
- constraint / concern indexer
- assistant stance / caveat indexer
- reasoning-span selector

These specialist calls should write into the shared IR, not directly into lane prompts.

### Phase gate

- Structural artifact: monolithic extraction is no longer the only way to populate context, each specialist pass writes provenance-bearing objects, and old summary fields become optional compatibility outputs rather than the core representation.
- Behavioral metric: specialist extraction improves packet quality or downstream lane quality on the protected cases enough to justify the added complexity.
- Cost / latency budget: a written steady-state ceiling must be approved before implementation begins; if specialist extraction exceeds that ceiling without proportional quality gains, it does not ship.
- Kill criteria: if specialist passes fail to improve behavior materially or they blow the approved cost budget, keep the monolith or a hybrid path instead of forcing the decomposition.

### Junior-dev-safe tasks

- boundary wrappers
- merge logic
- parser validators
- per-pass fixtures
- comparison scripts old vs new

---

## Phase 6: Remove the Legacy Summary-First Contract

**Goal:** retire the old compatibility path once the new context-engineering path is proven.

### Why

At this point the system should no longer depend on:

- `CritiqueRequest`
- `_context_to_critique`
- summary-first lane inputs

### What to build

- remove the legacy shim
- downgrade old summary fields from critical-path inputs to compatibility surfaces where still useful
- make lane packets the default input contract

### Phase gate

- Structural artifact: all lanes run through shared IR plus packet builders, the legacy shim is deleted, and no critical path depends on summary-only fields.
- Behavioral metric: the new default path matches or exceeds the protected baseline on quality and debuggability.
- Cost / latency budget: deleting the legacy path should reduce maintenance burden without introducing runtime regressions.
- Kill criteria: if removing the shim exposes hidden dependencies or quality regressions that are not understood, restore compatibility temporarily and fix the boundary first.

### Junior-dev-safe tasks

- deletion follow-through
- broken-reference cleanup
- serialization updates
- regression tests

---

## Phase 7: Split `pipeline.py` Using the New Boundaries

**Goal:** do the cleanup refactor only after the right seams exist.

### Why

`pipeline.py` is too large, but the fix is not "split it anywhere." The fix is to split it around stable architecture.

This is a hygiene phase, not the primary architectural move.

### Target module boundaries

At a high level, separate:

- orchestration
- context-engineering / packet assembly
- lane 1 runner
- lane 2 / 3 / 4 dispatch
- result assembly
- audit / serialization helpers
- telemetry helpers

One possible target shape:

- orchestration module
- conversation IR module family
- lane packet builder module family
- lane 1 execution module
- result / audit model module
- telemetry / serialization module

Exact file names can change. The responsibilities should not.

### Phase gate

- Structural artifact: `pipeline.py` becomes a thin orchestrator or disappears into an orchestration module, and runtime concerns are separated according to the stable boundaries.
- Behavioral metric: the refactor makes ownership and debugging clearer without changing architectural behavior.
- Cost / latency budget: this phase should be runtime-neutral.
- Kill criteria: if the boundaries still feel unstable or the split causes churn without clarity, defer it until the system is more boring.

### Suggested stable module boundaries

These are responsibility boundaries, not mandatory file names:

- orchestration:
  - pipeline entry point
  - high-level run sequence
  - timing and run lifecycle
- context engineering:
  - conversation IR
  - IR builders
  - packet builders
  - packet observability
- lane execution:
  - lane 1 runner
  - lane 2 runner
  - lane 3 runner
  - lane 4 runner
- substrate and routing:
  - graph traversal
  - deterministic selection
  - anti-echo
- result models:
  - audit trace
  - cards
  - packet manifests
- runtime support:
  - telemetry
  - serialization
  - health surfaces

### Junior-dev-safe tasks

- move-only refactors
- import cleanup
- snapshot tests
- structural maps

---

## Phase 8: Operationalize Expanded Evaluation and Guardrails

**Goal:** make the new architecture measurable on the kinds of conversations it actually needs to handle.

### Why

The synthetic corpus is valuable, but it does not fully cover:

- topic drift
- emotional turns
- repeated reframing
- partial decisions
- mixed technical + strategic conversations
- assistant position shifts

Real-case corpus and annotation work should already be underway from `Phase 1`; this phase makes that work durable and operational.

### What to build

Add:

- a protected set of real conversation captures
- new metrics for provenance and packet quality
- regression checks for context assembly behavior
- drill-back tooling so a reviewer can inspect packet -> IR -> transcript

### Suggested new metrics

- provenance coverage rate
- span-link success rate
- active-context precision
- unresolved-concern carry-through rate
- stance-trajectory accuracy
- lane packet token budget
- packet inclusion / exclusion trace

### Phase gate

- Structural artifact: a protected real-case eval set exists, packet-level metrics exist, and reviewers can inspect why a given lane saw the context it saw.
- Behavioral metric: the eval system is regularly catching regressions or design mistakes early enough to change implementation decisions.
- Cost / latency budget: eval and review tooling should stay off the user critical path except for lightweight observability surfaces.
- Kill criteria: if the expanded eval surface does not change decisions, reduce it to the subset that does.

### Junior-dev-safe tasks

- metrics scripts
- manifest generation
- review tooling
- dashboards or summary renderers

## What Not To Do

These are important guardrails for the junior dev and for future planning.

### 1. Do not add many more fields to the current monolithic extractor

That deepens the wrong abstraction.

### 2. Do not change too many architecture seams at once

That creates too many moving parts and makes regressions impossible to localize.

In particular:

- do not rewrite extraction and split `pipeline.py` at the same time
- do not build the Phase 1 IR and the Phase 5 extraction decomposition at the same time

### 3. Do not let summaries become the new hidden source of truth

Summaries are useful, but they should be views over indexed structure, not the canonical internal representation.

### 4. Do not delete superseded context

Archive it. Many audit failures are temporal: something was once live, then got silently dropped.

### 5. Do not make every derived object equally important

Only keep context that can plausibly change a lane output or a revision.

## Decision Rubric: What Is Worth Extracting?

When deciding whether a new object belongs in the IR, use this rubric.

Extract it only if most of these are true:

- it can change a lane output
- it can be tied to source turns or spans
- it would be expensive or brittle for every lane to re-derive independently
- it helps preserve temporal or structural nuance
- it can be measured or reviewed

Do not extract it if it is mainly:

- cosmetic summary text
- a nicer label for something already present
- unverifiable interpretation with no provenance

## Assumptions To Validate Against External Systems

Before freezing the architecture, validate these assumptions explicitly.

### 1. The promoted IR set should stay narrow unless measurement forces it wider

Current pressure points:

- `FrameAnchor`
- `UserIssueEvent` (single family with `kind` + lifecycle)
- `StanceEvent`
- `DecisionOption`
- `ReasoningSegment`
- `CoverageTarget`

Assumption to test:

- `Option A` can stay projection-first in v1 rather than drifting back into a broad bespoke ontology

What to check:

- whether an append-only event / thread model plus a few promoted projections is more stable
- which objects truly need first-class status in v1
- whether any projection is being re-derived often enough to justify promotion

### 2. Provenance needs tiers, not one generic field

Current draft assumes most derived objects can carry `source_turn_ids` or `source_spans`.

Assumption to test:

- exact span-level provenance is realistic and worth enforcing for most objects

What to check:

- which objects require exact spans
- which only need turn refs
- which need derivation lineage because they are inferred rather than extractive

### 3. A packet may need multiple context surfaces, not one compact prompt payload

Current draft assumes packet builders emit narrow lane-ready context.

Assumption to test:

- the best packet is a single compact representation

What to check:

- whether packets should separate structured objects, notes, references, and manifests
- whether some context should remain outside the immediate prompt as drillable references

### 4. Hybrid upfront + just-in-time context may beat packet-only delivery

Assumption to test:

- packet builders should select everything a lane needs up front

What to check:

- what can be passed as lightweight identifiers and loaded only when needed
- where lazy retrieval improves precision without making the system too slow or brittle

### 5. Reversible compression needs an operational definition

Current draft uses the phrase "reversible entropy reduction" correctly, but the implementation boundary is still underdefined.

Assumption to test:

- design language alone is enough to keep compression reversible

What to check:

- which compactions are restorable by identifier
- which kinds of loss are acceptable
- which tool outputs or trace surfaces can be safely compacted or cleared

### 6. Retrieval is not the same thing as memory or state

Assumption to test:

- shared IR plus retrieval will cover long-horizon memory needs

What to check:

- whether Lolla needs a pinned working-memory surface for unresolved items
- whether recall history, archival transcript, and lane-local notes should stay distinct

### 6.5. A world-model graph is not automatically the right internal representation

Assumption to test:

- because graph-backed simulation systems are powerful, Lolla should also center its architecture on a large graph/world model

What to check:

- whether Lolla's primary source of truth is still best modeled as conversation turns plus derived projections
- which graph-backed patterns help only at retrieval or observability time
- how to avoid importing simulation-engine complexity where an audit system needs narrower context engineering

### 6.6. The existing curated knowledge graph should be treated as an asset, not an accidental casualty

Current reality:

- Lolla already ships with a curated knowledge graph and relationship graph that drive deterministic routing

Assumption to test:

- the conversation-first redesign can define its boundaries without explicitly deciding how the existing graph fits

What to check:

- which graph entities and edges remain authoritative in the new architecture
- whether the graph should stay a domain substrate joined onto conversation packets rather than becoming the conversation system's primary source of truth
- what new graph-like structures, if any, are needed specifically for conversation state instead of domain routing

### 7. Capture fidelity remains a gating dependency, not just layer-1 hygiene

`Phase 0.1` should already audit this directly. External study should still stress-test whether the resulting capture contract is truly sufficient.

Assumption to test:

- deep provenance can be built safely on top of the current capture path

What to check:

- whether the raw artifact should be a message / event record rather than only a rendered transcript
- what capture metadata must exist before provenance claims become trustworthy

### 8. Eval metrics need definitions before architecture lock-in

Current draft proposes:

- provenance coverage rate
- span-link success rate
- active-context precision
- unresolved-concern carry-through rate
- stance-trajectory accuracy

Assumption to test:

- these metrics can be specified later without affecting architecture

What to check:

- which metrics require gold annotations
- which can be automated
- which ablations should compare focused packets versus full-context baselines

## Recommended Ownership Split

This section is specifically for working with a junior developer.

### Senior / owner responsibilities

- decide the IR shape
- set prompt doctrine
- interpret qualitative evals
- define shipping thresholds
- approve deletions of legacy paths

### Junior-dev-safe ownership

- dataclasses / schemas
- loaders and converters
- validators
- span-matching utilities
- packet builders
- measurement scripts
- regression fixtures
- observability tooling
- move-only refactors after boundaries are agreed

### Shared work

- reviewing packet shapes
- diagnosing regressions
- validating provenance strategy
- checking whether a compacted representation still preserves nuance

## First Five Concrete Work Packets

If implementation starts immediately, do these next.

### Packet A: Finish and baseline the current migration

- close out Lane 2 quality evidence
- document the current architecture truthfully
- lock the baseline

### Packet B: Audit capture fidelity

- audit the current capture path end to end
- define the minimum capture contract for provenance
- fix or flag any degradation severe enough to block Phase 1

### Packet C: Ground the design against external systems

- study a small number of real systems and linked resources
- write an adoption / rejection memo
- decide how the new conversation layer will reuse or boundary with Lolla's existing curated graph
- define provenance tiers before the IR is frozen

### Packet D: Define v1 conversation IR

- commit to the small-core doctrine and promotion rule
- agree on the v1 promoted object set
- define the boundary between conversation-state objects and curated graph-backed domain knowledge
- implement provenance fields
- build transcript -> IR converter

### Packet E: Build the first packet builder

- start with Lane 3 or Lane 4
- make the packet explicit
- test packet output independently of the prompt

These five packets create the foundation for the rest of the roadmap.

## Bottom Line

Lolla should evolve from:

- conversation capture
- monolithic extraction
- lane prompts reconstructing what they need

to:

- raw transcript as immutable truth
- provenance-bearing conversation IR
- lane-specific context packets
- curated substrate applied to those packets
- final revision backed by drillable evidence

That is the right architecture for a conversation-driven reasoning audit system.

It preserves the best parts of the current design:

- curated knowledge
- deterministic routing
- auditability
- quality-first posture

while fixing the next real problem:

- how to reduce conversational entropy without summarizing away nuance, depth, conflict, or timeline.
