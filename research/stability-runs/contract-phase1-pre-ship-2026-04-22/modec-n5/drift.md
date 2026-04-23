# Extraction drift report — contract-phase1-pre-ship

Generated: 2026-04-22T20:41:50Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260422T204150Zdrift0, 20260422T204202Zdrift1, 20260422T204215Zdrift2, 20260422T204225Zdrift3, 20260422T204243Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.365 | 0.102 | 0.717 |
| `original_framing` | similarity | 0.223 | 0.162 | 0.355 |
| `synthesized_position` | similarity | 0.243 | 0.145 | 0.401 |
| `live_constraints` | jaccard | 0.000 | 0.000 | 0.000 |
| `reasoning_passages` | jaccard | 0.493 | 0.083 | 1.000 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |

**Fabricated-quote counts per run:** [0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260422T204150Zdrift0` vs `20260422T204202Zdrift1`
- **decision_situation**: similarity=0.495, lengths 678 ↔ 740
- **original_framing**: similarity=0.177, lengths 510 ↔ 460
- **synthesized_position**: similarity=0.285, lengths 921 ↔ 1151
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204150Zdrift0` vs `20260422T204215Zdrift2`
- **decision_situation**: similarity=0.494, lengths 678 ↔ 520
- **original_framing**: similarity=0.200, lengths 510 ↔ 429
- **synthesized_position**: similarity=0.281, lengths 921 ↔ 991
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204150Zdrift0` vs `20260422T204225Zdrift3`
- **decision_situation**: similarity=0.114, lengths 678 ↔ 479
- **original_framing**: similarity=0.250, lengths 510 ↔ 306
- **synthesized_position**: similarity=0.154, lengths 921 ↔ 728
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.083, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204150Zdrift0` vs `20260422T204243Zdrift4`
- **decision_situation**: similarity=0.610, lengths 678 ↔ 562
- **original_framing**: similarity=0.182, lengths 510 ↔ 434
- **synthesized_position**: similarity=0.175, lengths 921 ↔ 865
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.833, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204202Zdrift1` vs `20260422T204215Zdrift2`
- **decision_situation**: similarity=0.429, lengths 740 ↔ 520
- **original_framing**: similarity=0.279, lengths 460 ↔ 429
- **synthesized_position**: similarity=0.401, lengths 1151 ↔ 991
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204202Zdrift1` vs `20260422T204225Zdrift3`
- **decision_situation**: similarity=0.107, lengths 740 ↔ 479
- **original_framing**: similarity=0.162, lengths 460 ↔ 306
- **synthesized_position**: similarity=0.255, lengths 1151 ↔ 728
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.091, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204202Zdrift1` vs `20260422T204243Zdrift4`
- **decision_situation**: similarity=0.369, lengths 740 ↔ 562
- **original_framing**: similarity=0.289, lengths 460 ↔ 434
- **synthesized_position**: similarity=0.145, lengths 1151 ↔ 865
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204215Zdrift2` vs `20260422T204225Zdrift3`
- **decision_situation**: similarity=0.214, lengths 520 ↔ 479
- **original_framing**: similarity=0.166, lengths 429 ↔ 306
- **synthesized_position**: similarity=0.205, lengths 991 ↔ 728
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.091, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204215Zdrift2` vs `20260422T204243Zdrift4`
- **decision_situation**: similarity=0.717, lengths 520 ↔ 562
- **original_framing**: similarity=0.355, lengths 429 ↔ 434
- **synthesized_position**: similarity=0.270, lengths 991 ↔ 865
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=1.000, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T204225Zdrift3` vs `20260422T204243Zdrift4`
- **decision_situation**: similarity=0.102, lengths 479 ↔ 562
- **original_framing**: similarity=0.170, lengths 306 ↔ 434
- **synthesized_position**: similarity=0.255, lengths 728 ↔ 865
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.091, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0
