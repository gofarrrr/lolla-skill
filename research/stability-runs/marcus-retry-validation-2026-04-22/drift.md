# Extraction drift report — marcus-retry-validation

Generated: 2026-04-22T14:37:48Z
Conversation: `/private/tmp/lolla_20260422T113930Z_conversation.txt` (25742 bytes)
Runs: 3
Run IDs: 20260422T143748Zdrift0, 20260422T143756Zdrift1, 20260422T143804Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.389 | 0.341 | 0.453 |
| `original_framing` | similarity | 0.500 | 0.358 | 0.748 |
| `synthesized_position` | similarity | 0.518 | 0.477 | 0.556 |
| `live_constraints` | jaccard | 0.000 | 0.000 | 0.000 |
| `reasoning_passages` | jaccard | 0.690 | 0.571 | 0.833 |
| `dropped_threads` | jaccard | 0.083 | 0.000 | 0.250 |

**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260422T143748Zdrift0` vs `20260422T143756Zdrift1`
- **decision_situation**: similarity=0.341, lengths 401 ↔ 630
- **original_framing**: similarity=0.395, lengths 358 ↔ 453
- **synthesized_position**: similarity=0.477, lengths 734 ↔ 760
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **fabricated**: a=0, b=0

### `20260422T143748Zdrift0` vs `20260422T143804Zdrift2`
- **decision_situation**: similarity=0.453, lengths 401 ↔ 558
- **original_framing**: similarity=0.748, lengths 358 ↔ 380
- **synthesized_position**: similarity=0.556, lengths 734 ↔ 909
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T143756Zdrift1` vs `20260422T143804Zdrift2`
- **decision_situation**: similarity=0.374, lengths 630 ↔ 558
- **original_framing**: similarity=0.358, lengths 453 ↔ 380
- **synthesized_position**: similarity=0.522, lengths 760 ↔ 909
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **fabricated**: a=0, b=0
