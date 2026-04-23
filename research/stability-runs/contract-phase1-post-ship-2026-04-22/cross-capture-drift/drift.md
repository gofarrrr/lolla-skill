# Extraction drift report — contract-phase1-post-ship-cross

Generated: 2026-04-22T21:05:50Z
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
| `decision_situation` | similarity | 0.359 | 0.082 | 0.910 |
| `original_framing` | similarity | 0.163 | 0.054 | 0.449 |
| `synthesized_position` | similarity | 0.175 | 0.026 | 0.451 |
| `live_constraints` | jaccard | 0.064 | 0.000 | 0.500 |
| `reasoning_passages` | jaccard | 0.418 | 0.300 | 0.667 |
| `dropped_threads` | jaccard | 0.090 | 0.000 | 0.333 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | 0.332 | 0.100 | 0.714 |

**`invalid_key_rate` per run:** [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
**`invalid_key_rate` overall:** 0.000 (0 invalid of 50 total constraints)
**Fabricated-quote counts per run:** [0, 0, 1, 2, 0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.804, lengths 503 ↔ 412
- **original_framing**: similarity=0.125, lengths 366 ↔ 452
- **synthesized_position**: similarity=0.051, lengths 919 ↔ 655
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.813, lengths 503 ↔ 395
- **original_framing**: similarity=0.166, lengths 366 ↔ 441
- **synthesized_position**: similarity=0.045, lengths 919 ↔ 634
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=1

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.464, lengths 503 ↔ 433
- **original_framing**: similarity=0.244, lengths 366 ↔ 389
- **synthesized_position**: similarity=0.026, lengths 919 ↔ 614
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=2

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.281, lengths 503 ↔ 267
- **original_framing**: similarity=0.114, lengths 366 ↔ 301
- **synthesized_position**: similarity=0.056, lengths 919 ↔ 687
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.444, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.240, lengths 503 ↔ 304
- **original_framing**: similarity=0.207, lengths 366 ↔ 360
- **synthesized_position**: similarity=0.042, lengths 919 ↔ 620
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.536, lengths 503 ↔ 456
- **original_framing**: similarity=0.118, lengths 366 ↔ 326
- **synthesized_position**: similarity=0.040, lengths 919 ↔ 588
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.114, lengths 503 ↔ 319
- **original_framing**: similarity=0.076, lengths 366 ↔ 269
- **synthesized_position**: similarity=0.053, lengths 919 ↔ 578
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.164, lengths 503 ↔ 461
- **original_framing**: similarity=0.070, lengths 366 ↔ 438
- **synthesized_position**: similarity=0.225, lengths 919 ↔ 838
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.910, lengths 412 ↔ 395
- **original_framing**: similarity=0.092, lengths 452 ↔ 441
- **synthesized_position**: similarity=0.033, lengths 655 ↔ 634
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=1

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.580, lengths 412 ↔ 433
- **original_framing**: similarity=0.278, lengths 452 ↔ 389
- **synthesized_position**: similarity=0.079, lengths 655 ↔ 614
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=2

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.239, lengths 412 ↔ 267
- **original_framing**: similarity=0.189, lengths 452 ↔ 301
- **synthesized_position**: similarity=0.253, lengths 655 ↔ 687
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.625, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.221, lengths 412 ↔ 304
- **original_framing**: similarity=0.054, lengths 452 ↔ 360
- **synthesized_position**: similarity=0.334, lengths 655 ↔ 620
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.611, lengths 412 ↔ 456
- **original_framing**: similarity=0.278, lengths 452 ↔ 326
- **synthesized_position**: similarity=0.235, lengths 655 ↔ 588
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.101, lengths 412 ↔ 319
- **original_framing**: similarity=0.094, lengths 452 ↔ 269
- **synthesized_position**: similarity=0.451, lengths 655 ↔ 578
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.165, lengths 412 ↔ 461
- **original_framing**: similarity=0.265, lengths 452 ↔ 438
- **synthesized_position**: similarity=0.161, lengths 655 ↔ 838
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.546, lengths 395 ↔ 433
- **original_framing**: similarity=0.111, lengths 441 ↔ 389
- **synthesized_position**: similarity=0.194, lengths 634 ↔ 614
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=1, b=2

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.350, lengths 395 ↔ 267
- **original_framing**: similarity=0.151, lengths 441 ↔ 301
- **synthesized_position**: similarity=0.071, lengths 634 ↔ 687
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.333, counts 6 ↔ 6
- **fabricated**: a=1, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.338, lengths 395 ↔ 304
- **original_framing**: similarity=0.105, lengths 441 ↔ 360
- **synthesized_position**: similarity=0.056, lengths 634 ↔ 620
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.500, counts 6 ↔ 6
- **fabricated**: a=1, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.649, lengths 395 ↔ 456
- **original_framing**: similarity=0.091, lengths 441 ↔ 326
- **synthesized_position**: similarity=0.244, lengths 634 ↔ 588
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.500, counts 6 ↔ 6
- **fabricated**: a=1, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.246, lengths 395 ↔ 319
- **original_framing**: similarity=0.107, lengths 441 ↔ 269
- **synthesized_position**: similarity=0.315, lengths 634 ↔ 578
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.500, counts 6 ↔ 6
- **fabricated**: a=1, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.231, lengths 395 ↔ 461
- **original_framing**: similarity=0.073, lengths 441 ↔ 438
- **synthesized_position**: similarity=0.124, lengths 634 ↔ 838
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=1, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.214, lengths 433 ↔ 267
- **original_framing**: similarity=0.304, lengths 389 ↔ 301
- **synthesized_position**: similarity=0.132, lengths 614 ↔ 687
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=2, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.176, lengths 433 ↔ 304
- **original_framing**: similarity=0.139, lengths 389 ↔ 360
- **synthesized_position**: similarity=0.227, lengths 614 ↔ 620
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=2, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.479, lengths 433 ↔ 456
- **original_framing**: similarity=0.266, lengths 389 ↔ 326
- **synthesized_position**: similarity=0.160, lengths 614 ↔ 588
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 5 ↔ 6
- **fabricated**: a=2, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.093, lengths 433 ↔ 319
- **original_framing**: similarity=0.097, lengths 389 ↔ 269
- **synthesized_position**: similarity=0.116, lengths 614 ↔ 578
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=2, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.172, lengths 433 ↔ 461
- **original_framing**: similarity=0.215, lengths 389 ↔ 438
- **synthesized_position**: similarity=0.099, lengths 614 ↔ 838
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 5
- **fabricated**: a=2, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.588, lengths 267 ↔ 304
- **original_framing**: similarity=0.206, lengths 301 ↔ 360
- **synthesized_position**: similarity=0.332, lengths 687 ↔ 620
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.333, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.343, lengths 267 ↔ 456
- **original_framing**: similarity=0.223, lengths 301 ↔ 326
- **synthesized_position**: similarity=0.166, lengths 687 ↔ 588
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.444, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.200, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.601, lengths 267 ↔ 319
- **original_framing**: similarity=0.449, lengths 301 ↔ 269
- **synthesized_position**: similarity=0.199, lengths 687 ↔ 578
- **live_constraints**: jaccard=0.500, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.300, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.714, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.110, lengths 267 ↔ 461
- **original_framing**: similarity=0.119, lengths 301 ↔ 438
- **synthesized_position**: similarity=0.172, lengths 687 ↔ 838
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.326, lengths 304 ↔ 456
- **original_framing**: similarity=0.064, lengths 360 ↔ 326
- **synthesized_position**: similarity=0.311, lengths 620 ↔ 588
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.500, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.552, lengths 304 ↔ 319
- **original_framing**: similarity=0.073, lengths 360 ↔ 269
- **synthesized_position**: similarity=0.307, lengths 620 ↔ 578
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.333, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.115, lengths 304 ↔ 461
- **original_framing**: similarity=0.093, lengths 360 ↔ 438
- **synthesized_position**: similarity=0.262, lengths 620 ↔ 838
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.245, lengths 456 ↔ 319
- **original_framing**: similarity=0.158, lengths 326 ↔ 269
- **synthesized_position**: similarity=0.369, lengths 588 ↔ 578
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.333, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.214, lengths 456 ↔ 461
- **original_framing**: similarity=0.346, lengths 326 ↔ 438
- **synthesized_position**: similarity=0.171, lengths 588 ↔ 838
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.082, lengths 319 ↔ 461
- **original_framing**: similarity=0.093, lengths 269 ↔ 438
- **synthesized_position**: similarity=0.188, lengths 578 ↔ 838
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 5
- **fabricated**: a=0, b=0
