# Extraction drift report — contract-phase1-diagnostic-cross

Generated: 2026-04-23T07:31:59Z
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
| `decision_situation` | similarity | 0.335 | 0.044 | 0.973 |
| `original_framing` | similarity | 0.218 | 0.016 | 0.663 |
| `synthesized_position` | similarity | 0.165 | 0.005 | 0.358 |
| `live_constraints` | jaccard | 0.109 | 0.000 | 0.429 |
| `reasoning_passages` | jaccard | 0.393 | 0.083 | 0.857 |
| `dropped_threads` | jaccard | 0.117 | 0.000 | 0.667 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 36 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (49 invalid of 49 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.432, lengths 532 ↔ 375
- **original_framing**: similarity=0.265, lengths 396 ↔ 328
- **synthesized_position**: similarity=0.013, lengths 1178 ↔ 655
- **live_constraints**: jaccard=0.091, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.500, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.442, lengths 532 ↔ 355
- **original_framing**: similarity=0.273, lengths 396 ↔ 300
- **synthesized_position**: similarity=0.005, lengths 1178 ↔ 586
- **live_constraints**: jaccard=0.091, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.170, lengths 532 ↔ 419
- **original_framing**: similarity=0.034, lengths 396 ↔ 313
- **synthesized_position**: similarity=0.016, lengths 1178 ↔ 610
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.449, lengths 532 ↔ 489
- **original_framing**: similarity=0.102, lengths 396 ↔ 429
- **synthesized_position**: similarity=0.005, lengths 1178 ↔ 884
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.078, lengths 532 ↔ 292
- **original_framing**: similarity=0.299, lengths 396 ↔ 340
- **synthesized_position**: similarity=0.015, lengths 1178 ↔ 738
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.492, lengths 532 ↔ 342
- **original_framing**: similarity=0.148, lengths 396 ↔ 376
- **synthesized_position**: similarity=0.014, lengths 1178 ↔ 729
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.625, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.405, lengths 532 ↔ 475
- **original_framing**: similarity=0.097, lengths 396 ↔ 303
- **synthesized_position**: similarity=0.015, lengths 1178 ↔ 796
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.400, counts 6 ↔ 8
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.382, lengths 532 ↔ 626
- **original_framing**: similarity=0.336, lengths 396 ↔ 355
- **synthesized_position**: similarity=0.022, lengths 1178 ↔ 935
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.973, lengths 375 ↔ 355
- **original_framing**: similarity=0.646, lengths 328 ↔ 300
- **synthesized_position**: similarity=0.326, lengths 655 ↔ 586
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.166, lengths 375 ↔ 419
- **original_framing**: similarity=0.016, lengths 328 ↔ 313
- **synthesized_position**: similarity=0.152, lengths 655 ↔ 610
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.850, lengths 375 ↔ 489
- **original_framing**: similarity=0.238, lengths 328 ↔ 429
- **synthesized_position**: similarity=0.191, lengths 655 ↔ 884
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.123, lengths 375 ↔ 292
- **original_framing**: similarity=0.404, lengths 328 ↔ 340
- **synthesized_position**: similarity=0.293, lengths 655 ↔ 738
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.530, lengths 375 ↔ 342
- **original_framing**: similarity=0.466, lengths 328 ↔ 376
- **synthesized_position**: similarity=0.186, lengths 655 ↔ 729
- **live_constraints**: jaccard=0.091, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.444, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.431, lengths 375 ↔ 475
- **original_framing**: similarity=0.127, lengths 328 ↔ 303
- **synthesized_position**: similarity=0.249, lengths 655 ↔ 796
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.400, counts 6 ↔ 8
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.484, lengths 375 ↔ 626
- **original_framing**: similarity=0.231, lengths 328 ↔ 355
- **synthesized_position**: similarity=0.147, lengths 655 ↔ 935
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.171, lengths 355 ↔ 419
- **original_framing**: similarity=0.020, lengths 300 ↔ 313
- **synthesized_position**: similarity=0.145, lengths 586 ↔ 610
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.822, lengths 355 ↔ 489
- **original_framing**: similarity=0.236, lengths 300 ↔ 429
- **synthesized_position**: similarity=0.276, lengths 586 ↔ 884
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.127, lengths 355 ↔ 292
- **original_framing**: similarity=0.487, lengths 300 ↔ 340
- **synthesized_position**: similarity=0.266, lengths 586 ↔ 738
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.488, lengths 355 ↔ 342
- **original_framing**: similarity=0.663, lengths 300 ↔ 376
- **synthesized_position**: similarity=0.236, lengths 586 ↔ 729
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.625, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.441, lengths 355 ↔ 475
- **original_framing**: similarity=0.113, lengths 300 ↔ 303
- **synthesized_position**: similarity=0.278, lengths 586 ↔ 796
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.400, counts 6 ↔ 8
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.453, lengths 355 ↔ 626
- **original_framing**: similarity=0.241, lengths 300 ↔ 355
- **synthesized_position**: similarity=0.213, lengths 586 ↔ 935
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.121, lengths 419 ↔ 489
- **original_framing**: similarity=0.067, lengths 313 ↔ 429
- **synthesized_position**: similarity=0.103, lengths 610 ↔ 884
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.065, lengths 419 ↔ 292
- **original_framing**: similarity=0.080, lengths 313 ↔ 340
- **synthesized_position**: similarity=0.147, lengths 610 ↔ 738
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.155, lengths 419 ↔ 342
- **original_framing**: similarity=0.102, lengths 313 ↔ 376
- **synthesized_position**: similarity=0.075, lengths 610 ↔ 729
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.167, counts 7 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.154, lengths 419 ↔ 475
- **original_framing**: similarity=0.075, lengths 313 ↔ 303
- **synthesized_position**: similarity=0.198, lengths 610 ↔ 796
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.154, counts 7 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.117, lengths 419 ↔ 626
- **original_framing**: similarity=0.033, lengths 313 ↔ 355
- **synthesized_position**: similarity=0.076, lengths 610 ↔ 935
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.083, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.120, lengths 489 ↔ 292
- **original_framing**: similarity=0.257, lengths 429 ↔ 340
- **synthesized_position**: similarity=0.211, lengths 884 ↔ 738
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.351, lengths 489 ↔ 342
- **original_framing**: similarity=0.251, lengths 429 ↔ 376
- **synthesized_position**: similarity=0.358, lengths 884 ↔ 729
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.398, lengths 489 ↔ 475
- **original_framing**: similarity=0.183, lengths 429 ↔ 303
- **synthesized_position**: similarity=0.211, lengths 884 ↔ 796
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 5 ↔ 8
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.357, lengths 489 ↔ 626
- **original_framing**: similarity=0.209, lengths 429 ↔ 355
- **synthesized_position**: similarity=0.205, lengths 884 ↔ 935
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.063, lengths 292 ↔ 342
- **original_framing**: similarity=0.575, lengths 340 ↔ 376
- **synthesized_position**: similarity=0.308, lengths 738 ↔ 729
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.857, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.065, lengths 292 ↔ 475
- **original_framing**: similarity=0.093, lengths 340 ↔ 303
- **synthesized_position**: similarity=0.218, lengths 738 ↔ 796
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.556, counts 6 ↔ 8
- **dropped_threads**: jaccard=0.667, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.044, lengths 292 ↔ 626
- **original_framing**: similarity=0.115, lengths 340 ↔ 355
- **synthesized_position**: similarity=0.221, lengths 738 ↔ 935
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.438, lengths 342 ↔ 475
- **original_framing**: similarity=0.085, lengths 376 ↔ 303
- **synthesized_position**: similarity=0.194, lengths 729 ↔ 796
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.440, lengths 342 ↔ 626
- **original_framing**: similarity=0.112, lengths 376 ↔ 355
- **synthesized_position**: similarity=0.179, lengths 729 ↔ 935
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.247, lengths 475 ↔ 626
- **original_framing**: similarity=0.173, lengths 303 ↔ 355
- **synthesized_position**: similarity=0.188, lengths 796 ↔ 935
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.167, counts 8 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0
