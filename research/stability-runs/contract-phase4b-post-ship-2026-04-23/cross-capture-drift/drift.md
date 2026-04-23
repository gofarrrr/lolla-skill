# Extraction drift report — contract-phase4b-cross

Generated: 2026-04-23T09:13:27Z
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
| `decision_situation` | similarity | 0.869 | 0.677 | 1.000 |
| `original_framing` | similarity | 0.340 | 0.019 | 0.787 |
| `synthesized_position` | similarity | 0.216 | 0.003 | 0.589 |
| `live_constraints` | jaccard | 0.345 | 0.100 | 1.000 |
| `reasoning_passages` | jaccard | 0.657 | 0.375 | 1.000 |
| `dropped_threads` | jaccard | 0.222 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 36 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (48 invalid of 48 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.248, lengths 217 ↔ 259
- **synthesized_position**: similarity=0.003, lengths 799 ↔ 413
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.473, lengths 217 ↔ 168
- **synthesized_position**: similarity=0.013, lengths 799 ↔ 418
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.471, lengths 217 ↔ 165
- **synthesized_position**: similarity=0.015, lengths 799 ↔ 428
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.737, lengths 180 ↔ 170
- **original_framing**: similarity=0.329, lengths 217 ↔ 190
- **synthesized_position**: similarity=0.041, lengths 799 ↔ 517
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.323, lengths 217 ↔ 210
- **synthesized_position**: similarity=0.033, lengths 799 ↔ 423
- **live_constraints**: jaccard=0.571, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.677, lengths 180 ↔ 154
- **original_framing**: similarity=0.250, lengths 217 ↔ 191
- **synthesized_position**: similarity=0.005, lengths 799 ↔ 388
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.871, lengths 180 ↔ 160
- **original_framing**: similarity=0.391, lengths 217 ↔ 249
- **synthesized_position**: similarity=0.012, lengths 799 ↔ 739
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.871, lengths 180 ↔ 160
- **original_framing**: similarity=0.243, lengths 217 ↔ 260
- **synthesized_position**: similarity=0.021, lengths 799 ↔ 545
- **live_constraints**: jaccard=0.571, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.689, lengths 259 ↔ 168
- **synthesized_position**: similarity=0.267, lengths 413 ↔ 418
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.406, lengths 259 ↔ 165
- **synthesized_position**: similarity=0.345, lengths 413 ↔ 428
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.896, lengths 138 ↔ 170
- **original_framing**: similarity=0.432, lengths 259 ↔ 190
- **synthesized_position**: similarity=0.267, lengths 413 ↔ 517
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.776, lengths 259 ↔ 210
- **synthesized_position**: similarity=0.589, lengths 413 ↔ 423
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=1.000, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.836, lengths 138 ↔ 154
- **original_framing**: similarity=0.244, lengths 259 ↔ 191
- **synthesized_position**: similarity=0.327, lengths 413 ↔ 388
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.327, lengths 259 ↔ 249
- **synthesized_position**: similarity=0.208, lengths 413 ↔ 739
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.778, lengths 259 ↔ 260
- **synthesized_position**: similarity=0.336, lengths 413 ↔ 545
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=1.000, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.456, lengths 168 ↔ 165
- **synthesized_position**: similarity=0.300, lengths 418 ↔ 428
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.896, lengths 138 ↔ 170
- **original_framing**: similarity=0.374, lengths 168 ↔ 190
- **synthesized_position**: similarity=0.368, lengths 418 ↔ 517
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.487, lengths 168 ↔ 210
- **synthesized_position**: similarity=0.245, lengths 418 ↔ 423
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.836, lengths 138 ↔ 154
- **original_framing**: similarity=0.334, lengths 168 ↔ 191
- **synthesized_position**: similarity=0.189, lengths 418 ↔ 388
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.283, lengths 168 ↔ 249
- **synthesized_position**: similarity=0.311, lengths 418 ↔ 739
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.411, lengths 168 ↔ 260
- **synthesized_position**: similarity=0.272, lengths 418 ↔ 545
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.896, lengths 138 ↔ 170
- **original_framing**: similarity=0.293, lengths 165 ↔ 190
- **synthesized_position**: similarity=0.286, lengths 428 ↔ 517
- **live_constraints**: jaccard=1.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.027, lengths 165 ↔ 210
- **synthesized_position**: similarity=0.216, lengths 428 ↔ 423
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.836, lengths 138 ↔ 154
- **original_framing**: similarity=0.309, lengths 165 ↔ 191
- **synthesized_position**: similarity=0.167, lengths 428 ↔ 388
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.019, lengths 165 ↔ 249
- **synthesized_position**: similarity=0.214, lengths 428 ↔ 739
- **live_constraints**: jaccard=0.833, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.099, lengths 165 ↔ 260
- **synthesized_position**: similarity=0.452, lengths 428 ↔ 545
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.896, lengths 170 ↔ 138
- **original_framing**: similarity=0.215, lengths 190 ↔ 210
- **synthesized_position**: similarity=0.177, lengths 517 ↔ 423
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.951, lengths 170 ↔ 154
- **original_framing**: similarity=0.488, lengths 190 ↔ 191
- **synthesized_position**: similarity=0.316, lengths 517 ↔ 388
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.836, lengths 170 ↔ 160
- **original_framing**: similarity=0.155, lengths 190 ↔ 249
- **synthesized_position**: similarity=0.220, lengths 517 ↔ 739
- **live_constraints**: jaccard=0.833, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.836, lengths 170 ↔ 160
- **original_framing**: similarity=0.133, lengths 190 ↔ 260
- **synthesized_position**: similarity=0.247, lengths 517 ↔ 545
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.836, lengths 138 ↔ 154
- **original_framing**: similarity=0.309, lengths 210 ↔ 191
- **synthesized_position**: similarity=0.244, lengths 423 ↔ 388
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.353, lengths 210 ↔ 249
- **synthesized_position**: similarity=0.217, lengths 423 ↔ 739
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.787, lengths 210 ↔ 260
- **synthesized_position**: similarity=0.254, lengths 423 ↔ 545
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=1.000, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.777, lengths 154 ↔ 160
- **original_framing**: similarity=0.041, lengths 191 ↔ 249
- **synthesized_position**: similarity=0.140, lengths 388 ↔ 739
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.777, lengths 154 ↔ 160
- **original_framing**: similarity=0.084, lengths 191 ↔ 260
- **synthesized_position**: similarity=0.292, lengths 388 ↔ 545
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.833, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=1.000, lengths 160 ↔ 160
- **original_framing**: similarity=0.189, lengths 249 ↔ 260
- **synthesized_position**: similarity=0.167, lengths 739 ↔ 545
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0
