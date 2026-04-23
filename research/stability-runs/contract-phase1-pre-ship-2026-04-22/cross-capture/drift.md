# Extraction drift report — contract-phase1-pre-ship-cross

Generated: 2026-04-22T20:46:15Z
Conversation: `<SKILL_ROOT>/tmp_placeholder` (? bytes)
Runs: 9
Run IDs: extraction_20260421T144534Z, extraction_20260421T162225Z, extraction_20260421T172513Z, extraction_20260422T091837Z, extraction_20260422T100308Z, extraction_20260422T113930Z, extraction_20260422T123205Z, extraction_20260422T130506Z, extraction_20260422T155622Z

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.367 | 0.134 | 0.946 |
| `original_framing` | similarity | 0.209 | 0.084 | 0.504 |
| `synthesized_position` | similarity | 0.169 | 0.006 | 0.586 |
| `live_constraints` | jaccard | 0.010 | 0.000 | 0.125 |
| `reasoning_passages` | jaccard | 0.357 | 0.083 | 1.000 |
| `dropped_threads` | jaccard | 0.132 | 0.000 | 1.000 |

**Fabricated-quote counts per run:** [0, 0, 0, 0, 0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.631, lengths 441 ↔ 500
- **original_framing**: similarity=0.084, lengths 423 ↔ 410
- **synthesized_position**: similarity=0.018, lengths 894 ↔ 872
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 5 ↔ 7
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.359, lengths 441 ↔ 490
- **original_framing**: similarity=0.136, lengths 423 ↔ 489
- **synthesized_position**: similarity=0.012, lengths 894 ↔ 766
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.083, counts 5 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.217, lengths 441 ↔ 387
- **original_framing**: similarity=0.146, lengths 423 ↔ 302
- **synthesized_position**: similarity=0.011, lengths 894 ↔ 773
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.473, lengths 441 ↔ 727
- **original_framing**: similarity=0.157, lengths 423 ↔ 443
- **synthesized_position**: similarity=0.009, lengths 894 ↔ 891
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.312, lengths 441 ↔ 398
- **original_framing**: similarity=0.101, lengths 423 ↔ 385
- **synthesized_position**: similarity=0.006, lengths 894 ↔ 665
- **live_constraints**: jaccard=0.125, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.182, counts 5 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.400, lengths 441 ↔ 638
- **original_framing**: similarity=0.165, lengths 423 ↔ 387
- **synthesized_position**: similarity=0.016, lengths 894 ↔ 836
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.306, lengths 441 ↔ 410
- **original_framing**: similarity=0.175, lengths 423 ↔ 422
- **synthesized_position**: similarity=0.006, lengths 894 ↔ 713
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.376, lengths 441 ↔ 648
- **original_framing**: similarity=0.171, lengths 423 ↔ 502
- **synthesized_position**: similarity=0.019, lengths 894 ↔ 809
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.404, lengths 500 ↔ 490
- **original_framing**: similarity=0.283, lengths 410 ↔ 489
- **synthesized_position**: similarity=0.154, lengths 872 ↔ 766
- **live_constraints**: jaccard=0.125, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.364, counts 7 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.165, lengths 500 ↔ 387
- **original_framing**: similarity=0.202, lengths 410 ↔ 302
- **synthesized_position**: similarity=0.140, lengths 872 ↔ 773
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.625, counts 7 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.319, lengths 500 ↔ 727
- **original_framing**: similarity=0.159, lengths 410 ↔ 443
- **synthesized_position**: similarity=0.177, lengths 872 ↔ 891
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.249, lengths 500 ↔ 398
- **original_framing**: similarity=0.146, lengths 410 ↔ 385
- **synthesized_position**: similarity=0.290, lengths 872 ↔ 665
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.654, lengths 500 ↔ 638
- **original_framing**: similarity=0.090, lengths 410 ↔ 387
- **synthesized_position**: similarity=0.362, lengths 872 ↔ 836
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.244, lengths 500 ↔ 410
- **original_framing**: similarity=0.375, lengths 410 ↔ 422
- **synthesized_position**: similarity=0.202, lengths 872 ↔ 713
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.415, lengths 500 ↔ 648
- **original_framing**: similarity=0.154, lengths 410 ↔ 502
- **synthesized_position**: similarity=0.174, lengths 872 ↔ 809
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.278, lengths 490 ↔ 387
- **original_framing**: similarity=0.187, lengths 489 ↔ 302
- **synthesized_position**: similarity=0.586, lengths 766 ↔ 773
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.273, counts 8 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.299, lengths 490 ↔ 727
- **original_framing**: similarity=0.236, lengths 489 ↔ 443
- **synthesized_position**: similarity=0.237, lengths 766 ↔ 891
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.083, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.619, lengths 490 ↔ 398
- **original_framing**: similarity=0.162, lengths 489 ↔ 385
- **synthesized_position**: similarity=0.212, lengths 766 ↔ 665
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.333, counts 8 ↔ 8
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.239, lengths 490 ↔ 638
- **original_framing**: similarity=0.249, lengths 489 ↔ 387
- **synthesized_position**: similarity=0.152, lengths 766 ↔ 836
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.083, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.582, lengths 490 ↔ 410
- **original_framing**: similarity=0.360, lengths 489 ↔ 422
- **synthesized_position**: similarity=0.161, lengths 766 ↔ 713
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.313, lengths 490 ↔ 648
- **original_framing**: similarity=0.224, lengths 489 ↔ 502
- **synthesized_position**: similarity=0.217, lengths 766 ↔ 809
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.083, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.176, lengths 387 ↔ 727
- **original_framing**: similarity=0.164, lengths 302 ↔ 443
- **synthesized_position**: similarity=0.221, lengths 773 ↔ 891
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.897, lengths 387 ↔ 398
- **original_framing**: similarity=0.504, lengths 302 ↔ 385
- **synthesized_position**: similarity=0.182, lengths 773 ↔ 665
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.556, counts 6 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.144, lengths 387 ↔ 638
- **original_framing**: similarity=0.099, lengths 302 ↔ 387
- **synthesized_position**: similarity=0.121, lengths 773 ↔ 836
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.841, lengths 387 ↔ 410
- **original_framing**: similarity=0.146, lengths 302 ↔ 422
- **synthesized_position**: similarity=0.205, lengths 773 ↔ 713
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.137, lengths 387 ↔ 648
- **original_framing**: similarity=0.144, lengths 302 ↔ 502
- **synthesized_position**: similarity=0.243, lengths 773 ↔ 809
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.229, lengths 727 ↔ 398
- **original_framing**: similarity=0.123, lengths 443 ↔ 385
- **synthesized_position**: similarity=0.183, lengths 891 ↔ 665
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.182, counts 5 ↔ 8
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.330, lengths 727 ↔ 638
- **original_framing**: similarity=0.289, lengths 443 ↔ 387
- **synthesized_position**: similarity=0.156, lengths 891 ↔ 836
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.229, lengths 727 ↔ 410
- **original_framing**: similarity=0.268, lengths 443 ↔ 422
- **synthesized_position**: similarity=0.118, lengths 891 ↔ 713
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.492, lengths 727 ↔ 648
- **original_framing**: similarity=0.428, lengths 443 ↔ 502
- **synthesized_position**: similarity=0.287, lengths 891 ↔ 809
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.147, lengths 398 ↔ 638
- **original_framing**: similarity=0.088, lengths 385 ↔ 387
- **synthesized_position**: similarity=0.284, lengths 665 ↔ 836
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.182, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.946, lengths 398 ↔ 410
- **original_framing**: similarity=0.131, lengths 385 ↔ 422
- **synthesized_position**: similarity=0.324, lengths 665 ↔ 713
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.444, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.138, lengths 398 ↔ 648
- **original_framing**: similarity=0.117, lengths 385 ↔ 502
- **synthesized_position**: similarity=0.164, lengths 665 ↔ 809
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.182, counts 8 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.139, lengths 638 ↔ 410
- **original_framing**: similarity=0.336, lengths 387 ↔ 422
- **synthesized_position**: similarity=0.192, lengths 836 ↔ 713
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.376, lengths 638 ↔ 648
- **original_framing**: similarity=0.414, lengths 387 ↔ 502
- **synthesized_position**: similarity=0.098, lengths 836 ↔ 809
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.134, lengths 410 ↔ 648
- **original_framing**: similarity=0.303, lengths 422 ↔ 502
- **synthesized_position**: similarity=0.152, lengths 713 ↔ 809
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **fabricated**: a=0, b=0
