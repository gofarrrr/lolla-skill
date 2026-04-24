# Legacy PR design archaeology — inputs for Phase 0.5

**Date:** 2026-04-24
**Purpose:** preserve the design thinking behind PRs paused during the prompt-saturation era (#1b, #2, #3, #5) as structured input for the Phase 0.5 external-systems study and the Phase 1 v1 IR freeze.
**Discipline:** archaeology, not revival. No old-extractor polish. No new extraction fields under the current monolithic shape. The question this note answers is: **what must the new IR make unnecessary, and what must it make tractable?**

## Context

During 2026-04-22/23, four extraction-contract improvements were paused when we discovered the monolithic extraction prompt couldn't absorb new rules without polluting adjacent fields (prompt saturation). The strategic shift to conversation-first rearchitecture (handover: `research/conversation-first-rearchitecture-handover.md`) deferred those PRs on the premise that producing more extraction output in a broken contract is premature. Phase 2 has now completed — all four lanes consume `ConversationContext` directly — which changes the question from "how do we unpause these?" to "what do they tell us about what the new IR needs to handle?"

Classification uses the roadmap's (`plans/conversation-first-context-engineering-roadmap.md`) tightened v1 object set:

- **Substrate:** `Turn`, `SpanRef` (`ActorRef` deferred until multi-actor ambiguity evidence accumulates).
- **Semantic v1:** `FrameAnchor`, `UserIssueEvent` (one family, `kind` + lifecycle), `StanceEvent`.
- **Projection candidates (not yet first-class):** `DecisionOption`, `ReasoningSegment`, `CoverageTarget`.

Paused PRs map against this taxonomy as design inputs — what does the IR design need to absorb, and what can die outright?

## Archaeology table

| Paused PR | Problem it was solving | Why the old form should die | Where the intent survives in the new architecture | Target phase | What we lose if we ignore it entirely |
|---|---|---|---|---|---|
| **#1b** `canonical_key` on `live_constraints` (≤4-token slug, regex-validated, substring-embedding Jaccard measurement) | cross-run stability measurement: "same constraint across runs" needs a stable identifier because text paraphrases differ. Without identity, Jaccard-style stability metrics collapse to text comparison, which is too strict. | synthetic slugs are a workaround for missing provenance. They require a second LLM call to generate, they drift between runs (slugs vary with paraphrase), and they encode no information the IR won't provide structurally. | `UserIssueEvent(kind="constraint", source_turn_ids=[...])`. Identity becomes "same source span across runs." Cross-run stability measurement becomes "do two runs' UserIssueEvents resolve to overlapping turn-span sets?" — a structural comparison, not a synthetic-ID comparison. | Phase 1 (IR) — by default, by construction. | cross-run stability measurement methodology. If the IR doesn't give us stable identity via provenance, we need to re-design stability measurement. **Phase 0.5 must verify this claim.** |
| **#2** `canonical_key` on `dropped_threads` | same as #1b but for dropped/superseded threads | same as #1b — synthetic identity vs structural identity | `UserIssueEvent(kind="concern" \| "open_loop", status="active" \| "resolved" \| "superseded", introduced_at_turn=N, resolved_at_turn=M, superseded_by=ref)`. Lifecycle states + span provenance replace the slug approach. | Phase 1 (IR) — by default | same as #1b — just for the concern/open-loop subset of user-side issues |
| **#3** `synthesized_position` as `Position` object (`stance: accept \| reject \| defer`, `mechanical_anchor: span`) | structure the free-text "bottom line" so Lane 1's tendency detection can dispatch on stance without re-parsing prose | a single end-of-conversation stance is a point-estimate that loses the trajectory. Lane 1 already re-derives stance from passages in Pass 2; a point-estimate doesn't help much vs reading passages directly. | `StanceEvent` **trajectory** — roadmap's Phase 3 ("Index Assistant-Side Reasoning as Trajectory"). Each stance change is a typed event with span provenance. Latest stance is a projection (`latest(stance_events)`). | Roadmap **Phase 3** (assistant-side trajectory). In v1 IR (Phase 1), `StanceEvent` is part of the semantic core but can be minimal (emit one StanceEvent per assistant turn with a stance classification); the trajectory richness comes in Phase 3. | ability to detect **stance shifts** — "assistant agreed at turn 3, hedged at turn 5, disclaimed at turn 7" is a distinctive audit signal that PR #3's point-estimate couldn't capture. |
| **#5** `move_type` enum on `reasoning_passages` (`leap`, `dismissal`, `assertion_without_evidence`, `framing_shift`, `closure`) | classify the type of reasoning move each passage represents so Lane 1/Lane 2 can filter/match by move type without re-classifying | reasoning-passage classification is a lane concern, not a shared-IR concern. Most lanes don't need it; the two that do (Lane 1's Pass 2 sub_pattern detection, Lane 2's fingerprint move labeling) already do their own classification internally. Promoting move_type to first-class without cross-lane reuse is gratuitous. | **v1:** packet-local convenience in Lane 1/Lane 2 packets (`Phase 4 packet builder` output, roadmap Phase 4). **Future:** field on `ReasoningSegment` IF Phase 3's assistant-trajectory work promotes `ReasoningSegment` to first-class. Promotion test: do ≥2 lanes independently re-derive move_type? If only Lane 1 needs it, it stays packet-local. | the enum itself (the 5 specific move-types) is a real curation artifact — distilled from the 2026-04-22 observation-doc. If we let this fully die, we lose the taxonomy. Preserve the taxonomy in the Lane 1/Lane 2 packet-builder spec (Phase 4) even if it doesn't graduate to first-class IR. |

## Cross-cutting observations

### What the archaeology confirms

1. **Provenance solves #1b and #2 for free.** If the IR carries `source_turn_ids` on every derived object, synthetic stable identifiers become redundant. Phase 1's acceptance criteria (provenance coverage, drill-back speed, annotation agreement on protected cases) are exactly the behavioral gate that proves this.

2. **Trajectory beats point-estimate (#3 → `StanceEvent`).** This is the roadmap's Phase 3 premise. PR #3 is evidence that this premise is correct — we already knew the point-estimate was useful; the roadmap upgrades it to a trajectory.

3. **Lane-local > IR-global for taxonomies that only one or two lanes need (#5).** The promotion rule protects against over-promoting; #5 is evidence of what it protects against. If move_type were first-class and only Lane 1 used it, we'd carry a field all lanes pay for that only one lane reads.

4. **Cross-run stability measurement methodology will need revision.** The 2026-04-22 observation-doc assumed stability could be measured at the slug-identity level via Jaccard. Under the new IR, stability is measured at the span-identity level. This is a Phase 0.5 check: does span-based stability measurement give us a cleaner signal than slug-based? Probably yes, but verify.

### What the archaeology should *not* do

- It should NOT become "let's revive these PRs in the new IR." The PRs' intent absorbs into structural design decisions; the PRs themselves die.
- It should NOT become a spec for Phase 1. Phase 1 decides its own object set based on Phase 0.5's external-systems study + capture-fidelity audit (Phase 0.1). This archaeology is one input among several.
- It should NOT preserve the extraction-layer thinking as "these fields will survive in ExtractionPayload." The roadmap's Phase 5 (Decompose Extraction Around the New IR) explicitly replaces ExtractionPayload's summary fields with specialist-pass IR writes. ExtractionPayload becomes a compatibility surface, not the canonical representation.

## What this note produces for Phase 0.5

A concrete checklist of IR design claims that Phase 0.5's external-systems study should validate:

- [ ] **Provenance-based identity is sufficient for cross-run stability measurement.** Check against: langgraph checkpoint identity, graphrag span references, GAIR's recommended provenance tiers. Reject IR design if external evidence shows synthetic identifiers are needed even with strong provenance.
- [ ] **Single-family `UserIssueEvent` with `kind` + lifecycle is tighter than splitting into `ConstraintEvent` / `ConcernEvent` / `OpenLoop`.** Check against: real annotation exercises on messy conversations. Reject if annotation shows kind discrimination is unreliable in practice (annotators can't agree on whether something is a constraint vs a concern).
- [ ] **StanceEvent trajectory is structurally important for audit.** Check against: real cases where stance shifts are the audit signal (e.g., assistant hedges then drops the hedge).
- [ ] **move_type enum does not need to be first-class in v1.** Check against: two lanes independently re-deriving — does Lane 1 and Lane 2 actually want the same 5-value enum, or different classifications? If different, keep packet-local.
- [ ] **`ActorRef` deferral is safe.** Check against: annotation exercises where multi-actor ambiguity (user talking about multiple people, assistant reasoning about multiple stakeholders) creates clear pain. If the pain is clear, promote `ActorRef` to substrate v1.1.

## What changes if Phase 0.5 contradicts these claims

- If synthetic identifiers turn out to be necessary: revive #1b / #2 as IR-adjacent projection-layer concerns, not as extraction fields.
- If stance trajectory isn't important: collapse `StanceEvent` to a single end-of-conversation stance, making it essentially an IR object form of PR #3's original intent.
- If move_type is cross-lane-valuable: promote `ReasoningSegment` to v1 semantic core (5 families instead of 3).
- If `ActorRef` is necessary: add to substrate v1.1.

These are revisable. The point is: Phase 0.5 can falsify the current design, and this archaeology note is one piece of evidence it should weigh.

## Cross-reference

- Roadmap: `plans/conversation-first-context-engineering-roadmap.md` (Layer 2, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5)
- Handover: `research/conversation-first-rearchitecture-handover.md` (§"What's paused and why")
- Original observation-doc: `research/extraction-contract-observations-2026-04-22.md` (the move_type taxonomy origin)
- Memory: `~/.claude/projects/-Users-marcin-Desktop-Apps-lolla-skill/memory/project_extraction_contract_roadmap.md`
