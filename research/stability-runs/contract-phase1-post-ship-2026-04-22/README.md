# Post-ship acceptance gate — Extraction Contract Phase 1

**Date:** 2026-04-22
**Extractor:** `feat/extraction-contract-phase-1-live-constraints` (commit 3340a24 + 28e9440)
**Result:** **PAUSED — canonical_key Jaccard axes below target.**

## Summary

| Axis | Target | Actual | Pass? |
|---|---|---|---|
| Mode C N=5 `canonical_key` Jaccard (empty-excl) | ≥ 0.80 | **0.466** | ❌ FAIL |
| Cross-capture (9 captures) `canonical_key` Jaccard (empty-excl) | ≥ 0.70 | **0.332** | ❌ FAIL |
| Mode C `invalid_key_rate` | ≤ 10% | 0.0% | ✅ PASS |
| Cross-capture `invalid_key_rate` | ≤ 10% | 0.0% | ✅ PASS |
| Qualitative: canonical_keys read as stable identifiers | yes | MIXED — format solid, identity drifts (see spot-check) | PARTIAL |
| Regression: `live_constraints.constraint` exact-text Jaccard | no decrease | Mode C 0.000 → **0.330** (+0.330); cross 0.010 → **0.064** (+0.054) | ✅ IMPROVED (bonus side-effect) |
| Regression: `decision_situation` similarity | no decrease | Mode C 0.365 → 0.282 (−0.083); cross 0.367 → 0.359 (−0.008) | ❌ Mode C regressed |
| Regression: `original_framing` similarity | no decrease | Mode C 0.223 → 0.181 (−0.042); cross 0.209 → 0.163 (−0.046) | ❌ regressed both |
| Regression: `synthesized_position` similarity | no decrease | Mode C 0.243 → 0.233 (−0.010); cross 0.169 → 0.175 (+0.006) | ≈ flat |
| Regression: `reasoning_passages` Jaccard | no decrease | Mode C 0.493 → 0.371 (−0.122); cross 0.357 → 0.418 (+0.061) | MIXED |
| Regression: `dropped_threads` Jaccard | no decrease | Mode C 0.000 → 0.100 (+0.100); cross 0.132 → 0.090 (−0.042) | MIXED |
| Fabricated-quote count | 0 always | Mode C 0; cross-capture 3 total (one run had 1, another had 2) | ❌ new fabrications cross-capture |

## Why it failed

See `qualitative-spot-check.md` for the detailed pattern. One-line read: the **slug format rule works (0% invalid) but the slug identity rule doesn't force a single canonical answer when a constraint has multiple plausible subjects.** The LLM oscillates between semantically-equivalent valid slugs:

- `marcus-comp` / `marcus-comp-below-market` / `marcus-comp-undermarket` — same concept, 3 valid slugs.
- `marcus-retention-risk` / `team-retention-risk` / `engineer-retention-risk` / `talent-retention-risk` / `engineer-flight-risk` — same concept, 5 valid slugs.
- `platform-prototype` (9/14) / `platform-productization` / `platform-idea` — same concept, 3 valid slugs.

Exact-text Jaccard treats near-matches as disjoint. The concept-level agreement is higher than 0.466 / 0.332; the metric just doesn't see it.

## What's still valuable even on this pause

1. **Exact-text Jaccard on `constraint` improved massively** (Mode C 0.000 → 0.330 — thirty-point improvement from nothing). The ≤120-char canonical-form rule is doing real work. This alone was the biggest quantitative signal in the observations doc's baseline.
2. **Invalid_key_rate = 0%** across all 14 runs. The regex format is well-specified; the LLM obeys it reliably.
3. **Ship-or-stop discipline held.** The acceptance gate caught a failure the pre-ship doc authors didn't predict. The honesty clause about Marcus-only validation wasn't the limit — the measurement metric itself was miscalibrated for the actual failure mode.

## What's concerning beyond the headline

- **Fabricated-quote count regressed on cross-capture** from 0/9 to 3/9 (one capture produced 1 fabrication, another 2). Needs investigation: is the expanded live_constraints prompt crowding attention on reasoning_passages?
- **`original_framing` regressed on both axes.** Similarly possibly a crowding effect of the larger prompt.
- **`decision_situation` regressed Mode C.** Smaller but directionally consistent with "expanded prompt = noisier other fields."

## Decision points for the user

These are big-picture calls I won't make unilaterally:

### (A) How to interpret "failure"

Option A1 — **Strict reading**: the gate failed. Pause PR #1, revise either the prompt (force deterministic slug) or the metric (fuzzy / embedding-based) before re-measuring.
Option A2 — **Partial-win reading**: ship the pieces that work (≤120-char rule + validator + harness metrics), defer the canonical_key prompt-rule to iteration. Split into two PRs.
Option A3 — **Re-hypothesize**: the 0.80 / 0.70 targets assumed exact-text would work. Evidence says it won't for this field type. Move to embedding-cosine on slugs (Option C from the observations doc) and keep the prompt as-is.

My read: **A2 or A3 is more truthful than A1.** The prompt change did produce real canonical-form slugs; the metric is undercounting concept-agreement. A1 risks over-tuning the prompt to a metric that might itself be wrong.

### (B) How to diagnose the regressions on other fields

Single hypothesis: the expanded `live_constraints` block (canonical_key rules + examples + canonical-form + good/bad examples) is ~3× the previous size and may be pulling attention away from other fields. Check: re-run with a condensed canonical_key block and see if other-field similarity recovers.

### (C) Fabricated-quote regression

Three fabrications on cross-capture where pre-ship had zero is a signal, not noise. Warrants a look at which captures produced them before proceeding.

## Artifacts in this directory

- `modec-n5/` — Mode C N=5 post-ship: drift.json + drift.md + runs.txt + config.json.
- `cross-capture/` — 9 post-ship extractions (1 per Marcus capture).
- `cross-capture-drift/` — drift.json + drift.md + runs.txt + config.json from `--from-extractions` on the 9 cross-capture JSONs.
- `qualitative-spot-check.md` — slug-cluster analysis showing the near-match pattern.
- `README.md` — this file.

## Status

**Roadmap PR #1 flipped from `IN PROGRESS` to `PAUSED`.** No PR opened. Awaiting user decision on A / B / C.
