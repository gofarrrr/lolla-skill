# Extraction drift report — contract-phase1b-iter2-cross

Generated: 2026-04-23T09:02:53Z
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
| `decision_situation` | similarity | 0.287 | 0.077 | 0.825 |
| `original_framing` | similarity | 0.152 | 0.028 | 0.595 |
| `synthesized_position` | similarity | 0.154 | 0.009 | 0.383 |
| `live_constraints` | jaccard | 0.020 | 0.000 | 0.222 |
| `reasoning_passages` | jaccard | 0.560 | 0.200 | 1.000 |
| `dropped_threads` | jaccard | 0.032 | 0.000 | 0.250 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | 0.215 | 0.000 | 0.667 |
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | 0.664 | 0.516 | 0.881 |

**`invalid_key_rate` per run:** [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
**`invalid_key_rate` overall:** 0.000 (0 invalid of 50 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 1, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.415, lengths 271 ↔ 505
- **original_framing**: similarity=0.119, lengths 364 ↔ 293
- **synthesized_position**: similarity=0.044, lengths 799 ↔ 561
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.825, lengths 271 ↔ 277
- **original_framing**: similarity=0.274, lengths 364 ↔ 338
- **synthesized_position**: similarity=0.009, lengths 799 ↔ 495
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.144, lengths 271 ↔ 411
- **original_framing**: similarity=0.035, lengths 364 ↔ 256
- **synthesized_position**: similarity=0.017, lengths 799 ↔ 573
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.159, lengths 271 ↔ 295
- **original_framing**: similarity=0.075, lengths 364 ↔ 274
- **synthesized_position**: similarity=0.009, lengths 799 ↔ 586
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=0, b=1

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.122, lengths 271 ↔ 498
- **original_framing**: similarity=0.235, lengths 364 ↔ 351
- **synthesized_position**: similarity=0.015, lengths 799 ↔ 717
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.091, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.134, lengths 271 ↔ 340
- **original_framing**: similarity=0.183, lengths 364 ↔ 399
- **synthesized_position**: similarity=0.028, lengths 799 ↔ 720
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.444, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.135, lengths 271 ↔ 423
- **original_framing**: similarity=0.104, lengths 364 ↔ 387
- **synthesized_position**: similarity=0.015, lengths 799 ↔ 631
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.536, lengths 271 ↔ 337
- **original_framing**: similarity=0.258, lengths 364 ↔ 325
- **synthesized_position**: similarity=0.024, lengths 799 ↔ 629
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.450, lengths 505 ↔ 277
- **original_framing**: similarity=0.067, lengths 293 ↔ 338
- **synthesized_position**: similarity=0.062, lengths 561 ↔ 495
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.250, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.190, lengths 505 ↔ 411
- **original_framing**: similarity=0.106, lengths 293 ↔ 256
- **synthesized_position**: similarity=0.049, lengths 561 ↔ 573
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.147, lengths 505 ↔ 295
- **original_framing**: similarity=0.095, lengths 293 ↔ 274
- **synthesized_position**: similarity=0.134, lengths 561 ↔ 586
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.100, counts 5 ↔ 6
- **fabricated**: a=0, b=1

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.130, lengths 505 ↔ 498
- **original_framing**: similarity=0.112, lengths 293 ↔ 351
- **synthesized_position**: similarity=0.016, lengths 561 ↔ 717
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.100, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.095, lengths 505 ↔ 340
- **original_framing**: similarity=0.090, lengths 293 ↔ 399
- **synthesized_position**: similarity=0.083, lengths 561 ↔ 720
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.444, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.110, lengths 505 ↔ 423
- **original_framing**: similarity=0.074, lengths 293 ↔ 387
- **synthesized_position**: similarity=0.027, lengths 561 ↔ 631
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.684, lengths 505 ↔ 337
- **original_framing**: similarity=0.236, lengths 293 ↔ 325
- **synthesized_position**: similarity=0.015, lengths 561 ↔ 629
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.250, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.142, lengths 277 ↔ 411
- **original_framing**: similarity=0.040, lengths 338 ↔ 256
- **synthesized_position**: similarity=0.268, lengths 495 ↔ 573
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.154, lengths 277 ↔ 295
- **original_framing**: similarity=0.157, lengths 338 ↔ 274
- **synthesized_position**: similarity=0.339, lengths 495 ↔ 586
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=1

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.129, lengths 277 ↔ 498
- **original_framing**: similarity=0.505, lengths 338 ↔ 351
- **synthesized_position**: similarity=0.259, lengths 495 ↔ 717
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.100, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.136, lengths 277 ↔ 340
- **original_framing**: similarity=0.537, lengths 338 ↔ 399
- **synthesized_position**: similarity=0.257, lengths 495 ↔ 720
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.137, lengths 277 ↔ 423
- **original_framing**: similarity=0.028, lengths 338 ↔ 387
- **synthesized_position**: similarity=0.298, lengths 495 ↔ 631
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.580, lengths 277 ↔ 337
- **original_framing**: similarity=0.124, lengths 338 ↔ 325
- **synthesized_position**: similarity=0.249, lengths 495 ↔ 629
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.176, lengths 411 ↔ 295
- **original_framing**: similarity=0.042, lengths 256 ↔ 274
- **synthesized_position**: similarity=0.053, lengths 573 ↔ 586
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.091, counts 6 ↔ 6
- **fabricated**: a=0, b=1

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.464, lengths 411 ↔ 498
- **original_framing**: similarity=0.036, lengths 256 ↔ 351
- **synthesized_position**: similarity=0.202, lengths 573 ↔ 717
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.091, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.362, lengths 411 ↔ 340
- **original_framing**: similarity=0.070, lengths 256 ↔ 399
- **synthesized_position**: similarity=0.045, lengths 573 ↔ 720
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.625, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.537, lengths 411 ↔ 423
- **original_framing**: similarity=0.059, lengths 256 ↔ 387
- **synthesized_position**: similarity=0.154, lengths 573 ↔ 631
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.094, lengths 411 ↔ 337
- **original_framing**: similarity=0.055, lengths 256 ↔ 325
- **synthesized_position**: similarity=0.155, lengths 573 ↔ 629
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.366, lengths 295 ↔ 498
- **original_framing**: similarity=0.147, lengths 274 ↔ 351
- **synthesized_position**: similarity=0.173, lengths 586 ↔ 717
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=1, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.409, lengths 295 ↔ 340
- **original_framing**: similarity=0.184, lengths 274 ↔ 399
- **synthesized_position**: similarity=0.302, lengths 586 ↔ 720
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=1, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.345, lengths 295 ↔ 423
- **original_framing**: similarity=0.088, lengths 274 ↔ 387
- **synthesized_position**: similarity=0.196, lengths 586 ↔ 631
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=1, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.171, lengths 295 ↔ 337
- **original_framing**: similarity=0.097, lengths 274 ↔ 325
- **synthesized_position**: similarity=0.295, lengths 586 ↔ 629
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=1, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.484, lengths 498 ↔ 340
- **original_framing**: similarity=0.595, lengths 351 ↔ 399
- **synthesized_position**: similarity=0.164, lengths 717 ↔ 720
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.660, lengths 498 ↔ 423
- **original_framing**: similarity=0.087, lengths 351 ↔ 387
- **synthesized_position**: similarity=0.372, lengths 717 ↔ 631
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.000, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.077, lengths 498 ↔ 337
- **original_framing**: similarity=0.257, lengths 351 ↔ 325
- **synthesized_position**: similarity=0.290, lengths 717 ↔ 629
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.469, lengths 340 ↔ 423
- **original_framing**: similarity=0.071, lengths 399 ↔ 387
- **synthesized_position**: similarity=0.249, lengths 720 ↔ 631
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.095, lengths 340 ↔ 337
- **original_framing**: similarity=0.130, lengths 399 ↔ 325
- **synthesized_position**: similarity=0.301, lengths 720 ↔ 629
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.084, lengths 423 ↔ 337
- **original_framing**: similarity=0.101, lengths 387 ↔ 325
- **synthesized_position**: similarity=0.383, lengths 631 ↔ 629
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0
