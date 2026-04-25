# Phase 5.8 — Decision-Situation Design Memo (no formal gate)

**Date:** 2026-04-25
**Status:** design memo, not annotation gate
**Decision:** apply Phase 5.7's heuristic (FrameAnchor with `DerivationProvenance` over all user turns) to `decision_situation`, parallel to `original_framing`.

## Why no formal gate

The previous specialist phases each ran a 9-20 candidate annotation gate to test whether the field's content was substring-anchorable. Phase 5.7's gate scored:

- Anchorability agreement: 82.5% (PASS)
- Inferred rate by component type: situation 0%, assumption 50%, exclusion 100%

The gate produced one clear architectural finding: `original_framing` is best handled by a heuristic FrameAnchor enhancement (DerivationProvenance over all user turns), not an LLM specialist, because (a) downstream consumers don't exist yet, (b) the inferred-rate distribution is type-stratified, and (c) the IR-quality delta from a hybrid 3-mode specialist is small.

`decision_situation` has the same structural shape as `original_framing`. Running another full gate would consume 1+ hour to re-discover the same finding. The honest tech-lead call: write a brief structural analysis instead, cite Phase 5.7 as evidence, ship the heuristic.

## Structural analysis of `decision_situation`

10 cases in the corpus. Universal pattern:

> "Whether [agent] should [decision verb + object], [context clause]."

Or:

> "[Agent description] decid[ing/es] [between options] amid [constraints]."

Decomposing each into components:

| Case | Wrapper template | Decision verb + object | Agent description | Context clause |
|---|---|---|---|---|
| `friendship_money` | "Whether the user should... amid..." | "give their best friend $10K" | "the user" | "repeated prior unpaid loans and her financial crisis with kids" |
| `messy_three_problems` | "Whether the user should..., considering..." | "accept the Seattle job offer" | "the user" | "boyfriend cohabitation, mother's care needs, lease expiration in 60 days" |
| `multi_offer` | "[Agent] deciding among... amid..." | "deciding among three job offers (FAANG staff+, Series B startup founding engineer, stay current)" | "Senior SWE with 12 years FAANG experience" | "family and career plateau constraints" |
| `oncologist` | "Whether the [agent] should... given..." | "accept the 3x salary Medical Director role at Merck" | "46-year-old oncologist" | "family, career, and patient commitments" |
| `parenting_teen` | "[Agent] deciding how to... while..." | "protect 14-year-old daughter from 19-year-old online groomer" | "Mother" | "rebuilding trust amid divorce and custody sharing" |
| `phd_research` | "[Agent] deciding between... amid..." | "between three dissertation directions" | "Third-year PhD student" | "advisor's retirement in 2-3 years and 3-month deadline" |
| `real_estate` | "Whether the [agent] should... in..." | "raise their $905K offer on a $850K asking 1940s Somerville house needing $120K work, up to $950K" | "the couple" | "a 6-offer bidding war with deadline tomorrow" |
| `startup_pivot` | "[Agent] decides whether to... amid..." | "pivot B2B SaaS product from current offering to new workflow tool" | "Solo founder" | "flat growth, $4K MRR, and 14 months runway" |
| `user_has_plan` | "Whether the user should... or..., given..." | "launch independent B2B fintech consulting practice in 6 weeks or delay" | "the user" | "no committed pipeline and 8-month zero-revenue runway" |
| `whistleblower` | "Whether the [agent] should..., balancing..." | "report witnessing a senior partner shredding client documents during an active regulatory audit" | "mid-level consultant" | "legal, career, and moral risks" |

**Hypothesis (confirmed by 10/10 cases):**

- **Wrapper template** (10 of 10): pure extractor synthesis. "Whether X should Y" / "[Agent] decid[ing/es] Z amid W". Always inferred. Never anchorable.
- **Decision verb + object** (10 of 10): substring-grounded. Every case has the decision pulled directly from user turns 1-2 ("$10K", "Seattle job offer", "three job offers", "raise their offer up to $950K"). Anchorable.
- **Agent description** (10 of 10): substring-grounded with mild paraphrase. "12 years FAANG experience" comes from "12 years experience, currently at a FAANG"; "46-year-old oncologist" from user's self-description; "Solo founder" from "Solo founder". Anchorable.
- **Context clause** (10 of 10): substring-grounded across multiple user turns. "$4K MRR and 14 months runway" appears verbatim in turn 1; "family, career, and patient commitments" synthesizes constraints stated across turns. Anchorable, often multi-turn.

So the inferred rate is roughly **25%** of components (the wrapper template only). Significantly LESS inferred than original_framing (whose exclusions were 100% inferred).

## Comparison to `original_framing`

| Field | Wrapper inferred | Substantive content anchored |
|---|---|---|
| `original_framing` | yes ("seeks/assumes/excludes" structure) | situation 100%, assumption 50%, exclusion 0% |
| `decision_situation` | yes ("Whether X should Y" structure) | decision 100%, agent 100%, context 100% |

`decision_situation` is *more* anchorable than `original_framing`, not less. The same heuristic recommendation applies a fortiori: emit as `FrameAnchor` with `DerivationProvenance` over all user turns.

## Implementation

Phase 5.8 mirrors Phase 5.7's PR (#27) with one change: a second FrameAnchor for `decision_situation`.

In `ir_constructor.py`:

```python
# Existing — original_framing FrameAnchor (Phase 5.7 heuristic)
if context.extraction.original_framing:
    ...  # FrameAnchor(anchor_id="frame_001", frame_pattern="original_framing", ...)

# New — decision_situation FrameAnchor (Phase 5.8 heuristic)
if context.extraction.decision_situation:
    user_turn_refs = tuple(...)  # all user turns
    ir = add_frame_anchor(
        ir,
        FrameAnchor(
            anchor_id="frame_002",
            text=context.extraction.decision_situation,
            provenance=DerivationProvenance(
                turn_refs=user_turn_refs,
                source_object_ids=(),
                note=(
                    "decision_situation is multi-turn extractor synthesis; "
                    "decision/agent/context parts are substring-grounded across "
                    "user turns, the 'Whether X should Y' wrapper is inferred"
                ),
            ),
            frame_pattern="decision_situation",
        ),
    )
```

Same defensive fallback to `TurnRefProvenance` if no user turns exist.

## What this commits us to watching

Same as Phase 5.7: when lane packet builders (Phase 4) land, they'll surface whether per-component substring excerpts within the FrameAnchor are needed. If yes, an LLM specialist becomes worthwhile. Until then, both `original_framing` and `decision_situation` ship with honest multi-turn provenance for free.

## Falsification: when to revisit

Run a formal Phase 5.8 gate IF:

1. A lane packet builder consumer ships and complains "I can't drill into the decision-object substring directly"
2. The corpus shifts to include cases with `decision_situation` text containing material extractor invention (e.g., dollar amounts substituted, demographics fabricated) — current 10 cases show no such cases
3. Production telemetry (once cost/token tracking lands) reveals that lanes consume `decision_situation` heavily and would benefit from sub-anchoring

None of these triggers exist today. Ship the heuristic.
