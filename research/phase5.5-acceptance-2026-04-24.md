# Phase 5.5 dropped_threads specialist — acceptance (partial pass)

**Date:** 2026-04-24
**Branch:** `feat/conversation-first-phase-5.5-dropped-threads`
**Task file:** `tasks/tasks-conversation-first-phase-5.5-dropped-threads-specialist.md`
**Gate:** `research/phase5.5-dropped-threads-annotation-gate-2026-04-24.md` (PASS)
**Eval:** `research/phase5.5-dropped-threads-eval-2026-04-24.md`

## What shipped

An injectable LLM-backed specialist for `dropped_threads`, emitting `UserIssueEvent` objects with `SpanProvenance` spanning either user OR assistant turns. Copy-adapt of the Phase 5 scaffolding; new wrinkles: dual-speaker SOURCE, `speaker` field per event, `superseded_by` label passthrough, single-span-only for v1 (no derivation — all 9 gate items had clean single-turn anchors).

Same injection pattern: `construct_conversation_ir(context, dropped_threads_extractor=...)`. When provided, REPLACES the monolith's `dropped_threads → UserIssueEvent` mapping. `live_constraints`, `original_framing`, `decision_situation` untouched.

## Acceptance against gate axes

| Axis | Target | Result | Verdict |
|---|---|---:|:---:|
| Structural artifact | 3 new files + constructor hook | ✓ | PASS |
| Unit tests | mocked-boundary tests pass | 26/26 green | PASS |
| Substring validation | every emitted event's text resolves against named speaker's turn | 100% (no fabrication in eval) | PASS |
| Speaker validation | emitted SpanRef.speaker matches claimed raised_by | enforced in-function + unit-tested + 100% in eval | PASS |
| Recall on 9 gold | ≥55% | **56%** (5/9) | PASS (at threshold) |
| Validation pass rate | ≥90% | **100%** (12/12) | PASS |
| Kind agreement | ≥75% | **40%** (2/5 matched) | **FAIL** |
| Speaker agreement | ≥90% | **100%** (5/5) | PASS |
| Constructor no-harm (default None) | existing tests pass | 325/325 full-suite | PASS |
| Lane behavior unchanged | pipeline tests green | 325/325 | PASS |
| Kill criteria (strict) | recall <45% OR validation <85% OR fabrication >5% | 56% / 100% / 0% | **NOT TRIPPED** |

**Outcome: PARTIAL PASS.** 3 of 4 primary gate thresholds clear. Kind agreement fails at 40% vs 75%. Strict kill criteria not tripped. Ship decision is PM judgment, not automatic.

## Decision: SHIP (Option A)

PM call on 2026-04-24: ship the specialist behind the optional `dropped_threads_extractor` hook with documented kind-agreement caveat. Rationale:

1. **Mechanism works.** 100% validation pass rate, 100% speaker agreement, zero fabrication. The specialist never invents content and always picks from the correct speaker's turn.
2. **Kind disagreement is methodological, not a bug.** All 3 kind mismatches (WB-D1, FRI-D1, MSY-D1) were items BOTH reviewers flagged `kind_ambiguity=yes` in the gate — genuinely mixed between `open_loop` and `concern`. The LLM reads the span's emotional weight and chooses `concern`; the gate took the monolith's `acknowledged_then_dropped` status and mapped to `open_loop`. Neither is wrong; they're different axes of the same content.
3. **No downstream consumer exists yet.** Lane packet builders (Phase 4) haven't been built. Until a consumer exercises the field, we don't know which kind axis matters operationally. Shipping Option A lets downstream eventually tell us.
4. **Iteration budget remaining.** 1 of 2 allowed iterations used. If downstream packet builders show the status-based `open_loop` axis matters more than content-based `concern`, a second prompt iteration is still available.

## What this commits us to watching

- **Kind distribution in production runs.** If the specialist emits >>50% `concern` events where the monolith would have emitted `open_loop`, the drift will be visible in `ConversationIR.provenance_tier_counts()` over time.
- **Lane consumer feedback.** When Phase 4 packet builders land, watch for complaints like "I need to filter dropped threads by whether they've been superseded" — that's a signal we need the status-based axis back.

## Observations for future specialists

### 1. Prompt iteration is Pareto-trade-prone (reconfirmed)

First-pass recall was 22% — the LLM over-emitted conversation moves (clarifying questions, final-summary bullets). One prompt iteration tightening the include/exclude rules moved recall to 56% (+34pp), validation 95% → 100%, kind 50% → 40%. **Three dimensions moved; one got worse.** Same pattern Phase 3b saw. Phase 5 avoided this by not iterating.

### 2. "Dropped thread" is inherently harder to define than "live constraint"

Live constraints are factual: a deadline, a resource limit, a fixed external input. Dropped threads are relational: one party raised X, the other pivoted. The judgment call lives in "pivoted vs addressed", which is soft. Hence the kind-agreement seam — the LLM makes legitimate content-based judgments that disagree with the monolith's status-based labels.

### 3. The monolith under-counts dropped_threads

Gate measured 9 items across 10 cases. The LLM (after tightening) emitted 12 valid events across the same 8 cases. Over-emission = 7 extras. Some of these are likely real dropped threads the monolith missed. A future gate could use reviewer-identified (not monolith-derived) gold to test whether coverage improves.

### 4. Assistant-raised threads are real

The gate had 1 assistant-raised item (PHD-D1). The LLM did not emit any assistant-raised dropped threads after tightening — it became over-conservative toward user turns. This is a gap. Future iteration should balance.

## Residual risks

1. **Kind drift from monolith.** Documented above. Watch lane consumer behavior.
2. **Assistant-raised under-emission.** The post-iteration prompt may be too user-biased. The 1 assistant-raised gold item (PHD-D1 turn 3) wasn't recovered. If downstream needs assistant-raised threads, prompt needs rework.
3. **Recall at threshold, not above it.** 56% vs 55% threshold is a thin margin. If the corpus shifts, recall could drop below.
4. **First-iteration Pareto trade.** The iteration traded 10pp of kind agreement for 34pp of recall. The trade was worth it to clear the kill criteria (recall) but locks in the kind gap.

## What's next

Per roadmap: next specialist is `original_framing` (likely derivation-heavy since framing is a cross-turn synthesis by nature). Phase 5.5's learnings argue for:

- Designing the Phase 5.7 gate with reviewer-identified framings, not monolith-derived (monolith is also paraphrased for framing).
- Expecting the derivation code path from Phase 5 to finally get exercised.
- Measuring kind separately from recall; they're independent axes on a soft task.

Phase 5.5 ships.
