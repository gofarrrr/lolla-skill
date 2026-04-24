# Phase 0.5 — Adoption memo

**Date:** 2026-04-24
**Gate function:** approves Phase 1 (IR implementation) OR forces revision of the roadmap + archaeology before Phase 1 starts.
**Input signals:** 4 external-systems fetches + general knowledge on well-known patterns + the 3-case production evidence we already generated.

## Executive summary

The v1 IR design sketched in the roadmap (small core: `Turn`, `SpanRef`, `FrameAnchor`, `UserIssueEvent`, `StanceEvent`) survives Phase 0.5 largely intact. External systems validate the *pattern* — typed objects over raw text with span-level provenance — but none provide a drop-in ontology. Specifically:

- **GraphRAG's TextUnit → Entity/Relationship → Community pattern** validates our substrate (Turn/SpanRef) → semantic objects (UserIssueEvent/StanceEvent/FrameAnchor) → projection (memo, observatory) layering.
- **LangGraph's typed-state-with-reducers pattern** gives us a clean model for how IR objects accumulate over the pipeline and how checkpoints enable drill-back.
- **12-factor-agents Factor 12 ("stateless reducer over accumulated context")** validates our "IR as substrate, projections as views" approach and explicitly warns against frameworks that hide the state.
- **GAIR Context-Engineering 2.0** names the concept ("entropy reduction") and the risk ("context rot") but is a bibliography, not an API — no concrete ontology to adopt.

The only meaningful revision: we should adopt LangGraph's **reducer model** for IR updates and **explicit checkpointing semantics** for drill-back, rather than inventing our own mutation scheme. Everything else in the archaeology sketch stands.

**Recommendation: Phase 1 may proceed.** With two concrete adoptions and one explicit rejection, detailed below.

---

## Per-system findings

### GAIR-NLP Context-Engineering-2.0

Curated bibliography + research positioning paper. Names two concepts we should keep in our vocabulary:

- **"Entropy reduction"** — explicit framing of the transformation from high-entropy raw input to low-entropy machine-usable structure. Our "reversible entropy reduction" phrasing is correct; their framing supports it.
- **"Context rot"** — degradation of LLM output quality as context length grows. Supports our "packet-local projections" argument (roadmap Phase 4): lanes should consume narrow packets, not the whole context.

What's NOT there: concrete schemas, API prescriptions, or adoptable ontology. The paper references MemGPT, MEM0, Memos, Letta memory-blocks — naming them without specifying them. Useful for vocabulary and for validating the direction; not useful for implementation.

**Adoption:** Keep "entropy reduction" and "context rot" as explicit terms in the architecture. No concrete API to adopt.

### GraphRAG (Microsoft)

Most directly relevant to our IR design. Core pattern:

**TextUnit → Entity/Relationship/Claim → Community (with summaries)**

- **TextUnit** = fine-grained reference anchor. Entities and claims are tied to TextUnits for provenance. Maps cleanly onto our `SpanRef`.
- **Entity / Relationship / Claim** = typed objects extracted from text, linked to source TextUnits. Maps onto our `UserIssueEvent` / `FrameAnchor` / `StanceEvent`.
- **Community** = hierarchical grouping with bottom-up summaries. Maps onto our "projections" (lane packets, observatory views).
- **Dual access** preserved: you can always traverse from a high-level summary back to the specific TextUnits that generated it. This is exactly our drill-back goal.

**Adoption (strong):** GraphRAG validates the three-layer pattern `substrate → typed semantic objects → projections/summaries`. This is what our roadmap sketches. Keep going.

**Not adopted:** The entity-centric graph model. GraphRAG is designed for document knowledge graphs (who/what/when/where). Our use case is conversation audit — temporal, speaker-attributed, decision-shaped. The semantic object set differs. We take the *layering pattern*, not the entity vocabulary.

### LangGraph (general knowledge; fetch was empty)

LangGraph's persistence model (well-documented in general knowledge):

- **State = typed dict** (TypedDict / dataclass). Every field has a type; every node produces updates to specific fields.
- **Reducers** combine state updates (e.g., "append to this list", "merge this dict"). This makes state composition explicit and observable.
- **Checkpoints** = snapshots of the full state, written at every superstep. A thread is a sequence of checkpoints.
- **Time-travel** = replay from a prior checkpoint. Full reproducibility.

**Adoption (strong):** The reducer pattern for IR updates. Instead of ad-hoc mutation, each IR update should be an explicit, typed, named operation (e.g., `add_user_issue_event`, `supersede_issue`, `record_stance_shift`). This buys us:
- Testable mutation logic
- Observability (log the reducer calls, you have a running record of how IR was built)
- Eventual checkpointing if we need it

**Adoption (medium):** Checkpoint semantics, but deferred. Phase 1 doesn't need checkpointing; the archive already persists run artifacts. Checkpointing becomes relevant in Phase 3+ when the assistant-trajectory IR spans multi-turn evolution we want to replay.

**Not adopted:** The StateGraph execution model. LangGraph is a framework for orchestrating LLM calls; we already have orchestration (`pipeline.py`). We're not rebuilding the orchestrator.

### humanlayer/12-factor-agents

Doctrine document. Most relevant factors:

- **Factor 12: "Stateless reducer over accumulated context"** — agent as a pure function of (context → new context). Our pipeline already behaves this way: each lane is a function over `ConversationContext`. The IR layer fits this cleanly.
- **Factor 5: "Unify execution state and business state"** — don't have two separate states. Our `ConversationContext` + IR should be one thing, not a dev-only scratch layer.
- **Factor 8: "Own your control flow"** — explicit, not framework magic. Our `run_pipeline.py` does this; IR adoption shouldn't regress this.
- **Factor 3: "Own your context window"** — actively manage what's in context. Directly maps onto our Phase 4 "lane packet builders" goal.

**Adoption:** Factor 12 as an explicit invariant for Phase 1: the IR builder should be a pure function of `(raw conversation, extraction artifacts) → IR`. No hidden global state, no side effects. Factor 3 as Phase 4 guidance.

---

## Archaeology checklist — explicit answers

Five claims we said Phase 0.5 should validate or falsify.

### 1. Provenance-based identity is sufficient for cross-run stability measurement

**VALIDATED.** GraphRAG's TextUnit-anchored entities demonstrate stability identity via source references without synthetic slugs. LangGraph's checkpointing shows state-identity via structural hashing of typed state, not synthetic IDs. Neither system uses slug-based identity.

**Implication:** PR #1b and PR #2 (canonical_key slugs) stay dead. IR provenance is the replacement.

### 2. Single-family `UserIssueEvent` with `kind` + lifecycle is tighter than separate `ConstraintEvent`/`ConcernEvent`/`OpenLoop`

**VALIDATED with caveat.** GraphRAG's Entity type uses a `kind`/`type` discriminator (person / place / organization) within a single family, not separate top-level types per kind. This is the pattern we want.

**Caveat:** annotation discrimination between kinds (constraint vs concern vs open_loop) may be unreliable in practice. Phase 1 should include annotation-agreement measurement on protected cases; if annotators can't reliably tell the kinds apart, that's a signal to simplify further (e.g., drop `kind` and use `status` alone).

### 3. `StanceEvent` trajectory is structurally important for audit

**VALIDATED.** Our 3-case production evidence already showed stance shifts mattering (parenting_teen: user's decision-made → doubt re-opening; whistleblower: external-first → channel-selection-is-counsel's-call). External systems (GraphRAG communities-over-time, LangGraph checkpoint sequences) model evolving state as a first-class concern.

**Implication:** PR #3 (synthesized_position as Position object — point-estimate) stays dead. Trajectory is right.

### 4. `move_type` enum is packet-local in v1, not IR-global

**VALIDATED.** GraphRAG's claims attach attributes at the claim level (packet-local) rather than promoting move-type-like taxonomies to graph schema. LangGraph's channels support packet-local enrichment without requiring state-level commitment. Both support the principle: don't promote a classification to global IR unless ≥2 consumers independently re-derive it.

**Implication:** PR #5 (move_type enum) lives as packet-local classification in Lane 1/Lane 2 packet builders (Phase 4). Promotes to IR only if Phase 3's `ReasoningSegment` adoption proves necessary.

### 5. `ActorRef` deferral is safe

**VALIDATED.** None of the 3 production cases showed multi-actor ambiguity that would have required explicit ActorRef resolution. GraphRAG does promote an Entity abstraction that covers "actors" — but it promotes it because its use case demands it (cross-document entity resolution). Our use case (2-speaker conversation) rarely hits actor ambiguity.

**Implication:** Defer `ActorRef` to v1.1. If a real case surfaces multi-actor ambiguity that can't be resolved from turn context, promote.

---

## Adoption / rejection table

| Pattern | Source | Decision | Reason |
|---|---|---|---|
| Three-layer `substrate → typed semantic objects → projections` | GraphRAG | **Adopt** | Validates our roadmap sketch. No change to layout; explicit naming. |
| Typed IR with `kind` discriminator on single families (`UserIssueEvent(kind=...)`) | GraphRAG Entity pattern | **Adopt** | Keeps v1 IR tight. Already in roadmap. |
| Reducer pattern for IR updates (explicit, typed, named mutations) | LangGraph | **Adopt** | Makes IR construction testable and observable. Add to Phase 1. |
| "Entropy reduction" and "context rot" as explicit architecture vocabulary | GAIR | **Adopt** | Validates existing framing. No code change. |
| Factor 12: IR builder as pure function of (raw + extraction) → IR | 12-factor-agents | **Adopt** | Explicit invariant for Phase 1 acceptance. |
| Source-span provenance on every derived object | GraphRAG TextUnit model | **Adopt** | Already in roadmap; GraphRAG confirms practicality. |
| LangGraph StateGraph/reducer framework itself | LangGraph | **Reject** | We have our own orchestration in `pipeline.py`. Adopting the pattern, not the framework. |
| GraphRAG's entity-centric graph as primary representation | GraphRAG | **Reject** | Our use case is conversation audit, not document knowledge. Graph stays substrate for routing (curated models), not conversation state. Preserves archaeology §6.5 decision. |
| Global actor ontology (`ActorRef` in v1) | All | **Reject/Defer** | No evidence of need in our 3 production cases. Promote in v1.1 if evidence surfaces. |
| Checkpointing in Phase 1 | LangGraph | **Defer** | Phase 1 doesn't need it. Revisit at Phase 3 when trajectory IR spans multi-turn evolution. |

---

## Drill-back spike — design

**Goal:** Prove the provenance layer is feasible on one real run before Phase 1 builds it.

**Scope:** one case (user_has_plan — the cleanest), one lane (Lane 3 — simplest semantic layer since it already has substring validation).

**What the spike demonstrates:**

1. **Construct v1 IR from existing artifacts.** Read the archived `conversation.txt` + `extraction.json` for the `user_has_plan` run. Emit:
   - `Turn[]` from the conversation (trivial — turn_index + speaker + text)
   - `SpanRef`s for each assertion in the extraction output (character offset in the raw turn)
   - `UserIssueEvent`s for each `live_constraint` and `dropped_thread`, with kind and source_span
   - `FrameAnchor` for the first-turn framing anchor
   - `StanceEvent` for the user's "I've decided to quit" stance
2. **Packet for Lane 3.** Build a minimal Lane 3 packet that consumes the IR rather than raw `ConversationContext`. Should include: user-turn excerpts (via SpanRef), FrameAnchors, UserIssueEvents with `kind=concern`.
3. **Drill-back.** Given a Lane 3 finding (one of the 3 frame elements produced in the real run), walk:  
   `finding.source_ref → IR object → SpanRef → raw turn character range → original conversation text.`  
   Output as a markdown showing each step.

**What the spike does NOT demonstrate:**

- Production-ready builder (it's one-shot scripting)
- Other lanes
- Performance
- Alternative IR designs (we're proving one works, not comparing)

**Acceptance:** drill-back markdown exists; shows for at least 1 Lane 3 finding, the full chain finding → IR object → source span → raw text. Reviewable in ~5 minutes.

**Artifact:** `research/phase0.5-drillback-spike-2026-04-24.md` (to be produced in Phase 0.5 completion).

---

## Plan for how we build Phase 1

Based on the adoption/rejection calls above, here's the concrete shape Phase 1 implementation takes:

### File layout

- **`engine/system_b/ir.py` (new):** typed dataclasses — `Turn`, `SpanRef`, `FrameAnchor`, `UserIssueEvent`, `StanceEvent`, plus `ConversationIR` aggregate.
- **`engine/system_b/ir_builders.py` (new):** reducer-style builders. Each IR update is a named function: `add_turn`, `add_span`, `add_frame_anchor`, `add_user_issue_event(kind, status, source_span)`, `supersede_issue(issue_id, by_ref)`, `add_stance_event`. Pure functions of (IR, input) → IR.
- **`engine/system_b/ir_constructor.py` (new):** maps `ConversationContext` + `ExtractionPayload` → initial `ConversationIR`. This is the bridge: existing artifacts come in, IR comes out. No lane code changes.
- **`tests/test_ir.py` (new):** shape + construction tests.
- **`tests/test_ir_drillback.py` (new):** drill-back test from finding-like object to source turn.

### What does NOT change in Phase 1

- Lane behavior (this is the roadmap's Phase 1 gate: "no lane behavior changes yet")
- `pipeline.py` orchestration
- `ConversationContext` itself (IR sits alongside; ConversationContext is the input to the builder)
- Extraction layer (`run_extract.py` stays as-is)

### Phase 1 acceptance gates (from roadmap, concretized with memo evidence)

| Axis | Target | How we measure |
|---|---|---|
| Structural artifact | IR types + builder + constructor all committed | file existence + test coverage |
| Behavioral metric — provenance coverage | every IR object has non-empty source_span | unit test asserts coverage |
| Behavioral metric — drill-back | from a packet, can resolve to a source turn in ≤3 steps | automated test + spike artifact |
| Behavioral metric — annotation agreement (protected cases) | two reviewers agree on `UserIssueEvent.kind` classification ≥80% of time on our 3 real runs | manual exercise once builder exists |
| Cost/latency | IR construction adds <50ms to pipeline run | bench test |
| Kill criteria | if annotation agreement <80%, reduce IR ontology before proceeding | explicit threshold |

### Phase 1 does NOT include

- Lane packet builders (that's Phase 4)
- Extraction decomposition (Phase 5)
- Checkpointing (deferred to Phase 3+)
- Observatory drill-back UI (Phase 1 gives the raw data; UI is incremental)

### Phase 1 task decomposition (for future task file)

1. Define IR dataclasses (TDD per object family)
2. Implement reducer builders (TDD, one operation at a time)
3. Implement `ir_constructor.py` (maps existing artifacts → IR)
4. Manual annotation exercise on 3 real runs (us, not coder)
5. Integrate into pipeline (IR is constructed but not consumed — adds observability, not behavior change)
6. Ship Phase 1 PR

Expected coder time: 2-3 days once task file is ready.

---

## Summary — what we decided

1. **Phase 1 may proceed.** The 5-family v1 IR sketch survives external-systems scrutiny.
2. **Two concrete adoptions:** reducer pattern (LangGraph) + TextUnit-anchored semantic objects (GraphRAG).
3. **One explicit rejection:** LangGraph StateGraph framework itself (we keep our own orchestration).
4. **Drill-back spike needed before Phase 1 kicks off** — `phase0.5-drillback-spike-2026-04-24.md` on the `user_has_plan` run, Lane 3 scope.
5. **Phase 1 file layout + acceptance gates specified** above.
6. **BI-as-Lane-5** is orthogonal to this gate; can bundle or ship separately whenever convenient.

Phase 0.5 closes with Phase 1 approved-to-proceed on the above plan.
