# Extraction drift report — marcus-retry-natural-test

Generated: 2026-04-22T14:39:07Z
Conversation: `/private/tmp/lolla_20260421T162225Z_conversation.txt` (25868 bytes)
Runs: 5
Run IDs: 20260422T143907Zdrift0, 20260422T143924Zdrift1, 20260422T143937Zdrift2, 20260422T143948Zdrift3, 20260422T143959Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.509 | 0.258 | 0.915 |
| `original_framing` | similarity | 0.211 | 0.093 | 0.279 |
| `synthesized_position` | similarity | 0.298 | 0.054 | 0.410 |
| `live_constraints` | jaccard | 0.000 | 0.000 | 0.000 |
| `reasoning_passages` | jaccard | 0.490 | 0.182 | 1.000 |
| `dropped_threads` | jaccard | 0.087 | 0.000 | 0.667 |

**Fabricated-quote counts per run:** [0, 0, 0, 0, 1]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260422T143907Zdrift0` vs `20260422T143924Zdrift1`
- **decision_situation**: similarity=0.358, lengths 514 ↔ 643
- **original_framing**: similarity=0.274, lengths 501 ↔ 427
- **synthesized_position**: similarity=0.260, lengths 684 ↔ 917
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `20260422T143907Zdrift0` vs `20260422T143937Zdrift2`
- **decision_situation**: similarity=0.444, lengths 514 ↔ 558
- **original_framing**: similarity=0.151, lengths 501 ↔ 450
- **synthesized_position**: similarity=0.324, lengths 684 ↔ 866
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `20260422T143907Zdrift0` vs `20260422T143948Zdrift3`
- **decision_situation**: similarity=0.743, lengths 514 ↔ 590
- **original_framing**: similarity=0.093, lengths 501 ↔ 424
- **synthesized_position**: similarity=0.378, lengths 684 ↔ 925
- **live_constraints**: jaccard=0.000, counts 4 ↔ 6
- **reasoning_passages**: jaccard=0.182, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T143907Zdrift0` vs `20260422T143959Zdrift4`
- **decision_situation**: similarity=0.772, lengths 514 ↔ 571
- **original_framing**: similarity=0.225, lengths 501 ↔ 504
- **synthesized_position**: similarity=0.410, lengths 684 ↔ 824
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.625, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=1

### `20260422T143924Zdrift1` vs `20260422T143937Zdrift2`
- **decision_situation**: similarity=0.386, lengths 643 ↔ 558
- **original_framing**: similarity=0.198, lengths 427 ↔ 450
- **synthesized_position**: similarity=0.151, lengths 917 ↔ 866
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **fabricated**: a=0, b=0

### `20260422T143924Zdrift1` vs `20260422T143948Zdrift3`
- **decision_situation**: similarity=0.360, lengths 643 ↔ 590
- **original_framing**: similarity=0.249, lengths 427 ↔ 424
- **synthesized_position**: similarity=0.054, lengths 917 ↔ 925
- **live_constraints**: jaccard=0.000, counts 4 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T143924Zdrift1` vs `20260422T143959Zdrift4`
- **decision_situation**: similarity=0.442, lengths 643 ↔ 571
- **original_framing**: similarity=0.206, lengths 427 ↔ 504
- **synthesized_position**: similarity=0.358, lengths 917 ↔ 824
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **fabricated**: a=0, b=1

### `20260422T143937Zdrift2` vs `20260422T143948Zdrift3`
- **decision_situation**: similarity=0.258, lengths 558 ↔ 590
- **original_framing**: similarity=0.279, lengths 450 ↔ 424
- **synthesized_position**: similarity=0.305, lengths 866 ↔ 925
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.667, counts 3 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T143937Zdrift2` vs `20260422T143959Zdrift4`
- **decision_situation**: similarity=0.409, lengths 558 ↔ 571
- **original_framing**: similarity=0.164, lengths 450 ↔ 504
- **synthesized_position**: similarity=0.402, lengths 866 ↔ 824
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **fabricated**: a=0, b=1

### `20260422T143948Zdrift3` vs `20260422T143959Zdrift4`
- **decision_situation**: similarity=0.915, lengths 590 ↔ 571
- **original_framing**: similarity=0.272, lengths 424 ↔ 504
- **synthesized_position**: similarity=0.336, lengths 925 ↔ 824
- **live_constraints**: jaccard=0.000, counts 6 ↔ 4
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=1
