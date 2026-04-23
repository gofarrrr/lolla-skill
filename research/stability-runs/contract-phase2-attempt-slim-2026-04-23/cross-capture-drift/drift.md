# Extraction drift report — contract-phase2-slim

Generated: 2026-04-23T09:18:34Z
Conversation: `cross-capture (no single conversation)` (? bytes)
Runs: 9
Run IDs: extraction_20260421T144534Z, extraction_20260421T162225Z, extraction_20260421T172513Z, extraction_20260422T091837Z, extraction_20260422T100308Z, extraction_20260422T113930Z, extraction_20260422T123205Z, extraction_20260422T130506Z, extraction_20260422T155622Z

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.879 | 0.733 | 1.000 |
| `original_framing` | similarity | 0.387 | 0.118 | 0.820 |
| `synthesized_position` | similarity | 0.182 | 0.005 | 0.378 |
| `live_constraints` | jaccard | 0.190 | 0.000 | 1.000 |
| `reasoning_passages` | jaccard | 0.430 | 0.222 | 1.000 |
| `dropped_threads` | jaccard | 0.153 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 36 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (48 invalid of 48 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.762, lengths 159 ↔ 122
- **original_framing**: similarity=0.304, lengths 193 ↔ 235
- **synthesized_position**: similarity=0.006, lengths 799 ↔ 432
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.929, lengths 159 ↔ 138
- **original_framing**: similarity=0.177, lengths 193 ↔ 214
- **synthesized_position**: similarity=0.005, lengths 799 ↔ 473
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.667, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.828, lengths 159 ↔ 138
- **original_framing**: similarity=0.247, lengths 193 ↔ 187
- **synthesized_position**: similarity=0.014, lengths 799 ↔ 638
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.929, lengths 159 ↔ 138
- **original_framing**: similarity=0.383, lengths 193 ↔ 193
- **synthesized_position**: similarity=0.044, lengths 799 ↔ 484
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.929, lengths 159 ↔ 138
- **original_framing**: similarity=0.300, lengths 193 ↔ 180
- **synthesized_position**: similarity=0.024, lengths 799 ↔ 589
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.667, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.828, lengths 159 ↔ 138
- **original_framing**: similarity=0.375, lengths 193 ↔ 255
- **synthesized_position**: similarity=0.019, lengths 799 ↔ 664
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.929, lengths 159 ↔ 138
- **original_framing**: similarity=0.560, lengths 193 ↔ 193
- **synthesized_position**: similarity=0.024, lengths 799 ↔ 607
- **live_constraints**: jaccard=1.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.741, lengths 159 ↔ 154
- **original_framing**: similarity=0.353, lengths 193 ↔ 141
- **synthesized_position**: similarity=0.022, lengths 799 ↔ 636
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.823, lengths 122 ↔ 138
- **original_framing**: similarity=0.205, lengths 235 ↔ 214
- **synthesized_position**: similarity=0.241, lengths 432 ↔ 473
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.938, lengths 122 ↔ 138
- **original_framing**: similarity=0.270, lengths 235 ↔ 187
- **synthesized_position**: similarity=0.086, lengths 432 ↔ 638
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.823, lengths 122 ↔ 138
- **original_framing**: similarity=0.364, lengths 235 ↔ 193
- **synthesized_position**: similarity=0.314, lengths 432 ↔ 484
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.823, lengths 122 ↔ 138
- **original_framing**: similarity=0.352, lengths 235 ↔ 180
- **synthesized_position**: similarity=0.259, lengths 432 ↔ 589
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.938, lengths 122 ↔ 138
- **original_framing**: similarity=0.241, lengths 235 ↔ 255
- **synthesized_position**: similarity=0.073, lengths 432 ↔ 664
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.823, lengths 122 ↔ 138
- **original_framing**: similarity=0.734, lengths 235 ↔ 193
- **synthesized_position**: similarity=0.133, lengths 432 ↔ 607
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.884, lengths 122 ↔ 154
- **original_framing**: similarity=0.207, lengths 235 ↔ 141
- **synthesized_position**: similarity=0.139, lengths 432 ↔ 636
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.559, lengths 214 ↔ 187
- **synthesized_position**: similarity=0.164, lengths 473 ↔ 638
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.762, lengths 214 ↔ 193
- **synthesized_position**: similarity=0.378, lengths 473 ↔ 484
- **live_constraints**: jaccard=0.571, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.584, lengths 214 ↔ 180
- **synthesized_position**: similarity=0.203, lengths 473 ↔ 589
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.269, lengths 214 ↔ 255
- **synthesized_position**: similarity=0.127, lengths 473 ↔ 664
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.246, lengths 214 ↔ 193
- **synthesized_position**: similarity=0.159, lengths 473 ↔ 607
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.733, lengths 138 ↔ 154
- **original_framing**: similarity=0.485, lengths 214 ↔ 141
- **synthesized_position**: similarity=0.216, lengths 473 ↔ 636
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.647, lengths 187 ↔ 193
- **synthesized_position**: similarity=0.225, lengths 638 ↔ 484
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.659, lengths 187 ↔ 180
- **synthesized_position**: similarity=0.362, lengths 638 ↔ 589
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.118, lengths 187 ↔ 255
- **synthesized_position**: similarity=0.197, lengths 638 ↔ 664
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.389, lengths 187 ↔ 193
- **synthesized_position**: similarity=0.296, lengths 638 ↔ 607
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.500, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.836, lengths 138 ↔ 154
- **original_framing**: similarity=0.494, lengths 187 ↔ 141
- **synthesized_position**: similarity=0.174, lengths 638 ↔ 636
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.820, lengths 193 ↔ 180
- **synthesized_position**: similarity=0.270, lengths 484 ↔ 589
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.188, lengths 193 ↔ 255
- **synthesized_position**: similarity=0.193, lengths 484 ↔ 664
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.316, lengths 193 ↔ 193
- **synthesized_position**: similarity=0.231, lengths 484 ↔ 607
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.500, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.733, lengths 138 ↔ 154
- **original_framing**: similarity=0.395, lengths 193 ↔ 141
- **synthesized_position**: similarity=0.225, lengths 484 ↔ 636
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.152, lengths 180 ↔ 255
- **synthesized_position**: similarity=0.327, lengths 589 ↔ 664
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.402, lengths 180 ↔ 193
- **synthesized_position**: similarity=0.303, lengths 589 ↔ 607
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.733, lengths 138 ↔ 154
- **original_framing**: similarity=0.349, lengths 180 ↔ 141
- **synthesized_position**: similarity=0.294, lengths 589 ↔ 636
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.482, lengths 255 ↔ 193
- **synthesized_position**: similarity=0.212, lengths 664 ↔ 607
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.836, lengths 138 ↔ 154
- **original_framing**: similarity=0.268, lengths 255 ↔ 141
- **synthesized_position**: similarity=0.317, lengths 664 ↔ 636
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.733, lengths 138 ↔ 154
- **original_framing**: similarity=0.287, lengths 193 ↔ 141
- **synthesized_position**: similarity=0.286, lengths 607 ↔ 636
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0
