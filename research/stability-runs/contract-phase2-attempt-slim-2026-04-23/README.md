# PR #2 — Both Attempts Failed, PR Paused

**Date:** 2026-04-23
**Outcome:** PAUSED. Reverted. Deferred to Track A window alongside PR #1b (canonical_key).

## What was tried and what happened

### Attempt 1 — thread ≤120-char rule + tie-break prose

Added both the ≤120-char terse-form rule on `thread` AND a tie-break paragraph at the end of the prompt describing "third-party concern briefly addressed → live_constraint, not dropped_thread unless user abandoned it."

Cross-capture result (vs PR #4b baseline):
- dropped_threads (target): 0.222 → 0.278 (+0.056 ✓ hit target ≥ 0.20)
- reasoning_passages: 0.657 → **0.401 (−0.256)** ❌
- live_constraints: 0.345 → 0.261 (−0.084)
- synthesized_position: 0.216 → 0.166 (−0.050)
- decision_situation: 0.869 → 0.833 (−0.036 just outside noise)

Evidence at `research/stability-runs/contract-phase2-attempt-with-tiebreak-2026-04-23/`.

Interpretation: target field gained modestly; reasoning_passages crashed. Not a ship. The tie-break prose added ~400 chars of prompt text.

### Attempt 2 — thread ≤120-char rule only (tie-break removed)

Removed the tie-break paragraph, kept just the ≤120-char rule on thread text with one good/bad example.

Cross-capture result (vs PR #4b baseline):
- dropped_threads (target): 0.222 → **0.153 (−0.069)** ❌ target field REGRESSED
- reasoning_passages: 0.657 → 0.430 (−0.227)
- live_constraints: 0.345 → 0.190 (−0.155)
- original_framing: 0.340 → 0.387 (+0.047)
- decision_situation: 0.869 → 0.879 (+0.010)

Evidence at this directory (`contract-phase2-attempt-slim-2026-04-23/`).

Interpretation: the thread ≤120-char rule ALONE made the target field worse. The prompt addition's pollution cost exceeded its direct benefit even on its own target field.

## Doctrine observation: the prompt is at pollution saturation

After PR #4a + PR #4b, dropped_threads was already at 0.222 cross-capture (up from 0.117 pre-PR-#4a) — a 90% improvement from the terse-discipline ripple effect of PR #4a/#4b, with ZERO direct intervention on dropped_threads.

Adding an explicit ≤120-char rule on `thread` made it worse, not better. The extraction prompt has reached a state where each new rule addition costs more in pollution than it gives in direct field improvement. Continuing to stack prompt rules is net-negative.

## Pattern match with PR #1b

Both PR #1b and PR #2 hit the same wall:
- PR #1b (canonical_key): inline or footer, both iterations traded primary-field gain for adjacent-field pollution.
- PR #2 (dropped_threads): slim or with-tiebreak, both iterations traded primary-field outcome for adjacent-field regressions.

The structural fix for both is the same: **Track A decomposition** (separate LLM call per field). A field getting its own dedicated LLM call with only the context it needs escapes the attention-competition problem. Track A is deferred per the Cycle-1 handover; PR #1b and PR #2 are paused until Track A unblocks.

## Impact on roadmap

- PR #2 flipped to PAUSED.
- dropped_threads state preserved at PR #4b's 0.222 cross-capture (best of any tested state).
- PRs #3, #5 can still proceed; they don't depend on PR #2.
- After Track A ships, revisit PR #2 as part of the canonical_key + dropped_threads reconsideration window.

## What about the tie-break rule specifically?

The tie-break logic (third-party concern → live_constraint not dropped_thread) is a content rule that's orthogonal to canonical_key. It could be tried again as a tiny prompt addition (≤100 chars, no prose example) after Track A lands, when each field's dedicated call has budget for one terse additional instruction. Not shipping as part of this PR.
