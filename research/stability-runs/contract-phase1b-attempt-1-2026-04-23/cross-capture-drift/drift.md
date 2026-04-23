# Extraction drift report — contract-phase1b-cross

Generated: 2026-04-23T08:55:04Z
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
| `decision_situation` | similarity | 0.280 | 0.044 | 0.771 |
| `original_framing` | similarity | 0.136 | 0.026 | 0.370 |
| `synthesized_position` | similarity | 0.162 | 0.030 | 0.421 |
| `live_constraints` | jaccard | 0.050 | 0.000 | 0.375 |
| `reasoning_passages` | jaccard | 0.396 | 0.182 | 0.714 |
| `dropped_threads` | jaccard | 0.013 | 0.000 | 0.250 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | 0.438 | 0.100 | 1.000 |
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | 0.787 | 0.620 | 1.000 |

**`invalid_key_rate` per run:** [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
**`invalid_key_rate` overall:** 0.000 (0 invalid of 46 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0, 0, 0, 1, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.257, lengths 400 ↔ 518
- **original_framing**: similarity=0.204, lengths 426 ↔ 340
- **synthesized_position**: similarity=0.142, lengths 755 ↔ 698
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.205, lengths 400 ↔ 382
- **original_framing**: similarity=0.026, lengths 426 ↔ 356
- **synthesized_position**: similarity=0.163, lengths 755 ↔ 581
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.184, lengths 400 ↔ 570
- **original_framing**: similarity=0.089, lengths 426 ↔ 431
- **synthesized_position**: similarity=0.154, lengths 755 ↔ 800
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.358, lengths 400 ↔ 327
- **original_framing**: similarity=0.105, lengths 426 ↔ 317
- **synthesized_position**: similarity=0.157, lengths 755 ↔ 610
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.330, lengths 400 ↔ 285
- **original_framing**: similarity=0.131, lengths 426 ↔ 369
- **synthesized_position**: similarity=0.238, lengths 755 ↔ 663
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.265, lengths 400 ↔ 468
- **original_framing**: similarity=0.138, lengths 426 ↔ 427
- **synthesized_position**: similarity=0.148, lengths 755 ↔ 776
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.335, lengths 400 ↔ 531
- **original_framing**: similarity=0.230, lengths 426 ↔ 407
- **synthesized_position**: similarity=0.155, lengths 755 ↔ 689
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 7 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.308, lengths 400 ↔ 281
- **original_framing**: similarity=0.192, lengths 426 ↔ 367
- **synthesized_position**: similarity=0.079, lengths 755 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.273, counts 7 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.371, lengths 518 ↔ 382
- **original_framing**: similarity=0.055, lengths 340 ↔ 356
- **synthesized_position**: similarity=0.317, lengths 698 ↔ 581
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.263, lengths 518 ↔ 570
- **original_framing**: similarity=0.127, lengths 340 ↔ 431
- **synthesized_position**: similarity=0.053, lengths 698 ↔ 800
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.123, lengths 518 ↔ 327
- **original_framing**: similarity=0.280, lengths 340 ↔ 317
- **synthesized_position**: similarity=0.209, lengths 698 ↔ 610
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.142, lengths 518 ↔ 285
- **original_framing**: similarity=0.327, lengths 340 ↔ 369
- **synthesized_position**: similarity=0.279, lengths 698 ↔ 663
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.136, lengths 518 ↔ 468
- **original_framing**: similarity=0.154, lengths 340 ↔ 427
- **synthesized_position**: similarity=0.030, lengths 698 ↔ 776
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.263, lengths 518 ↔ 531
- **original_framing**: similarity=0.201, lengths 340 ↔ 407
- **synthesized_position**: similarity=0.040, lengths 698 ↔ 689
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 6 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=1.000, counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.115, lengths 518 ↔ 281
- **original_framing**: similarity=0.105, lengths 340 ↔ 367
- **synthesized_position**: similarity=0.139, lengths 698 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.330, lengths 382 ↔ 570
- **original_framing**: similarity=0.058, lengths 356 ↔ 431
- **synthesized_position**: similarity=0.162, lengths 581 ↔ 800
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.107, lengths 382 ↔ 327
- **original_framing**: similarity=0.033, lengths 356 ↔ 317
- **synthesized_position**: similarity=0.343, lengths 581 ↔ 610
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.150, lengths 382 ↔ 285
- **original_framing**: similarity=0.047, lengths 356 ↔ 369
- **synthesized_position**: similarity=0.421, lengths 581 ↔ 663
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.195, lengths 382 ↔ 468
- **original_framing**: similarity=0.033, lengths 356 ↔ 427
- **synthesized_position**: similarity=0.071, lengths 581 ↔ 776
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.215, lengths 382 ↔ 531
- **original_framing**: similarity=0.029, lengths 356 ↔ 407
- **synthesized_position**: similarity=0.058, lengths 581 ↔ 689
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.286, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 6 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.181, lengths 382 ↔ 281
- **original_framing**: similarity=0.050, lengths 356 ↔ 367
- **synthesized_position**: similarity=0.177, lengths 581 ↔ 642
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.116, lengths 570 ↔ 327
- **original_framing**: similarity=0.096, lengths 431 ↔ 317
- **synthesized_position**: similarity=0.156, lengths 800 ↔ 610
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.044, lengths 570 ↔ 285
- **original_framing**: similarity=0.122, lengths 431 ↔ 369
- **synthesized_position**: similarity=0.131, lengths 800 ↔ 663
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.191, lengths 570 ↔ 468
- **original_framing**: similarity=0.161, lengths 431 ↔ 427
- **synthesized_position**: similarity=0.137, lengths 800 ↔ 776
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.154, lengths 570 ↔ 531
- **original_framing**: similarity=0.189, lengths 431 ↔ 407
- **synthesized_position**: similarity=0.107, lengths 800 ↔ 689
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.286, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.092, lengths 570 ↔ 281
- **original_framing**: similarity=0.120, lengths 431 ↔ 367
- **synthesized_position**: similarity=0.082, lengths 800 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.771, lengths 327 ↔ 285
- **original_framing**: similarity=0.111, lengths 317 ↔ 369
- **synthesized_position**: similarity=0.284, lengths 610 ↔ 663
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.556, lengths 327 ↔ 468
- **original_framing**: similarity=0.094, lengths 317 ↔ 427
- **synthesized_position**: similarity=0.180, lengths 610 ↔ 776
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.224, lengths 327 ↔ 531
- **original_framing**: similarity=0.163, lengths 317 ↔ 407
- **synthesized_position**: similarity=0.149, lengths 610 ↔ 689
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 6 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.612, lengths 327 ↔ 281
- **original_framing**: similarity=0.140, lengths 317 ↔ 367
- **synthesized_position**: similarity=0.203, lengths 610 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.534, lengths 285 ↔ 468
- **original_framing**: similarity=0.196, lengths 369 ↔ 427
- **synthesized_position**: similarity=0.076, lengths 663 ↔ 776
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.311, lengths 285 ↔ 531
- **original_framing**: similarity=0.168, lengths 369 ↔ 407
- **synthesized_position**: similarity=0.071, lengths 663 ↔ 689
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.286, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.724, lengths 285 ↔ 281
- **original_framing**: similarity=0.122, lengths 369 ↔ 367
- **synthesized_position**: similarity=0.234, lengths 663 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.200, lengths 468 ↔ 531
- **original_framing**: similarity=0.151, lengths 427 ↔ 407
- **synthesized_position**: similarity=0.277, lengths 776 ↔ 689
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.286, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.497, lengths 468 ↔ 281
- **original_framing**: similarity=0.091, lengths 427 ↔ 367
- **synthesized_position**: similarity=0.144, lengths 776 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.209, lengths 531 ↔ 281
- **original_framing**: similarity=0.370, lengths 407 ↔ 367
- **synthesized_position**: similarity=0.068, lengths 689 ↔ 642
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 4 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=1, b=0
