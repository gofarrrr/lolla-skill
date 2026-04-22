# Pre-ship baseline — Extraction Contract Phase 1

**Date:** 2026-04-22
**Extractor:** current `main` (pre-PR-#1, no `canonical_key` field)
**Purpose:** establish the "before" state so post-ship acceptance-gate can verify (a) canonical_key Jaccard targets are met and (b) no regression on the fields PR #1 doesn't change.

## What's in this directory

- `modec-n5/` — Mode C drift N=5 on the newest Marcus capture (`lolla_20260422T155622Z_conversation.txt`). Measures extractor sampling variance with capture held constant.
- `cross-capture/` — 9 extraction JSONs produced by running `run_extract.py` once per archived Marcus capture. Plus `drift.json` / `drift.md` produced by `compute_cross_capture.py` computing pairwise drift across the 9.
- `compute_cross_capture.py` — one-off analysis script. Imports `compute_extraction_drift` from `scripts/stability_check.py` as a library; will be superseded by PR #1's new `--from-extractions` CLI mode.

## Baseline numbers

### Mode C N=5 (single capture, extractor variance only)

| Field | Metric | Mean | Min |
|---|---|---|---|
| `decision_situation` | similarity | 0.365 | 0.102 |
| `original_framing` | similarity | 0.223 | 0.162 |
| `synthesized_position` | similarity | 0.243 | 0.145 |
| `live_constraints` | jaccard (exact text) | **0.000** | 0.000 |
| `reasoning_passages` | jaccard (exact text) | 0.493 | 0.083 |
| `dropped_threads` | jaccard (exact text) | **0.000** | 0.000 |
| `_quote_validation.fabricated` | count per run | 0 / 0 / 0 / 0 / 0 | — |

### Cross-capture (9 Marcus captures, 1 extraction each; C(9,2)=36 pairs)

| Field | Metric | Mean | Min |
|---|---|---|---|
| `decision_situation` | similarity | 0.367 | 0.134 |
| `original_framing` | similarity | 0.209 | 0.084 |
| `synthesized_position` | similarity | 0.169 | 0.006 |
| `live_constraints` | jaccard (exact text) | **0.010** | 0.000 |
| `reasoning_passages` | jaccard (exact text) | 0.357 | 0.083 |
| `dropped_threads` | jaccard (exact text) | 0.132 | 0.000 |
| fabricated count per run | — | [0]×9 | — |

## Canonical_key baseline

**Undefined.** The field does not exist in any of the 14 pre-ship extraction outputs (confirmed by `grep -l canonical_key` returning 0 hits). The first canonical_key measurement is the post-ship Mode C + cross-capture run. No pre-ship target to beat; only the acceptance-gate targets (Mode C ≥ 0.80, cross-capture ≥ 0.70, invalid_key_rate ≤ 10%).

## What to compare post-ship

| Field | Pre-ship (Mode C N=5) | Pre-ship (cross-capture) | Post-ship gate |
|---|---|---|---|
| `live_constraints.canonical_key` jaccard (empty-excl) | undefined | undefined | Mode C ≥ 0.80; cross ≥ 0.70 |
| `invalid_key_rate` overall | undefined | undefined | ≤ 10% |
| `live_constraints.constraint` jaccard (exact text) | 0.000 | 0.010 | no decrease (bonus: tightening allowed) |
| `decision_situation` similarity | 0.365 | 0.367 | no decrease |
| `original_framing` similarity | 0.223 | 0.209 | no decrease |
| `synthesized_position` similarity | 0.243 | 0.169 | no decrease |
| `reasoning_passages` jaccard | 0.493 | 0.357 | no decrease |
| `dropped_threads` jaccard | 0.000 | 0.132 | no decrease |
| fabricated count per run | 0 | 0 | 0 always |

## Notes on the baseline

- **Confirms PR #1's motivating signal.** `live_constraints` exact-text Jaccard = 0.000 on Mode C matches the observations-doc N=3 finding (same 0.000 Jaccard). 9-capture cross-run adds 0.010 mean with 0.000 min — essentially the same "no two runs agree on exact constraint text" signal, now on a bigger sample.
- **`synthesized_position` is notably worse cross-capture (0.169 / 0.006 min) than Mode C (0.243).** The "shape drift" problem from the observations doc is visible here: different captures push the free-text synthesis in meaningfully different directions. This is PR #3's problem, not PR #1's — noted here for later reference.
- **No fabricated quotes in any of the 14 extraction runs.** The retry-then-drop validator didn't have to fire. Clean quote-validation baseline.
