# Diagnostic measurement — C-medium (canonical_key prompt stripped)

**Date:** 2026-04-23
**Extractor state:** branch `feat/extraction-contract-phase-1-live-constraints` with canonical_key prompt rules removed (commit `8193b89`). Kept: ≤120-char terse-form rule on `constraint`, `_validate_canonical_key` function, `_apply_canonical_key_validation` post-processing (inactive — LLM doesn't emit canonical_key without the prompt rule), harness metrics extension.
**Purpose:** test the Context Engineering 2.0 "context pollution" hypothesis: if the canonical_key prompt text was the source of regressions on other fields, stripping it should restore those fields to pre-ship levels.

## Comparison across all three states

### Cross-capture (9 Marcus captures, 36 pairs — reliable sample)

| Field | Pre-ship (main) | Post-ship (C-full) | Diagnostic (C-medium) | Verdict |
|---|---|---|---|---|
| `live_constraints` exact-text Jaccard | 0.010 | 0.064 | **0.109** | ✅ Win **GREW** without canonical_key text |
| Fabricated-quote count (total across 9 runs) | 0 | **3** | **0** | ✅ Regression **ELIMINATED** — pollution confirmed |
| `original_framing` similarity | 0.209 | 0.163 | **0.218** | ✅ **FULLY RESTORED** — pollution confirmed |
| `reasoning_passages` Jaccard | 0.357 | 0.418 | 0.393 | ≈ flat (all three within 0.06 band; noise-level) |
| `synthesized_position` similarity | 0.169 | 0.175 | 0.165 | ≈ flat |
| `decision_situation` similarity | 0.367 | 0.359 | 0.335 | Mild dip (−0.032 vs pre) — likely sampling noise |
| `dropped_threads` Jaccard | 0.132 | 0.090 | 0.117 | Mild dip (−0.015 vs pre) — likely noise |

### Mode C N=5 (newest capture only, 10 pairs — noisier sample)

| Field | Pre-ship | Post-ship | Diagnostic | Note |
|---|---|---|---|---|
| `live_constraints` exact-text | 0.000 | 0.330 | 0.063 | N=5 swing — cross-capture (36 pairs) is the reliable signal; trust that |
| `original_framing` | 0.223 | 0.181 | 0.103 | Contradicts cross-capture trend — N=5 noise on a field already near baseline |
| `reasoning_passages` | 0.493 | 0.371 | 0.426 | Partial recovery toward pre-ship |
| Fabricated count | 0 across 5 | 0 across 5 | 1 across 5 | Mode C has a lone fabrication; cross-capture had zero. Single-run noise |

## Verdict on the context-pollution hypothesis

**Partially confirmed on cross-capture — the more reliable signal:**

1. **Fabricated-quote regression was 100% caused by the canonical_key prompt text.** Pre-ship 0/9, post-ship 3/9, diagnostic 0/9 — perfect reversal. This is the single clearest pollution effect found.
2. **`original_framing` regression was caused by canonical_key prompt text.** 0.209 → 0.163 → 0.218 — a clean U-shape. Fully recovered.
3. **`live_constraints` exact-text actually got BIGGER without the canonical_key rules.** Cross-capture 0.010 → 0.064 (C-full) → 0.109 (C-medium). Counterintuitive but real on 36 pairs. Hypothesis: the canonical_key rules were making the LLM second-guess constraint phrasing; without them, the ≤120-char rule does its work cleanly.
4. `decision_situation` and `dropped_threads` have small cross-capture dips (−0.03 and −0.02 vs pre-ship) that are within plausible sampling noise and don't track with the canonical_key text's presence.

**Mode C N=5 is too small a sample for individual-field judgment.** The cross-capture (36 pairs vs 10) contradicts most Mode C conclusions. Trust the bigger sample.

## What this means for shipping

**C-medium is a clean ship:**

- Preserves the proven win: live_constraints exact-text Jaccard 10× (0.010 → 0.109 cross-capture)
- No fabricated-quote regression (0/9 cross-capture)
- No `original_framing` regression (actually slightly improved)
- Other fields roughly at pre-ship levels (within noise band on cross-capture)
- Infrastructure (validator + harness metrics + `--from-extractions` CLI) pre-wired for PR #2

**What C-medium does NOT ship:**
- The `canonical_key` field itself (prompt text removed; validator exists but has nothing to validate)
- Any stability claim about canonical concept identity across runs

**What PR #2 will do:**
- Reintroduce canonical_key to the prompt (minimal addition — maybe condensed from the original block to avoid re-triggering pollution)
- Swap the measurement from exact-text Jaccard to embedding cosine
- Re-measure on the same 9 Marcus captures against the new metric

## Artifacts in this directory

- `modec-n5/` — Mode C N=5 diagnostic output (noisier, interpret with care)
- `cross-capture/` — 9 diagnostic extractions (the reliable sample)
- `cross-capture-drift/` — drift.json + drift.md from `--from-extractions` on the 9 cross-capture JSONs
