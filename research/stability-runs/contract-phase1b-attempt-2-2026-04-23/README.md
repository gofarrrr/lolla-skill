# PR #1b — Attempt 2 (canonical_key rules in SCHEMA NOTES footer, inline reference)

**Date:** 2026-04-23
**Prompt variant:** canonical_key inside live_constraints block is a 1-line reference ("see SCHEMA NOTES below"); full rules live in a new SCHEMA NOTES footer section at the end of the prompt.
**Hypothesis:** move the rule out of the live_constraints block so attention competition within that block doesn't bleed to adjacent fields.
**Result:** Primary metric FAILED; pollution partially reduced on one field (reasoning_passages) but worsened on another (live_constraints exact-text). Trade, not a fix.

## Numbers (cross-capture, 36 pairs)

| Metric | Attempt 2 | Attempt 1 | Diagnostic (no canonical_key) | Target |
|---|---|---|---|---|
| canonical_key embedding cosine (mean) | **0.664** | 0.787 | n/a | ≥ 0.70 → **FAIL** |
| canonical_key embedding cosine (min) | 0.516 | 0.620 | n/a | ≥ 0.50 → PASS (barely) |
| invalid_key_rate overall | 0.000 | 0.000 | n/a | ≤ 10% → PASS |
| original_framing similarity | 0.152 | 0.136 | 0.218 | no decrease → FAIL (slightly less bad than attempt 1) |
| decision_situation similarity | 0.287 | 0.280 | 0.335 | no decrease > 0.03 → FAIL |
| live_constraints exact-text Jaccard | 0.020 | 0.050 | 0.109 | no decrease → FAIL (worse than attempt 1) |
| dropped_threads Jaccard | 0.032 | 0.013 | 0.117 | no decrease → FAIL |
| reasoning_passages Jaccard | 0.560 | 0.396 | 0.393 | **IMPROVED over attempt 1** |
| synthesized_position similarity | 0.154 | 0.162 | 0.165 | ≈ flat |
| fabricated count (9 runs) | 1 | 1 | 0 | always 0 → FAIL (one fabrication persists) |

## Interpretation

Trade-off: moving canonical_key to the footer reduced attention competition on the field directly after live_constraints (reasoning_passages improved 0.396 → 0.560, a real gain). But it also weakened the cue for canonical_key generation itself (embedding cosine dropped 0.787 → 0.664, below target).

The footer-reference pattern is not a clean fix. It trades one pollution problem for slug-quality degradation.

## Conclusion across both attempts

**Two iterations confirm: the canonical_key rule cannot be added to the monolithic extraction prompt without material trade-offs on other fields.** Inline placement produces good slugs but pollutes 4 adjacent fields. Footer placement reduces pollution on one field but degrades the slug quality. Neither is a clean ship.

The right architectural fix is **separate LLM calls per field** (Track A decomposition) — which structurally eliminates attention competition, not just works around it. That's out of scope for PR #1b.

## PR #1b outcome: DEFERRED

- The **embedding-cosine metric infrastructure** (`_cosine_similarity`, `_best_match_mean_cosine`, `_get_embedding`, extended `compute_extraction_drift`) is tested and works as designed. Keeping it in the codebase.
- The **canonical_key prompt addition** is REVERTED. The field is not emitted by the extractor.
- PR #1b in the roadmap flips to PAUSED with a Track-A-dependency note.
- Downstream PRs #2 (dropped_threads canonical_key) inherit the pause — re-scope or wait for Track A.
- PRs #3, #4a, #4b, #5 can proceed; they don't depend on canonical_key.
