# PR #1b — Attempt 1 (canonical_key inline in live_constraints block)

**Date:** 2026-04-23
**Prompt variant:** canonical_key rules INLINE as first subfield of live_constraints block (~240 chars added).
**Result:** Primary metric PASSED; pollution sentinel FAILED.

## Numbers (cross-capture, 36 pairs)

| Metric | Value | vs diagnostic (pre-1b) | vs target |
|---|---|---|---|
| canonical_key embedding cosine (mean) | **0.787** | n/a (new) | ≥ 0.70 → **PASS** |
| canonical_key embedding cosine (min) | 0.620 | n/a | ≥ 0.50 → PASS |
| invalid_key_rate overall | 0.000 | n/a | ≤ 10% → PASS |
| original_framing similarity (SENTINEL) | 0.136 | 0.218 (−0.082) | no decrease → **FAIL** |
| decision_situation similarity | 0.280 | 0.335 (−0.055) | no decrease > 0.03 → FAIL |
| live_constraints exact-text Jaccard | 0.050 | 0.109 (−0.059) | no decrease → FAIL |
| dropped_threads Jaccard | 0.013 | 0.117 (−0.104) | no decrease → FAIL |
| reasoning_passages Jaccard | 0.396 | 0.393 | ≈ flat |
| synthesized_position similarity | 0.162 | 0.165 | ≈ flat |
| fabricated count (9 runs) | 1 | 0 | always 0 → FAIL |

## Interpretation

Primary architectural validation succeeded: the EDC/Zep-style pattern (free extraction + embedding-cosine metric) achieves 0.787 cross-capture semantic agreement on canonical_key. This is the main thing PR #1b was supposed to prove.

But the prompt addition caused context pollution on 4 adjacent fields, some significantly. This mirrors (smaller than) PR #1 C-full's pattern.
